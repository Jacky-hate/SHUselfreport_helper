from urllib import request, parse
from pic import img
import os
import ctypes
import tkinter
from urllib import request, parse
import urllib
from io import BytesIO
import gzip
import time
import socket
import re
import base64
from urllib.parse import quote
import calendar
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
import threading
from tkinter import messagebox

datetime = calendar.datetime.datetime
timedelta = calendar.datetime.timedelta


class Calendar:

    def __init__(s, point=None, position=None):
        # point    提供一个基点，来确定窗口位置
        # position 窗口在点的位置 'ur'-右上, 'ul'-左上, 'll'-左下, 'lr'-右下
        # s.master = tk.Tk()
        s.master = tk.Toplevel()
        s.master.withdraw()
        fwday = calendar.SUNDAY

        year = datetime.now().year
        month = datetime.now().month
        locale = None
        sel_bg = '#ecffc4'
        sel_fg = '#05640e'

        s._date = datetime(year, month, 1)
        s._selection = None  # 设置为未选中日期

        s.G_Frame = ttk.Frame(s.master)

        s._cal = s.__get_calendar(locale, fwday)

        s.__setup_styles()  # 创建自定义样式
        s.__place_widgets()  # pack/grid 小部件
        s.__config_calendar()  # 调整日历列和安装标记
        # 配置画布和正确的绑定，以选择日期。
        s.__setup_selection(sel_bg, sel_fg)

        # 存储项ID，用于稍后插入。
        s._items = [s._calendar.insert('', 'end', values='') for _ in range(6)]

        # 在当前空日历中插入日期
        s._update()

        s.G_Frame.pack(expand=1, fill='both')
        s.master.overrideredirect(1)
        s.master.update_idletasks()
        width, height = s.master.winfo_reqwidth(), s.master.winfo_reqheight()
        if point and position:
            if position == 'ur':
                x, y = point[0], point[1] - height
            elif position == 'lr':
                x, y = point[0], point[1]
            elif position == 'ul':
                x, y = point[0] - width, point[1] - height
            elif position == 'll':
                x, y = point[0] - width, point[1]
        else:
            x, y = (s.master.winfo_screenwidth() - width) / 2, (s.master.winfo_screenheight() - height) / 2
        s.master.geometry('%dx%d+%d+%d' % (width, height, x, y))  # 窗口位置居中
        s.master.after(300, s._main_judge)
        s.master.deiconify()
        s.master.focus_set()
        s.master.wait_window()  # 这里应该使用wait_window挂起窗口，如果使用mainloop,可能会导致主程序很多错误

    def __get_calendar(s, locale, fwday):
        # 实例化适当的日历类
        if locale is None:
            return calendar.TextCalendar(fwday)
        else:
            return calendar.LocaleTextCalendar(fwday, locale)

    def __setitem__(s, item, value):
        if item in ('year', 'month'):
            raise AttributeError("attribute '%s' is not writeable" % item)
        elif item == 'selectbackground':
            s._canvas['background'] = value
        elif item == 'selectforeground':
            s._canvas.itemconfigure(s._canvas.text, item=value)
        else:
            s.G_Frame.__setitem__(s, item, value)

    def __getitem__(s, item):
        if item in ('year', 'month'):
            return getattr(s._date, item)
        elif item == 'selectbackground':
            return s._canvas['background']
        elif item == 'selectforeground':
            return s._canvas.itemcget(s._canvas.text, 'fill')
        else:
            r = ttk.tclobjs_to_py({item: ttk.Frame.__getitem__(s, item)})
            return r[item]

    def __setup_styles(s):
        # 自定义TTK风格
        style = ttk.Style(s.master)
        arrow_layout = lambda dir: (
            [('Button.focus', {'children': [('Button.%sarrow' % dir, None)]})]
        )
        style.layout('L.TButton', arrow_layout('left'))
        style.layout('R.TButton', arrow_layout('right'))

    def __place_widgets(s):
        # 标头框架及其小部件
        Input_judgment_num = s.master.register(s.Input_judgment)  # 需要将函数包装一下，必要的
        hframe = ttk.Frame(s.G_Frame)
        gframe = ttk.Frame(s.G_Frame)
        bframe = ttk.Frame(s.G_Frame)
        hframe.pack(in_=s.G_Frame, side='top', pady=5, anchor='center')
        gframe.pack(in_=s.G_Frame, fill=tk.X, pady=5)
        bframe.pack(in_=s.G_Frame, side='bottom', pady=5)

        lbtn = ttk.Button(hframe, style='L.TButton', command=s._prev_month)
        lbtn.grid(in_=hframe, column=0, row=0, padx=12)
        rbtn = ttk.Button(hframe, style='R.TButton', command=s._next_month)
        rbtn.grid(in_=hframe, column=5, row=0, padx=12)

        s.CB_year = ttk.Combobox(hframe, width=5, values=[str(year) for year in
                                                          range(datetime.now().year, datetime.now().year - 11, -1)],
                                 validate='key', validatecommand=(Input_judgment_num, '%P'))
        s.CB_year.current(0)
        s.CB_year.grid(in_=hframe, column=1, row=0)
        s.CB_year.bind('<KeyPress>', lambda event: s._update(event, True))
        s.CB_year.bind("<<ComboboxSelected>>", s._update)
        tk.Label(hframe, text='年', justify='left').grid(in_=hframe, column=2, row=0, padx=(0, 5))

        s.CB_month = ttk.Combobox(hframe, width=3, values=['%02d' % month for month in range(1, 13)], state='readonly')
        s.CB_month.current(datetime.now().month - 1)
        s.CB_month.grid(in_=hframe, column=3, row=0)
        s.CB_month.bind("<<ComboboxSelected>>", s._update)
        tk.Label(hframe, text='月', justify='left').grid(in_=hframe, column=4, row=0)

        # 日历部件
        s._calendar = ttk.Treeview(gframe, show='', selectmode='none', height=7)
        s._calendar.pack(expand=1, fill='both', side='bottom', padx=5)

        ttk.Button(bframe, text="确 定", width=6, command=lambda: s._exit(True)).grid(row=0, column=0, sticky='ns',
                                                                                    padx=20)
        ttk.Button(bframe, text="取 消", width=6, command=s._exit).grid(row=0, column=1, sticky='ne', padx=20)

        tk.Frame(s.G_Frame, bg='#565656').place(x=0, y=0, relx=0, rely=0, relwidth=1, relheigh=2 / 200)
        tk.Frame(s.G_Frame, bg='#565656').place(x=0, y=0, relx=0, rely=198 / 200, relwidth=1, relheigh=2 / 200)
        tk.Frame(s.G_Frame, bg='#565656').place(x=0, y=0, relx=0, rely=0, relwidth=2 / 200, relheigh=1)
        tk.Frame(s.G_Frame, bg='#565656').place(x=0, y=0, relx=198 / 200, rely=0, relwidth=2 / 200, relheigh=1)

    def __config_calendar(s):
        # cols = s._cal.formatweekheader(3).split()
        cols = ['日', '一', '二', '三', '四', '五', '六']
        s._calendar['columns'] = cols
        s._calendar.tag_configure('header', background='grey90')
        s._calendar.insert('', 'end', values=cols, tag='header')
        # 调整其列宽
        font = tkFont.Font()
        maxwidth = max(font.measure(col) for col in cols)
        for col in cols:
            s._calendar.column(col, width=maxwidth, minwidth=maxwidth,
                               anchor='center')

    def __setup_selection(s, sel_bg, sel_fg):
        def __canvas_forget(evt):
            canvas.place_forget()
            s._selection = None

        s._font = tkFont.Font()
        s._canvas = canvas = tk.Canvas(s._calendar, background=sel_bg, borderwidth=0, highlightthickness=0)
        canvas.text = canvas.create_text(0, 0, fill=sel_fg, anchor='w')

        canvas.bind('<Button-1>', __canvas_forget)
        s._calendar.bind('<Configure>', __canvas_forget)
        s._calendar.bind('<Button-1>', s._pressed)

    def _build_calendar(s):
        year, month = s._date.year, s._date.month

        # update header text (Month, YEAR)
        header = s._cal.formatmonthname(year, month, 0)

        # 更新日历显示的日期
        cal = s._cal.monthdayscalendar(year, month)
        for indx, item in enumerate(s._items):
            week = cal[indx] if indx < len(cal) else []
            fmt_week = [('%02d' % day) if day else '' for day in week]
            s._calendar.item(item, values=fmt_week)

    def _show_select(s, text, bbox):
        """为新的选择配置画布。"""
        x, y, width, height = bbox

        textw = s._font.measure(text)

        canvas = s._canvas
        canvas.configure(width=width, height=height)
        canvas.coords(canvas.text, (width - textw) / 2, height / 2 - 1)
        canvas.itemconfigure(canvas.text, text=text)
        canvas.place(in_=s._calendar, x=x, y=y)

    def _pressed(s, evt=None, item=None, column=None, widget=None):
        """在日历的某个地方点击。"""
        if not item:
            x, y, widget = evt.x, evt.y, evt.widget
            item = widget.identify_row(y)
            column = widget.identify_column(x)

        if not column or not item in s._items:
            # 在工作日行中单击或仅在列外单击。
            return

        item_values = widget.item(item)['values']
        if not len(item_values):  # 这个月的行是空的。
            return

        text = item_values[int(column[1]) - 1]
        if not text:  # 日期为空
            return

        bbox = widget.bbox(item, column)
        if not bbox:  # 日历尚不可见
            s.master.after(20, lambda: s._pressed(item=item, column=column, widget=widget))
            return

        # 更新，然后显示选择
        text = '%02d' % text
        s._selection = (text, item, column)
        s._show_select(text, bbox)

    def _prev_month(s):
        """更新日历以显示前一个月。"""
        s._canvas.place_forget()
        s._selection = None

        s._date = s._date - timedelta(days=1)
        s._date = datetime(s._date.year, s._date.month, 1)
        s.CB_year.set(s._date.year)
        s.CB_month.set(s._date.month)
        s._update()

    def _next_month(s):
        """更新日历以显示下一个月。"""
        s._canvas.place_forget()
        s._selection = None

        year, month = s._date.year, s._date.month
        s._date = s._date + timedelta(
            days=calendar.monthrange(year, month)[1] + 1)
        s._date = datetime(s._date.year, s._date.month, 1)
        s.CB_year.set(s._date.year)
        s.CB_month.set(s._date.month)
        s._update()

    def _update(s, event=None, key=None):
        """刷新界面"""
        if key and event.keysym != 'Return': return
        year = int(s.CB_year.get())
        month = int(s.CB_month.get())
        if year == 0 or year > 9999: return
        s._canvas.place_forget()
        s._date = datetime(year, month, 1)
        s._build_calendar()  # 重建日历

        if year == datetime.now().year and month == datetime.now().month:
            day = datetime.now().day
            for _item, day_list in enumerate(s._cal.monthdayscalendar(year, month)):
                if day in day_list:
                    item = 'I00' + str(_item + 2)
                    column = '#' + str(day_list.index(day) + 1)
                    s.master.after(100, lambda: s._pressed(item=item, column=column, widget=s._calendar))

    def _exit(s, confirm=False):
        """退出窗口"""
        if not confirm: s._selection = None
        s.master.destroy()

    def _main_judge(s):
        """判断窗口是否在最顶层"""
        try:
            # s.master 为 TK 窗口
            # if not s.master.focus_displayof(): s._exit()
            # else: s.master.after(10, s._main_judge)

            # s.master 为 toplevel 窗口
            if s.master.focus_displayof() == None or 'toplevel' not in str(s.master.focus_displayof()):
                s._exit()
            else:
                s.master.after(10, s._main_judge)
        except:
            s.master.after(10, s._main_judge)

        # s.master.tk_focusFollowsMouse() # 焦点跟随鼠标

    def selection(s):
        """返回表示当前选定日期的日期时间。"""
        if not s._selection: return None

        year, month = s._date.year, s._date.month
        return str(datetime(year, month, int(s._selection[0])))[:10]

    def Input_judgment(s, content):
        """输入判断"""
        # 如果不加上==""的话，就会发现删不完。总会剩下一个数字
        if content.isdigit() or content == "":
            return True
        else:
            return False


