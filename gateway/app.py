from flask import Flask, jsonify, request
from flask_cors import CORS 
import mysql.connector
import requests


app = Flask(__name__)
CORS(app)

def get_connection():
    return mysql.connector.connect(
        host = "db",
        user = "admin",
        password = "admin",
        database = "db",
        port = "3306"
    )


# ============================================================
# CIRCUIT BREAKER - Variables de estado
#
# El problema actual: si api-usuarios o api-transacciones se caen,
# el gateway sigue intentando llamarlos una y otra vez.
# Eso satura el sistema y hace que todo responda lento.
#
# Solución: el Circuit Breaker actúa como un interruptor eléctrico.
# Cuando detecta muchos fallos seguidos, "abre" el circuito y
# deja de intentar llamar al servicio caído.
#
# Por ahora solo declaramos las variables que vamos a necesitar.
# ============================================================

# Número de fallos consecutivos que toleramos antes de abrir el circuito
MAX_FALLOS = 3

# Diccionario con el estado de cada microservicio
# fallos          → cuántos fallos consecutivos lleva
# circuito_abierto→ False = CERRADO (normal) | True = ABIERTO (bloqueado)
estado_servicios = {
    "api-usuarios": {
        "fallos": 0,
        "circuito_abierto": False
    },
    "api-transacciones": {
        "fallos": 0,
        "circuito_abierto": False
    },
    "api-modules": {
        "fallos": 0,
        "circuito_abierto": False
    }
}