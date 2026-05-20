from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
import time

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


@app.route("/")
def info():
    print("[MODULES] Servicio activo", flush=True)
    return jsonify({
        "mensaje": "Servicio de modules funcionando correctamente",
        "endpoints": [
            "/modules",
            "/health",
        ]
    })


@app.route("/health")
def health():
    inicio = time.time()
    print("[MODULES] Verificando estado del servicio de modules...", flush=True)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        fin = time.time()
        print("[MODULES] Servicio funcionando correctamente - 200", flush=True)
        print(f"[INFO] Tiempo de verificación: {fin - inicio:.4f}s", flush=True)
        return jsonify({
            "status": "ok",
            "service": "api-modules",
            "database": "conectada",
            "response_time": round(fin - inicio, 4)
        }), 200
    except Exception as e:
        fin = time.time()
        print(f"[ERROR] Base de datos no disponible - {str(e)}", flush=True)
        return jsonify({
            "status": "down",
            "service": "api-modules",
            "database": "desconectada",
            "detalle": str(e)
        }), 503


@app.route("/modules")
def get_modules():
    inicio = time.time()
    print("[MODULES] Consultando módulos activos", flush=True)
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
        print("[MODULES] Servicio funcionando correctamente - 200", flush=True)
        print(f"[INFO] Tiempo de consulta de modules: {fin - inicio:.4f}s", flush=True)
        return jsonify({
            "mensaje": "Listado de modules activos",
            "modules": modules
        })
    except Exception as e:
        print(f"[ERROR] Error consultando modules - {str(e)}", flush=True)
        return jsonify({"error": "Error interno del servidor"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)