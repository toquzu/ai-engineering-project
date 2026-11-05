
import os
import json
import time

import anthropic
from dotenv import load_dotenv
from pydantic import ValidationError

from schemas import Incident
from clients.base import LLMClient, Result


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

load_dotenv(os.path.join(BASE_DIR, ".env"))


class AnthropicClient(LLMClient):

    def extract(
        self,
        text: str,
        prompt: str,
        params: dict,
    ) -> Result:

        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")

        model = params.get("model", "claude-haiku-5-5")

        client = anthropic.Anthropic(
            api_key=api_key,
            timeout=params.get("timeout", 60),
        )

        start_time = time.perf_counter()

        total_input_tokens = 0
        total_output_tokens = 0

        def generate(messages):
            nonlocal total_input_tokens, total_output_tokens

            response = client.messages.create(
                model=model,
                max_tokens=params.get("max_tokens", 1500),
                system=prompt,
                messages=messages,
            )

            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens

            content = next(
                block.text
                for block in response.content
                if block.type == "text"
            )

            return content

        def validate_response(content):
            data = json.loads(content)
            return Incident.model_validate(data)

        # First attempt
        content = generate([
            {
                "role": "user",
                "content": text,
            }
        ])

        try:
            incident = validate_response(content)

            return Result(
                incident=incident,
                provider="anthropic",
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
{content}

Please analyze the original incident report again.
Correct the errors and return valid JSON matching the required schema.
Do not add explanations or Markdown.
"""

            retry_content = generate([
                {
                    "role": "user",
                    "content": text,
                },
                {
                    "role": "assistant",
                    "content": content,
                },
                {
                    "role": "user",
                    "content": correction_message,
                },
            ])

            try:
                incident = validate_response(retry_content)

                return Result(
                    incident=incident,
                    provider="anthropic",
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
                    provider="anthropic",
                    model=model,
                    status="failed",
                    error=str(second_error),
                    validation_attempts=2,
                    input_tokens=total_input_tokens,
                    output_tokens=total_output_tokens,
                    latency_seconds=time.perf_counter() - start_time,
                )
