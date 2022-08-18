from lib2to3.pgen2.token import EQUAL
import mysql.connector
import pandas
import datetime
import time

class SQL_Master():
    def __init__(self):
        # table ='''CREATE TABLE tt(time_t TIMESTAMP NOT NULL ,frequency  DECIMAL(6,4) default 00.0000,local_frequency DECIMAL(6,4) default 00.0000,PRIMARY KEY(time_t))'''
        self.connection=mysql.connector.connect(host="localhost",
                                        port="3306",
                                        user="root",
                                        password="123456",
                                        database="test"
                                            )
        self.cursor = self.connection.cursor() #開始使用

        # self.save=False

        # transmit data to SQL
        self.local_f=12.456
        self.frequency=50.123
        self.now=time.strftime('%Y-%m-%d %H:%M:%S')

        # self.insert="INSERT INTO tt (time_t, frequency, local_frequency) VALUES (%s, %s, %s)" #insert to databse

    def transmit(self,gui):
        print("go in transmit")
        self.local_f=gui.data.local
        self.frequency=gui.data.test_f
        now_time=time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"self.now : {self.now[-1]} | now_time:{now_time[-1]}")
        print(f"self.now : {self.now} | now_time:{now_time}")
        if now_time[-1] is not self.now[-1]:
            print("SQL save true")
            self.now=now_time
            self.cursor.execute("INSERT INTO tt (time_t, frequency, local_frequency) VALUES (%s, %s, %s)",(self.now, str(self.frequency), str(self.local_f)))
            # self.cursor.close()
            self.connection.commit()
            # self.connection.close()
        else:
            print("SQL save False")

if __name__=="__main__":
    print("SQL compiler")
    SQL_Master()



