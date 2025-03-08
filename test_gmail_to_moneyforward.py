import unittest
from googleapiclient.discovery import build
from googleapiclient.http import HttpMockSequence
from gmail_to_moneyforward import decode_message_body, extract_information, get_gmail_service, search_emails

class TestGmailToMoneyforward(unittest.TestCase):

    def test_decode_message_body(self):
        message = {
            'payload': {
                'body': {
                    'data': 'SGVsbG8gV29ybGQh'
                }
            }
        }
        decoded_data = decode_message_body(message)
        expected_data = "Hello World!"
        self.assertEqual(decoded_data, expected_data)

    def test_get_gmail_service(self):
        resp = ({'status': '200'}, 'content')
        http = HttpMockSequence([resp])

        service = get_gmail_service()

        self.assertIsNotNone(service)

    def test_search_emails(self):
        resp = ({'status': '200'}, '{"messages": [{"id": "1951b4f409a6b95c"}]}')
        http = HttpMockSequence([resp])

        service = get_gmail_service()

        messages = search_emails(service, "query")

        self.assertIsNotNone(messages)
        self.assertEqual(messages[0]['id'], "1951b4f409a6b95c")
