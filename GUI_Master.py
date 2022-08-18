from functools import partial
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class RootGUI:
    def __init__(self, serial, data,sql):  # 設定物件本身(self)屬性
        self.root = Tk()
        self.root.title("Serial_Communication")
        self.root.geometry("400x150")  # 设置窗口的宽和高
        self.root.config(bg="white")  # 背景為白色
        # self.root.resizable(0, 0)

        self.serial = serial
        self.data = data
        self.sql=sql

        # 窗口管理器显式关闭窗口时发生的情况，執行close_window
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def close_window(self):
        print("Closing the window and exit")
        self.root.destroy()

        self.serial.SerialClose()
        self.serial.threading = False

        # self.sql.threading=False
        self.sql.cursor.close()
        # self.sql.connection.commit()
        self.sql.connection.close()


class ComGui():
    def __init__(self, root, serial, data,sql):
        # Frame
        self.root = root
        # serial
        self.serial = serial
        # data
        self.data = data
        #SQL
        self.sql=sql
        # LabelFrame就像一个容器，负责安排其他部件的位置
        self.frame = LabelFrame(root, text="Com Manger",
                                padx=5, pady=5, bg="white")
        # padX padY - 小部件從其佈局管理器請求的額外空間超出小部件在 x 和 y 方向顯示其內容所需的最小值。
        self.label_com = Label(self.frame, text="Available Port(s) ",
                               bg="white", width=15, anchor="w")  # anchor為物件在哪顯示(w為左邊)
        self.label_bd = Label(self.frame, text="Baue Rate ",
                              bg="white", width=15, anchor="center")  # anchor為物件在哪顯示(w為左邊)

        self.button_refresh = Button(
            self.frame, text="Refresh", width=8, command=self.com_refresh)
        self.button_connect = Button(
            self.frame, text="Connect", width=8, state="disable", command=self.serial_connect)
        self.padx = 10
        self.pady = 5
        self.ComOptionMenu()
        self.BaudOptionMenu()
        self.publish()

    def ComOptionMenu(self):
        #coms = ["-", "COM3", "COM4", "COM10"]
        self.serial.getComList()  # 執行getComList()，讓self.serial.com_list讀取com值
        self.clicked_com = StringVar()  # 宣告字串變數，要set印出的字
        self.clicked_com.set(self.serial.com_list[0])  # set字元為"-"印出
        # OptionMenu(master,variable,value,*values,**kwargs)
        self.drop_com = OptionMenu(
            self.frame, self.clicked_com, *self.serial.com_list, command=self.com_change)
        # config 拿來做物件的一些設定
        self.drop_com.config(width=15)

    def BaudOptionMenu(self):
        bd = ["-",
              "9600",
              "19200",
              "38400",
              "57600",
              "115200"
              ]
        self.clicked_bd = StringVar()
        self.clicked_bd.set(bd[0])
        self.drop_baud = OptionMenu(
            self.frame, self.clicked_bd, *bd, command=self.baud_change)
        self.drop_baud.config(width=15, anchor="center")

    def publish(self):
        # 按照網格的座標位置來安放控制元件
        # columnspan:有多少列小部件佔用 rowspan：有多少行小部件佔用
        # padx pady 元件邊框與容器之距離 (px, 預設=0)
        self.frame.grid(row=0, column=0, rowspan=3,
                        columnspan=3, padx=5, pady=5)
        self.label_com.grid(column=1, row=2)
        self.drop_com.grid(column=2, row=2, padx=self.padx, pady=self.pady)
        self.button_refresh.grid(column=3, row=2)

        self.label_bd.grid(column=1, row=3)
        self.drop_baud.grid(column=2, row=3, padx=self.padx, pady=self.pady)
        self.button_connect.grid(column=3, row=3)

    def com_change(self, widget):  # 下拉式選單(com port)更新確認
        # print("Change Com Port")
        # print(self.clicked_com.get())
        if "-" in self.clicked_com.get() or "-" in self.clicked_bd.get():
            self.button_connect["state"] = "disable"
        else:
            self.button_connect["state"] = "active"

    def baud_change(self, widget):  # 下拉式選單(baud rate)更新確認
        # print("Change Baud rate")
        #兩個都選了 後 connect button 才會active
        if "-" in self.clicked_com.get() or "-" in self.clicked_bd.get():
            self.button_connect["state"] = "disable"
        else:
            self.button_connect["state"] = "active"

    def com_refresh(self):  # button(com refresh)更新確認
        self.drop_com.destroy()  # 關閉 ComOptionMenu 視窗
        self.serial.com_list = []  # 要清空 list裡面的值
        self.ComOptionMenu()
        self.drop_com.grid(column=2, row=2, padx=self.padx, pady=self.pady)
        logic = []
        self.com_change(logic)  # 因為refresh connect button要被取消掉，所以在執行一次程式
        # print("Com Refresh")

    def serial_connect(self):  # button(connect)更新確認

        if self.button_connect["text"] in "Connect":
            # start connect
            self.serial.SerialOpen(self)
            if self.serial.ser.status:
                self.button_connect["text"] = "Disconnect"
                self.button_refresh["state"] = "disable"
                self.drop_baud["state"] = "disable"
                self.drop_com["state"] = "disable"
                InfoMsg = f"Successful to establish USART connection using {self.clicked_com.get()}"
                messagebox.showinfo("Successful", InfoMsg)
                # display the channel manager
                # print("self.conn is ok")
                self.conn = ConnGUI(self.root, self.serial, self.data, self.sql)
                # daemon thread a thread that runs in the background without worrying about shutting it down.
                # main跑完 (daemon=True) thread會自動關閉，不會等到thread跑完
                self.serial.t1 = threading.Thread(
                    target=self.serial.SerialSync, args=(self,), daemon=True)
                self.serial.t1.start()
            else:
                EroorMsg = f"Failure to establish USART connection using {self.clicked_com.get()}"
                messagebox.showerror("Error", EroorMsg)
        else:

            self.serial.threading = False
            self.conn.save = False
            # close the connection
            self.conn.ConnGUIClose()
            self.data.ClearData()
            # clsoe the serial  communication
            self.serial.SerialClose()
            InfoMsg = f"USART connection using {self.clicked_com.get()} is closed"
            messagebox.showwarning("InfoMsg", InfoMsg)
            self.button_connect["text"] = "Connect"
            self.button_refresh["state"] = "active"
            self.drop_baud["state"] = "active"
            self.drop_com["state"] = "active"

