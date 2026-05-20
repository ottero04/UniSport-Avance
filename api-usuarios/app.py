from flask import Flask, jsonify, request
from flask_cors import CORS 
import mysql.connector


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
def info():
    return jsonify({
        "endpont": [
            "/usuarios",
            "/usuario/<int:usuario_id>",
            "/auth",
            "/registro",
        ]
    })


@app.route("/usuarios")
def get_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            nombre, 
            nickname, 
            correo, 
            telefono,
            saldo
        FROM usuarios 
    """)
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios


@app.route("/usuario/<int:usuario_id>")
def get_usuario(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT 
            nombre, 
            nickname, 
            correo, 
            telefono,
            saldo 
        FROM usuarios
        WHERE id = {usuario_id}"""
    )
    usuario = cursor.fetchall()
    conn.close()
    return usuario


@app.route("/auth", methods=["POST"])
def auth():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Se requiere datos JSON"}), 400
    
    nickname = data.get("nickname")
    password_hash = data.get("password_hash")
    
    if not nickname or not password_hash:
        return jsonify({"error": "Faltan campos: 'nickname' y 'password_hash' son requeridos"}), 400
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(f"""
        SELECT id, nombre, nickname, correo, telefono, saldo, password_hash
        FROM usuarios
        WHERE nickname = '{nickname}'
    """)
    
    usuario = cursor.fetchone()
    conn.close()
    
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    if usuario["password_hash"] != password_hash:
        return jsonify({"error": "Contraseña incorrecta"}), 401
    
    usuario.pop("password_hash", None) 

    return jsonify({
        "mensaje": "Autenticación exitosa",
        "usuario": usuario
    }), 200


@app.route("/registro", methods=["POST"])
def registro():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Se requiere datos JSON"}), 400
    
    nombre = data.get("nombre")
    nickname = data.get("nickname")
    correo = data.get("correo")
    telefono = data.get("telefono")
    password_hash = data.get("password_hash")
    identificacion = data.get("identificacion")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(f"""
        SELECT id, nombre, nickname, correo, telefono, saldo, password_hash
        FROM usuarios
        WHERE identificacion = '{identificacion}'
    """)
    usuario = cursor.fetchone()
    conn.close()

    
    if usuario:
        return jsonify({"error": "Usuario ya existe"}), 404

    if not all([nombre, nickname, correo, telefono, password_hash, identificacion]):
        return jsonify({"error": "Faltan campos: 'nombre', 'nickname', 'correo', identificacion, 'telefono' y 'password_hash' son requeridos"}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO usuarios (nombre, nickname, correo, telefono, password_hash, identificacion)
        VALUES ('{nombre}', '{nickname}', '{correo}', '{telefono}', '{password_hash}', '{identificacion}')
    """)
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)