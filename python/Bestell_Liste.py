#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
cgitb.enable()

print("Content-Type: text/plain;charset=utf-8")
print()

import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="pl$E5465",
    database="W-W-System"
)
 
# cursor object c
c = db.cursor()
 
# select statement for tblemployee which returns all columns
Bestell_Liste_select = """SELECT * FROM Bestell_Liste"""
 
# execute the select query to fetch all rows
c.execute(Bestell_Liste_select)
 
# fetch all the data returned by the database
Bestell_Liste_data = c.fetchall()
 
# print all the data returned by the database
for e in Bestell_Liste_data:
    print(e)
 
# finally closing the database connection
db.close()
