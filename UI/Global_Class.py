import sqlite3
from sqlite3.dbapi2 import Error

con = None
rs = None
def getdbconnection():
    con = sqlite3.connect("db.sqlite3") #Database Connction
    
    if con==None:                      #Check Connction is ok or not
         return con
    return con

def recordreader(con,sqlcmd):      #To read Data from database
    try:
        cur = con.cursor()
        cur.execute(sqlcmd)
        rs=cur.fetchall() 
        return rs    #getting all data
    except:
        print("Error While Reading Database")

def idreader(obj,sqlcmd):      #to get id like eid,student_id
    try:
        cur = obj.cursor()
        t=1                #if no data then t=1
        cur.execute(sqlcmd)
        rs=cur.fetchall()
        for i in rs:            
            t=i[0]+1         #if data available t increment
        else:
            pass
        print(t)        
        return t
    except Error:
        for i in Error:
            print(i)
        print("Error While Reading Database")

def recordmanip(obj,sqlcmd):       #to insert ,update,drop or manipulate data
    try:
        cur = obj.cursor()
        cur.execute(sqlcmd)       
        obj.commit() 
                       #saving data to table
    except:
        print("Error While Reading Database")
