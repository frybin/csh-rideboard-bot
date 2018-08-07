import os

# Flask Config
DEBUG = True
IP = os.environ.get('API_IP', '127.0.0.1')
PORT = os.environ.get('API_PORT', 5000)
SERVER_NAME = os.environ.get('API_SERVER_NAME', '')

# Your app's Slack bot user token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

