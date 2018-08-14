import os
import json
import requests
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
OAUTH_ID = app.config['OAUTH_TOKEN']
RIDEURL = app.config['RIDEBOARD_ADDR']+"/"+app.config['RIDEBOARD_KEY']

def new_button(name, text, value):
    attachment = {
        "name": name,
        "text": text,
        "type": "button",
        "value": value
    }
    return attachment

def create_numbers(max_option=10):
    options = []
    for i in range(2, max_option+2):
        options.append({
            "label": i,
            "value": i
        })
    return options

def get_user_info(user_id):
    addr = 'https://slack.com/api/users.profile.get?'
    addr += 'token=' + OAUTH_ID + '&user=' + user_id
    res = requests.get(addr)
    print(res.json())

def dialog_popup(trigger, user_id_pram):
    open_dialog = slack_client.api_call(
            "dialog.open",
            trigger_id=trigger,
            dialog={
                "title": "Create Car",
                "submit_label": "Submit",
                "callback_id": user_id_pram + "car_creation_form",
                "elements": [
                    {
                        "label": "Amount of passengers",
                        "type": "select",
                        "name": "passanger_amount",
                        "placeholder": "Select number of passengers",
                        "options": create_numbers
                    }
                ]
            }
        )
    return open_dialog

def ephm_messgae(user_id, channel_id, actions, main_text, button_text):
    order_dm = slack_client.api_call(
        "chat.postEphemeral",
        channel=channel_id,
        text=main_text,
        attachments=[{
            "text": button_text,
            "callback_id": user_id + "all_rides",
            "color": "#fc6819",
            "attachment_type": "default",
            "actions": actions
        },],
        user=user_id
    )
    return order_dm

def event_info(event_id, user_id, channel_id):
    # Change URL to get a single ride event
    ride_info = requests.get(RIDEURL+"/"+event_id)
    ride = json.loads(ride_info.text)
    event_name = ride['name']
    event_address = ride['address']
    event_creator = ride['creator']
    event_start_time = ride['start_time']
    event_end_time = ride['end_time']
    count_cars = len(ride['cars'])
    car_buttons = []
    for car in ride['cars']:
        car_buttons.append(new_button("get_car_info",car['name']+"'s Car",car['id']+"_car_id"))
    main_text = "Name of The Event: %d \nAddress of the Event:  %d \nStart Time of Event:  %d \nEnd Time of Event: %d \nCurrent Amount of Cars in the Event:  %d \n Event Creator:  %d \n"
    button_text = "Click on a Car to see Car info"
    shown_message = ephm_messgae(user_id, channel_id, car_buttons, main_text, button_text)
    return shown_message
    

@app.route("/slack/slash_actions", methods=["POST"])
def slash_actions():
    # Parse the request payload
    request_json = request.form
    print(request_json)
    user_ida = request_json["user_id"]
    # Show the ordering dialog to the user
    dialog_popup(request_json["trigger_id"], user_ida)
    return make_response("", 200)

@app.route("/slack/test_ride", methods=["POST"])
def ride_test():
    request_json = request.form
    print(request_json)
    user_id = request_json["user_id"]
    channel_id = request_json["channel_id"]
    actions = []
    # create_row_data = {'name': 'First Last',
    #               'address':'Address',
    #               'start_time':"Thu, 02 Aug 2018 06:13:00",
    #               'end_time':"Thu, 15 Aug 2018 06:13:00",
    #               'creator':'red'}
    # res= requests.post(url=RIDEURL+"/create/event", json=create_row_data)
    rides_info = requests.get(RIDEURL+"/all")
    rides = json.loads(rides_info.text)
    for ride in rides:
        actions.append(new_button("get_event_info", ":blue_car:"+ride["name"], ride["id"]+"_event_id"))
    main_text = "I am Rideboard Bot :oncoming_automobile:, and I\'m here to find you a ride :ride:"
    button_text = "Click On the a Ride Button to see ride info"
    shown_message = ephm_messgae(user_id, channel_id, actions, main_text, button_text)
    print(shown_message)
    return make_response("", 200)

@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    message_action = json.loads(request.form["payload"])
    print(message_action)
    user_id = message_action["user"]["id"]
    if message_action["type"] == "interactive_message":
        # Show the ordering dialog to the user
        open_dialog = dialog_popup(message_action["trigger_id"], user_id)

    elif message_action["type"] == "dialog_submission":
        pass
    return make_response("", 200)


if __name__ == "__main__":
    app.run()
