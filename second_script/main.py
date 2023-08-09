import json

from second_script.automation import AutomationUtils
from dbutills import DatabaseUtils
from gmail import GmailApiUtils


if __name__ == '__main__':
    # Initialize DatabaseUtils for database connection
    db = DatabaseUtils()
    db.create_table_for_storing_email_message()
    emails = db.fetch_all_email_messages()

    # Initialize GmailApiUtils for authentication
    gmail = GmailApiUtils()

    rule = json.loads(open('rule.json').read())

    # Initialize AutomationUtils for processing emails
    automation = AutomationUtils(
        gmail=gmail,
        rule=rule,
        db=db
    )
    automation.process_automation(emails)
