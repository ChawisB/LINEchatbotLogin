# -*- coding: utf-8 -*-
from flask import Flask, request
import json
import requests
#  import pandas as pd
#  import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from readConfig import configBot

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
    fileLink = 'https://www.google.com/'  # Change to target file's link
    fileName = 'Forecast report'  # Change to file's name
    date = '04/03/2020'  # Change to date of said document

    req_dict = json.loads(request.data)
    # print(req_dict)
    user = req_dict["events"][0]['replyToken']
    print(req_dict)
    # user_id = req_dict["events"][0]['source']['userId']
    # mes = req_dict["events"][0]['message']['text']
    dict_type = req_dict["events"][0]['type']
    print(dict_type)

    get_Modes = login_collection.find_one({"_id": ObjectId(main_id)})
    login = get_Modes["Login_Mode"]
    mode = get_Modes["Mode"]
    print(mode)

    if dict_type == 'follow':
        print('incase')
        clear_csv()
        init_sign_in(user, "", "", "", mode)
        login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Login_Mode": 1}})
        login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Mode": 1}})
    else:
        mes = req_dict["events"][0]['message']['text']
        print(mes)

    if mes == 'Login':
        print('incase relogin')
        clear_csv()
        sign_in(user, "", "", "")
        login_collection.update_one({"_id": ObjectId(main_id)}, {"$set": {"Login_Mode": 2}})

    if login == 1:
        mes = str(mes)
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
            print(result)
            print(type(result))
            if result:
                if mes2 == result["Org"]:
                    if mes3 == result["Password"]:
                        loop_success(user, mes1)
                        clear_csv()
            else:
                return loop_error(user)
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


if __name__ == '__main__':
    app.run(debug=True, port=4000, host='127.0.0.1')