class ConnGUI():
    def __init__(self, root, serial, data, sql):
        # Frame
        self.root = root
        # serial
        self.serial = serial
        # data
        self.data = data
        # SQL
        self.sql = sql

        self.frame = LabelFrame(
            root, text="Connection Manger", padx=5, pady=5, bg="white", width=60)
        self.sync_label = Label(
            self.frame, text="Sync Status", bg="white", width=15, anchor="w")  # fg為text的字顏色
        self.sync_status = Label(
            self.frame, text="..Sync..", bg="white", fg="orange", width=5)

        self.ch_label = Label(self.frame, text="Active Channel",
                              bg="white", width=15, anchor="w")
        self.ch_status = Label(self.frame, text="...",
                               bg="white", fg="orange", width=5)

        self.button_start_stream = Button(
            self.frame, text="Start", state="disabled", width=5, command=self.start_stream)
        self.button_stop_stream = Button(
            self.frame, text="Stop", state="disabled", width=5, command=self.stop_stream)

        self.button_add_chart = Button(
            self.frame, text="+", state="disabled", width=5, bg="white", fg="#098577", command=self.new_chart)
        self.button_kill_chart = Button(
            self.frame, text="-", state="disabled", width=5, bg="white", fg="#CC252C", command=self.kill_chart)

        self.save = False
        self.sql.save=False
        self.start_stop_flag=False
        # 設定變數 Int 型別儲存目前內容
        self.SaveVar = IntVar()
        # 設定 variable屬性是可以綁定該 Checkbutton 的勾選狀態
        # 勾選的話會得到 1(onvalue)，沒勾選的話會得到 0(offvalue)
        self.Save_check = Checkbutton(self.frame, text="Save data", variable=self.SaveVar,
                                      onvalue=1, offvalue=0, bg="white", state="disabled", command=self.sava_data)
        # 垂直的線，做分開的動作
        self.separator = ttk.Separator(self.frame, orient='vertical')
        self.padx = 20
        self.pady = 15
        self.ConnGUIOpen()
        self.chartMaster = DisGUI(self.root, self.serial, self.data, self.sql)

    def ConnGUIOpen(self):
        self.root.geometry("800x150")
        self.frame.grid(row=0, column=4, rowspan=4,
                        columnspan=5, padx=5, pady=5)

        self.sync_label.grid(row=1, column=1)
        self.sync_status.grid(row=1, column=2)

        self.ch_label.grid(row=2, column=1)
        self.ch_status.grid(row=2, column=2, pady=self.pady)

        self.button_start_stream.grid(column=3, row=1, padx=self.padx)
        self.button_stop_stream.grid(column=3, row=2, padx=self.padx)

        self.button_add_chart.grid(column=4, row=1, padx=self.padx)
        self.button_kill_chart.grid(column=5, row=1, padx=self.padx)

        self.Save_check.grid(column=4, row=2, columnspan=2)

        self.separator.place(relx=0.58, rely=0, relwidth=0.001, relheight=1)

    def ConnGUIClose(self):
        # 把ConnGUI(frame)介面的裡面每一個物件去掉
        for widget in self.frame.winfo_children():
            # print(widget)
            widget.destroy()
        # 把ConnGUI(frame)去掉
        self.frame.destroy()
        self.root.geometry("400x150")

    def start_stream(self):
        self.start_stop_flag=True
        self.button_start_stream["state"] = "disabled"
        self.button_stop_stream["state"] = "active"
        self.serial.t1 = threading.Thread(
            target=self.serial.DataStream, args=(self,), daemon=True)
        self.serial.t1.start()

    def UpdataChart(self):
        try:
            # mydisplayChannels = []
            # VieVar 是一個GUI frame 裡有多少channel被新增近來
            for MyChannelOpt in range(len(self.chartMaster.ViewVar)):
                self.chartMaster.figs[MyChannelOpt][1].clear()
                for cnt, state in enumerate(self.chartMaster.ViewVar[MyChannelOpt]):
                    # print(f"state:{state}")
                    if state.get():
                        MyChannel = self.chartMaster.OptionVar[MyChannelOpt][cnt].get(
                        )
                        # mydisplayChannels.append(MyChannel)
                        ChannelIndex = self.data.ChannelNum[MyChannel]  # ch幾
                        FuncName = self.chartMaster.FunVar[MyChannelOpt][cnt].get(
                        )
                        self.chart = self.chartMaster.figs[MyChannelOpt][1]
                        self.color = self.data.ChannelColor[MyChannel]
                        self.y = self.data.YDisplay[len(self.data.YDisplay)-1]
                        self.x = np.linspace(
                            0, (1/self.data.sample_frequency)*self.data.messageLen, self.data.messageLen)
                        self.data.FunctionMaster[FuncName](self)
                        # print(f"self.y:{self.y}")
                self.chartMaster.figs[MyChannelOpt][1].grid(
                    color='b', linestyle='-', linewidth=0.2)
                self.chartMaster.figs[MyChannelOpt][0].canvas.draw()
        except Exception as e:
            print("UpdataChart Exception error")
            print(e)
        if self.serial.threading:
            self.root.after(40, self.UpdataChart)  # 給定時間後(40mS)呼叫函式

    def stop_stream(self):
        self.start_stop_flag=False
        self.button_start_stream["state"] = "active"
        self.button_stop_stream["state"] = "disabled"
        self.serial.threading = False
        self.data.a = 1

    def new_chart(self):
        self.chartMaster.AddChannelMaster()

    def kill_chart(self):
        print("kill_chart_command")

        try:
            if len(self.chartMaster.frames) > 0:
                # print("test2")
                totalFrame = len(self.chartMaster.frames)-1
                # 關閉LabelFrame('+','-') 的視窗
                self.chartMaster.frames[totalFrame].destroy()
                self.chartMaster.frames.pop()
                self.chartMaster.figs.pop()  # pop() 函数用于移除列表中的一个元素（默认最后一个元素），并且返回该元素的值。
                self.chartMaster.ControlFrames[totalFrame][0].destroy()
                self.chartMaster.ControlFrames.pop()

                self.chartMaster.ChannelFrame[totalFrame][0].destroy()
                self.chartMaster.ChannelFrame.pop()

                self.chartMaster.ViewVar.pop()
                self.chartMaster.OptionVar.pop()
                self.chartMaster.FunVar.pop()

                self.chartMaster.AdjustRootFrame()
        except:
            pass

    def sava_data(self):

        print("save change")
        if self.save :
            self.save = False
            self.sql.save=False
        else :
            self.save = True
            self.sql.save=True
        print(f"go in save change : {self.save}")
