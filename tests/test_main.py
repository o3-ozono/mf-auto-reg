"""
Tests for main function.
"""
import unittest
from unittest.mock import patch, MagicMock
from mf_auto_reg.gmail_to_moneyforward import main


class TestMain(unittest.TestCase):
    """メイン関数のテスト"""
    
    @patch('mf_auto_reg.gmail_to_moneyforward.get_gmail_service')
    @patch('mf_auto_reg.gmail_to_moneyforward.search_emails')
    @patch('mf_auto_reg.gmail_to_moneyforward.get_email_content')
    @patch('mf_auto_reg.gmail_to_moneyforward.decode_message_body')
    @patch('mf_auto_reg.gmail_to_moneyforward.extract_information')
    def test_main_success(self, mock_extract, mock_decode, mock_get_content, mock_search, mock_get_service):
        """正常系のテスト"""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_messages = [{'id': '123'}]
        mock_search.return_value = mock_messages
        mock_message = {'payload': {'body': {'data': 'test'}}}
        mock_get_content.return_value = mock_message
        mock_decoded = 'decoded data'
        mock_decode.return_value = mock_decoded
        mock_info = {'date': '2023-01-01', 'amount': '1000', 'store': 'Test Store'}
        mock_extract.return_value = mock_info
        
        main()
        
        mock_get_service.assert_called_once()
        mock_search.assert_called_once_with(mock_service, '[ANA Pay] ご利用のお知らせ')
        mock_get_content.assert_called_once_with(mock_service, '123')
        mock_decode.assert_called_once_with(mock_message)
        mock_extract.assert_called_once_with(mock_decoded)

    @patch('mf_auto_reg.gmail_to_moneyforward.get_gmail_service')
    def test_main_no_service(self, mock_get_service):
        """サービスが取得できない場合のテスト"""
        mock_get_service.return_value = None
        
        main()
        
        mock_get_service.assert_called_once()

    @patch('mf_auto_reg.gmail_to_moneyforward.get_gmail_service')
    @patch('mf_auto_reg.gmail_to_moneyforward.search_emails')
    def test_main_no_messages(self, mock_search, mock_get_service):
        """メッセージが見つからない場合のテスト"""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_search.return_value = []
        
        main()
        
        mock_get_service.assert_called_once()
        mock_search.assert_called_once_with(mock_service, '[ANA Pay] ご利用のお知らせ')

    @patch('mf_auto_reg.gmail_to_moneyforward.get_gmail_service')
    @patch('mf_auto_reg.gmail_to_moneyforward.search_emails')
    @patch('mf_auto_reg.gmail_to_moneyforward.get_email_content')
    def test_main_no_content(self, mock_get_content, mock_search, mock_get_service):
        """メール内容が取得できない場合のテスト"""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_messages = [{'id': '123'}]
        mock_search.return_value = mock_messages
        mock_get_content.return_value = None
        
        main()
        
        mock_get_service.assert_called_once()
        mock_search.assert_called_once_with(mock_service, '[ANA Pay] ご利用のお知らせ')
        mock_get_content.assert_called_once_with(mock_service, '123')

    @patch('mf_auto_reg.gmail_to_moneyforward.get_gmail_service')
    @patch('mf_auto_reg.gmail_to_moneyforward.search_emails')
    @patch('mf_auto_reg.gmail_to_moneyforward.get_email_content')
    @patch('mf_auto_reg.gmail_to_moneyforward.decode_message_body')
    def test_main_no_decoded_data(self, mock_decode, mock_get_content, mock_search, mock_get_service):
        """デコードに失敗した場合のテスト"""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_messages = [{'id': '123'}]
        mock_search.return_value = mock_messages
        mock_message = {'payload': {'body': {'data': 'test'}}}
        mock_get_content.return_value = mock_message
        mock_decode.return_value = None
        
        main()
        
        mock_get_service.assert_called_once()
        mock_search.assert_called_once_with(mock_service, '[ANA Pay] ご利用のお知らせ')
        mock_get_content.assert_called_once_with(mock_service, '123')
        mock_decode.assert_called_once_with(mock_message)

    @patch('mf_auto_reg.gmail_to_moneyforward.get_gmail_service')
    @patch('mf_auto_reg.gmail_to_moneyforward.search_emails')
    @patch('mf_auto_reg.gmail_to_moneyforward.get_email_content')
    @patch('mf_auto_reg.gmail_to_moneyforward.decode_message_body')
    @patch('mf_auto_reg.gmail_to_moneyforward.extract_information')
    def test_main_no_extracted_info(self, mock_extract, mock_decode, mock_get_content, mock_search, mock_get_service):
        """情報抽出に失敗した場合のテスト"""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_messages = [{'id': '123'}]
        mock_search.return_value = mock_messages
        mock_message = {'payload': {'body': {'data': 'test'}}}
        mock_get_content.return_value = mock_message
        mock_decoded = 'decoded data'
        mock_decode.return_value = mock_decoded
        mock_extract.return_value = None
        
        main()
        
        mock_get_service.assert_called_once()
        mock_search.assert_called_once_with(mock_service, '[ANA Pay] ご利用のお知らせ')
        mock_get_content.assert_called_once_with(mock_service, '123')
        mock_decode.assert_called_once_with(mock_message)
        mock_extract.assert_called_once_with(mock_decoded)


if __name__ == '__main__':
    unittest.main() 