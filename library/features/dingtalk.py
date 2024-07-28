import base64
import hashlib
import hmac
import json
import requests

from urllib3 import encode_multipart_formdata


def check_sig(timestamp):
    app_secret = 'wplwdeGfN4BSeikwkMGlRdJOdmaKYgBca1Le1y6gAuHDulFrbZGJsTB4s6bGLG4f'
    app_secret_enc = app_secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, app_secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


def getToken():
    corpid = 'dingzxs8cdfse4kfpsk9'
    secrect = 'wplwdeGfN4BSeikwkMGlRdJOdmaKYgBca1Le1y6gAuHDulFrbZGJsTB4s6bGLG4f'
    url = 'https://oapi.dingtalk.com/gettoken?appkey=%s&appsecret=%s' % (corpid, secrect)
    req = requests.get(url)
    access_token = json.loads(req.text)
    return access_token['access_token']


def get_media_id(file_path, file_name, access_token):
    url_post = r"https://oapi.dingtalk.com/media/upload?access_token=%s&type=file" % access_token
    headers = {}
    data = {}
    data['media'] = (file_name, open(file_path, 'rb').read())  # 说明：file_name,不支持中文，必须为应为字符
    encode_data = encode_multipart_formdata(data)
    data = encode_data[0]
    headers['Content-Type'] = encode_data[1]
    r = requests.post(url_post, headers=headers, data=data)
    media_id = json.loads(r.text)["media_id"]
    return media_id


def send_md_msg(userid, title, message, webhook_url):
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": message
        },
        '''
        "msgtype": "text",
        "text": {
            "content": message
        },
        '''
        "at": {
            "atUserIds": [
                userid
            ],
        }
    }
    # 利用requests发送post请求
    req = requests.post(webhook_url, json=data)


def send_text_msg(userid, content, webhook_url, p=False):
    data = {
        "msgtype": "text",
        "text": {"content": content},
        "at": {
            "atUserIds": [
                userid
            ],
        }
    }
    # 利用requests发送post请求
    req = requests.post(webhook_url, json=data)
