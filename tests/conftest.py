"""
Common fixtures for tests.
"""
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_gmail_service():
    """Gmail APIサービスのモック"""
    mock_service = MagicMock()
    mock_users = MagicMock()
    mock_messages_obj = MagicMock()
    mock_service.users.return_value = mock_users
    mock_users.messages.return_value = mock_messages_obj
    return mock_service, mock_users, mock_messages_obj 