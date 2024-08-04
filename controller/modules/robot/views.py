from controller.modules.robot import robot_blu
from library.features.dingtalk import send_md_msg, send_text_msg, check_sig
from library.features.robot_cmd_process import RobotCommands
from library.server.basic_algorithms import dict_cmp, reset_data, read_data, get_init_data, save_data
from tasks import fileio, logger
from flask import jsonify, request
from datetime import datetime
import json
import os
import time
import traceback
import secrets
import threading


def handle_info(req_data):
    # global init_dat
    text_info = req_data['text']['content'].strip()
    webhook_url = req_data['sessionWebhook']
    sender_id = req_data['senderId']
    sender_nick = req_data["senderNick"]
    init_dat = get_init_data()
    try:
        dat = read_data(fileio)
    except:
        dat = reset_data(fileio)
        send_md_msg(sender_id, "[Error Message]",
                    "**Data Error**<br>Failed while reading data file.<br>Recreated data file.<br>Time:" + datetime.now().strftime(
                        "%c"), webhook_url)
        return
    if not dict_cmp(init_dat, dat):
        dat = reset_data(fileio)
        send_md_msg(sender_id, "[Error Message]",
                    "**Data Error**<br>The data file format is incorrect.<br>Recreated data file.<br>Time:" + datetime.now().strftime(
                        "%c"), webhook_url)
        return

    try:
        # logger.log("INFO", "")
        logger.log("INFO", f"Received message from user {sender_nick} (ID {sender_id}):")
        for lines in text_info.split("\n"):
            logger.log("INFO", lines)
        # logger.log("INFO", "")
        if sender_id not in dat["users"]:
            dat["users"][sender_id] = [sender_nick]
            save_data(fileio, dat)
        elif sender_nick not in dat["users"][sender_id]:
            dat["users"][sender_id].append(sender_nick)
            save_data(fileio, dat)
        else:
            pass
        if sender_id in dat["ban"]:
            send_md_msg(sender_id, "[Error Message]",
                        "**Access Denied**<br>**" + sender_nick + "** has been banned from this robot.", webhook_url)
            return

        elif sender_nick in dat["ban"]:
            # cmd = Commands(req_data)
            # cmd.run("c$ban$add$"+sender_id)
            dat["ban"].append(sender_id)
            save_data(fileio, dat)
            send_md_msg(sender_id, "[Error Message]",
                        "**Access Denied**<br>**" + sender_nick + "**'s ID has been banned from this robot.",
                        webhook_url)

            return

        elif text_info in dat["ref"]:
            if dat["ref"][text_info]["type"] == "md":
                send_md_msg(sender_id, "[Robot Message]", dat["ref"][text_info]["answer"], webhook_url)
            elif dat["ref"][text_info]["type"] == "txt":
                send_text_msg(sender_id, dat["ref"][text_info]["answer"], webhook_url)

        else:
            cmd = RobotCommands(req_data, fileio, logger)
            cmd.run(text_info)

    except Exception as e:
        err_id = secrets.token_hex(16)
        dat["error"][err_id] = {}
        dat["error"][err_id]["time"] = time.time()
        dat["error"][err_id]["error"] = traceback.format_exc()
        logger.log("ERROR", "")
        logger.log("ERROR", f"Caught Exception in handle_info (Error ID {err_id}):")
        for lines in traceback.format_exc().split("\n"):
            logger.log("ERROR", lines)
        logger.log("ERROR", "")
        save_data(fileio, dat)
        send_md_msg(sender_id, "[Error Message]",
                    "**Error Report**<br>**Brief**:\n```text\n" + dat["error"][err_id]["error"].split("\n")[
                        -2] + "\n```\n**Time**:" + datetime.now().strftime(
                        "%c") + "<br>**Error ID:**:" + err_id + "<br>**Detailed Error Report:**<br>[http://180.166.0.98:1453/error?id={err_id}](http://180.166.0.98:1453/error?id={err_id})".format(
                        err_id=err_id), webhook_url)


@robot_blu.route("/", methods=["POST"])
def get_data():
    if request.method == "POST":
        timestamp = request.headers.get('Timestamp')
        sign = request.headers.get('Sign')
        if check_sig(timestamp) == sign:
            req_data = json.loads(str(request.data, 'utf-8'))
            ref = handle_info(req_data)
            logger.log("INFO", 'Root route received request, 200 OK')
            return jsonify({"success": True, "msg": "200 OK", "data": None}), 200
        logger.log("WARN", 'Root route received request with invalid signature')
        return jsonify({"success": False, "msg": "invalid signature", "data": None}), 403
    logger.log("WARN", 'Root route received Non-POST Request')
    return jsonify({"success": False, "msg": "only accept POST", "data": None}), 403