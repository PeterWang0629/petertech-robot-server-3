from flask import Blueprint

# 创建蓝图对象
admin_blu = Blueprint("admin", __name__)

# 让视图函数和主程序建立关联
from controller.modules.admin.views import *
