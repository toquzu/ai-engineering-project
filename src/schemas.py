
from enum import Enum
from pydantic import BaseModel, Field


class Category(str, Enum):
    PHISHING = "phishing"
    ACCOUNT_COMPROMISE = "account_compromise"
    MALWARE = "malware"
    NETWORK_SECURITY = "network_security"
    DATA_LEAK = "data_leak"
    DATA_LOSS_PREVENTION = "data_loss_prevention"
    CUSTOMER_SUPPORT = "customer_support"
    FRAUD = "fraud"
    AVAILABILITY = "availability"
    PHYSICAL_SECURITY = "physical_security"
    VULNERABILITY = "vulnerability"
    OTHER = "other"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(str, Enum):
    SUSPECTED = "suspected"
    INVESTIGATING = "investigating"
    REPORTED = "reported"
    CONFIRMED_ALERT = "confirmed_alert"
    BLOCKED_BY_CONTROL = "blocked_by_control"


class RecommendedAction(BaseModel):
    action: str = Field(description="Recommended response step")
    priority: int = Field(
        ge=1,
        le=3,
        description="1 is highest priority"
    )


class Incident(BaseModel):
    category: Category
    severity: Severity
    status: Status
    asset: str = Field(
        description="Affected or potentially affected asset"
    )
    summary: str = Field(description="Short incident summary")
    indicators: list[str] = Field(
        description="Evidence found in the text"
    )
    recommended_actions: list[RecommendedAction]
    needs_human_review: bool
