from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

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

@app.route("/modules")
def get_modules():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, description, code, status, route
        FROM modules
        WHERE status = 1
    """)

    modules = cursor.fetchall()
    conn.close()

    return jsonify(modules)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)