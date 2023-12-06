# 文档名称：InterGUI
# 编码格式：utf-8
# 编写者：罗伟峰
# 文档作用：软件主程序及与GUI相关的代码操作

from tkinter import *
from tkinter.ttk import *

from functools import partial

# import datetime
from datetime import datetime
import os
# import random
import re
# import requests
import sys
import time
import webbrowser

import threading
# import asyncio
# import multiprocessing

import pystray
from PIL import Image

# import ctypes
import UserData as UD
import DataLibrary as DL


def 初始界面(框架):
    # 设定文本Label和输入框Entry，使用grid方式进行布局
    日期 = Label(框架, text='日期')
    日期.grid(row=0, column=0, columnspan=1, sticky=W)
    日期详情 = Label(框架, text=time.strftime("%Y-%m-%d", time.localtime()))
    日期详情.grid(row=0, column=1, columnspan=1)
    周数详情 = Label(框架, text="第" + str(DL.周数差(设置文档["semester"]["begins"])) + "周")
    周数详情.grid(row=0, column=2, columnspan=1)

    用户名 = Label(框架, text='用户名：')
    用户名.grid(row=1, column=0, columnspan=1, sticky=W)
    用户名详情 = Entry(框架)
    用户名详情.insert(0, 用户文档['data']['name'])
    用户名详情.grid(row=1, column=1, columnspan=1, sticky=E)

    密码 = Label(框架, text='密码：')
    密码.grid(row=2, column=0, columnspan=1, sticky=W)
    密码详情 = Entry(框架)
    密码详情['show'] = '*'
    密码详情.insert(0, 用户文档['data']['pwmd5'])
    密码详情.grid(row=2, column=1, columnspan=1, sticky=E)

    def 显示切换():
        if (密码详情['show'] == "*"):
            密码详情['show'] = ""
        else:
            密码详情['show'] = '*'
    # 设定一个按钮，点击按钮使其可以切换密码位置是否显示密码
    显示切换按钮 = Button(框架, text='显示切换', command=显示切换)
    显示切换按钮.grid(row=2, column=2, columnspan=1)
    '''验证码预留位置，后期对软件升级使其可以捕获验证码
    # 验证码 = Label(框架, text='验证码：')
    # 验证码.grid(row=3, column=0, columnspan=2, sticky=W)
    # 验证码详情 = Entry(框架)
    # 验证码详情.grid(row=3, column=2, columnspan=2, sticky=E)
    '''
    # 设定3个int值，用于存储自启动、自播、复拨三个是否被选择，1为勾选
    var_自启动 = IntVar(value=设置文档['button']['turnon'])
    var_自拨 = IntVar(value=设置文档['button']['autodial'])
    var_复拨 = IntVar(value=设置文档['button']['redial'])
    # 设定三个单选框和一个按钮
    自启动按钮 = Checkbutton(框架, text='自启动', variable=var_自启动)
    自启动按钮.grid(row=4, column=0, sticky=W)
    自拨按钮 = Checkbutton(框架, text='自动拨号', variable=var_自拨)
    自拨按钮.grid(row=4, column=1, sticky=W)
    复拨按钮 = Checkbutton(框架, text='自动复拨', variable=var_复拨)
    复拨按钮.grid(row=4, column=2, sticky=W)
    链接按钮 = Button(框架, text='校站链接', command=校站界面)
    链接按钮.grid(row=5, column=0, columnspan=1)

    def 保存并拨号():
        # 首先获取用户文档和设置文档并保存在一个新变量上，好用于后续判断和覆盖
        新用户文档 = 用户文档
        新设置文档 = 设置文档
        # 判断输入框的用户名和密码跟用户文档的用户名和密码是否一致
        # 如果不一致则将输入框的用户名和密码保存到新用户文档中，再对源文档进行覆盖
        if 用户名详情.get() != 用户文档['data']['name'] or \
                密码详情.get() != 用户文档['data']['pwmd5']:
            新用户文档['data']['name'] = 用户名详情.get()
            新用户文档['data']['password'] = 密码详情.get()
            新用户文档['data']['pwmd5'] = DL.md5_text(密码详情.get())
            UD.保存用户数据(新用户文档)
            # 用户数据保存后会导致设置文档的usermd5产生变化，所以需要重新获取
            新设置文档 = UD.读取设置数据()

        # 判断自启动、自播、复拨三个单选框状态跟设置文档的状态是否一致
        if var_自启动.get() != 设置文档['button']['turnon'] or \
                var_自拨.get() != 设置文档['button']['autodial'] or \
                var_复拨.get() != 设置文档['button']['redial']:
            新设置文档['button']['turnon'] = var_自启动.get()
            新设置文档['button']['autodial'] = var_自拨.get()
            新设置文档['button']['redial'] = var_复拨.get()
            UD.保存设置数据(新设置文档)

        # 如果勾选自启动，则立即执行设置自启动功能
        # 使其在启动文档保存一个开启该软件的bat批命令
        # 如果没有勾选，则删除启动文档的bat批命令
        if var_自启动.get() == 1:
            UD.设置自启动(sys.argv[0])
        else:
            UD.关闭自启动()
        # 如果勾选自动复拨，则启动自动复拨功能
        # 使软件根据用户的设定，是否需要进行自动复拨
        # 如果没有勾选，则终止自动复拨
        if var_复拨.get() == 1 and ga.is_alive() is False:
            自动复拨.start()
        elif ga.is_alive():
            pass
        '''# 复拨终止，因有故障，暂时废除
        else:
            自动复拨.是否终止 = True

        进行主功能：拨号上网
        '''
        拨号上网()

    '''# 测试按钮
    def testbutton():
        print("自动复拨.is_alive()", 自动复拨.is_alive())
        print("自动复拨", 自动复拨)
        print("DL.自动复拨()", DL.自动复拨())
        print("ga", ga)
        print("ga.is_alive()", ga.is_alive())

    test按钮 = Button(框架, text='test', command=testbutton)
    test按钮.grid(row=6, column=1, columnspan=2)
    '''

    保存按钮 = Button(框架, text='保存并拨号', command=保存并拨号)
    保存按钮.grid(row=5, column=1, columnspan=2)
    # 打开界面立即判断设置文档的自动拨号是否启动
    # 如果启动则直接拨号，无需用户手动点击拨号
    if (设置文档['button']['autodial'] == 1):
        拨号上网()


