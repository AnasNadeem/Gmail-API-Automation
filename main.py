import json

from automation import AutomationUtils

if __name__ == '__main__':
    rule = json.loads(open('rule.json').read())
    automation = AutomationUtils(rule=rule)
    automation.process_automation()
