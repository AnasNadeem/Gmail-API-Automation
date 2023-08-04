import psycopg2


class ConnectDB:
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
                to_email VARCHAR(255) NOT NULL
            )
            """
        )
        self.conn.commit()

    def insert_email_message(self, gmail_id, subject, from_email, to_email):
        try:
            self.cur.execute(
                """
                INSERT INTO email_message (gmail_id, subject, from_email, to_email)
                VALUES (%s, %s, %s, %s)
                """,
                (gmail_id, subject, from_email, to_email)
            )
            self.conn.commit()
        except Exception as e:
            print(f'Error while inserting email message: {e}')

    def update_email_message(self, gmail_id, subject, from_email, to_email):
        try:
            self.cur.execute(
                """
                UPDATE email_message
                SET subject = %s, from_email = %s, to_email = %s
                WHERE gmail_id = %s
                """,
                (subject, from_email, to_email, gmail_id)
            )
            self.conn.commit()
        except Exception as e:
            print(f'Error while updating email message: {e}')

    def create_or_update_email_message(self, gmail_id, subject, from_email, to_email):
        self.cur.execute(
            """
            SELECT * FROM email_message WHERE gmail_id = %s
            """,
            (gmail_id,)
        )
        email_message = self.cur.fetchone()
        if email_message:
            self.update_email_message(gmail_id, subject, from_email, to_email)
            return email_message

        self.insert_email_message(gmail_id, subject, from_email, to_email)
        return self.create_or_update_email_message(gmail_id, subject, from_email, to_email)
