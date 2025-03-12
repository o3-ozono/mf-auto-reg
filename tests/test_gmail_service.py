"""
Tests for get_gmail_service function.
"""
import unittest
from unittest.mock import patch, MagicMock, mock_open
from mf_auto_reg.gmail_to_moneyforward import get_gmail_service
from googleapiclient.errors import HttpError


class TestGmailService(unittest.TestCase):
    """Gmail APIサービス関連のテスト"""
    
    @patch('mf_auto_reg.gmail_to_moneyforward.os.path.exists')
    @patch('google.oauth2.credentials.Credentials')
    @patch('mf_auto_reg.gmail_to_moneyforward.build')
    def test_get_gmail_service_with_token(self, mock_build, mock_credentials, mock_exists):
        """token.jsonが存在する場合のテスト"""
        mock_exists.return_value = True
        mock_credentials.from_authorized_user_file.return_value = MagicMock(valid=True)
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        result = get_gmail_service()
        
        self.assertEqual(result, mock_service)
        mock_exists.assert_called_once_with('token.json')
        mock_credentials.from_authorized_user_file.assert_called_once()
        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_credentials.from_authorized_user_file.return_value)

    @patch('mf_auto_reg.gmail_to_moneyforward.os.path.exists')
    @patch('google.oauth2.credentials.Credentials')
    @patch('mf_auto_reg.gmail_to_moneyforward.InstalledAppFlow')
    @patch('mf_auto_reg.gmail_to_moneyforward.build')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_gmail_service_without_token(self, mock_file, mock_build, mock_flow, mock_credentials, mock_exists):
        """token.jsonが存在しない場合のテスト"""
        mock_exists.return_value = False
        mock_creds = MagicMock()
        mock_flow.from_client_secrets_file.return_value.run_local_server.return_value = mock_creds
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        result = get_gmail_service()
        
        self.assertEqual(result, mock_service)
        mock_exists.assert_called_once_with('token.json')
        mock_flow.from_client_secrets_file.assert_called_once_with('credentials.json', ['https://www.googleapis.com/auth/gmail.readonly'])
        mock_flow.from_client_secrets_file.return_value.run_local_server.assert_called_once_with(port=0)
        mock_file.assert_called_once_with('token.json', 'w')
        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)

    @patch('mf_auto_reg.gmail_to_moneyforward.os.path.exists')
    @patch('google.oauth2.credentials.Credentials')
    @patch('mf_auto_reg.gmail_to_moneyforward.Request')
    @patch('mf_auto_reg.gmail_to_moneyforward.build')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_gmail_service_refresh_token(self, mock_file, mock_build, mock_request, mock_credentials, mock_exists):
        """トークンが期限切れの場合のテスト"""
        mock_exists.return_value = True
        mock_creds = MagicMock(valid=False, expired=True, refresh_token=True)
        mock_creds.to_json.return_value = '{"token": "refreshed"}'
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        result = get_gmail_service()
        
        self.assertEqual(result, mock_service)
        mock_exists.assert_called_once_with('token.json')
        mock_credentials.from_authorized_user_file.assert_called_once()
        mock_creds.refresh.assert_called_once_with(mock_request.return_value)
        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)

    @patch('mf_auto_reg.gmail_to_moneyforward.os.path.exists')
    @patch('mf_auto_reg.gmail_to_moneyforward.InstalledAppFlow')
    @patch('mf_auto_reg.gmail_to_moneyforward.build')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_gmail_service_http_error(self, mock_file, mock_build, mock_flow, mock_exists):
        """HttpErrorが発生した場合のテスト"""
        mock_exists.return_value = False  # token.jsonが存在しないようにする
        mock_creds = MagicMock()
        mock_creds.to_json.return_value = '{"token": "test"}'
        mock_flow.from_client_secrets_file.return_value.run_local_server.return_value = mock_creds
        mock_build.side_effect = HttpError(resp=MagicMock(status=500), content=b'Error')
        
        result = get_gmail_service()
        
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main() 