from flask import Flask, jsonify, request
from flask_cors import CORS 
import mysql.connector
import time

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
    print("[USUARIOS] Servicio activo", flush=True)
    return jsonify({
        "mensaje": "Servicio de usuarios funcionando correctamente",
        "endpoints": [
            "/usuarios",
            "/usuario/<int:usuario_id>",
            "/auth",
            "/registro",
            "/health",
        ]
    })


@app.route("/health")
def health():
    inicio = time.time()
    print("[USUARIOS] Verificando estado del servicio de usuarios...", flush=True)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        fin = time.time()
        print("[USUARIOS] Servicio funcionando correctamente - 200", flush=True)
        print(f"[INFO] Tiempo de verificación: {fin - inicio:.4f}s", flush=True)
        return jsonify({
            "status": "ok",
            "service": "api-usuarios",
            "database": "conectada",
            "response_time": round(fin - inicio, 4)
        }), 200
    except Exception as e:
        fin = time.time()
        print(f"[ERROR] Base de datos no disponible - {str(e)}", flush=True)
        return jsonify({
            "status": "down",
            "service": "api-usuarios",
            "database": "desconectada",
            "detalle": str(e)
        }), 503


@app.route("/usuarios")
def get_usuarios():
    inicio = time.time()
    print("[USUARIOS] Consultando usuarios", flush=True)
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
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
        fin = time.time()
        print(f"[USUARIOS] Servicio funcionando correctamente - 200", flush=True)
        print(f"[INFO] Tiempo de consulta de usuarios: {fin - inicio:.4f}s", flush=True)
        return jsonify({
            "mensaje": "Listado de usuarios",
            "usuarios": usuarios
        })
    except Exception as e:
        print(f"[ERROR] Error consultando usuarios - {str(e)}", flush=True)
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/usuario/<int:usuario_id>")
def get_usuario(usuario_id):
    inicio = time.time()
    print(f"[USUARIOS] Consultando usuario {usuario_id}", flush=True)
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
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
        usuario = cursor.fetchone()
        conn.close()
        fin = time.time()
        if usuario:
            print(f"[USUARIOS] Servicio funcionando correctamente - 200", flush=True)
            print(f"[INFO] Tiempo de consulta usuario {usuario_id}: {fin - inicio:.4f}s", flush=True)
            return jsonify(usuario)
        else:
            print(f"[USUARIOS] Usuario {usuario_id} no encontrado - 404", flush=True)
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        print(f"[ERROR] Error consultando usuario {usuario_id} - {str(e)}", flush=True)
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/auth", methods=["POST"])
def auth():
    inicio = time.time()
    data = request.get_json()
    if not data:
        print("[USUARIOS] Solicitud de autenticación inválida - datos JSON faltantes", flush=True)
        return jsonify({"error": "Se requiere datos JSON"}), 400

    nickname = data.get("nickname")
    password_hash = data.get("password_hash")

    if not nickname or not password_hash:
        print(f"[USUARIOS] Campos faltantes en autenticación", flush=True)
        return jsonify({"error": "Faltan campos: 'nickname' y 'password_hash' son requeridos"}), 400

    print(f"[USUARIOS] Autenticando usuario: {nickname}", flush=True)

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
        fin = time.time()
        print(f"[USUARIOS] Usuario no encontrado: {nickname} - 404", flush=True)
        return jsonify({"error": "Usuario no encontrado"}), 404

    if usuario["password_hash"] != password_hash:
        fin = time.time()
        print(f"[USUARIOS] Contraseña incorrecta para: {nickname} - 401", flush=True)
        return jsonify({"error": "Contraseña incorrecta"}), 401

    usuario.pop("password_hash", None)
    fin = time.time()
    print(f"[USUARIOS] Autenticación exitosa para: {nickname} - 200", flush=True)
    print(f"[INFO] Tiempo de autenticación: {fin - inicio:.4f}s", flush=True)
    return jsonify({
        "mensaje": "Autenticación exitosa",
        "usuario": usuario
    }), 200


@app.route("/registro", methods=["POST"])
def registro():
    inicio = time.time()
    data = request.get_json()
    if not data:
        print("[USUARIOS] Solicitud de registro inválida - datos JSON faltantes", flush=True)
        return jsonify({"error": "Se requiere datos JSON"}), 400

    nombre        = data.get("nombre")
    nickname      = data.get("nickname")
    correo        = data.get("correo")
    telefono      = data.get("telefono")
    password_hash = data.get("password_hash")
    identificacion = data.get("identificacion")

    print(f"[USUARIOS] Registrando usuario: {nickname}", flush=True)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT id FROM usuarios
        WHERE identificacion = '{identificacion}'
    """)
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        print(f"[USUARIOS] Usuario ya existe: {identificacion} - 409", flush=True)
        return jsonify({"error": "Usuario ya existe"}), 409

    if not all([nombre, nickname, correo, telefono, password_hash, identificacion]):
        print("[USUARIOS] Campos faltantes en registro", flush=True)
        return jsonify({"error": "Faltan campos requeridos"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO usuarios (nombre, nickname, correo, telefono, password_hash, identificacion)
        VALUES ('{nombre}', '{nickname}', '{correo}', '{telefono}', '{password_hash}', '{identificacion}')
    """)
    conn.commit()
    conn.close()
    fin = time.time()
    print(f"[USUARIOS] Usuario registrado correctamente: {nickname} - 201", flush=True)
    print(f"[INFO] Tiempo de registro: {fin - inicio:.4f}s", flush=True)
    return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)