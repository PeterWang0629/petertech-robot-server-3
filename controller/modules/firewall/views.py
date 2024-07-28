# from controller.modules.robot import robot_blu
# from main import logger, fileio, app
# import traceback, secrets
# from flask import jsonify, request
# from controller.library.algorithms import *
# from werkzeug.exceptions import HTTPException
#
#
# def error_handler(error):
#     if not error.isinstance(HTTPException):
#         dat = read_data(fileio)
#         logger.log("ERROR", "Caught Exception in error_handler:")
#         for lines in traceback.format_exc().split("\n"):
#             logger.log("ERROR", lines)
#         logger.log("INFO", "[END].")
#         err_id = secrets.token_hex(16)
#         dat["error"][err_id] = {}
#         dat["error"][err_id]["time"] = time.time()
#         dat["error"][err_id]["error"] = traceback.format_exc()
#         save_data(fileio, dat)
#         return jsonify({"success": False, "msg": "Internal Server Error", "data": None}), 500
#     else:
#         return {"Success": False, "code": error.code, "msg": error.description}, error.code
