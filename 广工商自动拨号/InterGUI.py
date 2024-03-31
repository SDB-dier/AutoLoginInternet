# 文档名称：InterGUI
# 编码格式：utf-8
# 编写者：罗伟峰
# 文档作用：软件主程序及与GUI相关的代码操作

from tkinter import *
from tkinter.ttk import *
from functools import partial
from datetime import datetime
import os
import re
import sys
import time
import webbrowser
import threading
import pystray
from PIL import Image
import UserData as UD
import DataLibrary as DL


def 使用说明(框架):
    框架.columnconfigure(0, weight=1)
    画布 = Canvas(框架, width=530, height=330)
    滚动条 = Scrollbar(框架)
    滚动条.pack(side=RIGHT, fill=Y)

    # 滚动条x = Scrollbar(子界面, orient=HORIZONTAL)
    # 滚动条x.pack(side=BOTTOM, fill=X)
    画布.pack(side=LEFT, fill=Y)
    容器 = Frame(画布)
    容器.pack(fill=BOTH)
    画布.create_window((0, 0), window=容器, anchor="nw")

    说明文本 = "\
    自启动：开机自动运行本软件\n\
    自动拨号：当软件启动时自行拨号\n\
    自动复拨：在设定时间内会判定是否断网，断网后\n\
软件会自行拨号\n\
    学期假期：设定假期，假期不受复拨时间限制\n\
    固定放假日期：勾选当天不受复拨时间限制\n\
    学期补课：设定补课，补课受复拨时间限制\
    "
    警告文本 = "!!警告!!\n\
    UserData和UserSetting包含个人隐私信息，请勿\n\
泄露\n\
    DataSetting为假期设置信息，可设置好后发送他人"
    标题 = Label(容器, text='使用说明')
    标题.grid(row=0, column=0, columnspan=1, sticky=W)
    介绍 = Label(容器, text=说明文本)
    介绍.grid(row=1, column=0, columnspan=1, sticky=W)
    警告 = Label(容器, text=警告文本)
    警告.grid(row=2, column=0, columnspan=1, sticky=W)

    画布.update()
    画布.configure(yscrollcommand=滚动条.set,  # xscrollcommand=滚动条x.set,
                 scrollregion=画布.bbox("all"))
    滚动条.config(command=画布.yview)


