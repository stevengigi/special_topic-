import time
import numpy as np
from datetime import datetime  # 提供用于处理日期和时间的类
import csv
from scipy import signal
import math
import mysql.connector

class DataMaster():
    def __init__(self):
        self.sync = "#?#"
        self.sync_ok = "!"
        self.StartStream = "#A#\n"
        self.StopStream = "#S#\n"
        self.SynchChannel = 0
        self.a = 1
        self.msg = []

        self.XData = []
        self.YData = []

        self.estimate_f = []
        self.deviation_f = []
        self.EstFt = []
        self.local_frequency=[]

        self.estimate_wave = []

        self.data_test = []

        self.FunctionMaster = {
            # key:value  ,so FunctionMaster.keys() to get key
            "ADCvalue": self.ADCvalue,
            "Frequency": self.Frequency,
            "Amplitude": self.Amplitude,
            "Estimate": self.Estimate,
            "Filter": self.Filter,
            "Deviation_F": self.deviation_F,
            "Local Frequency":self.local_F
        }
        self.DisplayTimeRange = 5

        self.ChannelNum = {
            'Ch0': 0,
            'Ch1': 1,
            'Ch2': 2,
            'Ch3': 3
        }
        self.ChannelColor = {
            'Ch0': 'blue',
            'Ch1': 'green',
            'Ch2': 'red',
            'Ch3': 'cyan'
        }
        self.connection=mysql.connector.connect(host="localhost",
                                   port="3306",
                                   user="root",
                                   password="123456",
                                   database="test"
                                    )
        self.cursor =[]
        # self.cursor = self.connection.cursor() #開始使用

    def FileNameFunc(self):
        now = datetime.now()
        self.filename = now.strftime("%Y%m%d%H%M%S")+".csv"  # 返回以可读字符串表示的当地时间

    def SavaData(self, gui):

        data = [elt for elt in self.IntMsg]
        if data == self.data_test:
            pass
        else:
            self.data_test = data
            # data.append()
            # data.insert(0, self.XData[len(self.XData)-1])
            time_list = ["Time:", datetime.now()]
            data_list = ["ADC_value", data]
            Sample_Frequency_list = [
                'Sample_Frequency:', self.sample_frequency]
            Estimate_f_list = ["Estimate_frequency",
                               self.estimate_f[len(self.estimate_f)-1]]
            deviation_F_list = ["Deviation_frequency",
                                self.deviation_f[len(self.deviation_f)-1]]
            if gui.save:
                # with語法會給被使用到的文件創建了一個上下文環境，且區塊結束後會自動關閉
                with open(self.filename, 'a', newline='') as f:
                    data_writer = csv.writer(f)
                    data_writer.writerow(time_list)
                    data_writer.writerow(data_list)
                    data_writer.writerow(Sample_Frequency_list)
                    data_writer.writerow(Estimate_f_list)
                    data_writer.writerow(deviation_F_list)

    def DecodeMsg(self):
        temp = self.RowMsg.decode('utf8')
        print(f"temp:{temp}")
        print("Data Decode")
        if len(temp) > 0:
            if "#" in temp:
                self.msg = temp.split("#")
                del self.msg[0]  # 空格刪掉
                print(self.msg)

                if self.msg[0] in "D":
                    print("Data in D coming in")
                    self.messageLen = 0
                    self.messageLenCheck = 0
                    del self.msg[0]  # 刪除開頭的char D:adcvalue
                    del self.msg[len(self.msg)-1]  # 刪掉最後的'\n'
                    # self.messageLen = int(self.msg[len(self.msg)-1])  # 數據的量有多少

                    #local frequency
                    self.local=(int(self.msg[len(self.msg)-1])/10000)
                    del(self.msg[len(self.msg)-1])

                    self.rotate= -1 * int(self.msg[len(self.msg)-1]) #rotete adc number
                    del(self.msg[len(self.msg)-1])

                    self.test_f = (int(self.msg[len(self.msg)-1])/10000)
                    self.test_deviation_f = self.test_f - 60
                    # self.estimate_f.append(
                    #     int(self.msg[len(self.msg)-1])/10000)   # 擷取估計頻率

                    # self.deviation_f.append(
                    #     self.estimate_f[len(self.estimate_f)-1]-60)

                    del self.msg[len(self.msg)-1]

                    self.sample_frequency = int(
                        self.msg[len(self.msg)-1])  # 擷取 取樣頻率
                    del self.msg[len(self.msg)-1]

                    self.messageLen = int(self.msg[len(self.msg)-1])  # 多少個數據
                    del self.msg[len(self.msg)-1]

                    # for item in self.msg:
                    #     self.messageLenCheck += 1
                    self.messageLenCheck =len(self.msg)
                    # print(
                    #     f"messageLenCheck:{self.messageLenCheck },messageLen:{self.messageLen}")

    def GenChannels(self):
        # ['Ch0', 'Ch1', 'Ch2', 'Ch '....'Chn']
        self.Channels = [f"Ch{ch}" for ch in range(self.SynchChannel)]

    def buildYData(self):
        for _ in range(self.SynchChannel):
            # self.YData.append([])  # append() 方法用于在列表末尾添加新的对象
            pass

    def ClearData(self):
        self.Msg = ""
        self.msg = []
        self.YData = []

    def IntMsgFunc(self):
        self.IntMsg = [int(msg) for msg in self.msg]  # 所有傳送過來的資料轉為int
        self.IntMsg= np.roll(self.IntMsg,self.rotate)

    def StreamDataCheck(self):
        self.StreamData = False
        print(f"messageLen:{self.messageLen} || messageLenCheck:{self.messageLenCheck}")
        if self.messageLen == self.messageLenCheck:
            self.StreamData = True
            if len(self.estimate_f) > 5:
                del self.estimate_f[0]
            self.estimate_f.append(self.test_f)   # 擷取估計頻率
            self.deviation_f.append(self.test_deviation_f)
            self.local_frequency.append(self.local)
            # 寫入txt檔案
            # if self.a == 1:
            #     path = 'adcvalue.txt'
            #     f = open(path, 'w')
            #     f.truncate(0)
            #     self.msgline = [adc for adc in self.msg]
            #     for txt in self.msg:
            #         f.writelines(txt)
            #         f.writelines('\n')
            #     f.close()
            #     self.a += 1
            self.IntMsgFunc()

    def SetRefTime(self):
        if len(self.XData) == 0:
            self.RefTime = time.perf_counter()  # time.perf_counter:测量短持续时间
        else:
            self.RefTime = time.perf_counter() - self.XData[len(self.XData)-1]

    # time
    def UpdataXdata(self):
        if len(self.XData) == 0:
            self.XData.append(0)  # 矩陣[0]為0
        else:
            self.XData.append(time.perf_counter() -
                              self.RefTime)  # XData [n]為第n+1次-n的時間過多久
    # data

    def UpdataYdata(self):
        self.YData.clear()
        self.YData.append(self.IntMsg)
        # for ChNumber in range(self.SynchChannel):
        #     self.YData.append(self.IntMsg)
        # YData=[ [first usart data],[second usart data],....[nth usart data] ]
        # 不斷的refresh adc value data
        # print(f"upYdata{self.YData}")

    def AdjustData(self):
        lenXdata = len(self.XData)
        if (self.XData[lenXdata-1] - self.XData[0]) > self.DisplayTimeRange:
            print("Data is too much!! So delete data")
            del self.XData[0]
            # del self.YData[0]
        if lenXdata > 1000:
            self.XData.clear()

        x = np.array(self.XData)
        self.XDisplay = np.linspace(x.min(), x.max(), len(x), endpoint=0)
        # Numpy.linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None, axis=0)
        # endpoint：True則包含stop；False則不包含stop
        self.YDisplay = np.array(self.YData)
        # print(f"YDisplay:{self.YDisplay}")

    def ADCvalue(self, gui):
        gui.chart.plot(gui.x, gui.y, color=gui.color,
                       dash_capstyle='projecting', linewidth=1, label='ADC_value')
        gui.chart.legend(loc='upper left')

    def Frequency(self, gui):
        self.EstFt = np.zeros(len(self.estimate_f))
        lenx=len(self.XData)
        lens=len(self.estimate_f)
        for i in range(len(self.estimate_f)):
            self.EstFt[i] = self.XData[lenx-lens+i]
        # print(self.XData)
        # print("!!!!!!")
        # print(f"frequency:{self.estimate_f}")
        # print(f":frequency:{self.EstFt}")
        # print("!!!!!!")
        gui.chart.plot(self.EstFt, self.estimate_f, color=gui.color,
                       dash_capstyle='projecting', linewidth=1, label=f"f:{self.estimate_f[len(self.estimate_f)-1]}Hz")
        gui.chart.set_ylim(55, 65)
        gui.chart.legend(loc='upper left')

    def deviation_F(self, gui):
        if len(self.deviation_f) > 100:
            self.deviation_f.clear()
            self.DevFt.clear()
        else:
            self.DevFt = np.linspace(
                0, len(self.deviation_f)-1, len(self.deviation_f))
        gui.chart.plot(self.DevFt, self.deviation_f, color=gui.color,
                       dash_capstyle='projecting', linewidth=1, label=f"f:{self.estimate_f[len(self.estimate_f)-1]}Hz")
        gui.chart.set_ylim(-5, 5)
        gui.chart.set_xlim(0, 100)
        gui.chart.legend(loc='upper left')

    def Amplitude(self, gui):
        gui.chart.plot(gui.x, (gui.y/4095)*3.3, color=gui.color,
                       dash_capstyle='projecting', linewidth=1, label='Input')
        gui.chart.legend(loc='upper left')
    # 打出相對應頻率的弦波
    def Estimate(self, gui):
        t = np.linspace(0,0.1,1000)
        x = np.sin(2*np.pi*self.estimate_f[len(self.estimate_f)-1]*t)
        gui.chart.plot(t, x, color=gui.color,
                       dash_capstyle='projecting', linewidth=1, label=f"Esitmate:{self.estimate_f[len(self.estimate_f)-1]}")
        gui.chart.set_ylim(-5, 5)
        gui.chart.legend(loc='upper left')

    def local_F(self,gui):
        if len(self.local_frequency) > 100:
            self.local_frequency.clear()
            self.local_t.clear()
        else:
            self.local_t = np.linspace(
                0, len(self.local_frequency)-1, len(self.local_frequency))
        gui.chart.plot(self.local_t, self.local_frequency, color=gui.color,
                       dash_capstyle='projecting', linewidth=1, label=f"f:{self.local_frequency[len(self.local_frequency)-1]}Hz")
        gui.chart.set_ylim(55, 65)
        gui.chart.set_xlim(0, 100)
        gui.chart.legend(loc='upper left')


    def Filter(self, gui):
        samplingFreq = self.sample_frequency
        wc = 2*np.pi*360  # cutoff frequency (rad/s)
        n = 4  # Filter order
        # Compute the Butterworth filter coefficents
        a = np.zeros(n+1)
        gamma = np.pi/(2.0*n)
        a[0] = 1  # first coef is always 1
        for k in range(0, n):
            rfac = np.cos(k*gamma)/np.sin((k+1)*gamma)
            a[k+1] = rfac*a[k]  # Other coefficients by recursion

        # Adjust the cutoff frequency
        c = np.zeros(n+1)
        for k in range(0, n+1):
            c[n-k] = a[k]/pow(wc, k)

        num = [1]      # transfer function numerator(分子) coefficients
        den = c        # transfer function denominator(分母) coefficients
        dt = 1.0/samplingFreq
        lowPass = signal.TransferFunction(num, den)  # Transfer function

        discreteLowPass = lowPass.to_discrete(dt, method='gbt', alpha=0.5)
        b = discreteLowPass.num
        a = -discreteLowPass.den
        # print(b, a)
        y = np.zeros(len(gui.x))
        for temp in range(len(self.IntMsg)-n):
            y[n+temp] = a[1]*y[n+temp-1]+a[2]*y[n+temp-2] + a[3]*y[n+temp-3]+a[4]*y[n+temp-4] + \
                b[0]*self.IntMsg[n+temp]+b[1]*self.IntMsg[n+temp-1]+b[2] * \
                self.IntMsg[n+temp-2]+b[3]*self.IntMsg[n+temp-3] + \
                b[4]*self.IntMsg[n+temp-4]
        gui.chart.plot(gui.x, y, color=gui.color,
                       dash_capstyle='projecting', linewidth=1, label='Digital_Filter')
        gui.chart.legend(loc='upper left')
        # print(y)
        # print(len(y))


