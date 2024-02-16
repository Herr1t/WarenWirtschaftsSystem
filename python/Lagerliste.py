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
Lagerliste_select = """SELECT * FROM Lagerliste"""
 
# execute the select query to fetch all rows
c.execute(Lagerliste_select)
 
# fetch all the data returned by the database
Lagerliste_data = c.fetchall()
 
# print all the data returned by the database
for e in Lagerliste_data:
    row = e.split(",")
    _ = 0
    for _ in row[_]:
        print(f"\t{row[_]}\t")
 
# finally closing the database connection
db.close()