def 登录设置(框架):
    # 设定文本Label、输入框Entry和多选项Combobox，使用grid方式进行布局
    登录网站 = Label(框架, text='登录网站')
    登录网站.grid(row=0, column=0, columnspan=2, sticky=W)
    登录网站详情 = Entry(框架)
    登录网站详情.insert(0, 设置文档['setting']['web'])
    登录网站详情.grid(row=0, column=2, columnspan=2)

    登陆模式 = Label(框架, text='登陆模式')
    登陆模式.grid(row=1, column=0, columnspan=2, sticky=W)
    登陆模式详情 = Combobox(框架, state="readonly")
    登陆模式详情['value'] = ('代码提交', '模拟操作')
    登陆模式详情.current(list(登陆模式详情['value']).index(设置文档['setting']['login']))
    登陆模式详情.grid(row=1, column=2, columnspan=2)

    # 如果登录方式选择代码提交，则显示代码提交的编辑内容
    if (登陆模式详情.get() == '代码提交'):
        提交方式 = Label(框架, text='提交方式')
        提交方式.grid(row=2, column=0, columnspan=2, sticky=W)
        提交方式详情 = Combobox(框架, state="readonly")
        提交方式详情['value'] = ('get', 'post')
        提交方式详情.current(list(提交方式详情['value']).index(设置文档['setting']['submit']))
        提交方式详情.grid(row=2, column=2, columnspan=2)

        提交代码 = Label(框架, text='提交代码')
        提交代码.grid(row=3, column=0, columnspan=2, sticky=W)
        提交代码详情 = Button(框架, text='编辑提交代码', command=提交代码设置界面)
        提交代码详情.grid(row=3, column=2, columnspan=2)
    else:
        # 如果登录方式选择模拟操作，则显示模拟操作的编辑内容
        # 模拟操作还未编写
        pass

    def 保存登录设置():
        # 判断代码提交的设置内容是否与设置文档的内容一致，如果不一致则进行内容保存
        if (登陆模式详情.get == '代码提交'):
            if 登录网站详情.get() != 设置文档['setting']['web'] or \
                    登陆模式详情.get() != 设置文档['setting']['login'] or \
                    提交方式详情.get() != 设置文档['setting']['submit']:
                新设置文档 = 设置文档
                新设置文档['setting']['web'] = 登录网站详情.get()
                新设置文档['setting']['login'] = 登陆模式详情.get()
                新设置文档['setting']['submit'] = 提交方式详情.get()
                UD.保存设置数据(新设置文档)
        else:
            if 登录网站详情.get() != 设置文档['setting']['web'] or \
                    登陆模式详情.get() != 设置文档['setting']['login']:
                新设置文档 = 设置文档
                新设置文档['setting']['web'] = 登录网站详情.get()
                新设置文档['setting']['login'] = 登陆模式详情.get()
                UD.保存设置数据(新设置文档)

    保存按钮 = Button(框架, text='保存', command=保存登录设置)
    保存按钮.grid(row=4, column=0, columnspan=4)


def 学期设置(框架):
    # 设定文本Label、输入框Entry和按钮Button，使用grid方式进行布局
    开学日期 = Label(框架, text='开学日期')
    开学日期.grid(row=0, column=0, columnspan=2, sticky=W)
    开学日期详情 = Entry(框架)
    开学日期详情.insert(0, 设置文档['semester']['begins'])
    开学日期详情.grid(row=0, column=2, columnspan=2)

    学期假期 = Label(框架, text='学期假期')
    学期假期.grid(row=1, column=0, columnspan=2, sticky=W)
    # 点击假期按钮，调用学期假期界面函数，打开学期假期设置界面
    假期按钮 = Button(框架, text='学期假期', command=学期假期界面)
    假期按钮.grid(row=1, column=2, columnspan=4)

    学期补课 = Label(框架, text='学期补课')
    学期补课.grid(row=2, column=0, columnspan=2, sticky=W)
    # 点击补课按钮，调用学期补课界面函数，打开学期补课设置界面
    补课按钮 = Button(框架, text='学期补课', command=学期补课界面)
    补课按钮.grid(row=2, column=2, columnspan=4)

    def 保存学期设置():

        # 设置错误捕获，错误来源于用户填写的信息不符合格式化的要求
        try:
            开学日期详 = datetime.date.fromisoformat(开学日期详情.get())
        except ValueError:
            警告 = Toplevel()
            警告信息 = Label(警告, text='请确保日期格式为YYYY-MM-DD\n并且该日期确实存在',
                         justify=CENTER)
            警告信息.grid(row=2, column=0, columnspan=2, sticky=W)
            警告.after(5000, 警告.destroy)
            return
        # 判断设置日期是否超前，超前则发出警告
        # 该判断可以删除
        if 开学日期详.year > datetime.now().year:
            警告 = Toplevel()
            警告信息 = Label(警告, text='请不要设置未开始的年份',
                         justify=CENTER)
            警告信息.grid(row=2, column=0, columnspan=2, sticky=W)
            警告.after(5000, 警告.destroy)
            return
        # 判断学期设置的开学日期是否与设置文档的内容一致，如果不一致则进行内容保存
        if 开学日期详 != 设置文档['semester']['begins']:
            新设置文档 = 设置文档
            新设置文档['semester']['begins'] = str(开学日期详)
            UD.保存设置数据(新设置文档)

    保存按钮 = Button(框架, text='保存', command=保存学期设置)
    保存按钮.grid(row=3, column=0, columnspan=4)


