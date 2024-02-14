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
c.callproc('Geliefert')
Geliefert_fetch = c.stored_results()
Geliefert = []
x = 0
for i in Geliefert_fetch:
    Geliefert.append(i.fetchall())
for e in Geliefert[x]:
    print(e)
    x = x + 1

db.close()
