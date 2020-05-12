# -*- coding: utf-8 -*-
from flask import Flask, request
import json
import requests
import pandas as pd
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


def main_process():
    LINE_API = configBot.LineApiReply
    fileLink = 'https://www.google.com/'  # Change to target file's link
    fileName = 'Forecast report'  # Change to file's name
    date = '04/03/2020'  # Change to date of said document
    df = pd.read_csv("data.csv", delimiter=',')
    df[['Email', 'Org', 'Password']] = df[['Email', 'Org', 'Password']].astype(str)
    print(df)
    req_dict = json.loads(request.data)
    # print(req_dict)
    user = req_dict["events"][0]['replyToken']
    print(req_dict)
    # user_id = req_dict["events"][0]['source']['userId']
    # mes = req_dict["events"][0]['message']['text']
    dict_type = req_dict["events"][0]['type']
    print(dict_type)

    if dict_type == 'follow':
        print('incase')
        clear_csv(df)
        init_sign_in(user, "", "", "")
        df['Login Mode'].replace(0, 1, inplace=True)
        df['Mode'] = 1
        df.to_csv('data.csv', index=False)
    else:
        mes = req_dict["events"][0]['message']['text']
        print(mes)

    if mes == 'Login':
        print('incase relogin')
        clear_csv(df)
        sign_in(user, "", "", "")
        df['Login Mode'].replace(0, 2, inplace=True)
        df.to_csv('data.csv', index=False)

    if 1 in df['Login Mode'].values:
        mes = str(mes)
        mes1 = str(df.at[0, 'Email']).replace(".0", '')
        mes2 = str(df.at[0, 'Org']).replace(".0", '')
        mes3 = str(df.at[0, 'Password']).replace(".0", '')
        print(mes1, mes2, mes3)
        if (str(mes1) == 'NaN') or (str(mes1) == 'nan'):
            mes1 = ''
        if (str(mes2) == 'NaN') or (str(mes2) == 'nan'):
            mes2 = ''
        if (str(mes3) == 'NaN') or (str(mes3) == 'nan'):
            mes3 = ''

        if 1 in df['Mode'].values:
            print('incase mode 1')
            print(type(mes1))
            df['Email'] = mes
            mes1 = df.at[0, 'Email']
            init_sign_in(user, str(mes1), str(mes2), str(mes3))
            df['Mode'] = 2
            df.to_csv('data.csv', index=False)
        elif 2 in df['Mode'].values:
            print('incase mode 2')
            print(type(mes2))
            df['Org'] = mes
            mes2 = df.at[0, 'Org']
            init_sign_in(user, str(mes1), str(mes2), str(mes3))
            df['Mode'] = 3
            df.to_csv('data.csv', index=False)
        elif 3 in df['Mode'].values:
            print('incase mode 3')
            print(type(mes3))
            df['Password'] = mes
            mes3 = df.at[0, 'Password']
            sign_in(user, str(mes1), str(mes2), str(mes3))
            df['Login Mode'] = 2
            df['Mode'] = 0
            df.to_csv('data.csv', index=False)

    if 2 in df['Login Mode'].values:
        if mes == 'Email':
            print('incase email')
            loop_email(user)
            df['Mode'] = 1
            df.to_csv('data.csv', index=False)
        elif mes == 'Org':
            print('incase org')
            loop_org(user)
            df['Mode'] = 2
            df.to_csv('data.csv', index=False)
        elif mes == 'Password':
            print('incase password')
            loop_password(user)
            df['Mode'] = 3
            df.to_csv('data.csv', index=False)
        elif mes == 'Confirm':
            print('incase confirm')
            loop_confirm(user)
            # add function to send to server
            clear_csv(df)  # Exit login mode
            df.to_csv('data.csv', index=False)
        elif mes == 'Cancel':
            print('incase cancel')
            loop_cancel(user)
            clear_csv(df)  # Exit login mode
            df.to_csv('data.csv', index=False)
        #        elif (0 in df['Mode'].values) and (mes != 'Confirm') or (mes != 'Cancel'):
        #           loop_error(user)
        mes = str(mes)
        mes1 = str(df.at[0, 'Email']).replace(".0", '')
        mes2 = str(df.at[0, 'Org']).replace(".0", '')
        mes3 = str(df.at[0, 'Password']).replace(".0", '')
        print(mes1, mes2, mes3)
        if (str(mes1) == 'NaN') or (str(mes1) == 'nan'):
            mes1 = ''
        if (str(mes2) == 'NaN') or (str(mes2) == 'nan'):
            mes2 = ''
        if (str(mes3) == 'NaN') or (str(mes3) == 'nan'):
            mes3 = ''

        if 1 in df['Mode'].values:
            print('incase mode 1')
            print(type(mes1))
            df['Email'] = mes
            mes1 = df.at[0, 'Email']
            sign_in(user, str(mes1), str(mes2), str(mes3))
            df.to_csv('data.csv', index=False)
        elif 2 in df['Mode'].values:
            print('incase mode 2')
            print(type(mes2))
            df['Org'] = mes
            mes2 = df.at[0, 'Org']
            sign_in(user, str(mes1), str(mes2), str(mes3))
            df.to_csv('data.csv', index=False)
        elif 3 in df['Mode'].values:
            print('incase mode 3')
            print(type(mes3))
            df['Password'] = mes
            mes3 = df.at[0, 'Password']
            sign_in(user, str(mes1), str(mes2), str(mes3))
            df.to_csv('data.csv', index=False)