def 其他设置(框架):
    # 设定文本Label、输入框Entry和按钮Button，使用grid方式进行布局
    复拨时间段 = Label(框架, text='复拨时间段')
    复拨时间段.grid(row=0, column=0, columnspan=2, sticky=W)
    复拨时间段详情s = Entry(框架)
    复拨时间段详情s.insert(0, 设置文档['else']['redialtime'][0])
    复拨时间段详情s.grid(row=0, column=2, columnspan=1)
    复拨时间段详情e = Entry(框架)
    复拨时间段详情e.insert(0, 设置文档['else']['redialtime'][1])
    复拨时间段详情e.grid(row=0, column=3, columnspan=1)

    测试网站 = Label(框架, text='拨号测试网站')
    测试网站.grid(row=1, column=0, columnspan=2, sticky=W)
    # 点击测试网站按钮，调用测试网站界面函数，打开测试网站设置界面
    测试网站按钮 = Button(框架, text='拨号测试网站', command=测试网站界面)
    测试网站按钮.grid(row=1, column=2, columnspan=2)

    校站设置 = Label(框架, text='校站设置')
    校站设置.grid(row=2, column=0, columnspan=2, sticky=W)
    # 点击校站设置按钮，调用校站设置界面函数，打开测试校站设置界面
    校站设置按钮 = Button(框架, text='校站设置', command=校站设置界面)
    校站设置按钮.grid(row=2, column=2, columnspan=2)

    字体大小 = Label(框架, text='字体大小')
    字体大小.grid(row=3, column=0, columnspan=2, sticky=W)
    字体大小范围 = [i for i in range(10, 26)]
    字体大小详情 = Combobox(框架, values=字体大小范围, state="readonly")
    字体大小详情.current(newindex=int(设置文档['else']['fontsize']) - 10)
    字体大小详情.grid(row=3, column=2, columnspan=2)

    def 保存其他设置():
        # 判断其他设置的复拨时间段和字体大小是否与设置文档的内容一致，如果不一致则进行内容保存
        if 复拨时间段详情s.get() != 设置文档['else']['redialtime'][0] or \
                复拨时间段详情e.get() != 设置文档['else']['redialtime'][1] or \
                字体大小详情.get() != 设置文档['else']['fontsize']:
            新设置文档 = 设置文档
            新设置文档['else']['redialtime'][0] = 复拨时间段详情s.get()
            新设置文档['else']['redialtime'][1] = 复拨时间段详情e.get()
            新设置文档['else']['fontsize'] = 字体大小详情.get()
            UD.保存设置数据(新设置文档)
        '''# 有个未处理的问题
        # 修改字体大小后点击保存，字体大小并不会发生改变，需要软件重启后才会变化
        # 问题在于保存设置数据后，软件并没有重新读取字体大小来刷新界面
        # 该未处理问题等后续空闲时候在进行修复处理
        '''

    保存按钮 = Button(框架, text='保存', command=保存其他设置)
    保存按钮.grid(row=4, column=0, columnspan=4)


def 关于软件(框架):
    # 使框架占满该页面的所有部分，比重为1（占满）
    框架.columnconfigure(0, weight=1)
    # 设定样式类型'this.TLabel'。使其不受总样式修改
    Style().configure('this.TLabel', font=("微软雅黑", 16))
    # 设定文本Label，使用grid方式进行布局
    软件介绍text = "软件介绍:\n\
        整体软件功能趋于完整，可直接使用\n\
        目前登录方式仅有代码提交-get模式\n\
        后续会完善post登录和模拟登录方式\n\
        至于验证码的问题，需要再往后完善"
    软件介绍 = Label(框架, text=软件介绍text, style='this.TLabel')
    软件介绍.grid(row=0, column=0, columnspan=2, sticky=W)

    版本号text = "版本号：2.0\n"
    版本号 = Label(框架, text=版本号text, style='this.TLabel')
    版本号.grid(row=1, column=0, columnspan=1, sticky=W)

    封包时间text = "封包时间：2023/11/23\n"
    封包时间 = Label(框架, text=封包时间text, style='this.TLabel')
    封包时间.grid(row=1, column=1, columnspan=1, sticky=E)

    关于我text = "制作人：罗伟峰\n班级：22网工C1"
    关于我 = Label(框架, text=关于我text, style='this.TLabel')
    关于我.grid(row=2, column=0, columnspan=2, sticky=NE)


