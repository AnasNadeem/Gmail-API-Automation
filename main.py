import json

from automation import AutomationUtils
from gmail import GmailApiUtils


if __name__ == '__main__':
    gmail = GmailApiUtils()
    rule = json.loads(open('rule.json').read())
    automation = AutomationUtils(gmail=gmail, rule=rule)
    automation.process_automation()
