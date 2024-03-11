# 文档名称：UserData
# 编码格式：utf-8
# 编写者：罗伟峰
# 文档作用：数据存取操作

import os
import InterGUI as GUI
import DataLibrary as DL
import requests
import json
from datetime import datetime


def 初始化数据(路径, 选项, Reset):
    if ((os.path.exists(路径) is False) or Reset == 1):
        f = open(路径, "w", encoding='utf-8')
        if (选项 == 0):
            f.write(初始化用户数据文档())
        elif (选项 == 1):
            f.write(初始化用户设置文档())
        elif (选项 == 2):
            f.write(初始化共享设置文档())
        elif (选项 == 3):
            f.write(初始化跨线程变量文档())
        f.close()


def 读取数据(路径):
    # 函数作用：直接读取数据，而尽量不将数据存储到变量中
    文档 = open(路径, 'r', encoding='utf-8')
    返回文档 = json.loads(文档.read())
    文档.close()
    return 返回文档


def 保存数据(新文档, 路径):
    print(新文档, "1")
    保存文档 = json.dumps(新文档, ensure_ascii=False)
    文档 = open(路径, 'w', encoding='utf-8')
    文档.write(保存文档)
    文档.close()
    if (路径 == GUI.用户数据路径):
        print("2")
        新用户数据 = 读取数据(路径)
        设置数据 = 读取数据(GUI.用户设置路径)
        设置数据['Usermd5'] = DL.md5_text(str(新用户数据))
        保存数据(设置数据, GUI.用户设置路径)


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
    print(datetime.now(), "UD", "拨号上网值")
    # 函数作用：拨号上网

    # 获取get的传输值，并将json的用户密码修改为用户文档里的账户密码

    用户数据 = 读取数据(GUI.用户数据路径)

    参数 = {'callback': 'dr1003', 'DDDDD': 用户数据['UserData']['Name'],
          "upass": 用户数据['UserData']['Password'], '0MKKey': "123456"}

    requests.get(url='http://172.30.100.2/drcom/login?', params=参数)


def 初始化用户数据文档():
    文档 = {
        "UserData": {
            "Name": "",
            "Password": "",
            "pwmd5": ""
        },
        "UserID": {
            "CPU": "",
            "MAC": ""
        }
    }
    return json.dumps(文档, ensure_ascii=False)


def 初始化用户设置文档():
    文档 = {
        "Usermd5": "",
        "Button": {
            "Turnon": 0,
            "Autodial": 0,
            "Redial": 0
        },
    }
    return json.dumps(文档, ensure_ascii=False)


def 初始化共享设置文档():
    文档 = {
        "Semester": {
            "begins": "2024-03-04",
            "weekend": [0, 0, 0, 0, 0, 1, 1],
            "vacation": [
                "2024-04-04",
                "2024-04-05",
                "2024-05-01",
                "2024-05-02",
                "2024-05-03",
                "2024-06-10"
            ],
            "workday": [
                "2024-04-27",
                "2024-04-28"
            ]
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
                "教务系统（校内1）",
                "教务系统（校内2）",
                "教务系统（校内3）",
                "教务系统（校内4）",
                "教务系统（校内5）",
                "教务系统（校外1）"
            ],
            "schoolweb": [
                "http://172.30.100.2/",
                "http://172.18.100.81/jwweb/default.aspx",
                "http://172.18.100.82/jwweb/default.aspx",
                "http://172.18.100.83/jwweb/default.aspx",
                "http://172.18.100.84/jwweb/default.aspx",
                "http://172.18.100.85/jwweb/default.aspx",
                "http://218.15.245.162:9086/jwweb/home.aspx"
            ],
            "fontsize": "16"
        }
    }
    return json.dumps(文档, ensure_ascii=False)


def 初始化跨线程变量文档():
    文档 = "0"
    return 文档


if __name__ == '__main__':
    pass
