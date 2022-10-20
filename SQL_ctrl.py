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
        self.tablename = 2202_00_00 #SQL table name
        # transmit data to SQL
        self.local_f=0
        self.frequency=0
        self.now=time.strftime('%Y-%m-%d %H:%M:%S')
        self.index=0
        # self.insert="INSERT INTO tt (time_t, frequency, local_frequency) VALUES (%s, %s, %s)" #insert to databse
        self.tablecreat=0

    def transmit(self,gui):

        self.local_f=gui.data.local
        self.frequency=gui.data.test_f
        now_time=time.strftime('%Y-%m-%d %H:%M:%S')

        self.tablename=time.strftime('%Y_%m_%d')
        if now_time != self.now:
            self.index=self.index+1
            self.now=now_time
            if(self.tablecreat != self.tablename ):
                print(f"tablecreat: {self.tablecreat} | self.tablename : {self.tablename }")
                self.creatable()
                self.index=1
            print("SQL save true")

            self.cursor.execute("INSERT INTO {} (id , time_t, frequency, local_frequency) values ('%s','%s','%s','%s')".format(self.tablename)%(self.index,self.now,self.frequency,self.local_f))
            # self.cursor.close()
            self.connection.commit()
            # self.connection.close()
        else:
            print("SQL save False")

    def creatable(self):
        print("ddddddddddddddddddddddddddddddddddddddddddd")
        self.tablecreat=self.tablename
        self.cursor.execute('''CREATE TABLE {}(
                        id int,
                        time_t TIMESTAMP NOT NULL ,
                        frequency  DECIMAL(6,4) default 00.0000,
                        local_frequency DECIMAL(6,4) default 00.0000,
                        PRIMARY KEY(id)
                        )'''.format(self.tablename))
        self.connection.commit()

if __name__=="__main__":
    print("SQL compiler")
    SQL_Master()



