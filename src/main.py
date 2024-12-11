from __future__ import print_function
import os
import base64
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate_gmail():
    """Authenticate the user and return the Gmail API service."""
    creds = None
    # The token.json file stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_attachments(service, user_id='me'):
    """Get all email attachments from the user's Gmail account."""
    try:
        # Get the list of messages
        results = service.users().messages().list(userId=user_id).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found.')
            return

        for message in messages:
            msg = service.users().messages().get(userId=user_id, id=message['id']).execute()

            for part in msg['payload'].get('parts', []):
                if part['filename']:
                    attachment_id = part['body']['attachmentId']
                    attachment = service.users().messages().attachments().get(
                        userId=user_id, messageId=message['id'], id=attachment_id).execute()

                    data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    file_path = os.path.join('attachments', part['filename'])

                    if not os.path.exists('attachments'):
                        os.makedirs('attachments')

                    with open(file_path, 'wb') as f:
                        f.write(data)

                    print(f"Attachment saved: {file_path}")

    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    # Authenticate and create the Gmail API service
    service = authenticate_gmail()

    # Get attachments from the Gmail account
    get_attachments(service)
