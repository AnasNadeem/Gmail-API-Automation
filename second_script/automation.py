from datetime import datetime, timedelta


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
        'lte': lambda value, email_value: datetime.now() - timedelta(days=value) <= email_value,
        'gte': lambda value, email_value: datetime.now() + timedelta(days=value) >= email_value,
    }

    ACTION_LIST = ['mark_as', 'move_to']
    ACTION_VALUE_MAP = {
        'mark_as': lambda gmail, email_id, value: gmail.mark_label_via_api(email_id, value),
        'move_to': lambda gmail, email_id, value: gmail.move_email_via_api(email_id, value),
    }
    # id, gmail_id, subject, from_email, to_email, date_received
    DB_FIELDS = ['id', 'gmail_id', 'subject', 'from', 'to', 'date_received']

    def __init__(self, gmail, rule, db):
        self.gmail = gmail
        self.rule = rule
        self.db = db

    def process_automation(self, emails):
        for email in emails:
            print(f"Processing email: {email[0]}")
            self.execute_automation(email)

    def execute_automation(self, email):
        conditional_predicate = self.rule['conditional_predicate']
        trigger_action = False
        for condition in self.rule['conditions']:
            is_condition_matched = self.check_single_condition(email, condition)
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
            print(f"Condition not matched for email: {email[1]}")
            return

        print(f"Condition matched for email: {email[1]}, \n Triggering actions")
        self.trigger_actions(email)
        print(f"Actions triggered for email: {email[1]}")

    def check_single_condition(self, email, condition):
        field = condition['field']
        predicate = condition['predicate']
        value = condition['value']

        self.validate_condition(field, predicate, value)

        email_value = email[self.DB_FIELDS.index(field)]
        print(f"Checking condition for email: {email[1]}, field: {field}, predicate: {predicate}, value: {value}, email_value: {email_value}")
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
            self.trigger_action(email[1], action)

    def trigger_action(self, email_id, action):
        action_name = action['action']
        value = action['value']

        self.validate_action(action_name, value)

        self.ACTION_VALUE_MAP[action_name](self.gmail, email_id, value)

    def validate_action(self, action_name, value):
        if action_name not in self.ACTION_LIST:
            raise Exception(f'Invalid action: {action_name}')

        if action_name == 'mark_as' and value not in ['READ', 'UNREAD', 'IMPORTANT']:
            raise Exception(f'Invalid value for action: {action_name}')

        if action_name == 'move_to' and value not in ['INBOX', 'SPAM', 'TRASH']:
            raise Exception(f'Invalid value for action: {action_name}')
