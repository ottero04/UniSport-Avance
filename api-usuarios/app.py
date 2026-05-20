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