from flask import Blueprint
from main import fileio
import library.server.configure as configure

# 创建蓝图对象
robot_blu = Blueprint("robot", __name__)

files = [
    (configure.get_config("data_path"), "")
]
fileio.register_file(files)
from controller.modules.robot.views import *