class display():
    def __init__(self, master, fuc):
        self.processBarLen = 500
        self.win = master
        self.win.title("Selfreport helper")
        # self.win.title("Selfreport helper")
        self.setIcon()
        window = self.win

        window.resizable(0, 0)
        var = tk.StringVar()  # 文字变量储存器
        var.set('user: ')

        root = self.win
        width = 600
        height = 300
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        # 获取屏幕的缩放因子
        ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        # 设置程序缩放
        root.tk.call('tk', 'scaling', ScaleFactor / 75)
        width, height = root.winfo_reqwidth() + 50, 50  # 窗口大小
        x, y = (root.winfo_screenwidth() - width) / 2, (root.winfo_screenheight() - height) / 2

        date_str = tk.StringVar()
        date_str.set("2020-11-03")
        date = ttk.Entry(root, textvariable=date_str, width=20)
        date.place(x=350, y=120)

        # Calendar((x, y), 'ur').selection() 获取日期，x,y为点坐标
        date_str_gain = lambda: [
            date_str.set(date)
            for date in [Calendar((x, y), 'ur').selection()]
            if date]
        tk.Button(root, text='选择开始日期', command=date_str_gain).place(x=240, y=120)
        date_str_gain = lambda: [
            date_str2.set(date)
            for date in [Calendar((x, y), 'ur').selection()]
            if date]
        date_str2 = tk.StringVar()
        date_str2.set("2020-11-21")
        date2 = ttk.Entry(root, textvariable=date_str2, width=20)
        date2.place(x=350, y=160)

        # Calendar((x, y), 'ur').selection() 获取日期，x,y为点坐标
        tk.Button(root, text='选择结束日期', command=date_str_gain).place(x=240, y=160)

        l1 = tk.Label(self.win,
                      text="user:",  # 标签的文字
                      # bg='grey',  # 背景颜色
                      font=('Arial', 11),  # 字体和字体大小
                      # width=15, height=2  # 标签长宽
                      )
        l1.place(x=280, y=50)
        l2 = tk.Label(self.win,
                      text="pswd:",  # 标签的文字
                      # bg='grey',  # 背景颜色
                      font=('Arial', 11),  # 字体和字体大小
                      # width=15, height=2  # 标签长宽
                      )
        l2.place(x=280, y=80)
        e1 = tk.Entry(window, width=20, relief='flat')  # 创建文本框，用户可输入内容
        e1.place(x=350, y=50)
        e2 = tk.Entry(window, show='*', width=20, relief='flat')  # 输入框，输入时显示*
        e2.place(x=350, y=80)
        sc = tkinter.Scrollbar(root)
        sc.pack(side=tkinter.LEFT, fill=tkinter.Y)
        self.listbox = tkinter.Listbox(root, yscrollcommand=sc.set)
        self.listbox.pack(side=tkinter.LEFT, padx=5, pady=5)
        def load():
            self.listbox.insert(tkinter.END, "[info]: ")
            time.sleep(1)
            self.listbox.insert(tkinter.END, "This is a script for SHU")
            time.sleep(1)
            self.listbox.insert(tkinter.END, "selfreport during novel ")
            time.sleep(1)
            self.listbox.insert(tkinter.END, "coronavirus epidemic..")
            time.sleep(1)
            self.listbox.insert(tkinter.END, ",which was written for")
            time.sleep(1)
            self.listbox.insert(tkinter.END, "fun....")
            time.sleep(1)
            self.listbox.insert(tkinter.END, "Please tape in your")
            time.sleep(1)
            self.listbox.insert(tkinter.END, "information to continue...")
        threading.Thread(target=load).start()
        sc.config(command=self.listbox.yview)

        def func():
            self.listbox.insert(tkinter.END, "uploading...")
            time.sleep(0.5)
            fuc(e1.get(), e2.get(), date.get(), date2.get(), self.listbox)

        b = tk.Button(window,
                      text='submit',  # 显示按钮上的文字
                      width=10,
                      command=func)  # 点击按钮执行的命令
        b.place(x=450, y=200)

        var2 = tk.StringVar()
        var2.set((11, 22, 33, 44))  # 为变量设置值

        def do_job():
            i = 1

        menubar = tk.Menu(window)
        # 定义一个空菜单单元
        filemenu = tk.Menu(menubar, tearoff=0)
        # # 将上面定义的空菜单命名为`File`，放在菜单栏中，就是装入那个容器中
        # menubar.add_cascade(label='File', menu=filemenu)
        #
        # # 在File中加入New的小菜单，即我们平时看到的下拉菜单，每一个小菜单对应命令操作。
        # # 如果点击这些单元, 就会触发`do_job`的功能
        # filemenu.add_command(label='New', command=do_job)
        # filemenu.add_command(label='Open', command=do_job)
        # filemenu.add_command(label='Save', command=do_job)
        # # 添加一条分割线
        # filemenu.add_separator()
        # filemenu.add_command(label='Exit', command=window.quit)

        editmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Help', menu=editmenu)
        editmenu.add_command(label='Nothing to show', command=do_job)
        editmenu.add_command(label='Nothing to...', command=do_job)
        editmenu.add_command(label='Nothing...', command=do_job)

        submenu = tk.Menu(filemenu)
        filemenu.add_cascade(label='Import', menu=submenu, underline=0)
        # 这里和上面也一样，在`Import`中加入一个小菜单命令`Submenu1`
        submenu.add_command(label="Submenu1", command=do_job)

        window.config(menu=menubar)

        # messagebox.showinfo(title='', message='')  # 提示信息对话窗
        # messagebox.showwarning()  # 提出警告对话窗
        # messagebox.showerror()  # 提出错误对话窗
        # messagebox.askquestion()  # 询问选择对话窗
        #
        # print(messagebox.askquestion())  # 返回yes和no
        # print(messagebox.askokcancel())  # 返回true和false
        # print(messagebox.askyesno())  # 返回true和false
        # print(messagebox.askretrycancel())  # 返回true和false

        self.win.mainloop()

    def setIcon(self):
        tmp = open("tmp.ico", "wb+")
        tmp.write(base64.b64decode(img))  # 写入到临时文件中
        tmp.close()
        self.win.iconbitmap("tmp.ico")  # 设置图标
        os.remove("tmp.ico")  # 删除临死图标


