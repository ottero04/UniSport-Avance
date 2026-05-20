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
# ============================================================

# Número de fallos consecutivos que toleramos antes de abrir el circuito
MAX_FALLOS = 3

# Estado de cada microservicio
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

# ============================================================
# CIRCUIT BREAKER - Funciones de control
#
# Tres funciones que trabajan juntas:
#   registrar_fallo()       → cuando el servicio NO responde
#   registrar_exito()       → cuando el servicio SÍ responde
#   circuito_esta_abierto() → consulta si debemos bloquear
#
# Lógica:
#   - Cada fallo suma 1 al contador del servicio
#   - Si llega a MAX_FALLOS → abre el circuito (bloquea)
#   - Cuando el servicio vuelve → resetea todo
# ============================================================

def registrar_fallo(servicio):
    """
    Se llama cuando una petición falla.
    Suma 1 al contador. Si llega a MAX_FALLOS, abre el circuito.
    """
    estado_servicios[servicio]["fallos"] += 1
    fallos_actuales = estado_servicios[servicio]["fallos"]

    print(f"[CB] {servicio} - fallo #{fallos_actuales}", flush=True)

    if fallos_actuales >= MAX_FALLOS:
        estado_servicios[servicio]["circuito_abierto"] = True
        print(f"[CB] {servicio} - CIRCUITO ABIERTO tras {fallos_actuales} fallos. "
              f"Bloqueando llamadas.", flush=True)


def registrar_exito(servicio):
    """
    Se llama cuando una petición tiene éxito.
    Resetea el contador y cierra el circuito si estaba abierto.
    """
    if estado_servicios[servicio]["fallos"] > 0:
        print(f"[CB] {servicio} - respondió bien. Reseteando contador.", flush=True)

    estado_servicios[servicio]["fallos"] = 0
    estado_servicios[servicio]["circuito_abierto"] = False


def circuito_esta_abierto(servicio):
    """
    Consulta si el circuito está abierto (bloqueado).
    Retorna True si hay que bloquear, False si puede llamar.
    """
    return estado_servicios[servicio]["circuito_abierto"]

@app.route("/")
def get_info():
    try:
            transacciones = requests.get("http://api-transacciones:5001", timeout= 5).json()
    except requests.exceptions.ConnectionError:
            print("Error de conexión con api-transacciones", flush=True)
            transacciones = {"error": "Servicio no disponible"}, 503
    except requests.exceptions.Timeout:
            print("Tiempo de espera agotado para api-transacciones", flush=True)
            transacciones = {"error": "Tiempo de espera agotado"}, 503
    try:
            usuarios = requests.get("http://api-usuarios:5002", timeout=5).json()

    except requests.exceptions.ConnectionError:
            print("Error de conexión con api-usuarios", flush=True)
            usuarios = {"error": "Servicio no disponible"}, 503
    except requests.exceptions.Timeout:
            print("Tiempo de espera agotado para api-usuarios", flush=True)
            usuarios = {"error": "Tiempo de espera agotado"}, 503

    return jsonify({
            "api-transacciones": transacciones,
            "api-usuarios": usuarios
        })


@app.route("/usuarios")
def get_usuarios():
    try:
        usuarios = requests.get("http://api-usuarios:5002/usuarios", timeout=5).json()
        return jsonify(usuarios)
    except requests.exceptions.ConnectionError:
        print("Error de conexión con api-usuarios", flush=True)
        return jsonify({"error": "Servicio no disponible"}, 503)
    except requests.exceptions.Timeout:
        print("Tiempo de espera agotado para api-usuarios", flush=True)
        return jsonify({"error": "Tiempo de espera agotado"}, 503)


@app.route("/usuario/<int:usuario_id>")
def get_usuario(usuario_id):
    try:
        usuarios = requests.get(f"http://api-usuarios:5002/usuario/{usuario_id}", timeout=5).json()
        return jsonify(usuarios)
    except requests.exceptions.ConnectionError:
        print("Error de conexión con api-usuarios", flush=True)
        return jsonify({"error": "Servicio no disponible"}, 503)
    except requests.exceptions.Timeout:
        print("Tiempo de espera agotado para api-usuarios", flush=True)
        return jsonify({"error": "Tiempo de espera agotado"}, 503)


@app.route("/transacciones")
def get_transacciones():
    try:
        usuarios = requests.get(f"http://api-transacciones:5001/transacciones", timeout=5).json()
        return jsonify(usuarios)
    except requests.exceptions.ConnectionError:
        print("Error de conexión con api-transacciones", flush=True)
        return jsonify({"error": "Servicio no disponible"}, 503)
    except requests.exceptions.Timeout:
        print("Tiempo de espera agotado para api-transacciones", flush=True)
        return jsonify({"error": "Tiempo de espera agotado"}, 503)


@app.route("/transaccion/<int:transaccion_id>")
def get_transaccion(transaccion_id):
    try:
        usuarios = requests.get(f"http://api-transacciones:5001/transaccion/{transaccion_id}", timeout=5).json()
        return jsonify(usuarios)
    except requests.exceptions.ConnectionError:
        print("Error de conexión con api-transacciones", flush=True)
        return jsonify({"error": "Servicio no disponible"}, 503)
    except requests.exceptions.Timeout:
        print("Tiempo de espera agotado para api-transacciones", flush=True)
        return jsonify({"error": "Tiempo de espera agotado"}, 503)


@app.route("/transacciones/usuario/<int:usuario_id>")
def get_transacciones_usuario(usuario_id):
    try:
        usuarios = requests.get(f"http://api-transacciones:5001/transacciones/usuario/{usuario_id}", timeout=5).json()
        return jsonify(usuarios)
    except requests.exceptions.ConnectionError:
        print("Error de conexión con api-transacciones", flush=True)
        return jsonify({"error": "Servicio no disponible"}, 503)
    except requests.exceptions.Timeout:
        print("Tiempo de espera agotado para api-transacciones", flush=True)
        return jsonify({"error": "Tiempo de espera agotado"}, 503)


@app.route("/usuario/auth", methods=["POST"])
def auth():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Invalid JSON"},400) 
        resp = requests.post("http://api-usuarios:5002/auth", json=data, timeout=5)
        return jsonify(resp.json())
    except requests.exceptions.ConnectionError:
        print("Error de conexión con api-usuarios", flush=True)
        return jsonify({"error": "Servicio no disponible"}, 503)
    except requests.exceptions.Timeout:
        print("Tiempo de espera agotado para api-usuarios", flush=True)
        return jsonify({"error": "Tiempo de espera agotado"}, 503)


@app.route("/modules")
def modules():
    resp = requests.get("http://api-modules:5003/modules")
    return jsonify(resp.json()), resp.status_code


@app.route("/registro", methods=["POST"])
def registro():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Invalid JSON"}), 400
        resp = requests.post("http://api-usuarios:5002/registro", json=data, timeout=5)
        return jsonify(resp.json())
    except requests.exceptions.ConnectionError:
        print("Error de conexión con api-usuarios", flush=True)
        return jsonify({"error":"Servicio no disponible"}, 503)
    except requests.exceptions.Timeout:
        print("Tiempo de espera agotado para api-usuarios", flush=True)
        return jsonify({"error": "Tiempo de espera agotado"}, 503)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