def 测试网站界面():
    # 新建一个子窗口，并设定大小为400X300，并使第0列占比为2（占满）
    子界面 = Toplevel()
    子界面.geometry("400x300")
    子界面.columnconfigure(0, weight=2)

    def 新增行数():
        # 函数作用：用于新增填写测试网站的输入框数量
        # 调用DataLibrary的读取行数函数，并传入需要读取的窗口，返回已有行数
        已有行数 = DL.读取行数(子界面)
        # 当已有行数大于10的时候，弹出警告。
        # 已有行数没有大于的时候，新增输入框
        if 已有行数 > 10:
            new子界面 = Toplevel()
            说明 = Label(new子界面, text="最多新增10个测试网址")
            说明.grid(row=0, column=0, columnspan=1, sticky=S)
            new子界面.after(3000, new子界面.destroy)
        else:
            测试网站详情 = Entry(子界面)
            已有行数 = 已有行数 + 1
            测试网站详情.grid(row=已有行数, column=0, columnspan=2, sticky="NSEW")

    def 保存测试网址():
        # 函数作用：用于保存测试网站的输入框的值
        # 使用一个数组来存放输入框的值，然后遍历窗口的每一个组件，判断该组件是否为输入框且输入框的值不为空
        内容 = []
        for i in 子界面.winfo_children():
            if isinstance(i, Entry) and i.get() != "":
                内容.append(i.get())
        新设置文档 = 设置文档
        新设置文档['else']['testweb'] = 内容
        UD.保存设置数据(新设置文档)
    # 设定按钮Button，使用grid方式进行布局
    新增按钮 = Button(子界面, text='新增', command=新增行数)
    新增按钮.grid(row=0, column=0, columnspan=1)
    保存按钮 = Button(子界面, text='保存', command=保存测试网址)
    保存按钮.grid(row=0, column=1, columnspan=1)

    测试网站数量 = len(设置文档['else']['testweb'])
    # 此处for循环作用是在窗口创造时，根据从设置文档中读取测试网站内容，创建对应的输入框，并将值填入输入框中
    for i in range(测试网站数量):
        测试网站详情 = Entry(子界面)
        测试网站详情.insert(0, 设置文档['else']['testweb'][i])
        测试网站详情.grid(row=i + 1, column=0, columnspan=2, sticky="NSEW")


def 提交代码设置界面():
    # 新建一个子窗口，并设定大小为400X600，并使第0列占比为1、第1列占比为2（1列更宽）
    子界面 = Toplevel()
    子界面.geometry("400x600")
    子界面.columnconfigure(0, weight=1)
    子界面.columnconfigure(1, weight=2)

    def 新增行数():
        # 函数作用：用于新增填写提交代码的key和value的输入框数量。单次点击新增2个输入框
        # 调用DataLibrary的读取行数函数，并传入需要读取的窗口，返回已有行数
        已有行数 = DL.读取行数(子界面)
        # 当已有行数大于12的时候，弹出提示窗口，但仍然可以继续新增输入框
        if 已有行数 > 12:
            new子界面 = Toplevel()
            说明 = Label(new子界面, text="建议少于10个")
            说明.grid(row=0, column=0, columnspan=1, sticky=S)
            new子界面.after(3000, new子界面.destroy)
        代码key详情 = Entry(子界面)
        代码value详情 = Entry(子界面)
        已有行数 = 已有行数 + 1
        代码key详情.grid(row=已有行数, column=0, columnspan=1, sticky="NSEW")
        代码value详情.grid(row=已有行数, column=1, columnspan=1, sticky="NSEW")

    def 保存提交代码():
        # 函数作用：用于保存提交代码设置界面的所有输入框的值
        # 使用一个数组来存放输入框的值，然后遍历窗口的每一个组件，判断该组件是否为输入框且输入框的值不为空
        内容 = []
        新设置文档 = 设置文档
        # 读取多行输入框Text的值，并判断是否跟设置文档的值不一样
        # Text.get的"0.0"指的是从第0行第0个字符开始读取，"end"指读取到末尾，[:-1]作用是删除最后一个换行符
        if (headers详情.get("0.0", "end")[:-1] != 设置文档['GetValue']['headers'].get("User-Agent")):
            新设置文档['GetValue']['headers']['User-Agent'] = headers详情.get(
                "0.0", "end")[:-1]
        for i in 子界面.winfo_children():
            if isinstance(i, Entry) and i.get() != "":
                内容.append(i.get())
        # 将内容按key和value以字典的形式存储起来
        # 内容的偶数为key，奇数为value
        新设置文档['GetValue']['paramsed'] = dict(zip(内容[0::2], 内容[1::2]))
        UD.保存设置数据(新设置文档)
    # 设定按钮Button、文本Label和多行输入框Text，使用grid方式进行布局
    新增按钮 = Button(子界面, text='新增', command=新增行数)
    新增按钮.grid(row=0, column=0, columnspan=1)
    保存按钮 = Button(子界面, text='保存', command=保存提交代码)
    保存按钮.grid(row=0, column=1, columnspan=1)

    headers文字 = Label(子界面, text="代码key")
    headers文字.grid(row=1, column=0, columnspan=2, sticky=S)
    headers详情 = Text(子界面)
    headers详情.config(height=5)
    headers详情.insert("end", 设置文档['GetValue']['headers'].get("User-Agent"))
    headers详情.grid(row=2, column=0, columnspan=2, sticky="NSEW")

    代码key文字 = Label(子界面, text="代码key")
    代码key文字.grid(row=3, column=0, columnspan=1, sticky=S)
    代码value文字 = Label(子界面, text="代码value")
    代码value文字.grid(row=3, column=1, columnspan=1, sticky=S)

    # 此处for循环作用是在窗口创造时，根据从设置文档中读取key和value，创建对应的输入框，并将值填入输入框中
    for key, value in 设置文档['GetValue']['paramsed'].items():
        已有行数 = DL.读取行数(子界面)
        代码key详情 = Entry(子界面)
        代码key详情.insert(0, key)
        代码key详情.grid(row=已有行数 + 1, column=0, columnspan=1, sticky="NSEW")
        代码value详情 = Entry(子界面)
        代码value详情.insert(0, value)
        代码value详情.grid(row=已有行数 + 1, column=1, columnspan=1, sticky="NSEW")


