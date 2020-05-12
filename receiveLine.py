# -*- coding: utf-8 -*-
from flask import Flask, request
import json
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId
from readConfig import configBot
import datetime

Authorization = configBot.AccessKey
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World!"


@app.route('/callback', methods=['POST'])
def callback():
    main_process()
    return '', 200


cluster = MongoClient("mongodb+srv://dbadmin:12345@testcluster-kzj5m.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = cluster['line']
login_collection = db['login']
user_collection = db['users']
main_id = "5e75c27b1c9d44000088df21"  # ID for the temp data


def main_process():
    LINE_API = configBot.LineApiReply
    req_dict = json.loads(request.data)
    user = req_dict["events"][0]['replyToken']
    print(req_dict)
    user_id = req_dict["events"][0]['source']['userId']
    dict_type = req_dict["events"][0]['type']
    if not dict_type:
        dict_type = req_dict["events"]
    print(dict_type)

    get_Modes = login_collection.find_one({"_id": ObjectId(main_id)})
    login = get_Modes["Login_Mode"]
    lockout_status = get_Modes["Lockout_status"]
    current_time = datetime.datetime.now()
    check_current_user = user_collection.find_one({"line_id": user_id})
    if check_current_user:
        check_Login = check_current_user["Logged_in"]
        print(check_current_user)

    if dict_type == 'follow':
        print('incase')
        clear_csv()
        cancel_richmenu()
        get_Modes = login_collection.find_one({"_id": ObjectId(main_id)})
        mode = get_Modes["Mode"]
        print(mode)
        init_sign_in(user, "", "", "", mode)
        login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Login_Mode": 1}})
        login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Mode": 1}})
    elif dict_type == "unfollow":
        if check_current_user:
            if check_Login is True:
                login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Attempt_count": 0}})
                user_collection.update_one({"_id": ObjectId(check_current_user["_id"])}, {"$set": {"Logged_in": False}})
                user_collection.update_one({"_id": ObjectId(check_current_user["_id"])}, {"$set": {"line_id": ""}})
                cancel_richmenu()
    else:
        if check_current_user:
            check_Login = check_current_user["Logged_in"]
            if check_Login is True:
                rich_menu()
        quick_reply(user)
        mes = req_dict["events"][0]['message']['text']
        print(mes)

    if lockout_status is True:
        print("incase lockout")
        end_time = get_Modes["Lockout_finish_time"]
        print(end_time)
        print(current_time)
        if current_time > end_time:
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Lockout_status": False}})
        else:
            return loop_lockout(user, end_time)

    if mes:
        if mes == 'Login':
            print('incase relogin')
            clear_csv()
            sign_in(user, "", "", "")
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Login_Mode": 2}})
        elif mes == 'Logout':
            if check_current_user:
                if check_Login is True:
                    login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Attempt_count": 0}})
                    user_collection.update_one({"_id": ObjectId(check_current_user["_id"])}, {"$set": {"Logged_in": False}})
                    user_collection.update_one({"_id": ObjectId(check_current_user["_id"])}, {"$set": {"line_id": ""}})
                    logout_success(user)
                    cancel_richmenu()
            else:
                logout_failed(user)

    if login == 1:
        mes = str(mes)
        mode = get_Modes["Mode"]
        extract = login_collection.find_one({"_id": ObjectId(main_id)})
        print(extract)
        mes1 = extract["Email"]
        mes2 = extract["Org"]
        mes3 = extract["Password"]
        print(mes1, mes2, mes3)

        if mode == 1:
            print('incase mode 1')
            print(type(mes1))
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Email": mes}})
            extract = login_collection.find_one({"_id": ObjectId(main_id)})
            mes1 = extract["Email"]
            print(mes1)
            init_sign_in(user, mes1, mes2, mes3, mode)
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Mode": 2}})
        elif mode == 2:
            print('incase mode 2')
            print(type(mes2))
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Org": mes}})
            extract = login_collection.find_one({"_id": ObjectId(main_id)})
            mes2 = extract["Org"]
            init_sign_in(user, mes1, mes2, mes3, mode)
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Mode": 3}})
        elif mode == 3:
            print('incase mode 3')
            print(type(mes3))
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Password": mes}})
            extract = login_collection.find_one({"_id": ObjectId(main_id)})
            mes3 = extract["Password"]
            sign_in(user, mes1, mes2, mes3)
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Login_Mode": 2}})
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Mode": 0}})

    if login == 2:
        mes = str(mes)
        extract = login_collection.find_one({"_id": ObjectId(main_id)})
        print(extract)
        mes1 = extract["Email"]
        mes2 = extract["Org"]
        mes3 = extract["Password"]
        n = extract["Attempt_count"]
        print(mes1, mes2, mes3)

        if mes == 'Email':
            print('incase email')
            loop_email(user)
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Mode": 1}})
        elif mes == 'Org':
            print('incase org')
            loop_org(user)
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Mode": 2}})
        elif mes == 'Password':
            print('incase password')
            loop_password(user)
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Mode": 3}})
        elif mes == 'Confirm':
            print('incase confirm')
            result = user_collection.find_one({"Email": mes1})
            result_id = result["_id"]
            print(result_id)
            print(type(result_id))
            n = n + 1  # Adds 1 to attempt count
            if result:  # Checks if variable was found
                if mes2 == result["Org"]:
                    if mes3 == result["Password"]:
                        if result["Logged_in"] is True:
                            user_already_logged_in(user)
                        else:
                            loop_success(user, mes1)
                            clear_csv()
                            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Attempt_count": 0}})
                            user_collection.update_one({"_id": ObjectId(result["_id"])}, {"$set": {"Logged_in": True}})
                            user_collection.update_one({"_id": ObjectId(result["_id"])}, {"$set": {"line_id": user_id}})

            else:
                if n >= 3:  # Checks if attempt no. 3 or higher
                    if n > 3:  # Checks if over 3 then proceed to add 5 mins for every try above 3
                        locktime = 5 + ((n - 3) * 5)
                        end_time = current_time + datetime.timedelta(minutes=locktime)
                        login_collection.update_one({"_id": ObjectId(main_id)},
                                                    {"$set": {"Lockout_finish_time": end_time}})
                        login_collection.update_one({"_id": ObjectId(main_id)},
                                                    {"$set": {"Lockout_status": True}})
                    else:
                        end_time = current_time + datetime.timedelta(minutes=5)
                        login_collection.update_one({"_id": ObjectId(main_id)},
                                                    {"$set": {"Lockout_finish_time": end_time}})
                        login_collection.update_one({"_id": ObjectId(main_id)},
                                                    {"$set": {"Lockout_status": True}})
                else:
                    loop_error(user)
                    sign_in(user, mes1, mes2, mes3)
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Attempt_count": n}})

        elif mes == 'Cancel':
            print('incase cancel')
            loop_cancel(user)
            clear_csv()  # Exit login mode

        if mode == 1:
            print('incase mode 1')
            print(type(mes1))
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Email": mes}})
            extract = login_collection.find_one({"_id": ObjectId(main_id)})
            mes1 = extract["Email"]
            sign_in(user, mes1, mes2, mes3)
        elif mode == 2:
            print('incase mode 2')
            print(type(mes2))
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Org": mes}})
            extract = login_collection.find_one({"_id": ObjectId(main_id)})
            mes2 = extract["Org"]
            sign_in(user, mes1, mes2, mes3)
        elif mode == 3:
            print('incase mode 3')
            print(type(mes3))
            login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Password": mes}})
            extract = login_collection.find_one({"_id": ObjectId(main_id)})
            mes3 = extract["Password"]
            sign_in(user, mes1, mes2, mes3)


def clear_csv():
    login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Login_Mode": 0}})
    login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Mode": 0}})
    login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Email": ""}})
    login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Org": ""}})
    login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Password": ""}})


def rich_menu():
    print("incase rich menu")
    LINE_API = "https://api.line.me/v2/bot/user/all/richmenu/richmenu-20c0e113b3d0ac3bd5fdd0209fa798d9"
    headers = {
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data = json.dumps({})
    requests.post(LINE_API, headers=headers, data=data)


def cancel_richmenu():
    Line_api = "https://api.line.me/v2/bot/user/all/richmenu"
    headers = {
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    requests.delete(Line_api, headers=headers)


def add_friend(user):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "Thank you for being my friend"
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data)


def init_sign_in(user, mes1, mes2, mes3, mode):
    if mode == 0:
        ask = "email"
    elif mode == 1:
        ask = "org"
    elif mode == 2:
        ask = "password"
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "flex",
                    "altText": "sign in",
                    "backgroundColor": "#3ebb75",
                    "contents": {
                        "type": "bubble",
                        "size": "giga",
                        # "backgroundColor": "#3ebb75",
                        "header": {
                            "type": "box",
                            "layout": "vertical",
                            "backgroundColor": "#46CCFF",
                            "contents": [
                                {
                                    "type": "box",
                                    "position": "absolute",
                                    "offsetTop": "60%",
                                    "offsetBottom": "20%",
                                    "offsetStart": "1%",
                                    "offsetEnd": "60%",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "image",
                                            "url": "https://si-sawad.com/image_report/background.png",
                                            "aspectRatio": "3:1",
                                            "size": "md",
                                        }

                                    ]
                                },
                                {
                                    "type": "text",
                                    "text": "sign in",
                                    "gravity": "center",
                                    "size": "lg"
                                }
                            ]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "backgroundColor": "#F9FFFF",
                            "spacing": "md",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "Email :" + mes1,
                                                    "wrap": True,
                                                    "size": "lg",
                                                    "flex": 1,
                                                    "gravity": "center"
                                                },
                                                {
                                                    "type": "separator"
                                                },
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "Org :" + mes2,
                                                    "wrap": True,
                                                    "size": "lg",
                                                    "flex": 1,
                                                    "gravity": "center"
                                                },
                                                {
                                                    "type": "separator"
                                                },

                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "Password :" + mes3,
                                                    "wrap": True,
                                                    "size": "lg",
                                                    "flex": 1,
                                                    "gravity": "center"
                                                },
                                                {
                                                    "type": "separator"
                                                },
                                            ]
                                        }
                                    ]
                                },
                            ],

                        },
                    }
                },
                {
                    "type": "text",
                    "text": "กรุณากรอก " + ask
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def sign_in(user, mes1, mes2, mes3):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "flex",
                    "altText": "singin",
                    "backgroundColor": "#3ebb75",
                    "contents": {
                        "type": "bubble",
                        "size": "giga",
                        # "backgroundColor": "#3ebb75",
                        "header": {
                            "type": "box",
                            "layout": "vertical",
                            "backgroundColor": "#46CCFF",
                            "contents": [
                                {
                                    "type": "box",
                                    "position": "absolute",
                                    "offsetTop": "60%",
                                    "offsetBottom": "20%",
                                    "offsetStart": "1%",
                                    "offsetEnd": "60%",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "image",
                                            "url": "https://si-sawad.com/image_report/background.png",
                                            "aspectRatio": "3:1",
                                            "size": "md",
                                        }

                                    ]
                                },
                                # {
                                #     "type": "image",
                                #     "url": "https://si-sawad.com/image_report/background.jpg",
                                #     "size": "sm",
                                #     # "aspectMode": "f",
                                #     "aspectRatio": "1:1",
                                #     # "offsetTop": "0px",
                                #     # "offsetBottom": "0px",
                                #     # "offsetStart": "0px",
                                #     # "offsetEnd": "0px",
                                #     "aspectMode": "cover",
                                #     "gravity": "center"
                                # },
                                {
                                    "type": "text",
                                    "text": "signin",
                                    "gravity": "center",
                                    "size": "lg"
                                }
                            ]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "backgroundColor": "#F9FFFF",
                            "spacing": "md",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "Email :" + mes1,
                                                    "wrap": True,
                                                    "size": "lg",
                                                    "flex": 1,
                                                    "gravity": "center"
                                                },
                                                {
                                                    "type": "separator"
                                                },
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "Org :" + mes2,
                                                    "wrap": True,
                                                    "size": "lg",
                                                    "flex": 1,
                                                    "gravity": "center"
                                                },
                                                {
                                                    "type": "separator"
                                                },

                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "Password :" + mes3,
                                                    "wrap": True,
                                                    "size": "lg",
                                                    "flex": 1,
                                                    "gravity": "center"
                                                },
                                                {
                                                    "type": "separator"
                                                },
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "image",
                                    "url": "https://si-sawad.com/image_report/Edit.png",
                                    "size": "md",
                                    "position": "absolute",
                                    "offsetTop": "12%",
                                    "offsetBottom": "25%",
                                    "offsetStart": "85%",
                                    "offsetEnd": "5%",
                                    "aspectRatio": "3:1",
                                    "action": {
                                        "type": "message",
                                        "label": "รายละเอียด",
                                        "text": "Email"
                                    }
                                },

                                {
                                    "type": "image",
                                    "url": "https://si-sawad.com/image_report/Edit.png",
                                    "size": "md",
                                    "position": "absolute",
                                    "offsetTop": "50%",
                                    "offsetBottom": "25%",
                                    "offsetStart": "85%",
                                    "offsetEnd": "5%",
                                    "aspectRatio": "3:1",
                                    "action": {
                                        "type": "message",
                                        "label": "รายละเอียด",
                                        "text": "Org"
                                    }
                                },
                                {
                                    "type": "image",
                                    "url": "https://si-sawad.com/image_report/Edit.png",
                                    "size": "md",
                                    "position": "absolute",
                                    "offsetTop": "90%",
                                    "offsetBottom": "10%",
                                    "offsetStart": "85%",
                                    "offsetEnd": "5%",
                                    "aspectRatio": "3:1",
                                    "action": {
                                        "type": "message",
                                        "label": "รายละเอียด",
                                        "text": "Password"
                                    }
                                },
                                # {
                                #     "type": "separator"
                                # },
                            ],

                        },
                        "footer": {
                            "type": "box",
                            "layout": "horizontal",
                            # "layout": "vertical",
                            "spacing": "md",
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "secondary",
                                    # "layout": "horizontal",
                                    "color": "#3ebb75",
                                    "action": {
                                        "type": "message",
                                        "label": "Confirm",
                                        "text": "Confirm"
                                    }
                                },
                                {
                                    "type": "button",
                                    "style": "secondary",
                                    # "layout": "horizontal",
                                    "color": "#eb766b",
                                    "action": {
                                        "type": "message",
                                        "label": "Cancel",
                                        "text": "Cancel"
                                    }
                                }
                            ]
                        }
                    }
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def loop_email(user):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "กรุณากรอก email"
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def loop_org(user):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "กรุณากรอก org"
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def loop_password(user):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "กรุณากรอก password"
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def loop_confirm(user):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "Please wait"
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def loop_cancel(user):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "Login canceled"
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def loop_error(user):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "Invalid login"
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def loop_success(user, mes1):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "Login successful, Welcome " + mes1
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def loop_lockout(user, release_time):
    time = release_time.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "You are currently locked out until " + time
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def logout_failed(user):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "You are currently not logged in"
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def logout_success(user):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "Logout successful"
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def user_already_logged_in(user):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "This user is already logged in"
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


def quick_reply(user):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data_send = json.dumps(
        {
            "replyToken": user,
            "messages": [
                {
                    "type": "text",
                    "text": "Hello Quick Reply!",
                    "quickReply": {
                        "items": [
                            {
                                "type": "action",
                                "action": {
                                    "type": "message",
                                    "label": "รายงาน",
                                    "text": "รายงาน"
                                }
                            },
                            {
                                "type": "action",
                                "action": {
                                    "type": "message",
                                    "label": "รายการอนุมัติ",
                                    "text": "รายการอนุมัติ"
                                }
                            },
                            {
                                "type": "action",
                                "action": {
                                    "type": "message",
                                    "label": "สืนค้าคงเหลือ",
                                    "text": "สืนค้าคงเหลือ"
                                }
                            },
                            {
                                "type": "action",
                                "action": {
                                    "type": "message",
                                    "label": "จบการทำงาน",
                                    "text": "จบการทำงาน"
                                }
                            },
                        ]
                    }
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


if __name__ == '__main__':
    app.run(debug=True, port=4000, host='127.0.0.1')