class report():
    def __init__(self, master):
        self.master = master
        display(master, self.starting)  # 将我们定义的GUI类赋给服务类的属性，将执行的功能函数作为参数传入

    def post(self, year, month, day, half, head):
        time = "{}-{:0>2d}-{:0>2d}".format(year, month, day)
        url_des = "https://selfreport.shu.edu.cn/XueSFX/HalfdayReport.aspx?day=" + time + "&t=" + str(half)
        head = {
            "Host": "selfreport.shu.edu.cn",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
            "Referer": "https://selfreport.shu.edu.cn/XueSFX/HalfdayReport_History.aspx",
            "Accept-Encoding": "gzip, deflate, br",
            "Cookie": head["Cookie"],
        }
        req = request.Request(url=url_des, headers=head, method='GET')
        response = request.urlopen(req, timeout=2)
        # print(response.status, response.reason)
        # for key, values in response.getheaders():
        #     print(key + " " + values)
        buff = BytesIO(response.read())
        f = gzip.GzipFile(fileobj=buff)
        htmls = f.read().decode('utf-8')
        s = str(htmls)
        pattern = re.compile(r'id="__VIEWSTATE" value="(.*?)"')
        result_vs = str(re.findall(pattern, s)[0])
        result_vs = quote(result_vs, 'utf-8')
        pattern = re.compile(r'id="__VIEWSTATEGENERATOR" value="(.*?)"')
        result_vsg = str(re.findall(pattern, s)[0])
        result_vsg = quote(result_vsg, 'utf-8')
        result_base64 = '{"p1_BaoSRQ":{"Text":"' + time + '"},"p1_DangQSTZK":{"F_Items":[["良好","良好",1],["不适","不适",1]],"SelectedValue":"良好"},"p1_ZhengZhuang":{"Hidden":true,"F_Items":[["感冒","感冒",1],["咳嗽","咳嗽",1],["发热","发热",1]],"SelectedValueArray":[]},"p1_SuiSM":{"F_Items":[["红色","红色",1],["黄色","黄色",1],["绿色","绿色",1]],"SelectedValue":null},"p1_ShiFJC":{"F_Items":[["早餐","早餐",1],["午餐","午餐",1],["晚餐","晚餐",1]],"SelectedValueArray":[]},"p1_ctl00_btnSubmit":{"Hidden":false},"p1":{"Title":"每日两报（下午）","IFrameAttributes":{}}}'
        result_base64 = result_base64.encode("utf-8")
        result_base64 = base64.b64encode(result_base64)
        result_base64 = result_base64.decode('utf-8')
        r = quote(result_base64, 'utf-8')
        r = r[0:414] + 'F_STATE' + r[414:824]
        head = {
            "Host": "selfreport.shu.edu.cn",
            "Connection": "keep-alive",
            "Content-Length": " 1446",
            "Accept": " text/plain, */*; q=0.01",
            "X-FineUI-Ajax": " true",
            "User-Agent": " Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
            "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": " https://selfreport.shu.edu.cn",
            "Referer": " https://selfreport.shu.edu.cn/XueSFX/HalfdayReport.aspx?day=2020-11-19&t=1",
            "Accept-Encoding": " gzip, deflate, br",
            "Cookie": head["Cookie"],
        }
        data = bytes(
            "__EVENTTARGET=p1%24ctl00%24btnSubmit&__EVENTARGUMENT=&__VIEWSTATE=" + result_vs + "&__VIEWSTATEGENERATOR=" + result_vsg + "&p1%24ChengNuo=p1_ChengNuo&p1%24BaoSRQ=" + time + "&p1%24DangQSTZK=%E8%89%AF%E5%A5%BD&p1%24TiWen=37&p1%24SuiSM=%E7%BB%BF%E8%89%B2&F_TARGET=p1_ctl00_btnSubmit&p1_Collapsed=false&F_STATE=" + r,
            encoding='utf8')
        head["Content-Length"] = str(len(data))
        head["Referer"] = url_des
        req = request.Request(url=url_des, headers=head, method='POST', data=data)
        try:
            response = request.urlopen(req, timeout=2)
            print(time, " ", response.reason)
            self.listbox.insert(tkinter.END, time + " " + response.reason)
            self.listbox.yview(tkinter.END)
            # for key, values in response.getheaders():
            #     print(key + " " + values)
            buff = BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buff)
            htmls = f.read().decode('utf-8')
        except socket.timeout:
            print(time + "time out")
            self.listbox.insert(tkinter.END, time + " time out")
            self.listbox.yview(tkinter.END)

        # print(htmls)

    def login(self, username, password):
        username = str(username)
        password = str(password)
        start_url = "https://newsso.shu.edu.cn/login/eyJ0aW1lc3RhbXAiOjE2MDU3NjcxNTMzMzg1MzE0MDIsInJlc3BvbnNlVHlwZSI6ImNvZGUiLCJjbGllbnRJZCI6IldVSFdmcm50bldZSFpmelE1UXZYVUNWeSIsInNjb3BlIjoiMSIsInJlZGlyZWN0VXJpIjoiaHR0cHM6Ly9zZWxmcmVwb3J0LnNodS5lZHUuY24vTG9naW5TU08uYXNweD9SZXR1cm5Vcmw9JTJmIiwic3RhdGUiOiIifQ== "

        head = {
            "Host": "newsso.shu.edu.cn",
            "Connection": "keep-alive",
            "Content-Length": "51",
            "Origin": "https://newsso.shu.edu.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
            "Referer": "https://newsso.shu.edu.cn/login/eyJ0aW1lc3RhbXAiOjE2MDU3NjcxNTMzMzg1MzE0MDIsInJlc3BvbnNlVHlwZSI6ImNvZGUiLCJjbGllbnRJZCI6IldVSFdmcm50bldZSFpmelE1UXZYVUNWeSIsInNjb3BlIjoiMSIsInJlZGlyZWN0VXJpIjoiaHR0cHM6Ly9zZWxmcmVwb3J0LnNodS5lZHUuY24vTG9naW5TU08uYXNweD9SZXR1cm5Vcmw9JTJmIiwic3RhdGUiOiIifQ==",
            "Cookie": "",
        }
        data = {
            "username": str(username),
            "password": str(password),
            "login_submit": ""
        }
        data = bytes(parse.urlencode(data), encoding='utf8')
        head["Content-Length"] = str(len(data))
        req = request.Request(url=start_url, data=data, headers=head, method='POST')
        response = request.urlopen(req, timeout=2)
        head = {
            "Host": "newsso.shu.edu.cn",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
            "Referer": "https://newsso.shu.edu.cn/login/eyJ0aW1lc3RhbXAiOjE2MDU3NjcxNTMzMzg1MzE0MDIsInJlc3BvbnNlVHlwZSI6ImNvZGUiLCJjbGllbnRJZCI6IldVSFdmcm50bldZSFpmelE1UXZYVUNWeSIsInNjb3BlIjoiMSIsInJlZGlyZWN0VXJpIjoiaHR0cHM6Ly9zZWxmcmVwb3J0LnNodS5lZHUuY24vTG9naW5TU08uYXNweD9SZXR1cm5Vcmw9JTJmIiwic3RhdGUiOiIifQ==",
            "Cookie": "",
        }
        print(response.status, response.reason)
        self.listbox.insert(tkinter.END, str(response.status) + " " + response.reason)
        self.listbox.yview(tkinter.END)
        # print(response.read().decode())
        for key, values in response.getheaders():
            if key == 'set-cookie':
                head['Cookie'] = values
            if key == 'location':
                url2 = "https://" + head['Host'] + values
        req = request.Request(url=url2, headers=head, method='GET')
        response = request.urlopen(req, timeout=2)
        head = {
            "Host": "selfreport.shu.edu.cn",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
            "Referer": "https://newsso.shu.edu.cn/",
            # "Cookie": "",
        }
        print(response.status, response.reason)
        self.listbox.insert(tkinter.END, str(response.status) + " " + response.reason)
        self.listbox.yview(tkinter.END)
        for key, values in response.getheaders():
            if key == 'location':
                url3 = values
        req = request.Request(url=url3, headers=head, method='GET')
        response = request.urlopen(req, timeout=2)
        head = {
            "Host": "selfreport.shu.edu.cn",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
            "Referer": "https://newsso.shu.edu.cn/",
            "Cookie": "",
        }
        print(response.status, response.reason)
        self.listbox.insert(tkinter.END, str(response.status) + " " + response.reason)
        self.listbox.yview(tkinter.END)
        for key, values in response.getheaders():
            if key == 'location':
                url3 = head['Host'] + values
            if key == 'Set-Cookie':
                head['Cookie'] = values
        url4 = "https://selfreport.shu.edu.cn/Default.aspx"
        req = request.Request(url=url4, headers=head, method='GET')
        response = request.urlopen(req, timeout=2)
        print(response.status, response.reason)
        self.listbox.insert(tkinter.END, str(response.status) + " " + response.reason)
        self.listbox.yview(tkinter.END)
        for key, values in response.getheaders():
            print(key + " " + values)
            self.listbox.insert(tkinter.END, key + " " + values)
            self.listbox.yview(tkinter.END)
        return head

    def starting(self, us, ps, ds, dt, listbox):
        self.username = us
        self.password = ps
        self.date_s = ds
        self.date_t = dt
        self.listbox = listbox
        self.thread = threading.Thread(target=self.start)
        self.thread.start()

    def getEveryDay(self, begin_date='2020-11-21', end_date='2019-11-31'):
        """指定开始时间和结束时间，获取中间的日期"""
        date_list = []
        begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        while begin_date <= end_date:
            date_str = begin_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            begin_date += timedelta(days=1)
        return date_list

    def start(self):
        class RedirectHandler(urllib.request.HTTPRedirectHandler):
            def http_error_302(self, req, fp, code, msg, headers):
                result = urllib.request.HTTPError(req.get_full_url(), code, msg, headers, fp)
                result.status = code
                return result

            http_error_301 = http_error_303 = http_error_307 = http_error_302

        opener = urllib.request.build_opener(RedirectHandler())
        urllib.request.install_opener(opener)
        f = 1
        while f == 1:
            try:
                f = 0
                head = self.login(self.username, self.password)
                print("下面开始填报：")
                self.listbox.insert(tkinter.END, "[info]: ")
                self.listbox.yview(tkinter.END)
                time.sleep(1)
                self.listbox.insert(tkinter.END, "log in successfully...")
                self.listbox.yview(tkinter.END)
                time.sleep(1)
                self.listbox.insert(tkinter.END, "start reporting...")
                self.listbox.yview(tkinter.END)
                time.sleep(1)
                self.listbox.insert(tkinter.END, "Please wait...")
                self.listbox.yview(tkinter.END)
                time.sleep(1)
                self.listbox.insert(tkinter.END, ".")
                self.listbox.yview(tkinter.END)
                time.sleep(1)
                self.listbox.insert(tkinter.END, ".")
                self.listbox.yview(tkinter.END)
                time.sleep(1)
                self.listbox.insert(tkinter.END, ".")
                self.listbox.yview(tkinter.END)
                time.sleep(1)
                # ds=datetime.strptime(self.date_s, '%Y-%m-%d')
                # dt=datetime.strptime(self.date_t, '%Y-%m-%d')
                datelist = self.getEveryDay(str(self.date_s), str(self.date_t))
                for item in datelist:
                    for k in [1, 2]:
                        if type(item) != datetime:
                            item = datetime.strptime(item, '%Y-%m-%d')
                        self.post(item.__getattribute__("year"), item.__getattribute__("month"),
                                  item.__getattribute__("day"), k, head)
                        time.sleep(0.5)
                messagebox.showinfo(parent=self.master, title='提示', message='         填报完毕         ')
            except NameError:
                print("密码错误,请重试...")
                self.listbox.insert(tkinter.END, "密码错误,请重试...")
                self.listbox.yview(tkinter.END)
            except urllib.error.URLError:
                print("网络限制，请更换网络或稍候再试...")
                self.listbox.insert(tkinter.END, "网络限制，请更换网络或稍候再试...")
                self.listbox.yview(tkinter.END)
            except:
                print("发生未知错误，请联系管理员:sowhata@vip.qq.com ")
                self.listbox.insert(tkinter.END, "发生未知错误，请联系管理员:sowhata@vip.qq.com ")
                self.listbox.yview(tkinter.END)


if __name__ == '__main__':
    root = tkinter.Tk()
    tool = report(root)
    root.mainloop()
