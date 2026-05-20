from flask import Flask, jsonify
import mysql.connector
import time

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
    print("[TRANSACCIONES] Servicio activo", flush=True)
    return jsonify({
        "mensaje": "Servicio de transacciones funcionando correctamente",
        "endpoints": [
            "/transacciones",
            "/transaccion/<int:transaccion_id>",
            "/transacciones/usuario/<int:usuario_id>",
            "/health",
        ]
    })


@app.route("/health")
def health():
    inicio = time.time()
    print("[TRANSACCIONES] Verificando estado del servicio de transacciones...", flush=True)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        fin = time.time()
        print("[TRANSACCIONES] Servicio funcionando correctamente - 200", flush=True)
        print(f"[INFO] Tiempo de verificación: {fin - inicio:.4f}s", flush=True)
        return jsonify({
            "status": "ok",
            "service": "api-transacciones",
            "database": "conectada",
            "response_time": round(fin - inicio, 4)
        }), 200
    except Exception as e:
        fin = time.time()
        print(f"[ERROR] Base de datos no disponible - {str(e)}", flush=True)
        return jsonify({
            "status": "down",
            "service": "api-transacciones",
            "database": "desconectada",
            "detalle": str(e)
        }), 503


@app.route("/transacciones")
def get_transacciones():
    inicio = time.time()
    print("[TRANSACCIONES] Consultando transacciones", flush=True)
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
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
        print("[TRANSACCIONES] Servicio funcionando correctamente - 200", flush=True)
        print(f"[INFO] Tiempo de consulta de transacciones: {fin - inicio:.4f}s", flush=True)
        return jsonify({
            "mensaje": "Listado de transacciones",
            "transacciones": transacciones
        })
    except Exception as e:
        print(f"[ERROR] Error consultando transacciones - {str(e)}", flush=True)
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/transaccion/<int:transaccion_id>")
def get_transaccion(transaccion_id):
    inicio = time.time()
    print(f"[TRANSACCIONES] Consultando transaccion {transaccion_id}", flush=True)
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"""
            SELECT 
                id_usuario, 
                monto, 
                tipo, 
                descripcion 
            FROM transacciones 
            WHERE id = {transaccion_id}"""
        )
        transaccion = cursor.fetchone()
        conn.close()
        fin = time.time()
        if transaccion:
            print(f"[TRANSACCIONES] Servicio funcionando correctamente - 200", flush=True)
            print(f"[INFO] Tiempo de consulta transaccion {transaccion_id}: {fin - inicio:.4f}s", flush=True)
            return jsonify(transaccion)
        else:
            print(f"[TRANSACCIONES] Transaccion {transaccion_id} no encontrada - 404", flush=True)
            return jsonify({"error": "Transaccion no encontrada"}), 404
    except Exception as e:
        print(f"[ERROR] Error consultando transaccion {transaccion_id} - {str(e)}", flush=True)
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/transacciones/usuario/<int:usuario_id>")
def get_transacciones_usuario(usuario_id):
    inicio = time.time()
    print(f"[TRANSACCIONES] Consultando transacciones del usuario {usuario_id}", flush=True)
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"""
            SELECT 
                monto, 
                tipo, 
                descripcion 
            FROM transacciones 
            WHERE id_usuario = {usuario_id}"""
        )
        transacciones = cursor.fetchall()
        conn.close()
        fin = time.time()
        print(f"[TRANSACCIONES] Servicio funcionando correctamente - 200", flush=True)
        print(f"[INFO] Tiempo de consulta transacciones usuario {usuario_id}: {fin - inicio:.4f}s", flush=True)
        return jsonify({
            "mensaje": f"Transacciones del usuario {usuario_id}",
            "transacciones": transacciones
        })
    except Exception as e:
        print(f"[ERROR] Error consultando transacciones usuario {usuario_id} - {str(e)}", flush=True)
        return jsonify({"error": "Error interno del servidor"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)