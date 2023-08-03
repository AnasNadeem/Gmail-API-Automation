from authenticate import authenticate


class GmailAutomation:
    LABELS_LIST = ['INBOX', 'UNREAD', 'IMPORTANT', 'SENT', 'DRAFT', 'SPAM', 'TRASH']
    def __init__(self, service):
        self.messages = service.users().messages()

    def fetch_emails(self, labelIds=['INBOX']):
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


if __name__ == '__main__':
    scopes = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify',]
    service = authenticate('credentials.json', scopes)