def 一键登录(框架):
    # 设定文本Label和输入框Entry，使用grid方式进行布局

    def 更新():
        日期 = Label(框架, text='日期')
        日期.grid(row=0, column=0, columnspan=1, sticky=W)
        日期详情 = Label(框架, text=time.strftime(
            "%Y-%m-%d", time.localtime()))
        日期详情.grid(row=0, column=1, columnspan=1)

        if DL.周数差(共享设置["Semester"]["begins"]) >= 1:
            文本 = "第" + str(DL.周数差(共享设置["Semester"]["begins"])) + "周"
        else:
            文本 = "未开学"
        周数详情 = Label(框架, text=文本)
        周数详情.grid(row=0, column=2, columnspan=1)
        框架.after(3600000, 更新)

    更新()
    if DL.周数差(共享设置["Semester"]["begins"]) >= 1:
        文本 = "第" + str(DL.周数差(共享设置["Semester"]["begins"])) + "周"
    else:
        文本 = "未开学"
    周数详情 = Label(框架, text=文本)
    周数详情.grid(row=0, column=2, columnspan=1)

    用户名 = Label(框架, text='用户名：')
    用户名.grid(row=1, column=0, columnspan=1, sticky=W)
    用户名详情 = Entry(框架)
    用户名详情.insert(0, 用户数据['UserData']['Name'])
    用户名详情.grid(row=1, column=1, columnspan=1, sticky=E)

    密码 = Label(框架, text='密码：')
    密码.grid(row=2, column=0, columnspan=1, sticky=W)
    密码详情 = Entry(框架)
    密码详情['show'] = '*'
    密码详情.insert(0, 用户数据['UserData']['pwmd5'])
    密码详情.grid(row=2, column=1, columnspan=1, sticky=E)

    def 显示切换():
        print(datetime.now(), "GUI初始界面", "点击显示切换")
        if (密码详情['show'] == "*"):
            密码详情['show'] = ""
        else:
            密码详情['show'] = '*'
    # 设定一个按钮，点击按钮使其可以切换密码位置是否显示密码
    显示切换按钮 = Button(框架, text='显示切换', command=显示切换)
    显示切换按钮.grid(row=2, column=2, columnspan=1)

    # 设定3个int值，用于存储自启动、自播、复拨三个是否被选择，1为勾选
    var_自启动 = IntVar(value=用户设置['Button']['Turnon'])
    var_自拨 = IntVar(value=用户设置['Button']['Autodial'])
    var_复拨 = IntVar(value=用户设置['Button']['Redial'])
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
        print(datetime.now(), "GUI初始界面", "点击保存并拨号")
        # 首先获取用户文档和设置文档并保存在一个新变量上，好用于后续判断和覆盖
        新用户数据 = 用户数据
        新用户设置 = 用户设置
        # 判断输入框的用户名和密码跟用户文档的用户名和密码是否一致
        # 如果不一致则将输入框的用户名和密码保存到新用户文档中，再对源文档进行覆盖
        if 用户名详情.get() != 用户数据['UserData']['Name'] or \
                密码详情.get() != 用户数据['UserData']['pwmd5']:
            print(datetime.now(), "GUI初始界面", "用户名或密码不一致")
            新用户数据['UserData']['Name'] = 用户名详情.get()
            新用户数据['UserData']['Password'] = 密码详情.get()
            新用户数据['UserData']['pwmd5'] = DL.md5_text(密码详情.get())
            UD.保存数据(新用户数据, 用户数据路径)
            # 用户数据保存后会导致设置文档的usermd5产生变化，所以需要重新获取
            新用户设置 = UD.读取数据(用户设置路径)

        # 判断自启动、自播、复拨三个单选框状态跟设置文档的状态是否一致
        if var_自启动.get() != 用户设置['Button']['Turnon'] or \
                var_自拨.get() != 用户设置['Button']['Autodial'] or \
                var_复拨.get() != 用户设置['Button']['Redial']:
            print(datetime.now(), "GUI初始界面", "自启动或自动拨号或自动复拨不一致")
            新用户设置['Button']['Turnon'] = var_自启动.get()
            新用户设置['Button']['Autodial'] = var_自拨.get()
            新用户设置['Button']['Redial'] = var_复拨.get()
            UD.保存数据(新用户设置, 用户设置路径)

        # 如果勾选自启动，则立即执行设置自启动功能
        # 使其在启动文档保存一个开启该软件的bat批命令
        # 如果没有勾选，则删除启动文档的bat批命令
        print(datetime.now(), "GUI初始界面", "判断是否需要自启动")
        if var_自启动.get() == 1:
            UD.设置自启动(sys.argv[0])
            print(datetime.now(), "GUI初始界面", "启动自启动")
        else:
            UD.关闭自启动()
            print(datetime.now(), "GUI初始界面", "关闭自启动")

        # 如果勾选自动复拨，则启动自动复拨功能
        # 使软件根据用户的设定，是否需要进行自动复拨
        # 如果没有勾选，则终止自动复拨

        是否启动 = False
        for i in threading.enumerate():
            if str(DL.进程ID) in str(i):
                是否启动 = True
        print(datetime.now(), "GUI初始界面", "是否启动", 是否启动)
        if var_复拨.get() == 1 and 是否启动 is False:
            print("进程ID", DL.进程ID)
            print("所有进程", threading.enumerate())
            ga.start()
            print(datetime.now(), "GUI初始界面", "启动自动复拨")
        拨号上网()

    保存按钮 = Button(框架, text='保存并拨号', command=保存并拨号)
    保存按钮.grid(row=5, column=1, columnspan=2)
    # 打开界面立即判断设置文档的自动拨号是否启动
    # 如果启动则直接拨号，无需用户手动点击拨号
    if (用户设置['Button']['Autodial'] == 1):
        print(datetime.now(), "GUI", "自动拨号")
        拨号上网()


