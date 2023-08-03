import requests
from authenticate import authenticate


class GmailUtils:
    LABELS_LIST = ['INBOX', 'UNREAD', 'IMPORTANT', 'SENT', 'DRAFT', 'SPAM', 'TRASH']
    def __init__(self, service):
        self.messages = service.users().messages()

    def fetch_emails(self, labelIds=['INBOX', 'IMPORTANT']):
        emails = self.messages.list(userId='me', labelIds=labelIds).execute()
        return emails['messages']

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
        response = requests.post(modify_url, json=body)
        response.raise_for_status()

    def move_email_via_api(self, email_id, destination):
        modify_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{email_id}/modify'
        available_destinations = ['INBOX', 'SPAM', 'TRASH']
        if destination not in available_destinations:
            raise Exception(f'Invalid destination: {destination}')

        remove_labels = available_destinations.remove(destination)
        body = {'removeLabelIds': remove_labels, 'addLabelIds': [destination]}
        response = requests.post(modify_url, json=body)
        response.raise_for_status()


class AutomationUtils:
    """
        This script will process emails based on some rules and take action accordingly.
        Rules in json:
        {
            "name": "Rule name",
            "conditions_predicate": "ALL/ANY", 
            "conditions": [
                {
                    "field": "from",
                    "predicate": "contains/equals",
                    "value": "<value>"
                },
                {
                    "field": "subject",
                    "predicate": "contains/equals",
                    "value": "<value>"
                },
                {
                    "field": "date_received",
                    "predicate": "lte/gte/equals",
                    "value": "2"
                }
            ],
            "actions": [
                {
                    "action": "mark_as",
                    "value": "READ/UNREAD/IMPORTANT"
                },
                {
                    "action": "move_to",
                    "value": "INBOX/SPAM/TRASH"
                },
            ]
        }
    """

    def __init__(self, service, rules):
        self.gmail = GmailUtils(service)
        self.rules = rules

    def process_automation(self):
        emails = self.gmail.fetch_emails()
        pass

if __name__ == '__main__':
    scopes = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify',]
    service = authenticate('credentials.json', scopes)
    gmail = GmailUtils(service)
    emails = gmail.fetch_emails()
    print('Total mail fetched', len(emails))
    email = emails[0]
    email = gmail.get_email(email['id'])
    # from field, subject field, date received
    print(email['payload']['headers'][0]['value'], email['snippet'], email['payload']['headers'][2]['value'])
