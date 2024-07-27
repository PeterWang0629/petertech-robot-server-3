import secrets
import time

from controller.libraries.features.guijiao_lib import *

# 临时文件存放目录
tempOutputPath = "./guijiao_output/"


# 生成ID
def makeid():
    currentSec = str(int(time.time()))
    id = currentSec + "_" + secrets.token_hex(8)
    return id


# 用户发出生成音频的请求
def generate_audio(text: str):
    # 生成选项
    rawData = text
    inYsddMode = True
    norm = False
    reverse = False
    speedMult = 1
    pitchMult = 1
    # 获取ID
    id = makeid()
    # 活字印刷实例
    HZYS = huoZiYinShua("controller/static/guijiao/settings.json")
    # 导出音频
    HZYS.export(text,
                filePath=tempOutputPath + id + ".wav",
                inYsddMode=True,
                norm=False,
                reverse=False,
                speedMult=1,
                pitchMult=1)
    # 返回ID
    return id