def 学期设置(框架):
    print(datetime.now(), "GUI学期设置")
    # 设定文本Label、输入框Entry和按钮Button，使用grid方式进行布局
    开学日期 = Label(框架, text='开学日期')
    开学日期.grid(row=0, column=0, columnspan=2, sticky=W)
    开学日期详情 = Entry(框架)
    开学日期详情.insert(0, 共享设置['Semester']['begins'])
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
        print(datetime.now(), "GUI学期设置", "点击保存学期设置")
        # 设置错误捕获，错误来源于用户填写的信息不符合格式化的要求
        try:
            开学日期详 = datetime.date(datetime.fromisoformat(开学日期详情.get()))
        except ValueError:
            警告 = Toplevel()
            警告信息 = Label(警告, text='请确保日期格式为YYYY-MM-DD\n并且该日期确实存在',
                         justify=CENTER)
            警告信息.grid(row=2, column=0, columnspan=2, sticky=W)
            警告.after(5000, 警告.destroy)
            return
        # 判断学期设置的开学日期是否与设置文档的内容一致，如果不一致则进行内容保存
        if 开学日期详 != 共享设置['Semester']['begins']:
            新共享设置 = 共享设置
            新共享设置['Semester']['begins'] = str(开学日期详)
            UD.保存数据(新共享设置, 共享设置路径)

    保存按钮 = Button(框架, text='保存', command=保存学期设置)
    保存按钮.grid(row=3, column=0, columnspan=4)


def 其他设置(框架):
    print(datetime.now(), "GUI其他设置")
    # 设定文本Label、输入框Entry和按钮Button，使用grid方式进行布局
    复拨时间段 = Label(框架, text='复拨时间段')
    复拨时间段.grid(row=0, column=0, columnspan=2, sticky=W)
    复拨时间段详情s = Entry(框架)
    复拨时间段详情s.insert(0, 共享设置['else']['redialtime'][0])
    复拨时间段详情s.grid(row=0, column=2, columnspan=1)
    复拨时间段详情e = Entry(框架)
    复拨时间段详情e.insert(0, 共享设置['else']['redialtime'][1])
    复拨时间段详情e.grid(row=0, column=3, columnspan=1)

    字体大小 = Label(框架, text='字体大小')
    字体大小.grid(row=3, column=0, columnspan=2, sticky=W)
    字体大小范围 = [i for i in range(10, 26)]
    字体大小详情 = Combobox(框架, values=字体大小范围, state="readonly")
    字体大小详情.current(newindex=int(共享设置['else']['fontsize']) - 10)
    字体大小详情.grid(row=3, column=2, columnspan=2)

    def 保存其他设置():
        print(datetime.now(), "GUI其他设置", "点击保存其他设置")
        # 判断其他设置的复拨时间段和字体大小是否与设置文档的内容一致，如果不一致则进行内容保存
        if 复拨时间段详情s.get() != 共享设置['else']['redialtime'][0] or \
                复拨时间段详情e.get() != 共享设置['else']['redialtime'][1] or \
                字体大小详情.get() != 共享设置['else']['fontsize']:
            新共享设置 = 共享设置
            新共享设置['else']['redialtime'][0] = 复拨时间段详情s.get()
            新共享设置['else']['redialtime'][1] = 复拨时间段详情e.get()
            新共享设置['else']['fontsize'] = 字体大小详情.get()
            UD.保存数据(新共享设置, 共享设置路径)
        '''# 有个未处理的问题
        # 修改字体大小后点击保存，字体大小并不会发生改变，需要软件重启后才会变化
        # 问题在于保存设置数据后，软件并没有重新读取字体大小来刷新界面
        # 该未处理问题等后续空闲时候在进行修复处理
        '''

    保存按钮 = Button(框架, text='保存', command=保存其他设置)
    保存按钮.grid(row=4, column=0, columnspan=4)


