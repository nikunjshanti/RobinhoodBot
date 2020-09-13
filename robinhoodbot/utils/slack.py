from slack_webhook import Slack


slackcore = Slack(url='https://hooks.slack.com/services/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')

posttoslack = False

def post(text=''):
    if posttoslack:
        slackcore.post(text=text)

