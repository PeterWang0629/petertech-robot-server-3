import json

import requests
import sseclient


def new_chat(key, message="你好"):
    headers = {"content-type": "application/json", "Authorization": "Bearer " + key}
    body = {
        "content": message
    }
    res = requests.post('https://p0.kamiya.dev/api/openai/chatgpt/conversation', stream=True, json=body,
                        headers=headers)
    client = sseclient.SSEClient(res)
    # print("SSEClient created")
    for event in client.events():
        # print("in events")
        if 'fullContent' in json.loads(event.data):
            return json.loads(event.data)
    return {"status": 0}


def chat(key, id, message):
    headers = {"content-type": "application/json",
               "Authorization": "Bearer " + key}
    body = {
        "content": message
    }
    res = requests.post('https://p0.kamiya.dev/api/openai/chatgpt/conversation', stream=True, json=body,
                        headers=headers)
    client = sseclient.SSEClient(res)
    # print("SSEClient created")
    for event in client.events():
        # print("in events")
        if 'fullContent' in json.loads(event.data):
            return json.loads(event.data)


def bill(key):
    headers = {"content-type": "application/json",
               "Authorization": "Bearer " + key}
    res = requests.get('https://p0.kamiya.dev/api/billing/history?start=1&take=2', headers=headers)
    return json.loads(res.text)


def draw(key, prompts):
    headers = {"content-type": "application/json",
               "Authorization": "Bearer " + key}
    body = {
        "type": "text2image",
        "prompts": prompts,
        "negativePrompts": "",
        "step": 28,
        "cfg": 12,
        "seed": 218506577,
        "sampling": "DPM++ 2M Karras",
        "width": 768,
        "height": 512,
        "model": "original",
        "LoRAs": [
            {
                "id": "bocchiEdStyleLora_bocchiEdStyle",
                "weight": 60
            }
        ]
    }

    res = requests.post('https://p0.kamiya.dev/api/image/generate', json=body,
                        headers=headers)
    return json.loads(res.text)


def draw_state(key, hashid):
    headers = {"content-type": "application/json",
               "Authorization": "Bearer " + key}
    res = requests.get('https://p0.kamiya.dev/api/image/generate/' + hashid, headers=headers)
    return json.loads(res.text)


def draw_list(key):
    headers = {"content-type": "application/json",
               "Authorization": "Bearer " + key}
    res = requests.get('https://p0.kamiya.dev/api/image/generate/?start=1&take=1', headers=headers)
    return json.loads(res.text)


def account_info(key):
    headers = {"content-type": "application/json",
               "Authorization": "Bearer " + key}
    res = requests.get('https://p0.kamiya.dev/api/session/getDetails', headers=headers)
    return json.loads(res.text)
