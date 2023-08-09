import unittest

from second_script.automation import AutomationUtils
from gmail import GmailApiUtils


class GmailApiUtilsTest(unittest.TestCase):
    def setUp(self):
        self.gmail = GmailApiUtils()

    def test_fetch_emails(self):
        emails = self.gmail.fetch_emails()
        self.assertTrue(len(emails) > 0)

    def test_get_email(self):
        emails = self.gmail.fetch_emails()
        email = self.gmail.get_email(emails[0]['id'])
        self.assertEqual(email['id'], emails[0]['id'])
        self.assertEqual(email['snippet'] != '', True)

        email_headers_dict = {i['name']: i['value'] for i in email['payload']['headers']}
        self.assertEqual('Subject' in email_headers_dict, True)
        self.assertEqual('From' in email_headers_dict, True)
        self.assertEqual('To' in email_headers_dict, True)
        self.assertEqual('Date' in email_headers_dict, True)

    def test_fetch_emails_with_UNREAD_label(self):
        emails = self.gmail.fetch_emails(labelIds=['UNREAD'])
        self.assertTrue(len(emails) > 0)

        email = self.gmail.get_email(emails[0]['id'])
        self.assertEqual('UNREAD' in email['labelIds'], True)

    def test_mark_as_read(self):
        emails = self.gmail.fetch_emails(labelIds=['UNREAD'])
        self.assertTrue(len(emails) > 0)

        email = self.gmail.get_email(emails[0]['id'])
        self.assertEqual('UNREAD' in email['labelIds'], True)

        response = self.gmail.mark_label_via_api(email['id'], 'READ')
        self.assertEqual('UNREAD' in response['labelIds'], False)

        email = self.gmail.get_email(emails[0]['id'])
        self.assertEqual('UNREAD' in email['labelIds'], False)

    def test_move_email(self):
        emails = self.gmail.fetch_emails(labelIds=['SPAM'])
        self.assertTrue(len(emails) > 0)

        email = self.gmail.get_email(emails[0]['id'])
        self.assertEqual('SPAM' in email['labelIds'], True)

        response = self.gmail.move_email_via_api(email['id'], 'INBOX')
        self.assertEqual('SPAM' in response['labelIds'], False)
        self.assertEqual('INBOX' in response['labelIds'], True)

        email = self.gmail.get_email(emails[0]['id'])
        self.assertEqual('SPAM' in email['labelIds'], False)
        self.assertEqual('INBOX' in email['labelIds'], True)


class AutomationUtilsTest(unittest.TestCase):
    def setUp(self):
        self.gmail = GmailApiUtils()
        self.rule = {
            "name": "Rule name",
            "conditional_predicate": "ALL",
            "conditions": [
                {
                    "field": "from",
                    "predicate": "contains",
                    "value": "itsmeanas"
                },
                {
                    "field": "subject",
                    "predicate": "contains",
                    "value": "test"
                },
                {
                    "field": "date_received",
                    "predicate": "lte",
                    "value": 2
                }
            ],
            "actions": [
                {
                    "action": "mark_as",
                    "value": "IMPORTANT"
                }
            ]
        }
        self.automation = AutomationUtils(self.gmail, self.rule)

    def test_trigger_action(self):
        emails = self.gmail.fetch_emails(labelIds=['SPAM'])
        self.assertTrue(len(emails) > 0)

        email = self.gmail.get_email(emails[0]['id'])
        self.assertEqual('IMPORTANT' in email['labelIds'], False)

        self.automation.trigger_action(email, self.rule['actions'][0])

        email = self.gmail.get_email(emails[0]['id'])
        self.assertEqual('IMPORTANT' in email['labelIds'], True)


if __name__ == '__main__':
    unittest.main()
