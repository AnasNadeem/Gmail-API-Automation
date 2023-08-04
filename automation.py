from datetime import datetime, timezone, timedelta
from dateutil.parser import parse


class AutomationUtils:
    """
        This script will process emails based on some rules and take action accordingly.
        Rules in json:
        {
            "name": "Rule name",
            "conditional_predicate": "ALL/ANY",
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
    CONDITION_FIELD_LIST = ['from', 'to', 'subject', 'date_received']
    CONDITION_PREDICATE_LIST = ['contains', 'not_contains', 'equals', 'not_equals', 'lte', 'gte']
    PREDICATES_FUNC_MAP = {
        'contains': lambda value, email_value: value.lower() in email_value.lower(),
        'not_contains': lambda value, email_value: value.lower() not in email_value.lower(),
        'equals': lambda value, email_value: value == email_value,
        'not_equals': lambda value, email_value: value != email_value,
        'lte': lambda value, email_value: datetime.now(timezone.utc) - timedelta(days=value) <= email_value,
        'gte': lambda value, email_value: datetime.now(timezone.utc) + timedelta(days=value) >= email_value,
    }
    EMAIL_VALUE_MAP = {
        'from': lambda email: email['From'],
        'to': lambda email: email['To'],
        'subject': lambda email: email['Subject'],
        'date_received': lambda email: parse(email['Date']),
    }
    ACTION_LIST = ['mark_as', 'move_to']
    ACTION_VALUE_MAP = {
        'mark_as': lambda gmail, email_id, value: gmail.mark_label_via_api(email_id, value),
        'move_to': lambda gmail, email_id, value: gmail.move_email_via_api(email_id, value),
    }

    def __init__(self, gmail, rule):
        self.gmail = gmail
        self.rule = rule

    def process_automation(self):
        emails = self.gmail.fetch_emails()
        for email in emails:
            email = self.gmail.get_email(email['id'])

            # Passing email headers as dict to make it easy to access the data we need for now
            email_headers_dict = {i['name']: i['value'] for i in email['payload']['headers']}
            self.execute_automation(email, email_headers_dict)

    def execute_automation(self, email, email_headers_dict):
        conditional_predicate = self.rule['conditional_predicate']
        trigger_action = False
        for condition in self.rule['conditions']:
            is_condition_matched = self.check_single_condition(email, email_headers_dict, condition)
            if conditional_predicate == 'ANY':
                if not is_condition_matched:
                    continue
                trigger_action = True
                break

            if conditional_predicate == 'ALL':
                if not is_condition_matched:
                    trigger_action = False
                    break
                trigger_action = True

        if not trigger_action:
            print(f'Condition not matched for email: {email["id"]}, subject: {email_headers_dict["Subject"]}')
            return

        print(f"Condition matched for email: {email['id']}, subject: {email_headers_dict['Subject']} \n Triggering actions")
        self.trigger_actions(email)
        print(f"Actions triggered for email: {email['id']}, subject: {email_headers_dict['Subject']}")

    def check_single_condition(self, email, email_headers_dict, condition):
        field = condition['field']
        predicate = condition['predicate']
        value = condition['value']

        self.validate_condition(field, predicate, value)

        email_value = self.EMAIL_VALUE_MAP[field](email_headers_dict)
        return self.PREDICATES_FUNC_MAP[predicate](value, email_value)

    def validate_condition(self, field, predicate, value):
        if field not in self.CONDITION_FIELD_LIST:
            raise Exception(f'Invalid field: {field}')

        if predicate not in self.CONDITION_PREDICATE_LIST:
            raise Exception(f'Invalid predicate: {predicate}')

        if field == 'date_received':
            if predicate not in ['lte', 'gte']:
                raise Exception(f'Invalid predicate for field: {field}')

            if not type(value) in [int, float]:
                raise Exception(f'Invalid value for field: {field}')

    def trigger_actions(self, email):
        for action in self.rule['actions']:
            self.trigger_action(email, action)

    def trigger_action(self, email, action):
        action_name = action['action']
        value = action['value']

        self.validate_action(action_name, value)

        self.ACTION_VALUE_MAP[action_name](self.gmail, email['id'], value)

    def validate_action(self, action_name, value):
        if action_name not in self.ACTION_LIST:
            raise Exception(f'Invalid action: {action_name}')

        if action_name == 'mark_as' and value not in ['READ', 'UNREAD', 'IMPORTANT']:
            raise Exception(f'Invalid value for action: {action_name}')

        if action_name == 'move_to' and value not in ['INBOX', 'SPAM', 'TRASH']:
            raise Exception(f'Invalid value for action: {action_name}')
