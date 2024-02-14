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

c = db.cursor()
c.callproc('Lagerliste_Default')
Lagerliste_fetch = c.stored_results()
Lagerliste_Default = []
x = 0
for i in Lagerliste_fetch:
    Lagerliste_Default.append(i.fetchall())
for e in Lagerliste_Default[x]:
    print(e)
    x = x + 1

db.close()
