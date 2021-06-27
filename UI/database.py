from django.db import connection
import sqlite3
from sqlite3 import Error
def Hello():
    conn = None
    try:
        conn = sqlite3.connect("users")
        if conn:
            print(1)
    except Error as e:
        print(e)

    return conn