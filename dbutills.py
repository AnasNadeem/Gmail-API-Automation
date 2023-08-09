import psycopg2


class DatabaseUtils:
    def __init__(self, host, database, user, password):
        self.conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
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
                received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def insert_email_message(self, gmail_id, subject, from_email, to_email, received_date):
        try:
            self.cur.execute(
                """
                INSERT INTO email_message (gmail_id, subject, from_email, to_email, received_date)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (gmail_id, subject, from_email, to_email, received_date)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f'Error while inserting email message: {e}')
            return False

    def update_email_message(self, gmail_id, subject, from_email, to_email, received_date):
        try:
            self.cur.execute(
                """
                UPDATE email_message
                SET subject = %s, from_email = %s, to_email = %s, received_date = %s
                WHERE gmail_id = %s
                """,
                (subject, from_email, to_email, received_date, gmail_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f'Error while updating email message: {e}')
            return False

    def create_or_update_email_message(self, gmail_id, subject, from_email, to_email, received_date):
        email_message = self.fetch_email_message(gmail_id)
        if email_message:
            return self.update_email_message(gmail_id, subject, from_email, to_email, received_date)

        return self.insert_email_message(gmail_id, subject, from_email, to_email, received_date)

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