# Display GUI interface


class DisGUI():
    def __init__(self, root, serial, data,sql):
        self.root = root
        self.serial = serial
        self.data = data
        self.sql=sql
        self.frames = []  # 總共有多少個圖形介面
        self.framesCol = 0  # 每個圖形介面的 起始Col 和 Row
        self.framesRow = 4
        self.totalframes = 0  # totalframe=len(frames)-1 配合矩陣從0開始

        self.figs = []  # 增加圖形 類似示波器那種介面
        self.ControlFrames = []  # 增加每個圖形中其中一個介面的按鈕

        self.ChannelFrame = []  # 圖形介面裡面 其中一個介面 勾選的
        self.ViewVar = []
        self.OptionVar = []
        self.FunVar = []

    def AddChannelMaster(self):
        self.AddMasterFrame()
        self.AdjustRootFrame()
        self.AddGraph()
        self.AddChannelFrame()
        self.AddButtonFrame()

    def AddMasterFrame(self):
        self.frames.append(LabelFrame(
            self.root, text=f"Display Manger - {len(self.frames)+1}", padx=5, pady=5, bg="white"))  # 新增一個frame ,frame個數慛在list裡面(陣列)
        self.totalframes = len(self.frames)-1  # 一開始為(1-1) ，因為矩陣從0開始
        # print(f"self.frames{self.frames}")
        if self.totalframes % 2 == 0:
            self.framesCol = 0
        else:
            self.framesCol = 9

        self.framesRow = 4+4*int(self.totalframes/2)
        self.frames[self.totalframes].grid(
            padx=5, column=self.framesCol, row=self.framesRow, columnspan=9, sticky=NW)  # sticky=NW 物件插於左上方

    def AdjustRootFrame(self):
        self.totalframes = len(self.frames)-1
        if self.totalframes > 0:
            RootW = 800*2
        else:
            RootW = 800
        if self.totalframes+1 == 0:
            RootH = 150
        else:
            RootH = 150 + 430 * (int(self.totalframes/2)+1)

        self.root.geometry(f"{RootW}x{RootH}")

    def AddGraph(self):
        self.figs.append([])
        self.figs[self.totalframes].append(plt.Figure(
            figsize=(7, 5), dpi=80))  # 指定figsize的宽和高  dpi即每英寸多少个像素
        self.figs[self.totalframes].append(
            self.figs[self.totalframes][0].add_subplot(111))  # subplot(1,1,1) 秀出一張圖
        self.figs[self.totalframes].append(FigureCanvasTkAgg(
            self.figs[self.totalframes][0], master=self.frames[self.totalframes]))  # 繪製的圖形顯示到tkinter視窗上
        self.figs[self.totalframes][2].get_tk_widget().grid(
            column=1, row=0, rowspan=17, columnspan=4, sticky=N)  # 把matplotlib繪製圖形的導航工具欄顯示到tkinter視窗上

    def AddButtonFrame(self):
        buttonH = 2
        buttonW = 4
        self.ControlFrames.append([])
        # ControlFrames = [[LabelFrame1 button(+) button(-)] [LabelFrame2 button(+) button(-)]]
        self.ControlFrames[self.totalframes].append(
            LabelFrame(self.frames[self.totalframes], pady=5, bg="white"))
        self.ControlFrames[self.totalframes][0].grid(
            column=0, row=0, pady=4, padx=5, sticky=N)
        self.ControlFrames[self.totalframes].append(Button(
            self.ControlFrames[self.totalframes][0], text="+", bg="white", width=buttonW, height=buttonH, command=partial(self.AddChannel, self.ChannelFrame[self.totalframes])))
        self.ControlFrames[self.totalframes][1].grid(
            column=0, row=0, padx=5, pady=5)
        self.ControlFrames[self.totalframes].append(Button(
            self.ControlFrames[self.totalframes][0], text="-", bg="white", width=buttonW, height=buttonH, command=partial(self.DeleteChannel, self.ChannelFrame[self.totalframes])))
        self.ControlFrames[self.totalframes][2].grid(
            column=1, row=0, padx=5, pady=5)
        # functools.partial(func, *args, **keywords)
        # func: 需要被扩展的函数，返回的函数其实是一个类 func 的函数
        # *args: 需要被固定的位置参数
        # **kwargs: 需要被固定的关键字参数

    def AddChannelFrame(self):

        self.ChannelFrame.append([])
        self.ViewVar.append([])
        self.OptionVar.append([])
        self.FunVar.append([])

        self.ChannelFrame[self.totalframes].append(LabelFrame(
            self.frames[self.totalframes], pady=5, bg="white"))
        self.ChannelFrame[self.totalframes].append(self.totalframes)
        # .ChannelFrame =[ [LabelFrame1,totalframes(0)] , [LabelFrame2,totalframes(1)] ...]

        self.ChannelFrame[self.totalframes][0].grid(
            column=0, row=1, padx=5, pady=5, rowspan=16, sticky=N)
        self.AddChannel(self.ChannelFrame[self.totalframes])

    def AddChannel(self, ChannelFrame):
        # ChannelFrame = ChannelFrame[self.totalframes]
        if len(ChannelFrame[0].winfo_children()) < 8:
            NewFrameChannel = LabelFrame(ChannelFrame[0], bg="white")
            # print(
            #     f"Mumber of element into the Frame {len(ChannelFrame.winfo_children())}")

            NewFrameChannel.grid(column=0, row=len(
                ChannelFrame[0].winfo_children())-1)

            self.ViewVar[ChannelFrame[1]].append(IntVar())  # 每次近來增加一個
            print(f"self.ViewVar{self.ViewVar[ChannelFrame[1]]}")
            # ViewVar =[[ [ ].. ],[ [ ].. ],[ [ ].. ],[ [  ].. ] ] #總共增加幾個
            Ch_btn = Checkbutton(NewFrameChannel, variable=self.ViewVar[ChannelFrame[1]][len(self.ViewVar[ChannelFrame[1]])-1],
                                 onvalue=1, offvalue=0, bg="white")
            Ch_btn.grid(row=0, column=0, padx=1)
            self.ChannelOption(NewFrameChannel, ChannelFrame[1])
            self.ChannelFunc(NewFrameChannel, ChannelFrame[1])

    def ChannelOption(self, Frame, ChannelFrameNumber):
        self.OptionVar[ChannelFrameNumber].append(StringVar())
        # OptionVar = [ [ch1 ch1 ...] , [ch1 ..] .. [ ] ]
        bds = self.data.Channels
        self.OptionVar[ChannelFrameNumber][len(
            self.OptionVar[ChannelFrameNumber])-1].set(bds[0])
        # OptionMenu(container, variable, default=None, *values, **kwargs)
        # variable 是直接顯示在選項內
        drop_ch = OptionMenu(Frame, self.OptionVar[ChannelFrameNumber][len(
            self.OptionVar[ChannelFrameNumber])-1], *bds)
        drop_ch.config(width=5)
        drop_ch.grid(row=0, column=1, padx=1)

    def ChannelFunc(self, Frame, ChannelFrameNumber):
        # FunVar = [ [rowdata  rowdata ..] , [rowdata ..] .. [ ] ]
        self.FunVar[ChannelFrameNumber].append(StringVar())

        bds = [func for func in self.data.FunctionMaster.keys()]

        self.FunVar[ChannelFrameNumber][len(
            self.OptionVar[ChannelFrameNumber])-1].set(bds[0])
        drop_ch = OptionMenu(Frame, self.FunVar[ChannelFrameNumber][len(
            self.OptionVar[ChannelFrameNumber])-1], *bds)
        drop_ch.config(width=5)
        drop_ch.grid(row=0, column=2, padx=1)

    def DeleteChannel(self, ChannelFrame):
        if len(ChannelFrame[0].winfo_children()) > 1:
            ChannelFrame[0].winfo_children()[len(
                ChannelFrame[0].winfo_children())-1].destroy()
            self.ViewVar[ChannelFrame[1]].pop()
            self.OptionVar[ChannelFrame[1]].pop()
            self.FunVar[ChannelFrame[1]].pop()

        # 只有在單存執行 GUI_Master.py - if 才會成立，被引用時不會成立
if __name__ == "__main__":
    print("GUI compiler")
    RootGUI()
    ComGui()
    ConnGUI()
    DisGUI()
