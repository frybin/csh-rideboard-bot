####################################
# File name: utils.py              #
# Author: Fred Rybin               #
####################################
import re
from datetime import datetime, timedelta
from dateutil import tz
import requests
from csh_rideboard_bot import OAUTH_ID, RIDEURL

utc = tz.gettz('UTC')
gmt = tz.gettz('GMT')
edt = tz.gettz('America/New_York')
time_format = '%a, %d %b %Y %H:%M:%S %Z'
correct_time_format = '%a, %d %b %Y %H:%M:%S'

# Converts a datetime object from one timezone to another
def timezone_converter(time, from_zone, to_zone):
    time = time.replace(tzinfo=from_zone)
    time = time.astimezone(to_zone)
    return time

# Converts a string to a datetime object and then converts one timezone to another
def timezone_string_converter(time, from_zone, to_zone):
    time = datetime.strptime(time, time_format)
    time = time.replace(tzinfo=from_zone)
    time = time.astimezone(to_zone)
    return time

# Method used to delete a ephemeral message
def delete_ephemeral(url):
    create_row_data = {
                        'response_type': 'ephemeral',
                        'text': '',
                        'replace_original': True,
                        'delete_original': True
                        }
    res = requests.post(url=url, json=create_row_data)
    return res

# Create a button that can be used in a slack message
def new_button(name, text, value):
    attachment = {
        "name": name,
        "text": text,
        "type": "button",
        "value": value
    }
    return attachment

# Creates a list of numbers that can be used for slack dialog dropdown
def create_numbers(max_option=10):
    options = []
    for i in range(2, max_option+2):
        options.append({
            "label": i,
            "value": i
        })
    return options

# Creates a list of dates that can be used for slack dialog dropdown
def create_dates(max_option=10):
    options = []
    current_time = datetime.utcnow()
    for i in range(max_option+1):
        label = timezone_converter(current_time+timedelta(days=i), utc, edt).strftime(time_format)
        value = (current_time+timedelta(days=i)).strftime(correct_time_format)
        options.append({
            "label": label,
            "value": value
        })
    return options

# Creates a dictionary that makes a dropdown for a slack dialog popup
def create_dialog_dropdown(label, name, placeholder, options):
    result = {
            "label": label,
            "type": "select",
            "name": name,
            "placeholder": placeholder,
            "options": options
            }
    return result

# Creates a dictionary that makes a text field for a slack dialog popup
def create_dialog_text_field(label, name, placeholder, subtype=""):
    result = {
            "label": label,
            "name": name,
            "type": "text",
            "subtype": subtype,
            "placeholder": placeholder
            }
    return result

# Creates a dictionary that makes a text area for a slack dialog popup
def create_dialog_text_area(label, name, hint):
    result = {
            "label": label,
            "name": name,
            "type": "textarea",
            "hint": hint
            }
    return result

# Uses the variables to make a car for a ride and then sends post request to rideboard api
def create_car(event_id, username, name, departure_time, return_time, max_capacity, driver_comment=""):
    create_row_data = {
                        "name": name,
                        "username":username,
                        "departure_time":departure_time,
                        "return_time":return_time,
                        "max_capacity":max_capacity,
                        "driver_comment": driver_comment
                        }
    res = requests.post(url=RIDEURL+f"/create/car/{event_id}", json=create_row_data)
    return res

# Uses the variables to make a ride then sends post request to rideboard api
def create_event(event_name, address, start_time, end_time, username):
    create_row_data = {
                        'name': event_name,
                        'address': address,
                        'start_time': start_time,
                        'end_time': end_time,
                        'creator': username
                        }
    res = requests.post(url=RIDEURL+"/create/event", json=create_row_data)
    return res

# Get's a slack's user account information
def get_user_info(user_id):
    addr = 'https://slack.com/api/users.profile.get?'
    addr += 'token=' + OAUTH_ID + '&user=' + user_id
    res = requests.get(addr)
    return res.json()["profile"]

# Chesks user's email to see if they are part of csh or rit
def csh_user_check(user_id):
    user_email = get_user_info(user_id)["email"]
    rit_email = False
    csh_email = False
    username = ""
    if re.match(r'.+@csh\.rit\.edu', user_email):
        rit_email = True
        csh_email = True
        username = re.search(r'(.+)@csh\.rit\.edu', user_email).group(1)
    elif re.match(r'.+@rit\.edu', user_email):
        rit_email = True
        username = re.search(r'(.+)@rit\.edu', user_email).group(1)+ "(RIT)"
    return (rit_email, csh_email, username)
