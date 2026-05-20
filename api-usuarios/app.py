from flask import Flask, jsonify, request
from flask_cors import CORS 
import mysql.connector
import logging
import time

# Configuración de logs estructurados
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [api-usuarios] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

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
    logger.info("GET / - Info de endpoints solicitada")
    return jsonify({
        "endpont": [
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
    logger.info("GET /health - Verificando estado del servicio")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        fin = time.time()
        logger.info(f"GET /health - OK - DB conectada - {fin - inicio:.4f}s")
        return jsonify({
            "service": "api-usuarios",
            "status": "ok",
            "database": "conectada",
            "response_time": round(fin - inicio, 4)
        }), 200
    except Exception as e:
        fin = time.time()
        logger.error(f"GET /health - ERROR - DB desconectada - {str(e)}")
        return jsonify({
            "service": "api-usuarios",
            "status": "error",
            "database": "desconectada",
            "detalle": str(e),
            "response_time": round(fin - inicio, 4)
        }), 503


@app.route("/usuarios")
def get_usuarios():
    inicio = time.time()
    logger.info("GET /usuarios - Consultando todos los usuarios")
    try:
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
        fin = time.time()
        logger.info(f"GET /usuarios - OK - {len(usuarios)} usuarios - {fin - inicio:.4f}s")
        return jsonify(usuarios)
    except Exception as e:
        logger.error(f"GET /usuarios - ERROR - {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/usuario/<int:usuario_id>")
def get_usuario(usuario_id):
    inicio = time.time()
    logger.info(f"GET /usuario/{usuario_id} - Buscando usuario")
    try:
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
        fin = time.time()
        if usuario:
            logger.info(f"GET /usuario/{usuario_id} - OK - {fin - inicio:.4f}s")
        else:
            logger.warning(f"GET /usuario/{usuario_id} - No encontrado - {fin - inicio:.4f}s")
        return jsonify(usuario)
    except Exception as e:
        logger.error(f"GET /usuario/{usuario_id} - ERROR - {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/auth", methods=["POST"])
def auth():
    inicio = time.time()
    data = request.get_json()
    if not data:
        logger.warning("POST /auth - Datos JSON inválidos")
        return jsonify({"error": "Se requiere datos JSON"}), 400
    
    nickname = data.get("nickname")
    password_hash = data.get("password_hash")
    
    if not nickname or not password_hash:
        logger.warning(f"POST /auth - Campos faltantes para usuario: {nickname}")
        return jsonify({"error": "Faltan campos: 'nickname' y 'password_hash' son requeridos"}), 400
    
    logger.info(f"POST /auth - Intento de autenticación para: {nickname}")

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
        logger.warning(f"POST /auth - Usuario no encontrado: {nickname} - {fin - inicio:.4f}s")
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    if usuario["password_hash"] != password_hash:
        fin = time.time()
        logger.warning(f"POST /auth - Contraseña incorrecta para: {nickname} - {fin - inicio:.4f}s")
        return jsonify({"error": "Contraseña incorrecta"}), 401
    
    usuario.pop("password_hash", None) 
    fin = time.time()
    logger.info(f"POST /auth - Autenticación exitosa para: {nickname} - {fin - inicio:.4f}s")
    return jsonify({
        "mensaje": "Autenticación exitosa",
        "usuario": usuario
    }), 200


@app.route("/registro", methods=["POST"])
def registro():
    inicio = time.time()
    data = request.get_json()
    if not data:
        logger.warning("POST /registro - Datos JSON inválidos")
        return jsonify({"error": "Se requiere datos JSON"}), 400
    
    nombre = data.get("nombre")
    nickname = data.get("nickname")
    correo = data.get("correo")
    telefono = data.get("telefono")
    password_hash = data.get("password_hash")
    identificacion = data.get("identificacion")

    logger.info(f"POST /registro - Registrando usuario: {nickname}")

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
        logger.warning(f"POST /registro - Usuario ya existe: {identificacion}")
        return jsonify({"error": "Usuario ya existe"}), 404

    if not all([nombre, nickname, correo, telefono, password_hash, identificacion]):
        logger.warning("POST /registro - Campos faltantes")
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
    logger.info(f"POST /registro - Usuario registrado: {nickname} - {fin - inicio:.4f}s")
    return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
