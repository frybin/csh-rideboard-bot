import os

# Flask Config
DEBUG = True
IP = os.environ.get('IP', '0.0.0.0')
PORT = os.environ.get('PORT', 8080)
SERVER_NAME = os.environ.get('SERVER_NAME', 'rideboard-bot.csh.rit.edu')

# Your app's Slack bot user token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
