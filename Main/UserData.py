# coding:utf-8

import os
import InterGUI as GUI
import DataLibrary as DL
import requests
import json


def 初始化用户数据(Reset):
    # 函数作用：检查软件路径是否有用户文档或是否强制重置用户文档
    if ((os.path.exists(GUI.用户文档路径) is False) or Reset == 1):
        f = open(GUI.用户文档路径, "w", encoding='utf-8')
        f.write(初始化用户数据文档())
        f.close()


def 初始化设置数据(Reset):
    # 函数作用：检查软件路径是否有设置文档或是否强制重置设置文档
    if ((os.path.exists(GUI.设置文档路径) is False) or Reset == 1):
        f = open(GUI.设置文档路径, "w", encoding='utf-8')
        f.write(初始化设置数据文档())
        f.close()


def 初始化跨线程变量(Reset):
    # 函数作用：检查软件路径是否有设置文档或是否强制重置跨线程变量文档
    if ((os.path.exists(GUI.跨线程变量文档路径) is False) or Reset == 1):
        f = open(GUI.跨线程变量文档路径, "w", encoding='utf-8')
        f.write(初始化跨线程变量文档())
        f.close()


def 读取数据细(路径, 父元素, 子元素):
    # 函数作用：直接读取数据，而尽量不将数据存储到变量中
    文档 = open(路径, 'r', encoding='utf-8')
    用户文档 = json.loads(文档.read())
    文档.close()
    if 子元素 == "":
        return 用户文档[父元素]
    else:
        return 用户文档[父元素][子元素]


def 读取用户数据():
    # 函数作用：读取并返回用户文档
    文档 = open(GUI.用户文档路径, 'r', encoding='utf-8')
    用户文档 = json.loads(文档.read())
    文档.close()
    return 用户文档


def 读取设置数据():
    # 函数作用：读取并返回设置文档
    文档 = open(GUI.设置文档路径, 'r', encoding='utf-8')
    设置文档 = json.loads(文档.read())
    文档.close()
    return 设置文档


def 保存用户数据(新用户文档):
    # 函数作用：保存新的用户文档
    新用户文档 = json.dumps(新用户文档, ensure_ascii=False)
    文档 = open(GUI.用户文档路径, 'w', encoding='utf-8')
    文档.write(新用户文档)
    文档.close()
    # 保存用户数据的时候，会导致用户数据md5值改变
    # 所以需要同时更新设置数据里面的usermd5
    新用户数据 = 读取用户数据()
    设置数据 = 读取设置数据()
    设置数据['usermd5'] = DL.md5_text(str(新用户数据))
    保存设置数据(设置数据)


def 保存设置数据(新设置文档):
    # 函数作用：保存新的设置文档
    新设置文档 = json.dumps(新设置文档, ensure_ascii=False)
    文档 = open(GUI.设置文档路径, 'w', encoding='utf-8')
    文档.write(新设置文档)
    文档.close()


def 自启动脚本路径():
    # 函数作用：返回用户启动文件夹的自启动脚本路径
    用户路径 = os.environ['UserProfile']
    启动路径 = os.path.join(
        用户路径, 'AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    # print(用户路径)
    脚本路径 = os.path.join(启动路径, 'test.bat')
    return 脚本路径


def 设置自启动(file):
    # 函数作用：根据自启动脚本路径，创建一个自启动脚本，使其能够在开机时执自行启动所指向的程序
    脚本路径 = 自启动脚本路径()
    f = open(脚本路径, "w")
    内容 = "start " + file
    f.write(内容)
    f.close()


def 关闭自启动():
    # 函数作用：根据自启动脚本路径，判断是否有自启动脚本，如有就删除自启动脚本
    脚本路径 = 自启动脚本路径()
    # print(filetest)
    if (os.path.exists(脚本路径)):
        # print("路径有此文档")
        os.remove(脚本路径)
    # else:
        # print("路径无此文档")


def 拨号上网值():
    # 函数作用：拨号上网

    # 获取get的传输值，并将json的用户密码修改为用户文档里的账户密码
    参数 = 读取数据细(GUI.设置文档路径, 'GetValue', 'paramsed')
    参数_key = list(参数.keys())
    参数_value = list(参数.values())
    参数[参数_key[参数_value.index("UD_name")]] = 读取数据细(GUI.用户文档路径, 'data', 'name')
    参数[参数_key[参数_value.index("UD_password")]] = 读取数据细(
        GUI.用户文档路径, 'data', 'password')

    requests.get(url=读取数据细(GUI.设置文档路径, 'setting', 'web'), params=参数)


def 初始化用户数据文档():
    文档 = {
        "data": {
            "name": "",
            "password": "",
            "pwmd5": ""
        },
        "ID": {
            "cpu": "",
            "mac": ""
        }
    }
    return json.dumps(文档, ensure_ascii=False)


def 初始化设置数据文档():
    文档 = {
        "usermd5": "",
        "button": {
            "turnon": 0,
            "autodial": 0,
            "redial": 0
        },
        "setting": {
            "web": "http://172.30.100.2/drcom/login",
            "login": "代码提交",
            "submit": "get"
        },
        "semester": {
            "begins": "2023-09-04",
            "weekend": [0, 0, 0, 0, 0, 1, 1],
            "vacation": [],
            "workday": []
        },
        "GetValue": {
            "paramsed": {
                "callback": "dr1003",
                "DDDDD": "UD_name",
                "upass": "UD_password",
                "0MKKey": "123456"
            },
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
            }
        },
        "else": {
            "redialtime": [
                "06:00",
                "23:30"
            ],
            "testweb": [
                "https://www.baidu.com",
                "https://www.360.com",
                "https://www.sohu.com",
                "https://www.taobao.com",
                "https://www.jd.com"
            ],
            "schooltext": [
                "上网登录页",
                "教务系统",
                "教务系统（校外1）"
            ],
            "schoolweb": [
                "http://172.30.100.2/",
                "http://172.18.100.81/jwweb/default.aspx",
                "http://218.15.245.162:9086/jwweb/home.aspx"
            ],
            "fontsize": "16"
        }
    }
    return json.dumps(文档, ensure_ascii=False)


def 初始化跨线程变量文档():
    文档 = "0"
    return 文档
    # 文档 = {
    #     "data": 0
    # }
    # return json.dumps(文档, ensure_ascii=False)


if __name__ == '__main__':
    pass
