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
