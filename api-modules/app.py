from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
import logging
import time

# Configuración de logs estructurados
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [api-modules] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def get_connection():
    return mysql.connector.connect(
        host="db",
        user="admin",
        password="admin",
        database="db",
        port="3306"
    )

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
            "service": "api-modules",
            "status": "ok",
            "database": "conectada",
            "response_time": round(fin - inicio, 4)
        }), 200
    except Exception as e:
        fin = time.time()
        logger.error(f"GET /health - ERROR - DB desconectada - {str(e)}")
        return jsonify({
            "service": "api-modules",
            "status": "error",
            "database": "desconectada",
            "detalle": str(e),
            "response_time": round(fin - inicio, 4)
        }), 503

@app.route("/modules")
def get_modules():
    inicio = time.time()
    logger.info("GET /modules - Consultando módulos activos")
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, description, code, status, route
            FROM modules
            WHERE status = 1
        """)
        modules = cursor.fetchall()
        conn.close()
        fin = time.time()
        logger.info(f"GET /modules - OK - {len(modules)} módulos activos - {fin - inicio:.4f}s")
        return jsonify(modules)
    except Exception as e:
        logger.error(f"GET /modules - ERROR - {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)