def 关于软件(框架):
    print(datetime.now(), "GUI关于软件")
    # 使框架占满该页面的所有部分，比重为1（占满）
    框架.columnconfigure(0, weight=1)
    框架.columnconfigure(1, weight=1)
    # 设定样式类型'this.TLabel'。使其不受总样式修改
    Style().configure('this.TLabel', font=("微软雅黑", 16))
    # 设定文本Label，使用grid方式进行布局
    软件介绍text = "软件介绍:\n\
        本软件仅供参考学习，请勿用于商用\n"
    软件介绍 = Label(框架, text=软件介绍text, style='this.TLabel')
    软件介绍.grid(row=0, column=0, columnspan=2, sticky=W)

    版本号text = "版本号：1.02（测试版）"
    版本号 = Label(框架, text=版本号text, style='this.TLabel')
    版本号.grid(row=1, column=0, columnspan=1, sticky=SW)

    封包时间text = "封包时间：2024/03/22"
    封包时间 = Label(框架, text=封包时间text, style='this.TLabel')
    封包时间.grid(row=1, column=1, columnspan=1, sticky=SE)

    def 打开网页():
        print(datetime.now(), "GUI关于软件", "点击获取最新版")
        webbrowser.open("https://github.com/SDB-dier/AutoLoginInternet")

    获取按钮 = Button(框架, text="获取新版代码", command=打开网页)
    获取按钮.grid(row=2, column=0, columnspan=1)

    版本按钮 = Button(框架, text='版本记录', command=版本记录)
    版本按钮.grid(row=2, column=1, columnspan=1)

    关于我text = "作者：罗伟峰\n班级：22网工C1"
    关于我 = Label(框架, text=关于我text, style='this.TLabel')
    关于我.grid(row=3, column=1, columnspan=1, sticky=NE)


def 学期假期界面():
    print(datetime.now(), "GUI学期假期界面")
    # 新建一个子窗口，并设定大小为400X600，并使所有列占比为1（界面宽度平均分配）
    子界面 = Toplevel()
    子界面.geometry("400x600")
    子界面.columnconfigure(0, weight=1)
    子界面.columnconfigure(1, weight=1)
    子界面.columnconfigure(2, weight=1)
    子界面.columnconfigure(3, weight=1)

    def 新增行数():
        print(datetime.now(), "GUI学期假期界面", "点击新增行数")
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

    固定复拨文字 = Label(子界面, text="固定放假日期")
    固定复拨文字.grid(row=0, column=0, columnspan=4, sticky=S)

    # 设置一个字典，用于存放7个单选项，是为了后面进行读取查找对象
    星期 = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    星期_dict = dict()
    for i in range(len(星期)):
        星期_dict[星期[i]] = 共享设置['Semester']['weekend'][i]
    # 结果：星期_dict = {"星期一": 0, "星期二": 0, "星期三": 0,"星期四": 0, "星期五": 0, "星期六": 1, "星期日": 1}

    # 设置一个列表，用于存放7个IntVar值，等同于以下内容
    # var_星期一 = IntVar(value=设置文档['semester']['weekend'][0])
    # ...
    # var_星期日 = IntVar(value=设置文档['semester']['weekend'][6])
    # Checkbutton的值自认Tk自带的特定函数的值，所以得设IntVar
    var_星期 = []
    for i in range(len(星期_dict)):
        var_星期.append(IntVar(value=共享设置['Semester']['weekend'][i]))

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
        print(datetime.now(), "GUI学期假期界面", "点击保存")
        var_星期_list = []
        for new_var_星期 in var_星期:
            var_星期_list.append(new_var_星期.get())
        if var_星期_list != 共享设置['Semester']['weekend']:
            新共享设置 = 共享设置
            新共享设置['Semester']['weekend'] = var_星期_list

        内容 = []
        for i in 子界面.winfo_children():
            if isinstance(i, Entry) and i.get() != "":
                # 利用datetime.data.fromisoformat来确定是否有该日期，但是该函数对格式要求严格
                # 所以需要try来进行错误判断，格式不对或日期错误则报异常
                try:
                    补课日期详 = datetime.date(datetime.fromisoformat(i.get()))
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
        新共享设置 = 共享设置
        新共享设置['Semester']['vacation'] = 内容
        UD.保存数据(新共享设置, 共享设置路径)

    新增按钮 = Button(子界面, text='新增', command=新增行数)
    新增按钮.grid(row=3, column=0, columnspan=2)
    保存按钮 = Button(子界面, text='保存', command=保存)
    保存按钮.grid(row=3, column=2, columnspan=2)

    学期假期数量 = len(共享设置['Semester']['vacation'])

    for i in range(学期假期数量):
        已有行数 = DL.读取行数(子界面)
        学期假期日期 = Entry(子界面)
        if (i % 2 == 0):
            学期假期日期.insert(0, 共享设置['Semester']['vacation'][i])
            学期假期日期.grid(row=已有行数 + 1, column=0,
                        columnspan=2, sticky="NSEW")
        else:
            学期假期日期.insert(0, 共享设置['Semester']['vacation'][i])
            学期假期日期.grid(row=已有行数, column=2,
                        columnspan=2, sticky="NSEW")