def 学期假期界面():
    # 新建一个子窗口，并设定大小为400X600，并使所有列占比为1（界面宽度平均分配）
    子界面 = Toplevel()
    子界面.geometry("400x600")
    子界面.columnconfigure(0, weight=1)
    子界面.columnconfigure(1, weight=1)
    子界面.columnconfigure(2, weight=1)
    子界面.columnconfigure(3, weight=1)

    def 新增行数():
        已有组件 = DL.读取组件(子界面)
        已有行数 = DL.读取行数(子界面)
        if 已有行数 > 30:
            new子界面 = Toplevel()
            说明 = Label(new子界面, text="请确认本学期假期日期哦")
            说明.grid(row=0, column=0, columnspan=1, sticky=S)
        补课详情 = Entry(子界面)
        if (已有组件[-1]['column'] == 2):
            补课详情.grid(row=已有行数 + 1, column=0, columnspan=2, sticky="NSEW")
        else:
            补课详情.grid(row=已有行数, column=2, columnspan=2, sticky="NSEW")

    固定复拨文字 = Label(子界面, text="固定复拨日期")
    固定复拨文字.grid(row=0, column=0, columnspan=4, sticky=S)

    # 设置一个字典，用于存放7个单选项，是为了后面进行读取查找对象
    星期 = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    星期_dict = dict()
    for i in range(len(星期)):
        星期_dict[星期[i]] = 设置文档['semester']['weekend'][i]
    # 结果：星期_dict = {"星期一": 0, "星期二": 0, "星期三": 0,"星期四": 0, "星期五": 0, "星期六": 1, "星期日": 1}

    # 设置一个列表，用于存放7个IntVar值，等同于以下内容
    # var_星期一 = IntVar(value=设置文档['semester']['weekend'][0])
    # ...
    # var_星期日 = IntVar(value=设置文档['semester']['weekend'][6])
    # Checkbutton的值自认Tk自带的特定函数的值，所以得设IntVar
    var_星期 = []
    for i in range(len(星期_dict)):
        var_星期.append(IntVar(value=设置文档['semester']['weekend'][i]))

    # 默认为第2行第1列
    var_column = 0
    var_row = 1
    for key in 星期_dict.keys():
        # 如果该行已经添加的数量大于4个，就换行
        if var_column > 3:
            var_column = 0
            var_row = 2
        # Checkbutton的variable，根据key返回对应var_星期的值
        # 即key为“星期一”，则返回var_星期一的值
        Checkbutton(子界面, text=key,
                    variable=var_星期[list(星期_dict.keys()).index(key)]
                    ).grid(row=var_row, column=var_column, sticky=W)
        var_column = var_column + 1

    def 保存():
        var_星期_list = []
        for new_var_星期 in var_星期:
            var_星期_list.append(new_var_星期.get())
        if var_星期_list != 设置文档['semester']['weekend']:
            新设置文档 = 设置文档
            新设置文档['semester']['weekend'] = var_星期_list

        内容 = []
        for i in 子界面.winfo_children():
            if isinstance(i, Entry) and i.get() != "":
                # 利用datetime.data.fromisoformat来确定是否有该日期，但是该函数对格式要求严格
                # 所以需要try来进行错误判断，格式不对或日期错误则报异常
                try:
                    补课日期详 = datetime.date.fromisoformat(i.get())
                except ValueError:
                    警告 = Toplevel()
                    警告信息 = Label(
                        警告, text='请确保日期格式为YYYY-MM-DD\n并且该日期确实存在\n错误日期为第%d个'
                        % (len(内容) + 1), justify=CENTER)
                    警告信息.grid(row=2, column=0, columnspan=2, sticky=W)
                    警告.after(5000, 警告.destroy)
                    return
                内容.append(str(补课日期详))
                # print(内容)
        新设置文档 = 设置文档
        新设置文档['semester']['vacation'] = 内容
        UD.保存设置数据(新设置文档)

    新增按钮 = Button(子界面, text='新增', command=新增行数)
    新增按钮.grid(row=3, column=0, columnspan=2)
    保存按钮 = Button(子界面, text='保存', command=保存)
    保存按钮.grid(row=3, column=2, columnspan=2)

    学期假期数量 = len(设置文档['semester']['vacation'])

    for i in range(学期假期数量):
        已有行数 = DL.读取行数(子界面)
        学期假期日期 = Entry(子界面)
        if (i % 2 == 0):
            学期假期日期.insert(0, 设置文档['semester']['vacation'][i])
            学期假期日期.grid(row=已有行数 + 1, column=0,
                        columnspan=2, sticky="NSEW")
        else:
            学期假期日期.insert(0, 设置文档['semester']['vacation'][i])
            学期假期日期.grid(row=已有行数, column=2,
                        columnspan=2, sticky="NSEW")


