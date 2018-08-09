import os
import json
from functools import reduce
from flask import Flask, request, make_response, Response
from slackclient import SlackClient

# Flask web server for incoming traffic from Slack
app = Flask(__name__)

if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
else:
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))

# Slack client for Web API requests
slack_client = SlackClient(app.config['SLACK_BOT_TOKEN'])

# Dictionary to store coffee orders. In the real world, you'd want an actual key-value store
COFFEE_ORDERS = {}

def new_order(orders, channel, user_num):
    orders[user_num] = {
        "order_channel": channel,
        "message_ts": "",
        "order": {}
    }

def dialog_popup(trigger, user_id_pram):
    open_dialog = slack_client.api_call(
            "dialog.open",
            trigger_id=trigger,
            dialog={
                "title": "Request a coffee",
                "submit_label": "Submit",
                "callback_id": user_id_pram + "coffee_order_form",
                "elements": [
                    {
                        "label": "Coffee Type",
                        "type": "select",
                        "name": "meal_preferences",
                        "placeholder": "Select a drink",
                        "options": [
                            {
                                "label": "Cappuccino",
                                "value": "cappuccino"
                            },
                            {
                                "label": "Latte",
                                "value": "latte"
                            },
                            {
                                "label": "Pour Over",
                                "value": "pour_over"
                            },
                            {
                                "label": "Cold Brew",
                                "value": "cold_brew"
                            }
                        ]
                    }
                ]
            }
        )
    return open_dialog

def invis_messgae(user_id, channel_id):
    order_dm = slack_client.api_call(
        "chat.postEphemeral",
        channel=channel_id,
        text="I am RideboardBot :oncoming_automobile:, and I\'m here to find you a ride :ride:",
        attachments=[{
            "text": "Click to see Current Rides",
            "callback_id": user_id + "coffee_order_form",
            "color": "#fc6819",
            "attachment_type": "default",
            "actions": [{
            "name": "all_rides",
            "text": ":blue_car: Rides",
            "type": "button",
            "value": "all_rides"
            }]
        }, {
            "text": "",
            "callback_id": user_id + "coffee_order_form",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [{
            "name": "coffee_order",
            "text": ":coffee: Order Coffee",
            "type": "button",
            "value": "coffee_order"
            }]
        }],
        user=user_id
    )
    return order_dm

@app.route("/slack/slash_actions", methods=["POST"])
def slash_actions():
    # Parse the request payload
    request_json = request.form
    print(request_json)
    user_ida = request_json["user_id"]
    # Show the ordering dialog to the user
    dialog_popup(request_json["trigger_id"], user_ida)
    return make_response("", 200)

@app.route("/slack/test_actions", methods=["POST"])
def message_test():
    # Parse the request payload
    request_json = request.form
    print(request_json)
    user_id = request_json["user_id"]
    channel_id = request_json["channel_id"]
    # Show the ordering dialog to the user
    open_dialog = invis_messgae(user_id, channel_id)
    return make_response("", 200)

@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    message_action = json.loads(request.form["payload"])
    print(message_action)
    user_ida = message_action["user"]["id"]
    if user_ida not in COFFEE_ORDERS.keys():
        new_order(COFFEE_ORDERS, message_action["channel"]["id"], user_ida)
    if message_action["type"] == "interactive_message":
        # Add the message_ts to the user's order info
        COFFEE_ORDERS[user_ida]["message_ts"] = message_action["message_ts"]
        # Show the ordering dialog to the user
        open_dialog = dialog_popup(message_action["trigger_id"], user_ida)

        print(open_dialog)

        # Update the message to show that we're in the process of taking their order
        slack_client.api_call(
            "chat.update",
            channel=COFFEE_ORDERS[user_ida]["order_channel"],
            ts=message_action["message_ts"],
            text=":pencil: Taking your order...",
            attachments=[]
        )

    elif message_action["type"] == "dialog_submission":
        coffee_order = COFFEE_ORDERS[user_ida]

        # Update the message to show that we're in the process of taking their order
        slack_client.api_call(
            "chat.update",
            channel=COFFEE_ORDERS[user_ida]["order_channel"],
            ts=coffee_order["message_ts"],
            text=":white_check_mark: Order received!",
            attachments=[]
        )

    return make_response("", 200)


if __name__ == "__main__":
    app.run()
