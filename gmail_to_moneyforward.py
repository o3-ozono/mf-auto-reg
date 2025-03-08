import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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

    # メールの内容を表示する
    print(message)

if __name__ == '__main__':
    main()
