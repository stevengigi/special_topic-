import threading
import serial.tools.list_ports
import time


class SerialCtrl():
    def __init__(self):
        self.com_list = []
        self.sync_cnt = 200

    def getComList(self):
        ports = serial.tools.list_ports.comports()
        for p in ports:
            # 列表末尾添加新的对象 ， p.device為com port(也可用p.name)
            self.com_list.append(p.device)
        self.com_list.insert(0, "-")  # 在位置[0]插入"-"

    def SerialOpen(self, gui):
        try:  # 使用 try，測試內容是否正確
            self.ser.is_open  # 獲取串口的狀態，是否打開
        except:                      # 如果 try 的內容發生錯誤，就執行 except 裡的內容
            PORT = gui.clicked_com.get()
            BAUD = gui.clicked_bd.get()
            self.ser = serial.Serial()
            self.ser.baudrate = BAUD
            self.ser.port = PORT
            self.ser.timeout = 0.1  # 將超時設置為x秒（允許浮點數）當請求的字節數可用時立即返回，否則等到超時到期並返回在此之前收到的所有字節。
        try:  # 使用 try，測試內容是否正確
            if self.ser.is_open:  # Get the state of the serial port, whether it’s open.
                self.ser.status = True
            else:
                PORT = gui.clicked_com.get()
                BAUD = gui.clicked_bd.get()
                self.ser = serial.Serial()
                self.ser.baudrate = BAUD
                self.ser.port = PORT
                self.ser.timeout = 0.1
                self.ser.open()  # 打開端口
                self.ser.status = True
        except:                      # 如果 try 的內容發生錯誤，就執行 except 裡的內容
            self.ser.status = False

    def SerialClose(self):
        try:
            # self.ser.is_open
            self.ser.close()
            self.ser.status = False
        except:
            self.ser.status = False

    def SerialSync(self, gui):
        self.threading = True
        cnt = 0
        while self.threading:
            try:
                print("SerialSync Start")
                self.ser.write(gui.data.sync.encode())  # self.sync="#?#\n"
                gui.conn.sync_status["text"] = "..Sync.."
                gui.conn.sync_status["fg"] = "orange"
                gui.data.RowMsg = self.ser.readline()
                print(f"{gui.data.RowMsg}")
                gui.data.DecodeMsg()
                # ! in  gui.data.msg[0]
                if gui.data.sync_ok in gui.data.msg[0]:
                    if int(gui.data.msg[1]) > 0:  # channel 數量
                        gui.conn.button_start_stream["state"] = "active"
                        gui.conn.button_add_chart["state"] = "active"
                        gui.conn.button_kill_chart["state"] = "active"
                        gui.conn.Save_check["state"] = "active"
                        gui.conn.sync_status["text"] = "Ok"
                        gui.conn.sync_status["fg"] = "green"
                        # channel 數量
                        gui.conn.ch_status["text"] = gui.data.msg[1]
                        gui.conn.ch_status["fg"] = "green"

                        gui.data.SynchChannel = int(gui.data.msg[1])

                        gui.data.GenChannels()
                        gui.data.buildYData()
                        gui.data.FileNameFunc()
                        print(gui.data.Channels, gui.data.YData)
                        self.threading = False
                        break
                if self.threading == False:
                    break
            except Exception as e:  # 如果不知道會發生的錯誤類型為何，可以使用它，除了你寫下要捕捉的錯誤類型，其餘發生的錯誤都會執行這裡
                print("error")
                print(e)
            cnt += 1
            if self.threading == False:
                break
            if cnt > self.sync_cnt:
                cnt = 0
                gui.conn.sync_status["text"] = "failed"
                gui.conn.sync_status["fg"] = "blue"
                time.sleep(0.5)

    def DataStream(self, gui):
        self.threading = True
        cnt = 0
        while self.threading:
            try:
                print("Try DataStream Start")
                self.ser.write(gui.data.StartStream.encode())
                # self.StartStream="#A#\n"
                gui.data.RowMsg = self.ser.readline()
                gui.data.DecodeMsg()


                gui.data.StreamDataCheck()
                if gui.data.StreamData:
                    # start the ref time
                    gui.data.SetRefTime()
                    break  # 跳出while
            except Exception as e:
                print(e)
        gui.UpdataChart()
        print("Updata_Chart")
        while self.threading:
            try:

                print("DataStream Start")
                # print(gui.sql.local_f)
                self.ser.write(gui.data.StartStream.encode())
                # 確保資料串流
                gui.data.RowMsg = self.ser.readline()
                gui.data.DecodeMsg()

                # gui.sql.local_f=gui.data.local
                # gui.sql.frequency=gui.data.test_f

                gui.data.StreamDataCheck()
                if gui.data.StreamData:
                    gui.data.UpdataXdata()
                    gui.data.UpdataYdata()

                    # Ysample = [
                    #     Ysam for Ysam in gui.data.YData[len(gui.data.YData)-1]]
                    # Ysample = [Ysam[len(gui.data.XData)-1]
                    #            for Ysam in gui.data.YData[len(gui.data.YData)-1]]
                    # print(f"Ysample:{Ysample}")
                    gui.data.AdjustData()
                    # print(
                    #     f"X:{len(gui.data.XData)},YData_new:{Ysample}")
                    print(f"len(estimate f):{len(gui.data.estimate_f)}")
                    print(f"estimate f:{gui.data.estimate_f}")
                    if gui.save and gui.start_stop_flag:
                        print("excel save start")
                        t1 = threading.Thread(target=gui.data.SavaData, args=(gui,), daemon=True)
                        t1.start()
                        print("SQL save start")
                        t2=threading.Thread(target=gui.sql.transmit,args=(gui,),daemon=True)
                        t2.start()
            except Exception as e:
                print(e)


if __name__ == "__main__":
    print("Serial compiler")
    SerialCtrl()
