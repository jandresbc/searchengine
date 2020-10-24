#!/usr/bin/env python
# coding: utf-8

import pymysql
import pandas as pd

class conectMysql:
    
    host = "laika-prod.c401c5lcer4y.us-east-2.rds.amazonaws.com"
    port = "3306"
    user = "automatizacion"
    passwd = "iwyfsj3935$"
    database = "laika"
    
    def con(self):
        db = pymysql.connect(self.host,self.user,self.passwd,self.database)
        return db
    
    def query(self, db, sql):
        cadena = sql.find("select")
        cursor = db.cursor()
        
        if cadena >= 0:
            cursor.execute(sql)
            data = cursor.fetchall()
            description = cursor.description
            cursor.close()
            return self.convertDataframe(description,data)
        else:
            data = cursor.execute(sql)
            db.commit()
            cursor.close()
            return data
    
    def convertDataframe(self, description, data):
        lrows = []
        for row in data:
            lrows.append(list(row))
        colnames = tuple([desc[0] for desc in description])
        dataframe = pd.DataFrame(lrows, columns=colnames)
        return dataframe
