"""
Tests for decode_message_body function.
"""
import unittest
from mf_auto_reg.gmail_to_moneyforward import decode_message_body


class TestDecodeMessage(unittest.TestCase):
    """メッセージデコード機能のテスト"""
    
    def test_decode_message_body_valid(self):
        """有効なメッセージのデコードテスト"""
        # 有効なメッセージ
        message = {
            'payload': {
                'body': {
                    'data': 'SGVsbG8gV29ybGQ='  # "Hello World" in base64
                }
            }
        }
        result = decode_message_body(message)
        self.assertEqual(result, 'Hello World')
    
    def test_decode_message_body_invalid(self):
        """無効なメッセージのデコードテスト"""
        # 無効なメッセージ
        message = {}
        result = decode_message_body(message)
        self.assertIsNone(result)
    
    def test_decode_message_body_invalid_base64(self):
        """無効なbase64データのデコードテスト"""
        # 無効なbase64データ
        message = {
            'payload': {
                'body': {
                    'data': 'Invalid Base64'
                }
            }
        }
        result = decode_message_body(message)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main() 