def clear_csv(dataframe):
    dataframe['Login Mode'] = 0
    dataframe['Mode'] = 0
    dataframe['Email'] = ''
    dataframe['Org'] = ''
    dataframe['Password'] = ''


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


def send_sticker(user, mes):
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
                    "text": "ท่านพิมพ์คำว่า" + mes + "มาใช่หรือไม่"
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data)


def flex_message(user):
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
                    "type": "flex",
                    "altText": "This is a Flex Message",
                    "contents": {
                        "type": "bubble",
                        "size": "giga",
                        "header": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "Hello World!"
                                }
                            ]
                        },
                        "body": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "image",
                                            "url": "https://si-sawad.com/report_link/original.jpg",
                                            "size": "sm",
                                            "aspectRatio": "1:1",
                                            "aspectMode": "cover"
                                        }
                                    ]
                                }
                            ]
                            ,
                            "action": {
                                "type": "uri",
                                "uri": "https://www.google.com/"
                            }
                        },
                        "footer": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "secondary",
                                    "action": {
                                        "type": "uri",
                                        "label": "Link 1",
                                        "uri": "https://developers.line.biz/en/docs/messaging-api/flex-message-elements/#container"
                                    }
                                },
                                {
                                    "type": "button",
                                    "style": "secondary",
                                    "action": {
                                        "type": "uri",
                                        "label": "Link 2",
                                        "uri": "https://www.facebook.com/"
                                    }
                                }
                            ]
                        }
                    }
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data)


def template_block(user, fileLink, fileName, date):
    LINE_API = configBot.LineApiReply
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {' + Authorization + '}'
    }
    data = json.dumps(
        {
            "replyToken": user,
            "messages":
                [
                    {
                        "type": "flex",
                        "altText": "This is a Flex Message",
                        "contents": {
                            "type": "bubble",
                            "size": "giga",
                            "body": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "image",
                                        "url": "https://si-sawad.com/image_report/test.png",
                                        "size": "full",
                                        "aspectRatio": "1:1",
                                        "aspectMode": "cover",
                                        "gravity": "center"
                                    },
                                    {
                                        "type": "image",
                                        "url": "https://si-sawad.com/image_report/transparent_background.png",
                                        "position": "absolute",
                                        "aspectMode": "fit",
                                        "aspectRatio": "1:1",
                                        "offsetTop": "0px",
                                        "offsetBottom": "0px",
                                        "offsetStart": "0px",
                                        "offsetEnd": "0px",
                                        "size": "full"
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
                                                        "type": "box",
                                                        "layout": "horizontal",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": fileName,
                                                                "size": "xl",
                                                                "color": "#ffffff"
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        "type": "box",
                                                        "layout": "horizontal",
                                                        "contents": [
                                                            {
                                                                "type": "box",
                                                                "layout": "baseline",
                                                                "contents": [
                                                                    {
                                                                        "type": "text",
                                                                        "text": date,
                                                                        "color": "#ffffff",
                                                                        "size": "md",
                                                                        "flex": 0,
                                                                        "align": "end"
                                                                    }
                                                                ],
                                                                "flex": 0,
                                                                "spacing": "lg"
                                                            }
                                                        ]
                                                    }
                                                ],
                                                "spacing": "xs"
                                            }
                                        ],
                                        "position": "absolute",
                                        "offsetBottom": "0px",
                                        "offsetStart": "0px",
                                        "offsetEnd": "0px",
                                        "paddingAll": "20px"
                                    }
                                ],
                                "action": {
                                    "type": "uri",
                                    "uri": fileLink
                                },
                                "paddingAll": "0px"
                            }
                        }
                    }
                ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data)


def init_sign_in(user, mes1, mes2, mes3):
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
                                    "offsetTop": "34%",
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
                                    "offsetTop": "56%",
                                    "offsetBottom": "25%",
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
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "button",
                                            "style": "link",
                                            "color": "#905c44",
                                            "action": {
                                                "type": "message",
                                                "label": "รายละเอียด",
                                                "text": "รายละเอียด "
                                            }
                                        }
                                    ]
                                }
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
                    "text": "Login confirmed"
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
                    "text": "Invalid command"
                }
            ]
        }
    )
    requests.post(LINE_API, headers=headers, data=data_send)


if __name__ == '__main__':
    app.run(debug=True, port=4000, host='127.0.0.1')
