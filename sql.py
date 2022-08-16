import mysql.connector
import pandas
import datetime
import time
connection=mysql.connector.connect(host="localhost",
                                   port="3306",
                                   user="root",
                                   password="123456",
                                   database="test"
                                    )
cursor=[]
if(cursor):
    print("not empty")
cursor = connection.cursor() #開始使用
print(cursor)
# cursor.execute("CREATE DATABASE TEST")

cursor.execute("show databases")
record = cursor.fetchall()

for r in record:
    print(r)
sql ='''CREATE TABLE tt(
   time_t TIMESTAMP NOT NULL ,
   frequency  DECIMAL(6,4) default 00.0000,
   local_frequency DECIMAL(6,4) default 00.0000,
   PRIMARY KEY(time_t)
)'''
# create new table
# cursor.execute(sql)

#SQL  TIMESTAMP format
now=time.strftime('%Y-%m-%d %H:%M:%S')
print(type(now))
f=60.4516
print(str(f))
local_f=60.0000
print(str(local_f))

cursor.execute("INSERT INTO tt (time_t, frequency, local_frequency) VALUES (%s, %s, %s)",
               (now, str(f), str(local_f)))


# print(now)
cursor.close()
connection.commit()
connection.close()
