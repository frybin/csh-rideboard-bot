####################################
# File name: __init__.py           #
# Author: Fred Rybin               #
####################################
import os
import re
import json
import random
from datetime import datetime, timedelta
import requests
from flask import Flask, request, make_response, Response
from slackclient import SlackClient

# Flask web server for incoming traffic from Slack
app = Flask(__name__)

# Gets app config from absolute file path
if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
else:
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))

# Slack client for Web API requests
slack_client = SlackClient(app.config['SLACK_BOT_TOKEN'])

# Defines variables from the app config
OAUTH_ID = app.config['OAUTH_TOKEN']
RIDEURL = app.config['RIDEBOARD_ADDR']+"/"+app.config['RIDEBOARD_KEY']
MAINTAINER = app.config['MAINTAINER']
RIDEWEB = app.config['RIDEBOARD_WEB']
WORKSPACE_URL = app.config['SLACK_WORKSPACE']

# pylint: disable=wrong-import-position
from csh_rideboard_bot.utils import (delete_ephemeral, new_button, create_numbers, create_dates,
                                    create_dialog_dropdown, create_car, create_dialog_text_field,
                                    create_dialog_text_area, get_user_info, csh_user_check, create_event,
                                    timezone_string_converter, gmt, edt, time_format, correct_time_format)

# Uses Slack Client to make Dialog Popup
def dialog_popup(trigger, prams, elements, title):
    open_dialog = slack_client.api_call(
            "dialog.open",
            trigger_id=trigger,
            dialog={
                "title": title,
                "submit_label": "Submit",
                "callback_id": prams,
                "elements": elements
            }
        )
    return open_dialog

# Uses Slack Client to make Ephemeral Message
def ephm_messgae(user_id, channel_id, actions, main_text, button_text=""):
    order_dm = slack_client.api_call(
        "chat.postEphemeral",
        channel=channel_id,
        text=main_text,
        attachments=[{
            "text": button_text,
            "callback_id": user_id + "_all_rides",
            "color": "%06x" % random.randint(0, 0xFFFFFF),
            "attachment_type": "default",
            "actions": actions
        },],
        user=user_id
    )
    return order_dm

# Gets a specific event's information from the rideboard api then displays it to user
def event_info(event_id, user_id, channel_id):
    ride_info = requests.get(RIDEURL+"/all?id="+event_id)
    ride = json.loads(ride_info.text)[0]
    # Information for the event
    event_name = ride['name']
    event_address = ride['address']
    event_creator = ride['creator']
    event_start_time = ride['start_time']
    event_end_time = ride['end_time']
    count_cars = len(ride['cars'])
    car_buttons = []
    checks = csh_user_check(user_id)
    csh_check = checks[1]
    username = checks[2]
    real_name = get_user_info(user_id)["real_name_normalized"]
    event_start_time = timezone_string_converter(event_start_time, gmt, edt).strftime(time_format)
    event_end_time = timezone_string_converter(event_end_time, gmt, edt).strftime(time_format)
    # Makes buttons for each car in the event
    for car in ride['cars']:
        car_buttons.append(new_button("get_car_info", car['name']+"'s Car", str(car['id'])+"_car_id"))
    # Text Displayed to user
    main_text = (f"Name of The Event: {event_name} \nAddress of the Event:  {event_address} \n"
                f"Start Time of Event:  {event_start_time} \nEnd Time of Event: {event_end_time} \n"
                f"Current Amount of Cars in the Event:  {count_cars} \n Event Creator:  {event_creator} \n")
    button_text = "Click on a Car to see Car info"
    event_start_time = datetime.strptime(ride['start_time'], time_format).strftime(correct_time_format)
    event_end_time = datetime.strptime(ride['end_time'], time_format).strftime(correct_time_format)
    # If the user is a CSH member then they could create a car for the event
    if csh_check:
        car_buttons.append(new_button("create_car", "Create New Car", (f"{event_id};{username};"
                                        f"{real_name};{event_start_time};{event_end_time}")))
    # If the user is the event creator then they could delete the event
    if username == event_creator and csh_check:
        car_buttons.append(new_button("delete_event_action", "Delete Event", str(event_id)+","+username))
    # Makes and sends a Ephemeral Message to the user
    shown_message = ephm_messgae(user_id, channel_id, car_buttons, main_text, button_text)
    return shown_message

