from GUI_Master import RootGUI, ComGui
from Serial_Com_ctrl import SerialCtrl
from Data_Com_ctrl import DataMaster
from SQL_ctrl import SQL_Master
# Initiate the Root class that will manage the other classes

MySerial = SerialCtrl()
MyData = DataMaster()
MySQL = SQL_Master()
RootMaster = RootGUI(MySerial, MyData,MySQL)

# Initiate the Communication Master class that will manage all the other  GUI class
ComMaster = ComGui(RootMaster.root, MySerial, MyData, MySQL)
RootMaster.root.mainloop()  # mainloop() 除了監視事件外, 也是維持視窗持續存在之方法
