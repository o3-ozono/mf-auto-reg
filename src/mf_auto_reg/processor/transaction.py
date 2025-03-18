"""
Transaction data model for mf-auto-reg.
Defines the structure and validation for transaction data.
"""
from datetime import UTC, datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class TransactionStatus(str, Enum):
    """Enumeration of possible transaction statuses."""
    PENDING = "pending"           # Initial state when transaction is detected
    NOTIFIED = "notified"        # Notification sent to Slack
    APPROVED = "approved"        # User approved for registration
    SKIPPED = "skipped"         # User skipped registration
    REGISTERED = "registered"    # Successfully registered in MoneyForward
    FAILED = "failed"           # Registration failed


class Transaction(BaseModel):
    """Transaction data model."""
    id: UUID = Field(default_factory=uuid4, description="Unique transaction ID")
    email_id: str = Field(..., description="Gmail message ID")
    transaction_date: datetime = Field(..., description="Date and time of the transaction")
    amount: int = Field(..., description="Transaction amount in JPY")
    store: str = Field(..., description="Store name")
    status: TransactionStatus = Field(
        default=TransactionStatus.PENDING,
        description="Current status of the transaction"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Record update timestamp")
    error_message: Optional[str] = Field(default=None, description="Error message if status is FAILED")

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

    @validator("amount")
    def amount_must_be_positive(cls, v: int) -> int:
        """Validate that amount is positive."""
        if v <= 0:
            raise ValueError("Transaction amount must be positive")
        return v

    def update_status(self, status: TransactionStatus, error_message: Optional[str] = None) -> None:
        """
        Update the transaction status and error message.
        
        Args:
            status: New status to set
            error_message: Optional error message when status is FAILED
        """
        self.status = status
        self.error_message = error_message if status == TransactionStatus.FAILED else None
        self.updated_at = datetime.now(UTC)

    @property
    def is_completed(self) -> bool:
        """Check if the transaction processing is completed."""
        return self.status in {
            TransactionStatus.REGISTERED,
            TransactionStatus.SKIPPED,
            TransactionStatus.FAILED
        }

    @property
    def formatted_amount(self) -> str:
        """Format amount with Japanese Yen symbol and thousands separator."""
        return f"¥{self.amount:,}"

    def to_slack_message(self) -> str:
        """Format transaction details for Slack notification."""
        return (
            f"*新しい取引が検出されました*\n"
            f"日時: {self.transaction_date.strftime('%Y-%m-%d %H:%M')}\n"
            f"金額: {self.formatted_amount}\n"
            f"店舗: {self.store}\n"
            f"ステータス: {self.status.value}\n"
            f"{'エラー: ' + self.error_message if self.error_message else ''}"
        ) 
