#!/usr/bin/env python
# coding: utf-8

from conexion import conectMysql
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from modelos import modelos

class execute():
    
    def __init__(self):
        self.conn = conectMysql()
        self.db = self.conn.con()
        self.model = modelos()
    
    def exe(self,datauser,id_ciudad=None,retrain=False,enviroment="prod"):
        
        rt = self.data(id_ciudad)
        
        if retrain == True:
            self.model.retrain = True
        
        if len(rt) > 0:
            predicciones = self.executeModel(datauser,enviroment)
        else:
            predicciones = [{"error":True,"message":"No data returned","code":"406"}]
            
        return predicciones
    
    def data(self,id_ciudad):
        #Se lee todos los datos de productos almacenados en BD.
        if id_ciudad != None:
            consulta = "select r.id_producto, p.id_promocion, r.id_referencia, m.id_marca_producto, tp.id_tipo_producto, tp.tipo, m.marca, p.producto,r.referencia, r.precio, p.descripcion,p.caracteristicas,p.beneficios, concat('https://backend.laika.com.co/imgs_productos/',i.foto) as urlimagen from pro_productos p INNER JOIN pro_referencias r ON p.id_producto=r.id_referencia INNER JOIN pro_marcas m ON p.id_marca_producto = m.id_marca_producto INNER JOIN pro_tipos tp ON tp.id_tipo_producto = p.id_tipo_producto INNER JOIN pro_imagenes i ON p.id_producto = i.id_producto INNER JOIN pro_ciudades_productos cp ON cp.id_producto = p.id_producto where p.estado = 'activo' and tp.estado = 'activo' and r.estado = 'activo' and cp.id_ciudad = {}".format(id_ciudad)
        else:
            consulta = "select r.id_producto, p.id_promocion, r.id_referencia, m.id_marca_producto, tp.id_tipo_producto, tp.tipo, m.marca, p.producto,r.referencia, r.precio, p.descripcion,p.caracteristicas,p.beneficios, concat('https://backend.laika.com.co/imgs_productos/',i.foto) as urlimagen from pro_productos p INNER JOIN pro_referencias r ON p.id_producto=r.id_referencia INNER JOIN pro_marcas m ON p.id_marca_producto = m.id_marca_producto INNER JOIN pro_tipos tp ON tp.id_tipo_producto = p.id_tipo_producto INNER JOIN pro_imagenes i ON p.id_producto = i.id_producto where p.estado = 'activo' and tp.estado = 'activo' and r.estado = 'activo'"
        self.productos = self.conn.query(self.db,consulta)

        self.tipos = self.productos.drop_duplicates(subset="tipo")[["id_tipo_producto","tipo"]]
        self.tipos.tipo = self.tipos.tipo.apply(lambda x: x.lower())
        self.tipos.reset_index(inplace=True)
        self.marcas = self.productos.drop_duplicates(subset="marca")[["id_marca_producto","marca"]]
        self.marcas.marca = self.marcas.marca.apply(lambda x: x.lower())
        self.marcas.reset_index(inplace=True)

        self.productos["search"] = self.productos["marca"]+" "+self.productos["producto"] +" "+self.productos["referencia"]+" "+ self.productos["tipo"] +" "+ self.productos["descripcion"] +" "+ self.productos["caracteristicas"] +" "+ self.productos["beneficios"]
        
        return self.productos
    
    def executeModel(self,SearchClient,enviroment = "test"):
        clientquery = self.model.clientsaid(SearchClient)
        #Clasifica los datos escritos por el usuario, por marca, tipo y otros.
        userdata = self.classifierDataUser(clientquery)
        
        predMarcas = []
        if len(userdata["marcas"]) > 0:
            searchpredict = []
            #data
            products = self.productos["search"].values
            labels = self.productos['id_marca_producto'].values
            
            if enviroment == "test":
                data = self.model.train_test_split(products,labels)
                #data
                prod = data["train"]["X_train"]
                labels = data["train"]['y_train']

                #test
                X_test = data["test"]["X_test"]
                y_test = data["test"]["y_test"]
            elif enviroment == "prod":
                #data
                prod = products
                labels = labels
            
            #Se entrena el modelo
            self.model.classifier("tfid")
            self.model.fit("logistic",prod,labels)
            predMarcas = self.model.predict(userdata["marcas"])
            
            for p in predMarcas:
                datos = self.productos[self.productos["id_marca_producto"] == p][["id_producto","id_promocion","tipo","marca","producto","urlimagen"]].to_dict(orient="list")
                searchpredict.append(datos)
        
        predTipos = []
        if len(userdata["tipos"]) > 0:
            #data
            prod = self.productos["search"].values
            labels = self.productos['id_tipo_producto'].values
            
            #Arreglo que guarda las predicciones hechas por el modelo.
            searchpredict2 = []
            
            #Se entrena el modelo
            self.model.classifier("tfid")
            self.model.fit("logistic",prod,labels)
            predTipos = self.model.predict(userdata["tipos"])
            
            for p in predTipos:
                datos = self.productos[self.productos["id_tipo_producto"] == p][["tipo","producto"]].to_dict(orient="list")
                searchpredict2.append(datos)
        
        predOtros = []
        predult = []
        #Arreglo que guarda las predicciones hechas por el modelo.
        if len(userdata["otros"]) > 0:
            #data
            prod = self.productos["search"].values
            labels = self.productos['id_marca_producto'].values
            
            #Arreglo que guarda las predicciones hechas por el modelo.
            searchpredict3 = []
            
            #Se entrena el modelo
            self.model.classifier("tfid")
            self.model.fit("logistic",prod,labels)
            predult = self.model.predict(userdata["otros"])
            
            for p in range(10):
                datos = self.productos[self.productos["id_marca_producto"] == p][["id_producto","producto"]].to_dict(orient="list")
                predOtros.append(datos)
           
        if enviroment == "test":
            predictionScore = self.model.scoreModel(X_test,y_test)
            return {
                "prediction" : pred,
                "score" : predictionScore,
                "otros" : userdata
            }
        elif enviroment == "prod":
            return {
                "marcas" : predMarcas,
                "tipos" : predTipos,
                "otros" : predult
            }
    
    def classifierDataUser(self,userdata):
        PrediccionesDatos={}
        PrediccionesDatos["tipos"] = []
        PrediccionesDatos["marcas"] = []
        PrediccionesDatos["otros"] = []
        
        for x in userdata:
            ban = 0
            
            if ban == 0:
                for y in self.tipos.tipo:
                    if y in x:
                        if x not in PrediccionesDatos["tipos"]:
                            PrediccionesDatos["tipos"].append(x)
                            ban = 1
            if ban == 0:
                for z in self.marcas.marca:
                    if x in z:
                        if x not in PrediccionesDatos["marcas"]:
                            PrediccionesDatos["marcas"].append(x)
                            ban = 1
            if ban == 0:
                if x not in PrediccionesDatos["otros"]:
                    PrediccionesDatos["otros"].append(x)
        
        return PrediccionesDatos
    
    def showData(self,predictions):
        products = self.productos.copy()
        
        marcas = predictions["marcas"]
        tipos = predictions["tipos"]
        otros = predictions["otros"]
        
        response = {}
        dataframe = pd.DataFrame()
        data = pd.DataFrame()
        
        if len(marcas) > 0:
            for x in range(0,len(marcas)):
                if x+1 < len(marcas):
                    dataframe = products[products.id_marca_producto == marcas[x]]
                    data = dataframe.append(products[products.id_marca_producto == marcas[x+1]])
                else:
                    data = dataframe.append(products[products.id_marca_producto == marcas[x]])
                    
        if len(tipos) > 0:
            for x in range(0,len(tipos)):
                if x+1 < len(tipos):
                    if len(data) > 0:
                        data = data.append(products[products.id_tipo_producto == tipos[x+1]])
                    else:
                        dataframe = products[products.id_marca_producto == marcas[x]]
                        data = dataframe.append(products[products.id_tipo_producto == tipos[x+1]])
                else:
                    data = data.append(products[products.id_tipo_producto == tipos[x]])
                
        if len(otros) > 0:
            for x in range(0,len(otros)):
                if x+1 < len(otros):
                    if len(data) > 0:
                        data = data.append(products[products.id_marca_producto == otros[x+1]])
                    else:
                        dataframe = products[products.id_marca_producto == otros[x]]
                        data = dataframe.append(products[products.id_marca_producto == otros[x+1]])
                else:
                    data = data.append(products[products.id_marca_producto == otros[x]]) 
        
        return data
        