def 学期补课界面():
    子界面 = Toplevel()
    子界面.geometry("400x600")
    子界面.columnconfigure(0, weight=1)
    子界面.columnconfigure(1, weight=2)

    def 新增行数():
        已有组件 = DL.读取组件(子界面)
        已有行数 = DL.读取行数(子界面)
        # print(已有行数)
        if 已有行数 > 30:
            new子界面 = Toplevel()
            说明 = Label(new子界面, text="请确认本学期补课日期哦")
            说明.grid(row=0, column=0, columnspan=1, sticky=S)
        补课详情 = Entry(子界面)
        if (已有组件[-1]['column'] == 1 or len(已有组件) == 3):
            补课详情.grid(row=已有行数 + 1, column=0, columnspan=1, sticky="NSEW")
        else:
            补课详情.grid(row=已有行数, column=1, columnspan=1, sticky="NSEW")

    def 学期补课内容():
        内容 = []
        for i in 子界面.winfo_children():
            if isinstance(i, Entry) and i.get() != "":
                # 利用datetime.data.fromisoformat来确定是否有该日期，但是该函数对格式要求严格
                # 所以需要try来进行错误判断，格式不对或日期错误则报异常
                try:
                    补课日期详 = datetime.date.fromisoformat(i.get())
                except ValueError:
                    警告 = Toplevel()
                    警告信息 = Label(
                        警告, text='请确保日期格式为YYYY-MM-DD\n并且该日期确实存在\n错误日期为第%d个'
                        % (len(内容) + 1), justify=CENTER)
                    警告信息.grid(row=2, column=0, columnspan=2, sticky=W)
                    警告.after(5000, 警告.destroy)
                    return
                内容.append(str(补课日期详))
                # print(内容)
        新设置文档 = 设置文档
        新设置文档['semester']['workday'] = 内容
        UD.保存设置数据(新设置文档)

    新增按钮 = Button(子界面, text='新增', command=新增行数)
    新增按钮.grid(row=0, column=0, columnspan=1)
    保存按钮 = Button(子界面, text='保存', command=学期补课内容)
    保存按钮.grid(row=0, column=1, columnspan=1)
    学期补课文字 = Label(子界面, text="本学期补课日期")
    学期补课文字.grid(row=1, column=0, columnspan=2, sticky=S)

    学期补课数量 = len(设置文档['semester']['workday'])

    for i in range(学期补课数量):
        已有行数 = DL.读取行数(子界面)
        学期补课日期 = Entry(子界面)
        if (i % 2 == 0):
            学期补课日期.insert(0, 设置文档['semester']['workday'][i])
            学期补课日期.grid(row=已有行数 + 1, column=0,
                        columnspan=1, sticky="NSEW")
        else:
            学期补课日期.insert(0, 设置文档['semester']['workday'][i])
            学期补课日期.grid(row=已有行数, column=1,
                        columnspan=1, sticky="NSEW")


def 校站设置界面():
    子界面 = Toplevel()
    子界面.geometry("400x600")
    子界面.columnconfigure(0, weight=1)
    子界面.columnconfigure(1, weight=2)

    '''# 想要在右侧设置一个滚动条，但是失败了
    # 滚动条 = Scrollbar(子界面)
    # 滚动条.grid(row=0, column=3, columnspan=1)  # place(anchor=E, relheight=1)
    # 滚动条.config(command=子界面.yview)
    '''
    def 新增行数():
        已有行数 = DL.读取行数(子界面)
        print(已有行数)
        if 已有行数 == 11:
            new子界面 = Toplevel()
            说明 = Label(new子界面, text="最多新增10个校站网页")
            说明.grid(row=0, column=0, columnspan=1, sticky=S)
            new子界面.after(3000, new子界面.destroy)
        else:
            校站名称详情 = Entry(子界面)
            校站链接详情 = Entry(子界面)
            已有行数 = 已有行数 + 1
            校站名称详情.grid(row=已有行数, column=0, columnspan=2, sticky="NSEW")
            校站链接详情.grid(row=已有行数, column=1, columnspan=2, sticky="NSEW")

    def 保存校站网页():
        内容 = []
        for i in 子界面.winfo_children():
            if isinstance(i, Entry) and i.get() != "":
                内容.append(i.get())
        新设置文档 = 设置文档
        新设置文档['else']['schooltext'] = 内容[0::2]
        新设置文档['else']['schoolweb'] = 内容[1::2]
        UD.保存设置数据(新设置文档)

    新增按钮 = Button(子界面, text='新增', command=新增行数)
    新增按钮.grid(row=0, column=0, columnspan=1)
    保存按钮 = Button(子界面, text='保存', command=保存校站网页)
    保存按钮.grid(row=0, column=1, columnspan=1)
    校站文字 = Label(子界面, text="校站名称")
    校站文字.grid(row=1, column=0, columnspan=1, sticky=S)
    链接文字 = Label(子界面, text="校站链接")
    链接文字.grid(row=1, column=1, columnspan=1, sticky=S)

    校站数量 = len(设置文档['else']['schooltext'])

    for i in range(校站数量):
        已有行数 = DL.读取行数(子界面)
        校站详情 = Entry(子界面)
        校站详情.insert(0, 设置文档['else']['schooltext'][i])
        校站详情.grid(row=已有行数 + i + 1, column=0, columnspan=1, sticky="NSEW")
        校站链接详情 = Entry(子界面)
        校站链接详情.insert(0, 设置文档['else']['schoolweb'][i])
        校站链接详情.grid(row=已有行数 + i + 1, column=1, columnspan=1, sticky="NSEW")


