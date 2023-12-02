# coding:utf-8

import time
# import datetime
from datetime import datetime, timedelta
# import os

import InterGUI as GUI
import UserData as UD
# import SecondThread as ST

import uuid
import subprocess
from hashlib import md5
import requests
import random
# import aiohttp

# import multiprocessing
import threading


def md5_text(test):
    m = md5()
    m.update(test.encode("utf8"))
    return m.hexdigest()


'''
def 符号替换(文本):
    需换符号 = ['`', '@', '#', '$', '%', '^', '&', '=', '+']
    替换符号 = ['%60', '%40', '%23', '%24', '%25', '%5E', '%26', '%2B', '%3D']
    for i in 文本:
        if i in 需换符号:
            for y in range(len(需换符号)):
                if i == 需换符号[y]:
                    文本 = 文本.replace(i, 替换符号[y])
    return 文本
    # ~ %60 ! %40 %23 %24 %25 %5E %26 * ( ) - _ %2B %3D
    # ~ `   ! @   #   $   %   ^   &   * ( ) - _ =   +
'''


def 设备码():
    # 获取设备码，即CPU码和Mac地址
    command = "wmic cpu get processorid"
    output = subprocess.check_output(command, shell=True)
    cpu_serial = output.decode().split("\n")[1].strip()
    return cpu_serial, uuid.getnode()


def 周数差(开学时间):
    # 当前时间 = time.strftime("%Y %m %d", time.localtime())
    开学日期 = datetime.strptime(开学时间, "%Y-%m-%d")
    当前日期 = datetime.now()
    当前年份 = 当前日期.year
    开学年份 = 开学日期.year
    # print(当前年份, 开学年份)
    当前周数 = 当前日期.isocalendar()[1] + 1
    开学周数 = 开学日期.isocalendar()[1] + 1
    相隔周数 = abs(当前周数 - 开学周数) + 1 + abs(当前年份 - 开学年份) * 52
    if (开学年份 < 当前年份):
        相隔周数 = 相隔周数 + 当前周数

    return 相隔周数


def 读取行数(父组件):
    # 设置一个集合，用于存放所获取到组件的行数
    # 使用集合是为了防止获取到重复的行数
    所在行数 = set()
    for child in 父组件.winfo_children():
        所在行数.add(child.grid_info()['row'])
    return len(所在行数)


def 读取组件(父组件):
    组件 = []
    for child in 父组件.winfo_children():
        组件.append(child.grid_info())
    return 组件


def 联网测试线程():
    测试结果 = [0, 0, 0]
    设置文档 = UD.读取设置数据()
    try:
        登录页测试 = requests.get(设置文档['setting']['web'])
        if 登录页测试.status_code == 200:
            测试结果[0] = 1
    except Exception as e:
        print(e)
        return 测试结果
    测试结果[2] = len(设置文档['else']['testweb']
                  ) // 2 if (len(设置文档['else']['testweb']) // 2 < 4) else 4
    抽取结果 = random.sample(range(len(设置文档['else']['testweb'])), 测试结果[2])
    for i in 抽取结果:
        # print("测试网站:", i)
        try:
            登录页测试 = requests.get(设置文档['else']['testweb'][i])
            if 登录页测试.status_code == 200:
                测试结果[1] = 测试结果[1] + 1
        except Exception as e:
            print("测试网站:", i, "测试问题:", e)
            pass
    return 测试结果


class 自动复拨(threading.Thread):
    def __init__(self):
        super().__init__()
        self.设置文档 = UD.读取设置数据()
        self.开始时间 = datetime.strptime(
            self.设置文档['else']['redialtime'][0], "%H:%M").time()
        self.结束时间 = datetime.strptime(
            self.设置文档['else']['redialtime'][1], "%H:%M").time()
        self.补课日期 = self.设置文档['semester']['workday']
        self.假期日期 = self.设置文档['semester']['vacation']
        self.固定复拨日期 = self.设置文档['semester']['weekend']
        self.测试网站 = self.设置文档['else']['testweb']
        self.拨号网站 = self.设置文档['setting']['web']
        self.是否终止 = 自动复拨.读取终止(self)
        self.是否拨号 = False
        self.是否运行 = False
        self.联网失败次数 = 0

    def 读取终止(self):
        终止文档 = open(GUI.通用文档路径, "r")
        是否终止 = 终止文档.read()
        终止文档.close()
        return 是否终止

    def run(self):
        if self.是否运行 is False:
            self.是否运行 = True
            判断拨号线程 = threading.Thread(target=self.判断拨号, daemon=True)
            判断拨号线程.start()
            time.sleep(1)
            自动拨号线程 = threading.Thread(target=self.自动拨号, daemon=True)
            自动拨号线程.start()
            判断拨号线程.join()
            自动拨号线程.join()

    def 判断拨号(self):
        print("判断拨号,是否终止:", self.是否终止)
        while self.是否终止 == "0":
            时间 = datetime.now()
            今天 = 时间.date()
            今天星期几 = 时间.weekday()
            明天 = 时间.date() + timedelta(days=1)
            明天星期几 = 时间.weekday() + 1 if 时间.weekday() < 6 else 0
            现在时间 = datetime.now().time()

            if self.开始时间 <= 现在时间 <= self.结束时间 or \
                (现在时间 <= self.开始时间 and (今天 in self.假期日期 or (self.固定复拨日期[今天星期几] == 1 and 今天 not in self.补课日期))) or \
                    (明天 in self.假期日期 or (self.固定复拨日期[明天星期几] == 1 and 明天 not in self.补课日期)):
                self.是否拨号 = True
            else:
                self.是否拨号 = False

            print("判断拨号time.sleep", datetime.now(), "判断拨号是否拨号", self.是否拨号)
            time.sleep(600)
            self.是否终止 = 自动复拨.读取终止(self)
        self.是否拨号 = False

    def 自动拨号(self):
        print("自动拨号", self.是否终止)
        while self.是否终止 == "0":
            print("自动拨号while", self.是否拨号)
            time.sleep(1)
            while self.是否拨号:
                print("正在自动拨号，self.联网失败次数", self.联网失败次数)
                挑选测试网站 = random.choice(self.测试网站)
                try:
                    测试网站 = requests.get(挑选测试网站)
                    if 测试网站.status_code == 200:
                        print("测试网站.time.sleep", datetime.now())
                        time.sleep(180)
                        if self.联网失败次数 != 0:
                            self.联网失败次数 = 0
                except Exception as e:
                    print("测试网站:", 挑选测试网站, "测试问题:", e)
                    self.联网失败次数 = self.联网失败次数 + 1
                    if (self.联网失败次数 >= 5):
                        self.联网失败次数 = 0
                        try:
                            登录页测试 = requests.get(self.拨号网站)
                            if 登录页测试.status_code == 200:
                                pass
                        except Exception as e:
                            print("无法连接登录页", e)
                            GUI.弹出窗口("无法连接登录页")
                            break
                        UD.拨号上网值()
                print("自动拨号whilewhile是否拨号", self.是否拨号)
            self.是否终止 = 自动复拨.读取终止(self)
            print("自动拨号while.time.sleep", datetime.now())
            time.sleep(300)


# 源 读取组件(父组件) 组件
'''def get_grid_rows(父组件):
    rows = 0
    print("父组件.winfo_children():", 父组件.winfo_children())
    for child in 父组件.winfo_children():
        print("child", child, "child.grid()", child.grid_info())
    for child in 父组件.winfo_children():
        if child.grid():
            rows += 1
        rows += get_grid_rows(child)
    return rows
'''


if __name__ == "__main__":
    pass
