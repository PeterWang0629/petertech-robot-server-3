from flask import Blueprint

# 创建蓝图对象
firewall_blu = Blueprint("firewall", __name__)

# 让视图函数和主程序建立关联
from controller.modules.firewall.views import *