# Gets a specific car's information from the rideboard api then displays it to user
def car_info(car_id, user_id, channel_id):
    car_info_json = requests.get(RIDEURL+"/get/car?id="+car_id)
    car = json.loads(car_info_json.text)[0]
    # Information for the car
    car_driver = car['name']
    car_avalible_seats = int(car['max_capacity'])-int(car['current_capacity'])
    car_departure_time = car['departure_time']
    car_return_time = car['return_time']
    car_current_passangers = ", ".join(car['riders'])
    car_driver_comment = car['driver_comment']
    actions = []
    checks = csh_user_check(user_id)
    rit_check = checks[0]
    csh_check = checks[1]
    username = checks[2]
    real_name = get_user_info(user_id)["real_name_normalized"]
    car_departure_time = timezone_string_converter(car_departure_time, gmt, edt).strftime(time_format)
    car_return_time = timezone_string_converter(car_return_time, gmt, edt).strftime(time_format)
    # If the user is in the car, then they could leave the car
    if username in car_current_passangers and rit_check:
        actions.append(new_button("leave_car_action", "Leave Car", str(car['ride_id'])+","+username+","+str(car_id)))
    # If the user is the car creator then they could delete the car
    elif username == car['username'] and csh_check:
        actions.append(new_button("delete_car_action", "Delete Car", str(car['ride_id'])+","+username))
    # If the user is a RIT member(Freshman) the they could join the car
    elif rit_check:
        actions.append(new_button("join_car_action", "Join Car", f"{str(car_id)},{username},{real_name}"))
    # Text Displayed to user
    main_text = (f"Driver Name: {car_driver} \nAvalible Seats: {car_avalible_seats} \n"
                f"Departure Time: {car_departure_time} \n" f"Return Time: {car_return_time} \n"
                f"Current Passangers in the Car: {car_current_passangers} \nDriver Comments: {car_driver_comment} \n")
    button_text = ""
    # Makes and sends a Ephemeral Message to the user
    shown_message = ephm_messgae(user_id, channel_id, actions, main_text, button_text)
    return shown_message

# Is the route that the slack slash command goes to
@app.route("/slack/ride_start", methods=["POST"])
def ride_start():
    request_json = request.form
    user_id = request_json["user_id"]
    channel_id = request_json["channel_id"]
    actions = []
    rides_info = requests.get(RIDEURL+"/all")
    rides = json.loads(rides_info.text)
    checks = csh_user_check(user_id)
    csh_check = checks[1]
    username = checks[2]
    # Makes buttons to show all currently events in rideboard
    for ride in rides:
        actions.append(new_button("get_event_info", ":blue_car:"+ride["name"], str(ride["id"])+"_event_id"))
    # Text Displayed to user
    main_text = ("I am Rideboard Bot :oncoming_automobile:, and I\'m here to find you a ride\n"
    "If you are a CSH Member please use your @csh.rit.edu email as your slack email to interact with Rideboard Bot\n"
    "If you don't have a CSH email, use you're @rit.edu email to be able to join or leave cars"
    f"To change your email, <{WORKSPACE_URL}/account/settings#email|Click Here>")
    button_text = "Click on a Ride's Name to see the Ride's info \nClick on Create New Event to make a new event"
    # If the user is a CSH member then they could create a event
    if csh_check:
        actions.append(new_button("create_event", "Create New Event", (f"{username}")))
    # Makes and sends a Ephemeral Message to the user
    ephm_messgae(user_id, channel_id, actions, main_text, button_text)
    return make_response("", 200)

