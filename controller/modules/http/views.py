from flask import jsonify, send_file, request, render_template
from controller.modules.http import http_blu
from controller.libraries.server.basic_algorithms import *
from tasks import fileio, logger
import os

request_record = []
error_record = []


# @app.before_request
# def log_each_request():
#     global request_record
#     j = json.loads(requests.get("http://ip-api.com/json/" + request.remote_addr + "?lang=zh-CN").text)
#
#     if j['country'] != '中国':
#         e = send_md_msg("", "[REQUEST Report]",
#                         "**FOREIGN {method} Request recieved**<br/>{ip}<br/>{dt}<br/>*From HTTP sub server*".format(
#                             ip=request.remote_addr,
#                             dt=j["country"] + " " + j[
#                                 "regionName"] + " " + j[
#                                    "city"] + " " +
#                                j["timezone"] + "<br/>" + j["org"], method=request.method),
#                         "https://oapi.dingtalk.com/robot/send?access_token=b2b15239cd2204824b594c2b2c5bed7a5f3fe04e5df9461108ea420e03b884b3")
#         return redirect('https://www.google.com')
#     elif j["org"] == "Hangzhou Alibaba Advertising Co., Ltd." or j["org"] == "Aliyun Computing Co., LTD" or j[
#         "org"] == "Aliyun Computing Co.":
#         pass
#     else:
#         e = send_md_msg("", "[REQUEST Report]",
#                         "**Domestic {method} Request recieved**<br/>{ip}<br/>{dt}<br/>*From HTTP sub server*".format(
#                             ip=request.remote_addr,
#                             dt=j["country"] + " " + j[
#                                 "regionName"] + " " + j[
#                                    "city"] + " " +
#                                j["timezone"] + "<br/>" + j["org"], method=request.method),
#                         "https://oapi.dingtalk.com/robot/send?access_token=b2b15239cd2204824b594c2b2c5bed7a5f3fe04e5df9461108ea420e03b884b3")
#
# @app.errorhandler(Exception)
# def exception_handler(e):
#     if e.isinstance(werkzeug.exceptions.HTTPException):
#         return {"Success": False, "code": e.code, "msg": e.description}, e.code
#     else:
#
#         return {"Success": False, "code": 500, "msg": str(e), "data": {"exception": traceback.format_exc()}}, 500


# def save_data(data):
#     with open('data/data.dat', 'wb') as f:
#         pk.dump(data, f)
#
#
# def read_data():
#     with open("data/data.dat", 'rb') as f:
#         dat = pk.load(f)
#     return dat


# @http_blu.route('/<path:path>', methods=['GET'])
# def static_file(path):
#     if os.path.isdir(path):
#         if not path.endswith('/'): path += '/'
#         path += 'index.html'
#     if not os.path.isfile(path):
#         return "<h1>FILE NOT FOUND</h1>"
#     mimetype = get_mimetype(path)
#     response = Response(get_file(path), mimetype=mimetype)
#     if mimetype.startswith('audio/'): response.headers["Accept-Ranges"] = "bytes"
#     return response


@http_blu.route('/guijiao/<path:path>', methods=['GET'])
def guijiao_file(path):
    file_dir = os.path.join("guijiao_output", path + ".wav")
    if os.path.exists(file_dir):
        return send_file("..\\"+file_dir)

    else:
        return jsonify({"success": False, "code": 404, "message": "File not found", "data": None})


@http_blu.route('/guijiao/get-file', methods=['GET'])
def guijiao_get_file():
    data = request.get_json()
    fileid = data["fileid"]
    file_dir = os.path.join("guijiao_output", fileid + ".wav")
    if os.path.exists(file_dir):
        with open(file_dir, "rb") as f:
            dat = f.read()
        return jsonify({"success": True, "code": 200, "message": "200 OK", "data": {"file": dat}}), 200
    else:
        return jsonify({"success": False, "code": 404, "message": "File does not exist or outdated", "data": None}), 404


@http_blu.route("/error", methods=["GET"])
def recent_error():
    return render_template("error_report.html")


@http_blu.route("/history/get-error-history", methods=["POST"])
def get_error_history():
    dat = read_data(fileio)
    err_history = dat["error"]
    return jsonify({"success": True, "msg": "200 OK",  "code": 200, "data": {"error_history": err_history}}), 200

@http_blu.route("/history/get-guijiao-history", methods=["POST"])
def get_guijiao_history():
    dat = read_data(fileio)
    guijiao_history = dat["guijiao"]["history"]
    return jsonify({"success": True, "msg": "200 OK", "code": 200, "data": {"guijiao_history": guijiao_history}}), 200


@http_blu.route("/history/error")
def check_err_history():
    return render_template("error_history.html")


@http_blu.route("/history/guijiao")
def check_guijiao_history():
    return render_template("guijiao_history.html")



@http_blu.route("/")
def index_page():
    return render_template("index.html")
