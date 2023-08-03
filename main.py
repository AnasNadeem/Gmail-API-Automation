import json

from automation import AutomationUtils
from gmail import GmailApiUtils

if __name__ == '__main__':
    # gmail = GmailApiUtils()
    # emails = gmail.fetch_emails()
    # emails = emails[:2]
    # for email in emails:
    #     email = gmail.get_email(email['id'])
    #     print(email)
    #     # headers = email['payload']['headers']
    #     # subject = [i['value'] for i in headers if i["name"] == "Subject"]
    #     # print(subject)
    rule = json.loads(open('rule.json').read())
    automation = AutomationUtils(rule=rule)
    automation.process_automation()
