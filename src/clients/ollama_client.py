
import json
import time

import ollama
from pydantic import ValidationError

from schemas import Incident
from clients.base import LLMClient, Result


class OllamaClient(LLMClient):

    def extract(
        self,
        text: str,
        prompt: str,
        params: dict,
    ) -> Result:

        model = params.get("model", "llama3.2:3b")
        temperature = params.get("temperature", 0.0)
        top_p = params.get("top_p", 1.0)
        timeout = params.get("timeout", 60)

        client = ollama.Client(timeout=timeout)

        start_time = time.perf_counter()

        total_input_tokens = 0
        total_output_tokens = 0

        def generate(messages):
            return client.chat(
                model=model,
                messages=messages,
                format=Incident.model_json_schema(),
                options={
                    "temperature": temperature,
                    "top_p": top_p,
                },
            )

        def validate_response(response):
            data = json.loads(response.message.content)
            return Incident.model_validate(data)

        # First attempt
        response = generate([
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ])

        total_input_tokens += response.prompt_eval_count or 0
        total_output_tokens += response.eval_count or 0

        try:
            incident = validate_response(response)

            return Result(
                incident=incident,
                provider="ollama",
                model=model,
                status="success",
                validation_attempts=1,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                latency_seconds=time.perf_counter() - start_time,
            )

        except (json.JSONDecodeError, ValidationError) as first_error:

            # Second attempt: ask the model to correct its answer
            correction_message = f"""
The previous response did not pass validation.

Validation error:
{first_error}

Previous response:
{response.message.content}

Please analyze the original incident report again.
Correct the errors and return valid JSON matching the required schema.
Do not add explanations or Markdown.
"""

            retry_response = generate([
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
                {"role": "assistant", "content": response.message.content},
                {"role": "user", "content": correction_message},
            ])

            total_input_tokens += retry_response.prompt_eval_count or 0
            total_output_tokens += retry_response.eval_count or 0

            try:
                incident = validate_response(retry_response)

                return Result(
                    incident=incident,
                    provider="ollama",
                    model=model,
                    status="success",
                    validation_attempts=2,
                    input_tokens=total_input_tokens,
                    output_tokens=total_output_tokens,
                    latency_seconds=time.perf_counter() - start_time,
                )

            except (json.JSONDecodeError, ValidationError) as second_error:

                return Result(
                    incident=None,
                    provider="ollama",
                    model=model,
                    status="failed",
                    error=str(second_error),
                    validation_attempts=2,
                    input_tokens=total_input_tokens,
                    output_tokens=total_output_tokens,
                    latency_seconds=time.perf_counter() - start_time,
                )
