from gmail import GmailApiUtils
from dbutills import DatabaseUtils
from constants import (
    DB_HOST,
    DB_NAME,
    DB_PASS,
    DB_USER
)


if __name__ == '__main__':
    # Initialize GmailApiUtils for authentication
    gmail = GmailApiUtils()

    # Initialize DatabaseUtils for database connection
    db = DatabaseUtils(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    db.create_table_for_storing_email_message()

    # Fetch emails
    emails = gmail.fetch_emails()
    for email in emails:
        email = gmail.get_email(email['id'])
        email_headers_dict = {i['name']: i['value'] for i in email['payload']['headers']}

        # Preparing data
        gmail_id = email['id']
        subject = gmail.EMAIL_VALUE_MAP['subject'](email_headers_dict)
        from_email = gmail.EMAIL_VALUE_MAP['from'](email_headers_dict)
        to_email = gmail.EMAIL_VALUE_MAP['from'](email_headers_dict)
        received_date = gmail.EMAIL_VALUE_MAP['date_received'](email_headers_dict)

        db.create_or_update_email_message(
            gmail_id=gmail_id,
            subject=subject,
            from_email=from_email,
            to_email=to_email,
            received_date=received_date
        )

        print('First script completed. Emails are stored in database')
