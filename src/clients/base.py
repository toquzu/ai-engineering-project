from abc import ABC, abstractmethod
from dataclasses import dataclass

from schemas import Incident


@dataclass
class Result:
    incident: Incident | None
    provider: str
    model: str
    status: str = "success"
    error: str | None = None
    validation_attempts: int = 1
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_seconds: float | None = None


class LLMClient(ABC):

    @abstractmethod
    def extract(
        self,
        text: str,
        prompt: str,
        params: dict,
    ) -> Result:
        pass