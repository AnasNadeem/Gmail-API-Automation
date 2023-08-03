import os
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailApiUtils:
    LABELS_LIST = ['INBOX', 'UNREAD', 'IMPORTANT', 'SENT', 'DRAFT', 'SPAM', 'TRASH']

    def __init__(self):
        self.service = self.authenticate(['https://www.googleapis.com/auth/gmail.modify'])
        self.messages = self.service.users().messages()

    def authenticate(self, scopes):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('gmail', 'v1', credentials=creds)
            return service
        except HttpError as error:
            print(f'Error occurred in authenticate: {error}')
            return None

    def fetch_emails(self, labelIds=[]):
        emails = self.messages.list(userId='me', labelIds=labelIds).execute()
        return emails['messages']

    def fetch_emails_with_data(self, labelIds=['INBOX', 'IMPORTANT']):
        emails = self.messages.list(userId='me', labelIds=labelIds).execute()
        return [self.get_email(email['id']) for email in emails['messages']]

    def get_email(self, email_id):
        email = self.messages.get(userId='me', id=email_id).execute()
        return email

    def mark_label(self, email_id, label):
        # HACK: Mark email as read as READ is not a label
        if label == 'READ':
            self.messages.modify(userId='me', id=email_id, body={'removeLabelIds': ['UNREAD']}).execute()
            return

        if label not in self.LABELS_LIST:
            raise Exception(f'Invalid label: {label}')
        self.messages.modify(userId='me', id=email_id, body={'addLabelIds': [label]}).execute()

    def move_email(self, email_id, destination):
        available_destinations = ['INBOX', 'SPAM', 'TRASH']
        if destination not in available_destinations:
            raise Exception(f'Invalid destination: {destination}')

        remove_labels = available_destinations.remove(destination)
        body = {'removeLabelIds': remove_labels, 'addLabelIds': [destination]}
        self.messages.modify(userId='me', id=email_id, body=body).execute()

    def mark_label_via_api(self, email_id, label):
        modify_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{email_id}/modify'
        if label == 'READ':
            body = {'removeLabelIds': ['UNREAD']}
        else:
            body = {'addLabelIds': [label]}
        response = requests.post(
            modify_url,
            json=body,
            headers={'Authorization': f'Bearer {self.service._http.credentials.token}'})
        response.raise_for_status()

    def move_email_via_api(self, email_id, destination):
        modify_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{email_id}/modify'
        available_destinations = ['INBOX', 'SPAM', 'TRASH']
        if destination not in available_destinations:
            raise Exception(f'Invalid destination: {destination}')

        remove_labels = available_destinations.remove(destination)
        body = {'removeLabelIds': remove_labels, 'addLabelIds': [destination]}
        response = requests.post(
            modify_url,
            json=body,
            headers={'Authorization': f'Bearer {self.service._http.credentials.token}'})
        response.raise_for_status()
