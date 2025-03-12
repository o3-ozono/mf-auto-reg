"""
Tests for extract_information function.
"""
import unittest
from unittest.mock import patch
from mf_auto_reg.gmail_to_moneyforward import extract_information


class TestExtractInformation(unittest.TestCase):
    """情報抽出機能のテスト"""
    
    def test_extract_information_valid_email(self):
        """有効なメール本文からの情報抽出テスト"""
        # テスト用のメール本文
        email_body = """
        ANA Payでのお支払い
        ご利用日時：2023/03/01 12:34:56
        ご利用金額：1,234円
        ご利用店舗：テスト店舗
        """
        result = extract_information(email_body)
        self.assertEqual(result['date'], '2023/03/01 12:34:56')
        self.assertEqual(result['amount'], '1,234')
        self.assertEqual(result['store'], 'テスト店舗')
    
    def test_extract_information_invalid_email(self):
        """無効なメール本文からの情報抽出テスト"""
        # 無効なメール本文
        email_body = "これは無効なメール本文です"
        result = extract_information(email_body)
        # 実際の関数は None ではなく {'date': None, 'amount': None, 'store': None} を返す
        self.assertIsNotNone(result)
        self.assertIsNone(result['date'])
        self.assertIsNone(result['amount'])
        self.assertIsNone(result['store'])
    
    def test_extract_information_missing_fields(self):
        """一部のフィールドが欠けているメール本文からの情報抽出テスト"""
        # 一部のフィールドが欠けているメール本文
        email_body = """
        ANA Payでのお支払い
        ご利用日時：2023/03/01 12:34:56
        ご利用金額：1,234円
        """
        result = extract_information(email_body)
        self.assertIsNotNone(result)
        self.assertEqual(result['date'], '2023/03/01 12:34:56')
        self.assertEqual(result['amount'], '1,234')
        self.assertIsNone(result['store'])
    
    def test_extract_information_different_format(self):
        """異なるフォーマットのメール本文からの情報抽出テスト"""
        # 異なるフォーマットのメール本文
        email_body = """
        ANA Payでのお支払い
        支払日時: 2023/03/01 12:34:56
        支払金額: 1,234円
        お店: テスト店舗
        """
        result = extract_information(email_body)
        # 実際の関数は None ではなく {'date': None, 'amount': None, 'store': None} を返す
        self.assertIsNotNone(result)
        self.assertIsNone(result['date'])
        self.assertIsNone(result['amount'])
        self.assertIsNone(result['store'])
    
    def test_extract_information_edge_case(self):
        """特殊なケースのメール本文からの情報抽出テスト"""
        # 特殊なケースのメール本文
        email_body = """
        ANA Payでのお支払い
        ご利用日時：2023/12/31 23:59:59
        ご利用金額：10,000円
        ご利用店舗：特殊文字店舗!@#$%^&*()
        """
        result = extract_information(email_body)
        self.assertEqual(result['date'], '2023/12/31 23:59:59')
        self.assertEqual(result['amount'], '10,000')
        self.assertEqual(result['store'], '特殊文字店舗!@#$%^&*()')

    def test_extract_information_exception(self):
        """例外が発生する場合のテスト"""
        with patch('mf_auto_reg.gmail_to_moneyforward.re.search', side_effect=Exception('Test exception')):
            result = extract_information('Test email')
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main() 