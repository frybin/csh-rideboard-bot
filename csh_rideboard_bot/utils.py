import re
from datetime import datetime, timedelta
import requests
from csh_rideboard_bot import OAUTH_ID, RIDEURL

def delete_ephemeral(url):
    create_row_data = {
                        'response_type': 'ephemeral',
                        'text': '',
                        'replace_original': True,
                        'delete_original': True
                        }
    res = requests.post(url=url, json=create_row_data)
    return res

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

def create_dates(max_option=10):
    options = []
    time_format = '%a, %d %b %Y %H:%M:%S'
    for i in range(1, max_option+1):
        option = (datetime.now()+timedelta(days=i)).strftime(time_format)
        options.append({
            "label": option,
            "value": option
        })
    return options

def create_dialog_dropdown(label, name, placeholder, options):
    result = {
            "label": label,
            "type": "select",
            "name": name,
            "placeholder": placeholder,
            "options": options
            }
    return result

def create_dialog_text_field(label, name, placeholder, subtype=""):
    result = {
            "label": label,
            "name": name,
            "type": "text",
            "subtype": subtype,
            "placeholder": placeholder
            }
    return result

def create_dialog_text_area(label, name, hint):
    result = {
            "label": label,
            "name": name,
            "type": "textarea",
            "hint": hint
            }
    return result

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

def create_event(event_name, address, start_time, end_time, username,):
    create_row_data = {
                        'name': event_name,
                        'address': address,
                        'start_time': start_time,
                        'end_time': end_time,
                        'creator': username
                        }
    res = requests.post(url=RIDEURL+"/create/event", json=create_row_data)
    return res

def get_user_info(user_id):
    addr = 'https://slack.com/api/users.profile.get?'
    addr += 'token=' + OAUTH_ID + '&user=' + user_id
    res = requests.get(addr)
    return res.json()["profile"]

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
