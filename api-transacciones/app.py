from flask import Flask, jsonify
import mysql.connector
import logging
import time

# Configuración de logs estructurados
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [api-transacciones] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


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
            "/transacciones",
            "/transaccion/<int:transaccion_id>",
            "/transacciones/usuario/<int:usuario_id>",
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