def 校站界面():
    子界面 = Toplevel()
    子界面.geometry("400x300")
    子界面.columnconfigure(0, weight=1)
    子界面.columnconfigure(1, weight=1)

    def 打开网页(interesting):
        webbrowser.open(interesting)

    校站数量 = len(设置文档['else']['schooltext'])

    for i in range(校站数量):
        # print(i % 2 == 0)
        # print("row:", i // 2, "column:", i % 2)
        新增按钮 = Button(子界面, text=设置文档['else']['schooltext'][i],
                      command=partial(打开网页, 设置文档['else']['schoolweb'][i]))
        新增按钮.grid(row=(i // 2), column=i % 2, columnspan=1, sticky="NSEW")


def 拨号上网():

    UD.拨号上网值()
    global 拨号上网子界面
    拨号上网子界面 = Toplevel(主窗口)

    拨号文字 = Label(拨号上网子界面, text="已拨号")
    拨号文字.grid(row=0, column=0, columnspan=1, sticky=S)
    global 测试1
    测试1 = Label(拨号上网子界面, text="测试连通中")
    测试1.grid(row=1, column=0, columnspan=1, sticky=S)

    新增按钮 = Button(拨号上网子界面, text='关闭', command=拨号上网子界面.destroy)
    新增按钮.grid(row=2, column=0, columnspan=1)
    界面更新 = 拨号上网界面更新()
    界面更新.start()

    def 关闭():
        界面更新.StopTag = True
        拨号上网子界面.destroy()

    拨号上网子界面.protocol("WM_DELETE_WINDOW", 关闭)


class 拨号上网界面更新(threading.Thread):
    def __init__(self):
        super().__init__()
        self.StopTag = False
        self.测试结果 = None

    def run(self):
        threading.Thread(target=self.界面更新, daemon=True).start()

    def 界面更新(self):
        self.测试结果 = DL.联网测试()
        print(self.StopTag)
        try:
            if not self.StopTag:
                if self.测试结果[0] == 0:
                    测试1.destroy()
                    测试2 = Label(拨号上网子界面, text="无法连通登录网站")
                    测试2.grid(row=1, column=0, columnspan=1, sticky=S)
                elif self.测试结果[1] == 0:
                    测试1.destroy()
                    测试2 = Label(拨号上网子界面, text="无法连接外网")
                    测试2.grid(row=1, column=0, columnspan=1, sticky=S)
                elif self.测试结果[1] != self.测试结果[2]:
                    测试1.destroy()
                    测试2 = Label(拨号上网子界面, text="部分测试网址无法连通")
                    测试2.grid(row=1, column=0, columnspan=1, sticky=S)
                else:
                    测试1.destroy()
                    测试3 = Label(拨号上网子界面, text="已连通")
                    测试3.grid(row=1, column=0, columnspan=1, sticky=S)
                拨号上网子界面.after(10000, 拨号上网子界面.destroy)
            else:
                self._stop()
        except Exception:
            pass


def 询问退出():
    def 退出():
        sys.exit()

    def 最小化():
        主窗口.withdraw()
        退出窗口.destroy()

    退出窗口 = Toplevel()
    校站文字 = Label(退出窗口, text="是否退出程序\n退出程序会导致自动复拨失效", justify=CENTER)
    校站文字.grid(row=0, column=0, columnspan=2)
    新增按钮 = Button(退出窗口, text='最小化至托盘', command=最小化)
    新增按钮.grid(row=1, column=0, columnspan=1)
    保存按钮 = Button(退出窗口, text='退出程序', command=退出)
    保存按钮.grid(row=1, column=1, columnspan=1)


def 显示主窗口():
    # print("显示主窗口")
    # print(主窗口)
    # if not 主窗口.winfo_exists():
    主窗口.deiconify()


def 托盘确认退出(self):
    icon.stop()
    主窗口.quit()
    主窗口.destroy()


def 弹出窗口(提示):
    弹出窗口 = Toplevel()
    提示文字 = Label(弹出窗口, text=提示, justify=CENTER)
    提示文字.grid(row=0, column=0, columnspan=2)
    弹出窗口.after(10000, 弹出窗口.destroy)


def 类拨号启动():
    UD.初始化跨线程变量(1)
    # 终止文件 = open(跨线程变量文档路径, "w+")
    # 终止文件.write("0")
    # 终止文件.close()
    ga.start()


def get_resource_path(relative_path):
    # 函数作用：获取运行时软件解压的临时文件夹
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


# 获取文件路径，方便后面进行使用
主文件路径 = os.path.dirname(os.path.realpath(sys.argv[0]))
用户文档路径 = os.path.join(主文件路径, 'UserSettings.json')
设置文档路径 = os.path.join(主文件路径, 'DataSettings.json')
跨线程变量文档路径 = os.path.join(主文件路径, 'test.txt')

if __name__ == '__main__':
    # 进入程序，判断是否位于桌面或磁盘根目录
    用户路径 = os.environ['UserProfile']
    用户桌面路径 = os.path.join(用户路径, 'Desktop')
    正则判断 = re.compile(r"[A-Z+]:$")
    # 创建主窗口Tk，并命名标题和修改Logo
    主窗口 = Tk()
    主窗口.title("自动化登录程序")
    主窗口.iconbitmap(get_resource_path('kuku\\kuku.ico'))
    # 主窗口.iconbitmap(os.path.join(主文件路径, "kuku.ico"))
    # 判断该文档是否放在了桌面或磁盘根目录，如果放在了桌面或磁盘根目录，就提示放在此处并强制关闭程序
    if (主文件路径 == 用户桌面路径 or (not (正则判断.search(主文件路径) is None))):
        Style().configure('.', font=("微软雅黑", 16))
        提示文本 = Label(主窗口, text='请不要将此文件放在桌面或磁盘根目录')
        提示文本.grid(row=0, column=0)
        关闭按钮 = Button(主窗口, text='确认关闭', command=sys.exit)
        关闭按钮.grid(row=1, column=0)
        主窗口.mainloop()
        sys.exit()
    # 判断是否有用户文档跟设置文档
    UD.初始化用户数据(0)
    UD.初始化设置数据(0)
    UD.初始化跨线程变量(0)
    # 读取用户文档和设置文档
    用户文档 = UD.读取用户数据()
    设置文档 = UD.读取设置数据()
    # 判断设备码是否相同或是否被篡改用户文档，如设备码不同或被篡改，则重置用户文档跟设置文档的usermd5
    ID = DL.设备码()
    if (用户文档['ID']['cpu'] != ID[0] or 用户文档['ID']['mac'] != ID[1] or DL.md5_text(str(用户文档)) != 设置文档['usermd5']):
        # 初始化自启动、自动拨号和自动复拨，防止账户重置后使用空内容提交
        新设置文档 = 设置文档
        新设置文档['button']['turnon'] = 0
        新设置文档['button']['autodial'] = 0
        新设置文档['button']['redial'] = 0
        UD.保存设置数据(新设置文档)
        # 更新用户文档数据，格式化后写入到磁盘中
        新用户文档 = 用户文档
        新用户文档['ID']['cpu'] = ID[0]
        新用户文档['ID']['mac'] = ID[1]
        新用户文档['data']['name'] = ""
        新用户文档['data']['password'] = ""
        新用户文档['data']['pwmd5'] = ""
        UD.保存用户数据(新用户文档)
        # 重置后需要重新读取用户文档和设置文档
        用户文档 = UD.读取用户数据()
        设置文档 = UD.读取设置数据()
    # 判断软件是否需要自启动，如果需要就在启动文档添加一个bat批命令来打开软件
    # 如果不需要自启动就将启动文件夹的bat批命令删掉
    if 设置文档['button']['turnon'] == 1:
        UD.设置自启动(sys.argv[0])
    else:
        UD.关闭自启动()
    # 判断是否勾选了自动复拨功能，如果勾选则启用自动复拨

    global 自动复拨, ga
    # 自动复拨 = multiprocessing.Process(target=类拨号启动)
    自动复拨 = threading.Thread(target=类拨号启动, daemon=True)
    ga = DL.自动复拨()
    # 自动复拨.start()
    print("自动复拨.is_alive()", 自动复拨.is_alive())
    # 自动复拨 = DL.自动复拨()
    if 设置文档['button']['redial'] == 1:
        自动复拨.start()
    print("自动复拨.is_alive()", 自动复拨.is_alive())
    print("自动复拨", 自动复拨)

    # 设置主窗口大小
    主窗口.geometry("600x300")
    # 设置窗口样式
    Style().configure('.', font=("微软雅黑", 设置文档['else']['fontsize']))
    Style().configure('TNotebook', tabposition="wn")
    Style().configure('TNotebook.Tab', relief='flat',  # foreground="blue",
                      background="#0F0F0F", borderwidth=2)
    # 将主界面分为菜单栏和内容显示部分，内容显示部分显示主界面等细节界面
    菜单栏 = Notebook(主窗口, width=500, height=300)
    # 设置五个左侧菜单栏选项，使其被点击的时候切换至该界面
    主界面 = Frame(菜单栏)
    登陆设置界面 = Frame(菜单栏)
    学期设置界面 = Frame(菜单栏)
    其他设置界面 = Frame(菜单栏)
    关于软件界面 = Frame(菜单栏)
    初始界面(主界面)
    登录设置(登陆设置界面)
    学期设置(学期设置界面)
    其他设置(其他设置界面)
    关于软件(关于软件界面)
    主界面.grid(row=0, column=1)
    登陆设置界面.grid(row=0, column=1)
    学期设置界面.grid(row=0, column=1)
    其他设置界面.grid(row=0, column=1)
    关于软件界面.grid(row=0, column=1)
    # 将左侧菜单栏的内容添加上去
    菜单栏.add(主界面, text="一键启动")
    菜单栏.add(登陆设置界面, text="登录设置")
    菜单栏.add(学期设置界面, text="学期设置")
    菜单栏.add(其他设置界面, text="其他设置")
    菜单栏.add(关于软件界面, text="关于软件")

    菜单栏.grid(row=0, column=0)
    # 软件关闭捕获，使软件被点击关闭时弹出询问
    主窗口.protocol("WM_DELETE_WINDOW", 询问退出)
    # 系统托盘功能，设定该托盘的右键选项，并设置它的Logo
    菜单托盘 = (pystray.MenuItem("显示主窗口", 显示主窗口, default=True),
            pystray.MenuItem("退出程序", 托盘确认退出))

    # 获取软件图标位置，使用get_resource_path可以获取到运行时软件解压的临时文件夹
    # 从而可以获取到打包时附加在内的文件路径，如果使用os.path.join反而获取不了软件解压的临时文件夹
    image = Image.open(get_resource_path('kuku\\kuku.jpg'))
    # image = Image.open(os.path.join(主文件路径, "kuku.jpg"))
    icon = pystray.Icon("icon", image, "图标名称", 菜单托盘)

    # icon.run()
    # 启用子线程来启动托盘，否则会占用主线程导致GUI无法显示
    threading.Thread(target=icon.run, daemon=True).start()

    主窗口.mainloop()
