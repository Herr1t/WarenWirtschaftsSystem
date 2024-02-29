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
Header={"Inventarnummer":[], 
        "Klinik":[],
        "Typ":[],
        "Modell":[],
        "Spezifikation":[],
        "Investmittel":[],
        "Bestell_Nr.":[],
        "Ausgabe":[],
        "Ausgegeben":[]}
for e in Lagerliste_data:
    _ = 0
    for h in Header:
        Header[h].append(e[_])
        _ = _ + 1

for row in zip(*([key] + (value) for key, value in Header.items())):
    print(*row)
#header=['Inventarnummer','Klinik','Typ','Modell','Spezifikation','Investmittel','Bestell_Nr.','Ausgabe','Ausgegeben']
 
# finally closing the database connection
db.close()
