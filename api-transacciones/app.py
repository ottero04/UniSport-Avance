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
        logger.info(f"GET /health - OK - DB conectada - {fin - inicio:.4f}s")
        return jsonify({
            "service": "api-transacciones",
            "status": "ok",
            "database": "conectada",
            "response_time": round(fin - inicio, 4)
        }), 200
    except Exception as e:
        fin = time.time()
        logger.error(f"GET /health - ERROR - DB desconectada - {str(e)}")
        return jsonify({
            "service": "api-transacciones",
            "status": "error",
            "database": "desconectada",
            "detalle": str(e),
            "response_time": round(fin - inicio, 4)
        }), 503


@app.route("/transacciones")
def get_transacciones():
    inicio = time.time()
    logger.info("GET /transacciones - Consultando todas las transacciones")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                id_usuario, 
                monto, 
                tipo, 
                descripcion 
            FROM transacciones 
        """)
        transacciones = cursor.fetchall()
        conn.close()
        fin = time.time()
        logger.info(f"GET /transacciones - OK - {len(transacciones)} registros - {fin - inicio:.4f}s")
        return jsonify(transacciones)
    except Exception as e:
        logger.error(f"GET /transacciones - ERROR - {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/transaccion/<int:transaccion_id>")
def get_transaccion(transaccion_id):
    inicio = time.time()
    logger.info(f"GET /transaccion/{transaccion_id} - Buscando transacción")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                id_usuario, 
                monto, 
                tipo, 
                descripcion 
            FROM transacciones 
            WHERE id = {transaccion_id}"""
        )
        transaccion = cursor.fetchall()
        conn.close()
        fin = time.time()
        if transaccion:
            logger.info(f"GET /transaccion/{transaccion_id} - OK - {fin - inicio:.4f}s")
        else:
            logger.warning(f"GET /transaccion/{transaccion_id} - No encontrada - {fin - inicio:.4f}s")
        return jsonify(transaccion)
    except Exception as e:
        logger.error(f"GET /transaccion/{transaccion_id} - ERROR - {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/transacciones/usuario/<int:usuario_id>")
def get_transacciones_usuario(usuario_id):
    inicio = time.time()
    logger.info(f"GET /transacciones/usuario/{usuario_id} - Consultando transacciones del usuario")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                monto, 
                tipo, 
                descripcion 
            FROM transacciones 
            WHERE id_usuario = {usuario_id}"""
        )
        transaccion = cursor.fetchall()
        conn.close()
        fin = time.time()
        logger.info(f"GET /transacciones/usuario/{usuario_id} - OK - {len(transaccion)} registros - {fin - inicio:.4f}s")
        return jsonify(transaccion)
    except Exception as e:
        logger.error(f"GET /transacciones/usuario/{usuario_id} - ERROR - {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)