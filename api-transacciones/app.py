from flask import Flask, jsonify
import mysql.connector


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
    return jsonify({
        "endpont": [
            "/transacciones",
            "/transaccion/<int:transaccion_id>",
            "/transacciones/usuario/<int:usuario_id>",
        ]
    })


@app.route("/transacciones")
def get_transacciones():
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
    return transacciones


@app.route("/transaccion/<int:transaccion_id>")
def get_transaccion(transaccion_id):
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
    return transaccion


@app.route("/transacciones/usuario/<int:usuario_id>")
def get_transacciones_usuario(usuario_id):
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
    return transaccion




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)