import os

# Flask Config
DEBUG = True
IP = os.environ.get('IP', '0.0.0.0')
PORT = os.environ.get('PORT', 8080)
SERVER_NAME = os.environ.get('SERVER_NAME', 'rideboard-bot.csh.rit.edu')

# Your app's Slack bot user token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
OAUTH_TOKEN = os.environ.get('SLACK_OAUTH_TOKEN', '')

# RideBoard API config
RIDEBOARD_ADDR = os.environ.get('RIDEBOARD', 'https://rideboard-api.csh.rit.edu')
RIDEBOARD_KEY = os.environ.get('RIDEBOARD_API_KEY', '')

# Info
MAINTAINER = os.environ.get('MAINTAINER', 'red')