def 学期补课界面():
    print(datetime.now(), "GUI学期补课界面")
    子界面 = Toplevel()
    子界面.geometry("400x600")
    子界面.columnconfigure(0, weight=1)
    子界面.columnconfigure(1, weight=2)

    def 新增行数():
        print(datetime.now(), "GUI学期补课界面", "点击新增行数")
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
        print(datetime.now(), "GUI学期补课界面", "点击保存")
        内容 = []
        for i in 子界面.winfo_children():
            if isinstance(i, Entry) and i.get() != "":
                # 利用datetime.data.fromisoformat来确定是否有该日期，但是该函数对格式要求严格
                # 所以需要try来进行错误判断，格式不对或日期错误则报异常
                try:
                    补课日期详 = datetime.date(datetime.fromisoformat(i.get()))
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
        新共享设置 = 共享设置
        新共享设置['Semester']['workday'] = 内容
        UD.保存数据(新共享设置, 共享设置路径)

    新增按钮 = Button(子界面, text='新增', command=新增行数)
    新增按钮.grid(row=0, column=0, columnspan=1)
    保存按钮 = Button(子界面, text='保存', command=学期补课内容)
    保存按钮.grid(row=0, column=1, columnspan=1)
    学期补课文字 = Label(子界面, text="本学期补课日期")
    学期补课文字.grid(row=1, column=0, columnspan=2, sticky=S)

    学期补课数量 = len(共享设置['Semester']['workday'])

    for i in range(学期补课数量):
        已有行数 = DL.读取行数(子界面)
        学期补课日期 = Entry(子界面)
        if (i % 2 == 0):
            学期补课日期.insert(0, 共享设置['Semester']['workday'][i])
            学期补课日期.grid(row=已有行数 + 1, column=0,
                        columnspan=1, sticky="NSEW")
        else:
            学期补课日期.insert(0, 共享设置['Semester']['workday'][i])
            学期补课日期.grid(row=已有行数, column=1,
                        columnspan=1, sticky="NSEW")


