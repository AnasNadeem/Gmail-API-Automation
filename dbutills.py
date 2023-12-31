import psycopg2
from constants import (
    DB_HOST,
    DB_NAME,
    DB_PASS,
    DB_USER
)


class DatabaseUtils:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
        )
        self.cur = self.conn.cursor()

    def create_table_for_storing_email_message(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS email_message (
                id SERIAL PRIMARY KEY,
                gmail_id VARCHAR(255) UNIQUE NOT NULL,
                subject VARCHAR(255) NOT NULL,
                from_email VARCHAR(255) NOT NULL,
                to_email VARCHAR(255) NOT NULL,
                date_received TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def insert_email_message(self, gmail_id, subject, from_email, to_email, date_received):
        try:
            self.cur.execute(
                """
                INSERT INTO email_message (gmail_id, subject, from_email, to_email, date_received)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (gmail_id, subject, from_email, to_email, date_received)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f'Error while inserting email message: {e}')
            return False

    def update_email_message(self, gmail_id, subject, from_email, to_email, date_received):
        try:
            self.cur.execute(
                """
                UPDATE email_message
                SET subject = %s, from_email = %s, to_email = %s, date_received = %s
                WHERE gmail_id = %s
                """,
                (subject, from_email, to_email, date_received, gmail_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f'Error while updating email message: {e}')
            return False

    def create_or_update_email_message(self, gmail_id, subject, from_email, to_email, date_received):
        email_message = self.fetch_email_message(gmail_id)
        if email_message:
            return self.update_email_message(gmail_id, subject, from_email, to_email, date_received)

        return self.insert_email_message(gmail_id, subject, from_email, to_email, date_received)

    def fetch_email_message(self, gmail_id):
        self.cur.execute(
            """
            SELECT * FROM email_message WHERE gmail_id = %s
            """,
            (gmail_id,)
        )
        return self.cur.fetchone()

    def fetch_all_email_messages(self):
        self.cur.execute(
            """
            SELECT * FROM email_message
            """
        )
        return self.cur.fetchall()