# The route that all the interactive components in a message go to
@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    message_action = json.loads(request.form["payload"])
    response_url = message_action['response_url']
    user_id = message_action["user"]["id"]
    channel_id = message_action["channel"]["id"]
    # The app goes down this path if the user pressed a button
    if message_action["type"] == "interactive_message":
        # If the user pressed on a event name button then it does the nessesary actions to display the info
        if message_action["actions"][0]["name"] == "get_event_info":
            event_id = message_action["actions"][0]["value"].split("_")[0]
            event_info(event_id, user_id, channel_id)
        # If the user pressed on a car name button then it does the nessesary actions to display the info
        elif message_action["actions"][0]["name"] == "get_car_info":
            car_id = message_action["actions"][0]["value"].split("_")[0]
            car_info(car_id, user_id, channel_id)
        # If the user pressed on a leave car button then it does the nessesary actions to remove them from the car
        elif message_action["actions"][0]["name"] == "leave_car_action":
            payload = message_action["actions"][0]["value"].split(",")
            event_id = payload[0]
            username = payload[1]
            car_id = payload[2]
            car_action = requests.put(RIDEURL+f"/leave/{event_id}/{username}")
            if car_action.status_code == 200:
                ephm_messgae(user_id, channel_id, [], "You have successfully left the car")
                car_info(car_id, user_id, channel_id)
            else:
                ephm_messgae(user_id, channel_id, [], (f"Oops, something went wrong "
                                                        f"please contact @{MAINTAINER} on slack"))
        # If the user pressed on a delete car button then it does the nessesary actions to delete the car
        elif message_action["actions"][0]["name"] == "delete_car_action":
            payload = message_action["actions"][0]["value"].split(",")
            event_id = payload[0]
            username = payload[1]
            car_action = requests.delete(RIDEURL+f"/delete/car/{event_id}/{username}")
            if car_action.status_code == 200:
                ephm_messgae(user_id, channel_id, [], "You have successfully deleted your car")
                event_info(event_id, user_id, channel_id)
            else:
                ephm_messgae(user_id, channel_id, [], (f"Oops, something went wrong "
                                                        f"please contact @{MAINTAINER} on slack"))
        # If the user pressed on a delete event button then it does the nessesary actions to delete the event
        elif message_action["actions"][0]["name"] == "delete_event_action":
            payload = message_action["actions"][0]["value"].split(",")
            event_id = payload[0]
            username = payload[1]
            car_action = requests.delete(RIDEURL+f"/delete/event/{event_id}/{username}")
            if car_action.status_code == 200:
                ephm_messgae(user_id, channel_id, [], "You have successfully deleted your event")
            else:
                ephm_messgae(user_id, channel_id, [], (f"Oops, something went wrong "
                                                        f"please contact @{MAINTAINER} on slack"))
        # If the user pressed on a join car button then it does the nessesary actions to add them to the car
        elif message_action["actions"][0]["name"] == "join_car_action":
            payload = message_action["actions"][0]["value"].split(",")
            car_id = payload[0]
            username = payload[1]
            first_name = payload[2]
            last_name = "(Slack)"
            car_action = requests.put(RIDEURL+f"/join/{car_id}/{username}/{first_name}/{last_name}")
            if car_action.status_code == 200:
                ephm_messgae(user_id, channel_id, [], "You have successfully joined the car")
                car_info(car_id, user_id, channel_id)
            else:
                ephm_messgae(user_id, channel_id, [], (f"Oops, something went wrong "
                                                        f"please contact @{MAINTAINER} on slack"))
        # If the user pressed on a create car button then it does the nessesary actions to create a car
        elif message_action["actions"][0]["name"] == "create_car":
            elements = [create_dialog_dropdown("Amount of passengers", "passanger_amount",
                                                "Select number of passengers", create_numbers()),
                        create_dialog_text_area("Driver Comment", "driver_comment",
                                        "Add any comments that you would like your riders to know")]
            dialog_popup(message_action["trigger_id"],
                                        "car_creation_form;"+message_action["actions"][0]["value"],
                                        elements, "Create Car")
        # If the user pressed on a create event button then it does the nessesary actions to create a event
        elif message_action["actions"][0]["name"] == "create_event":
            start_dates = create_dates()
            elements = [create_dialog_text_field("Event Name", "event_name", "This is a New Event"),
            create_dialog_text_area("Event Address", "event_address", "Please enter full address for destination"),
            create_dialog_dropdown("Start Time of event", "start_time",
                                                "Select the date of when the event starts", start_dates)]
            dialog_popup(message_action["trigger_id"],
                                        "event_creation_form;"+message_action["actions"][0]["value"],
                                        elements, "Create Event")
    # The app goes down this path if they submitted a dialog message
    elif message_action["type"] == "dialog_submission":
        payload = message_action["callback_id"].split(";")
        # If the user submitted the dialog to make a car, it does the appropiate actions
        if payload[0] == 'car_creation_form':
            made_car = create_car(payload[1], payload[2], payload[3], payload[4],
                                payload[5], message_action["submission"]["passanger_amount"],
                                message_action["submission"]["driver_comment"])
            if made_car.status_code == 200:
                car_id = json.loads(made_car.text)["cars"][-1]["id"]
                ephm_messgae(user_id, channel_id, [], ("You have successfully made a car\nTo edit time or make changes"
                                                       " to the car please go to the "
                                                       f"<{RIDEWEB}/edit/carform/{car_id}|Web App>"))
                event_info(payload[1], user_id, channel_id)
            else:
                ephm_messgae(user_id, channel_id, [], (f"Oops, something went wrong "
                                                        f"please contact @{MAINTAINER} on slack"))
        # If the user submitted the dialog to make a event, it does the appropiate actions
        elif payload[0] == 'event_creation_form':
            end_time = datetime.strptime(message_action["submission"]["start_time"],
                                        correct_time_format)+timedelta(days=1)
            made_event = create_event(message_action["submission"]["event_name"],
            message_action["submission"]["event_address"], message_action["submission"]["start_time"],
            end_time.strftime(correct_time_format), payload[1])
            if made_event.status_code == 200:
                event_id = json.loads(made_event.text)["id"]
                ephm_messgae(user_id, channel_id, [], (f"You have successfully made a event\nTo edit time or make "
                                                       f"changes to the event please go to the "
                                                       f"<{RIDEWEB}/edit/rideform/{event_id}|Web App>"))
            else:
                ephm_messgae(user_id, channel_id, [], (f"Oops, something went wrong "
                                                        f"please contact @{MAINTAINER} on slack"))
    # Deletes the previous message in the end
    delete_ephemeral(response_url)
    return make_response("", 200)


if __name__ == "__main__":
    app.run()
