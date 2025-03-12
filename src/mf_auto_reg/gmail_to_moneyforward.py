import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import re
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# Gmail APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Gmail APIのサービスインスタンスを取得する"""
    creds = None
    # token.jsonファイルに認証情報が保存されている場合は、それを読み込む
    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 認証情報がない場合、または有効期限が切れている場合は、新しい認証情報を取得する
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 認証情報をtoken.jsonファイルに保存する
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        # Gmail APIのサービスインスタンスを作成する
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def search_emails(service, query):
    """Gmail APIを使って、指定されたクエリに一致するメールを検索する"""
    try:
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        return messages
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_email_content(service, msg_id):
    """Gmail APIを使って、指定されたメッセージIDのメールの内容を取得する"""
    try:
        message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        return message
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def decode_message_body(message):
    """メールの本文をデコードする"""
    try:
        encoded_data = message['payload']['body']['data']
        decoded_data = base64.urlsafe_b64decode(encoded_data).decode('UTF-8')
        return decoded_data
    except Exception as e:
        print(f"decode_message_body error: {e}")
        return None

def extract_information(decoded_data):
    """メールの本文から情報を抽出する"""
    try:
        # 正規表現を使って、利用日時、利用金額、利用店舗を抽出する
        date_match = re.search(r'ご利用日時：(.*)', decoded_data)
        amount_match = re.search(r'ご利用金額：(.*)円', decoded_data)
        store_match = re.search(r'ご利用店舗：(.*)', decoded_data)

        # 抽出した情報を変数に格納する
        date = date_match.group(1).strip() if date_match else None
        amount = amount_match.group(1).strip() if amount_match else None
        store = store_match.group(1).strip() if store_match else None

        # 抽出した情報を辞書に格納する
        extracted_info = {
            'date': date,
            'amount': amount,
            'store': store
        }
        return extracted_info
    except Exception as e:
        print(f"extract_information error: {e}")
        return None

def main():
    """メイン関数"""
    # Gmail APIのサービスインスタンスを取得する
    service = get_gmail_service()
    if not service:
        print('Gmail APIのサービスインスタンスを取得できませんでした')
        return

    # 検索クエリ
    query = '[ANA Pay] ご利用のお知らせ'

    # メールを検索する
    messages = search_emails(service, query)
    if not messages:
        print(f'クエリ "{query}" に一致するメールは見つかりませんでした')
        return

    print(f'クエリ "{query}" に一致するメールが見つかりました: {len(messages)}件')

    # 最初のメールの内容を取得する
    message = get_email_content(service, messages[0]['id'])
    if not message:
        print('メールの内容を取得できませんでした')
        return

    # メールの内容をデコードする
    decoded_data = decode_message_body(message)
    if not decoded_data:
        print('メールの本文をデコードできませんでした')
        return
    
    # 抽出した情報を表示する
    extracted_info = extract_information(decoded_data)
    if not extracted_info:
        print('メールの本文から情報を抽出できませんでした')
        return

    print(extracted_info)

if __name__ == '__main__':
    main() 