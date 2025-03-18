"""
Tests for the transaction data model.
"""
import unittest
from datetime import UTC, datetime, timedelta
from uuid import UUID

from pydantic import ValidationError

from mf_auto_reg.processor.transaction import Transaction, TransactionStatus


class TestTransaction(unittest.TestCase):
    """Test cases for Transaction model."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_transaction = Transaction(
            email_id="test_email_123",
            transaction_date=datetime.now(UTC),
            amount=1000,
            store="Test Store"
        )

    def test_transaction_creation(self):
        """Test basic transaction creation with required fields."""
        transaction = Transaction(
            email_id="test_email_123",
            transaction_date=datetime.now(UTC),
            amount=1000,
            store="Test Store"
        )

        self.assertIsInstance(transaction.id, UUID)
        self.assertEqual(transaction.email_id, "test_email_123")
        self.assertEqual(transaction.amount, 1000)
        self.assertEqual(transaction.store, "Test Store")
        self.assertEqual(transaction.status, TransactionStatus.PENDING)
        self.assertIsNone(transaction.error_message)

    def test_transaction_invalid_amount(self):
        """Test that negative amount raises validation error."""
        with self.assertRaises(ValidationError) as context:
            Transaction(
                email_id="test_email_123",
                transaction_date=datetime.now(UTC),
                amount=-1000,
                store="Test Store"
            )
        
        self.assertIn("Transaction amount must be positive", str(context.exception))

    def test_transaction_zero_amount(self):
        """Test that zero amount raises validation error."""
        with self.assertRaises(ValidationError) as context:
            Transaction(
                email_id="test_email_123",
                transaction_date=datetime.now(UTC),
                amount=0,
                store="Test Store"
            )
        
        self.assertIn("Transaction amount must be positive", str(context.exception))

    def test_update_status(self):
        """Test status update functionality."""
        original_updated_at = self.sample_transaction.updated_at
        
        # Wait a small amount to ensure timestamp difference
        datetime.now(UTC) + timedelta(microseconds=1)
        
        self.sample_transaction.update_status(TransactionStatus.NOTIFIED)
        
        self.assertEqual(self.sample_transaction.status, TransactionStatus.NOTIFIED)
        self.assertIsNone(self.sample_transaction.error_message)
        self.assertGreater(self.sample_transaction.updated_at, original_updated_at)

    def test_update_status_with_error(self):
        """Test status update with error message."""
        error_msg = "Test error message"
        self.sample_transaction.update_status(TransactionStatus.FAILED, error_msg)
        
        self.assertEqual(self.sample_transaction.status, TransactionStatus.FAILED)
        self.assertEqual(self.sample_transaction.error_message, error_msg)

    def test_update_status_clear_error(self):
        """Test that error message is cleared when status is not FAILED."""
        # First set an error
        self.sample_transaction.update_status(TransactionStatus.FAILED, "Test error")
        self.assertIsNotNone(self.sample_transaction.error_message)
        
        # Then update to non-error status
        self.sample_transaction.update_status(TransactionStatus.APPROVED)
        self.assertIsNone(self.sample_transaction.error_message)

    def test_is_completed_property(self):
        """Test is_completed property for different statuses."""
        # Test incomplete statuses
        for status in [TransactionStatus.PENDING, TransactionStatus.NOTIFIED, TransactionStatus.APPROVED]:
            self.sample_transaction.status = status
            self.assertFalse(self.sample_transaction.is_completed)

        # Test complete statuses
        for status in [TransactionStatus.REGISTERED, TransactionStatus.SKIPPED, TransactionStatus.FAILED]:
            self.sample_transaction.status = status
            self.assertTrue(self.sample_transaction.is_completed)

    def test_formatted_amount(self):
        """Test amount formatting."""
        self.sample_transaction.amount = 1234567
        self.assertEqual(self.sample_transaction.formatted_amount, "¥1,234,567")

    def test_to_slack_message(self):
        """Test Slack message formatting."""
        message = self.sample_transaction.to_slack_message()
        
        self.assertIn("新しい取引が検出されました", message)
        self.assertIn(f"金額: {self.sample_transaction.formatted_amount}", message)
        self.assertIn(f"店舗: {self.sample_transaction.store}", message)
        self.assertIn(f"ステータス: {self.sample_transaction.status.value}", message)
        self.assertNotIn("エラー", message)  # No error message by default

    def test_to_slack_message_with_error(self):
        """Test Slack message formatting with error."""
        error_msg = "テストエラー"
        self.sample_transaction.update_status(TransactionStatus.FAILED, error_msg)
        message = self.sample_transaction.to_slack_message()
        
        self.assertIn("エラー: " + error_msg, message)


if __name__ == '__main__':
    unittest.main() 