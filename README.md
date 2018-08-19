# RideBoard Bot

RideBoard Bot is Slack Bot that allows the members to communicate to the RideBoard API to see, create and delete rides and to create, join, leave and delete cars.

[![Travis](https://travis-ci.com/frybin/csh-rideboard-bot.svg?branch=master)](https://travis-ci.com/frybin/csh-rideboard-bot)
[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/frybin/csh-rideboard-bot/blob/master/LICENSE)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/frybin/csh-rideboard-bot/issues)

## Contributing
All contributors are welcome! If you would like to contribute:

### Dependencies
1. You will need `python3` ([Install Guide](https://docs.python-guide.org/starting/installation/#installation-guides)).
2. You will need `pip` ([Install Guide](https://packaging.python.org/tutorials/installing-packages/#ensure-you-can-run-pip-from-the-command-line)).
3. You will need `ngrok` ([Install Guide](https://ngrok.com/product)) if you want to run bot locally.

### Setup
1. Fork this repo and clone it locally by running `git clone https://github.com/<your_username>/csh-rideboard-bot.git`
2. `cd csh-rideboard-bot`
3. Create a python virtual environment, activate it and install requirements.
  - `python -m venv venv`
  - `source venv/bin/activate`
  - `pip install -r requirements.txt`
4. Activate ngrok
    - `<path to ngrok folder>/ngrok http 3000`
5. You will need the 'SLACK_BOT_TOKEN', 'SLACK_OAUTH_TOKEN', 'SLACK_VERIFICATION_TOKEN', and 'RIDEBOARD_API_KEY'. 
You can create your own by making a Slack App and you can get a RIDEBOARD_API_KEY from an RTP.
```
export SLACK_BOT_TOKEN = <SLACK_BOT_TOKEN>
export SLACK_VERIFICATION_TOKEN = <SLACK_VERIFICATION_TOKEN>
export IP = 127.0.0.1
export PORT = 3000
export SERVER_NAME = <ngrok URL>
export RIDEBOARD_API_KEY = <RIDEBOARD_API_KEY > 
export SLACK_OAUTH_TOKEN = <SLACK_OAUTH_TOKEN>
```
6. To run the application:
  - Set debug mode: `export FLASK_ENV=development`
  - Export application: `export FLASK_APP=app.py`
  - Run: `flask run`
7. Now you can make your changes. Make sure the changes made work and that your code passes pylint (run `pylint csh_rideboard_bot`). Once you do that you can make your pull request.