def 校站界面():
    print(datetime.now(), "GUI校站界面")
    子界面 = Toplevel()
    子界面.geometry("400x300")
    子界面.columnconfigure(0, weight=1)
    子界面.columnconfigure(1, weight=1)

    def 打开网页(interesting):
        print(datetime.now(), "GUI校站界面", "打开网页")
        webbrowser.open(interesting)

    校站数量 = len(共享设置['else']['schooltext'])

    for i in range(校站数量):
        # print(i % 2 == 0)
        # print("row:", i // 2, "column:", i % 2)
        新增按钮 = Button(子界面, text=共享设置['else']['schooltext'][i],
                      command=partial(打开网页, 共享设置['else']['schoolweb'][i]))
        新增按钮.grid(row=(i // 2), column=i % 2, columnspan=1, sticky="NSEW")


def 版本记录():
    子界面 = Toplevel()
    子界面.geometry("400x600")
    画布 = Canvas(子界面)
    滚动条 = Scrollbar(子界面)
    滚动条.pack(side=RIGHT, fill=Y)

    # 滚动条x = Scrollbar(子界面, orient=HORIZONTAL)
    # 滚动条x.pack(side=BOTTOM, fill=X)
    画布.pack(side=RIGHT, fill=BOTH)
    容器 = Frame(画布)
    容器.pack(fill=BOTH)
    画布.create_window((0, 0), window=容器, anchor="nw")
    # 滚动条.grid(row=0, column=2, columnspan=1)

    版本1_0 = "版本1.0    2024/03/08\n\
    完成软件设计。"
    版本文字 = Label(容器, text=版本1_0)
    版本文字.pack(side="top", anchor="nw")
    版本1_01 = "版本1.01    2024/03/11\n\
    修复首次勾选自动复播按钮，会引起\n\
    无法获取线程ID和是否启动的问题。\n\
    新增版本记录、固定了主窗口大小"
    版本文字 = Label(容器, text=版本1_01)
    版本文字.pack(side="top", anchor="nw")
    版本1_02 = "版本1.02    2024/03/22\n\
    添加了软件路径含有空格时的提示"
    版本文字 = Label(容器, text=版本1_02)
    版本文字.pack(side="top", anchor="nw")

    # 拨号文字.grid(row=1, column=0, columnspan=1, sticky=NW)
    画布.update()
    画布.configure(yscrollcommand=滚动条.set,  # xscrollcommand=滚动条x.set,
                 scrollregion=画布.bbox("all"))
    滚动条.config(command=画布.yview)
    # Listbox(子界面).grid(row=1, column=0, columnspan=1, sticky=W)

    # 滚动条.config(command=拨号文字.yview)


def 拨号上网():
    print(datetime.now(), "GUI拨号上网")
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
    print(datetime.now(), "GUI拨号上网界面更新CL")

    def __init__(self):
        super().__init__()
        self.StopTag = False
        self.测试结果 = None

    def run(self):
        threading.Thread(target=self.界面更新, daemon=True,
                         name="拨号上网界面更新").start()

    def 界面更新(self):
        self.测试结果 = DL.联网测试()
        print(datetime.now(), "self.StopTag", self.StopTag)
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


def 托盘确认退出(self):
    icon.stop()
    主窗口.quit()
    主窗口.destroy()


def 弹出窗口(提示):
    弹出窗口 = Toplevel()
    提示文字 = Label(弹出窗口, text=提示, justify=CENTER)
    提示文字.grid(row=0, column=0, columnspan=2)
    弹出窗口.after(10000, 弹出窗口.destroy)


def get_resource_path(relative_path):
    # 函数作用：获取运行时软件解压的临时文件夹
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


# 获取文件路径，方便后面进行使用
主文件路径 = os.path.dirname(os.path.realpath(sys.argv[0]))
用户数据路径 = os.path.join(主文件路径, 'UserData.json')
用户设置路径 = os.path.join(主文件路径, 'UserSetting.json')
共享设置路径 = os.path.join(主文件路径, 'DataSetting.json')
跨线程变量文档路径 = os.path.join(主文件路径, 'test.txt')


if __name__ == '__main__':
    print(datetime.now(), "GUI", "进入主程序")
    # 进入程序，判断是否位于桌面或磁盘根目录
    用户路径 = os.environ['UserProfile']
    用户桌面路径 = os.path.join(用户路径, 'Desktop')
    正则判断 = re.compile(r"[A-Z+]:$")
    # 创建主窗口Tk，并命名标题和修改Logo
    主窗口 = Tk()
    主窗口.title("广工商自动化登录程序")
    主窗口.iconbitmap(get_resource_path('kuku\\kuku.ico'))
    # 主窗口.iconbitmap(os.path.join(主文件路径, "kuku.ico"))
    # 判断该文档是否放在了桌面或磁盘根目录，如果放在了桌面或磁盘根目录，就提示放在此处并强制关闭程序
    print(datetime.now(), "GUI", "判断程序是否在桌面或磁盘根目录")
    if (主文件路径 == 用户桌面路径 or (not (正则判断.search(主文件路径) is None))):
        Style().configure('.', font=("微软雅黑", 16))
        提示文本 = Label(主窗口, text='请不要将此文件放在桌面或磁盘根目录')
        提示文本.grid(row=0, column=0)
        关闭按钮 = Button(主窗口, text='确认关闭', command=sys.exit)
        关闭按钮.grid(row=1, column=0)
        主窗口.mainloop()
        sys.exit()
    elif (" " in 主文件路径):
        Style().configure('.', font=("微软雅黑", 16))
        提示文本 = Label(主窗口, text='请不要将此文件放在含有空格的路径')
        提示文本.grid(row=0, column=0)
        关闭按钮 = Button(主窗口, text='确认关闭', command=sys.exit)
        关闭按钮.grid(row=1, column=0)
        主窗口.mainloop()
        sys.exit()
    # 判断是否有用户文档跟设置文档
    print(datetime.now(), "GUI", "初始化用户数据、用户设置、共享设置和跨线程变量")
    UD.初始化数据(用户数据路径, 0, 0)
    UD.初始化数据(用户设置路径, 1, 0)
    UD.初始化数据(共享设置路径, 2, 0)
    UD.初始化数据(跨线程变量文档路径, 3, 0)
    print(datetime.now(), "GUI", "读取用户数据和设置数据")
    # 读取用户文档和设置文档
    用户数据 = UD.读取数据(用户数据路径)
    用户设置 = UD.读取数据(用户设置路径)
    共享设置 = UD.读取数据(共享设置路径)
    # 判断设备码是否相同或是否被篡改用户文档，如设备码不同或被篡改，则重置用户文档跟设置文档的usermd5
    ID = DL.设备码()
    print(datetime.now(), "GUI", "判断是否被篡改用户数据")

    if (用户数据['UserID']['CPU'] != ID[0] or
            用户数据['UserID']['MAC'] != ID[1] or
            DL.md5_text(str(用户数据)) != 用户设置['Usermd5']):
        print(datetime.now(), "GUI", "用户数据被篡改")
        # 初始化自启动、自动拨号和自动复拨，防止账户重置后使用空内容提交
        新用户设置 = 用户设置
        新用户设置['Button']['Turnon'] = 0
        新用户设置['Button']['Autodial'] = 0
        新用户设置['Button']['Redial'] = 0
        UD.保存数据(新用户设置, 用户设置路径)
        # 更新用户文档数据，格式化后写入到磁盘中
        新用户数据 = 用户数据
        新用户数据['UserID']['CPU'] = ID[0]
        新用户数据['UserID']['MAC'] = ID[1]
        新用户数据['UserData']['Name'] = ""
        新用户数据['UserData']['Password'] = ""
        新用户数据['UserData']['pwmd5'] = ""
        UD.保存数据(新用户数据, 用户数据路径)
        # 重置后需要重新读取用户文档和设置文档
        用户数据 = UD.读取数据(用户数据路径)
        用户设置 = UD.读取数据(用户设置路径)
    # 判断软件是否需要自启动，如果需要就在启动文档添加一个bat批命令来打开软件
    # 如果不需要自启动就将启动文件夹的bat批命令删掉

    print(datetime.now(), "GUI", "判断是否需要自启动")
    if 用户设置['Button']['Turnon'] == 1:
        UD.设置自启动(sys.argv[0])
        print(datetime.now(), "GUI", "启动自启动")
    else:
        UD.关闭自启动()
        print(datetime.now(), "GUI", "关闭自启动")
    # 判断是否勾选了自动复拨功能，如果勾选则启用自动复拨
    global ga
    ga = DL.自动复拨()
    if 用户设置['Button']['Redial'] == 1:
        ga.start()
        print(datetime.now(), "GUI", "启动自动复拨")

    # 设置主窗口大小
    主窗口.geometry("630x330")
    主窗口.resizable(0, 0)
    # 设置窗口样式
    Style().configure('.', font=("微软雅黑", 共享设置['else']['fontsize']))
    Style().configure('TNotebook', tabposition="wn")
    Style().configure('TNotebook.Tab', relief='flat',  # foreground="blue",
                      background="#0F0F0F", borderwidth=2)
    # 将主界面分为菜单栏和内容显示部分，内容显示部分显示主界面等细节界面
    菜单栏 = Notebook(主窗口, width=530, height=330)
    # 设置五个左侧菜单栏选项，使其被点击的时候切换至该界面
    使用说明界面 = Frame(菜单栏)
    一键登录界面 = Frame(菜单栏)
    # 登陆设置界面 = Frame(菜单栏)
    学期设置界面 = Frame(菜单栏)
    其他设置界面 = Frame(菜单栏)
    关于软件界面 = Frame(菜单栏)
    使用说明(使用说明界面)
    一键登录(一键登录界面)
    # 登录设置(登陆设置界面)
    学期设置(学期设置界面)
    其他设置(其他设置界面)
    关于软件(关于软件界面)
    使用说明界面.grid(row=0, column=1)
    一键登录界面.grid(row=0, column=1)
    # 登陆设置界面.grid(row=0, column=1)
    学期设置界面.grid(row=0, column=1)
    其他设置界面.grid(row=0, column=1)
    关于软件界面.grid(row=0, column=1)
    # 将左侧菜单栏的内容添加上去
    菜单栏.add(使用说明界面, text="使用说明")
    菜单栏.add(一键登录界面, text="一键登录")
    # 菜单栏.add(登陆设置界面, text="登录设置")
    菜单栏.add(学期设置界面, text="学期设置")
    菜单栏.add(其他设置界面, text="其他设置")
    菜单栏.add(关于软件界面, text="关于软件")

    菜单栏.grid(row=0, column=0)
    # 软件关闭捕获，使软件被点击关闭时弹出询问
    主窗口.protocol("WM_DELETE_WINDOW", 询问退出)
    # 系统托盘功能，设定该托盘的右键选项，并设置它的Logo
    菜单托盘 = (pystray.MenuItem("显示主窗口", 主窗口.deiconify, default=True),
            pystray.MenuItem("退出程序", 托盘确认退出))

    # 获取软件图标位置，使用get_resource_path可以获取到运行时软件解压的临时文件夹
    # 从而可以获取到打包时附加在内的文件路径，如果使用os.path.join反而获取不了软件解压的临时文件夹
    image = Image.open(get_resource_path('kuku\\kuku.jpg'))
    # image = Image.open(os.path.join(主文件路径, "kuku.jpg"))
    icon = pystray.Icon("icon", image, "图标名称", 菜单托盘)

    # icon.run()
    # 启用子线程来启动托盘，否则会占用主线程导致GUI无法显示
    threading.Thread(target=icon.run, daemon=True, name="菜单托盘").start()

    主窗口.mainloop()
