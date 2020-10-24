#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request
from flask import jsonify
from execute import execute

app = Flask(__name__)
app.debug = True
execute = execute()

@app.route("/", methods=["GET"])
def search():
    if request.method == 'GET':
        json = None
        usersearch = request.args.get("usersearch")
        idciudad = request.args.get("city")
        nro = request.args.get("nrows")
        response = execute.exe(usersearch,idciudad)
        if "marcas" in response:
            json = execute.showData(response)
            json.reset_index(inplace=True)
            return json[["id_producto","id_promocion","tipo","marca","producto","urlimagen"]].to_json(orient="records")
        else:
            return response[0]
    else:
        return "Method not supported"
