"""
Tests for email operations functions.
"""
import unittest
from unittest.mock import MagicMock
from mf_auto_reg.gmail_to_moneyforward import search_emails, get_email_content
from googleapiclient.errors import HttpError


class TestEmailOperations(unittest.TestCase):
    """メール操作関連のテスト"""
    
    def test_search_emails_success(self):
        """メール検索成功のテスト"""
        mock_service = MagicMock()
        mock_messages = [{'id': '123'}, {'id': '456'}]
        mock_list = MagicMock()
        mock_list.execute.return_value = {'messages': mock_messages}
        mock_messages_obj = MagicMock()
        mock_messages_obj.list.return_value = mock_list
        mock_users = MagicMock()
        mock_users.messages.return_value = mock_messages_obj
        mock_service.users.return_value = mock_users
        
        result = search_emails(mock_service, 'test query')
        
        self.assertEqual(result, mock_messages)
        mock_service.users.assert_called_once()
        mock_users.messages.assert_called_once()
        mock_messages_obj.list.assert_called_once_with(userId='me', q='test query')
        mock_list.execute.assert_called_once()

    def test_search_emails_no_messages(self):
        """メッセージがない場合のテスト"""
        mock_service = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.return_value = {}
        mock_messages_obj = MagicMock()
        mock_messages_obj.list.return_value = mock_list
        mock_users = MagicMock()
        mock_users.messages.return_value = mock_messages_obj
        mock_service.users.return_value = mock_users
        
        result = search_emails(mock_service, 'test query')
        
        self.assertEqual(result, [])
        mock_service.users.assert_called_once()
        mock_users.messages.assert_called_once()
        mock_messages_obj.list.assert_called_once_with(userId='me', q='test query')
        mock_list.execute.assert_called_once()

    def test_search_emails_http_error(self):
        """HttpErrorが発生した場合のテスト"""
        mock_service = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.side_effect = HttpError(resp=MagicMock(status=500), content=b'Error')
        mock_messages_obj = MagicMock()
        mock_messages_obj.list.return_value = mock_list
        mock_users = MagicMock()
        mock_users.messages.return_value = mock_messages_obj
        mock_service.users.return_value = mock_users
        
        result = search_emails(mock_service, 'test query')
        
        self.assertIsNone(result)
        mock_service.users.assert_called_once()
        mock_users.messages.assert_called_once()
        mock_messages_obj.list.assert_called_once_with(userId='me', q='test query')
        mock_list.execute.assert_called_once()

    def test_get_email_content_success(self):
        """メール内容取得成功のテスト"""
        mock_service = MagicMock()
        mock_message = {'id': '123', 'payload': {'body': {'data': 'test'}}}
        mock_get = MagicMock()
        mock_get.execute.return_value = mock_message
        mock_messages_obj = MagicMock()
        mock_messages_obj.get.return_value = mock_get
        mock_users = MagicMock()
        mock_users.messages.return_value = mock_messages_obj
        mock_service.users.return_value = mock_users
        
        result = get_email_content(mock_service, '123')
        
        self.assertEqual(result, mock_message)
        mock_service.users.assert_called_once()
        mock_users.messages.assert_called_once()
        mock_messages_obj.get.assert_called_once_with(userId='me', id='123', format='full')
        mock_get.execute.assert_called_once()

    def test_get_email_content_http_error(self):
        """HttpErrorが発生した場合のテスト"""
        mock_service = MagicMock()
        mock_get = MagicMock()
        mock_get.execute.side_effect = HttpError(resp=MagicMock(status=500), content=b'Error')
        mock_messages_obj = MagicMock()
        mock_messages_obj.get.return_value = mock_get
        mock_users = MagicMock()
        mock_users.messages.return_value = mock_messages_obj
        mock_service.users.return_value = mock_users
        
        result = get_email_content(mock_service, '123')
        
        self.assertIsNone(result)
        mock_service.users.assert_called_once()
        mock_users.messages.assert_called_once()
        mock_messages_obj.get.assert_called_once_with(userId='me', id='123', format='full')
        mock_get.execute.assert_called_once()


if __name__ == '__main__':
    unittest.main() 