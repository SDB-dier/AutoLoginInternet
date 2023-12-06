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
    # 函数作用：对文本进行md5加密
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
    # 函数作用：获取设备码，即CPU码和Mac地址
    command = "wmic cpu get processorid"
    output = subprocess.check_output(command, shell=True)
    cpu_serial = output.decode().split("\n")[1].strip()
    return cpu_serial, uuid.getnode()


def 周数差(开学时间):
    # 函数作用：计算传入日期与当前日期的周数差的值并+1（同周数为1）
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
    # 函数作用：读取传入父组件内部的子组件行数，并返回存放子组件行数的集合的长度
    # 设置一个集合，用于存放所获取到子组件的行数
    # 使用集合是为了防止获取到重复的行数
    所在行数 = set()
    for child in 父组件.winfo_children():
        所在行数.add(child.grid_info()['row'])
    return len(所在行数)
    """# 可能会遇到的问题
    # 因为是返回存放子组件行数的集合的长度，但有可能子组件的行数会大于集合的长度
    # 即组件的row设为0、1、5，组件仍然会按照顺序排列，row为空的部分跳过布局
    # 但返回的集合的长度却是3，有可能会导致新增的组件row插入在源组件中
    """


def 读取组件(父组件):
    # 函数作用：读取传入父组件内部的所有组件，并将组件以列表形式返回
    组件 = []
    for child in 父组件.winfo_children():
        组件.append(child.grid_info())
    return 组件


def 联网测试():
    # 函数作用：测试是否能够连通网络，并以列表的形式返回登录页测试结果、测试网站结果和抽取数量
    # 测试结果的第一个值为是否能连接至登录页，能够连通则赋值为1
    # 测试结果的第二个值为能连接至测试网站的数量，能够连通则数值加1
    # 测试结果的第三个值为抽取测试网站的数量，用于判断测试网站是否都能连通
    测试结果 = [0, 0, 0]
    设置文档 = UD.读取设置数据()
    # 首先测试能否连通登录页，如果登录页都无法连通，则说明无法进行登录，直接返回测试结果
    try:
        登录页测试 = requests.get(设置文档['setting']['web'])
        if 登录页测试.status_code == 200:
            测试结果[0] = 1
    except Exception as e:
        print(e)
        return 测试结果
    # 测试结果的第三个值，使用三元表达式判断设置文档的测试网站数量的一半（整除2）是否少于4
    # 若少于4则测试结果的第三个值为测试网站数量的一半（整除2）
    # 否则测试结果的第三个值最大值为4
    测试结果[2] = len(设置文档['else']['testweb']
                  ) // 2 if (len(设置文档['else']['testweb']) // 2 < 4) else 4
    # 使用random.sample，根据 抽取数量 从 设置文档的测试网站 中随机抽出 测试网站的编号
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
    # 类作用：启动自动复拨，利用每个类只能start一次，防止多个自动复拨判断
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
        # 函数作用：读取来用存放跨线程的通用变量
        # 本函数是为了应对无法跨线程读取同一个变量，而采用读取文档的内容来确定变量信息
        终止文档 = open(GUI.跨线程变量文档路径, "r")
        是否终止 = 终止文档.read()
        终止文档.close()
        return 是否终止

    def run(self):
        # 函数作用：新建两个线程，分别判断该时间段是否需要拨号，以及当前是否联网来进行复播
        if self.是否运行 is False:
            self.是否运行 = True
            判断拨号线程 = threading.Thread(target=self.判断拨号, daemon=True)
            判断拨号线程.start()
            time.sleep(1)
            # 暂停1秒的作用是使判断拨号函数先修改 是否拨号 变量
            自动拨号线程 = threading.Thread(target=self.自动拨号, daemon=True)
            自动拨号线程.start()
            判断拨号线程.join()
            自动拨号线程.join()

    def 判断拨号(self):
        # 函数作用：判断当前时间是否需要拨号，如果不需要则使 是否拨号 变量为否，使其终止自动复拨
        while 1:
            print("判断拨号,是否终止:", self.是否终止)
            while self.是否终止 == "0":
                时间 = datetime.now()
                今天 = 时间.date()
                今天星期几 = 时间.weekday()
                明天 = 时间.date() + timedelta(days=1)
                明天星期几 = 时间.weekday() + 1 if 时间.weekday() < 6 else 0
                现在时间 = datetime.now().time()
                # 判断条件：
                # 1.是否在复拨时间段，在复拨时间段则可进行复拨，否则进入判断2
                # 2.判断当前时间是否在开始时间之前，且今天是假期或今天是不补课的周末，如果是则可进行复拨，否则进入判断3
                # 3.判断明天是否为假期或是不补课的周末（已包含当前时间在结束时间之后的隐形条件），如果是则可进行复拨，否则不进行复拨
                if self.开始时间 <= 现在时间 <= self.结束时间 or \
                    (现在时间 <= self.开始时间 and (今天 in self.假期日期 or (self.固定复拨日期[今天星期几] == 1 and 今天 not in self.补课日期))) or \
                        (明天 in self.假期日期 or (self.固定复拨日期[明天星期几] == 1 and 明天 not in self.补课日期)):
                    self.是否拨号 = True
                else:
                    self.是否拨号 = False

                print("判断拨号time.sleep", datetime.now(), "判断拨号是否拨号", self.是否拨号)
                time.sleep(600)
                # 暂停600秒（5分钟）的判断，减少资源占用
                self.是否终止 = 自动复拨.读取终止(self)
            self.是否拨号 = False
            time.sleep(60)

    def 自动拨号(self):
        # 函数作用：根据 是否拨号 变量决定是否进行复拨
        while 1:
            print("自动拨号", self.是否终止)
            while self.是否终止 == "0":
                print("自动拨号while", self.是否拨号)
                while self.是否拨号:
                    print("正在自动拨号，self.联网失败次数", self.联网失败次数)
                    挑选测试网站 = random.choice(self.测试网站)
                    # 先测试是否能够连通外网，如果无法连通外网5次再进行拨号
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
                        # 当连续测试5次连接外网都失败，则进行拨号
                        if (self.联网失败次数 >= 5):
                            self.联网失败次数 = 0
                            try:
                                登录页测试 = requests.get(self.拨号网站)
                                if 登录页测试.status_code == 200:
                                    UD.拨号上网值()
                            except Exception as e:
                                print("无法连接登录页", e)
                                GUI.弹出窗口("无法连接登录页")
                                break
                    print("自动拨号whilewhile是否拨号", self.是否拨号)
                self.是否终止 = 自动复拨.读取终止(self)
                print("自动拨号while.time.sleep", datetime.now())
                time.sleep(300)
            time.sleep(60)


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
