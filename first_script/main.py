from gmail import GmailApiUtils
from dbutills import DatabaseUtils


if __name__ == '__main__':
    # Initialize GmailApiUtils for authentication
    gmail = GmailApiUtils()

    # Initialize DatabaseUtils for database connection
    db = DatabaseUtils()
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
        to_email = gmail.EMAIL_VALUE_MAP['to'](email_headers_dict)
        date_received = gmail.EMAIL_VALUE_MAP['date_received'](email_headers_dict)

        print(f'Processing email: gmail_id={gmail_id}')
        db.create_or_update_email_message(
            gmail_id=gmail_id,
            subject=subject,
            from_email=from_email,
            to_email=to_email,
            date_received=date_received
        )

    print('First script completed. Emails are stored in database')
