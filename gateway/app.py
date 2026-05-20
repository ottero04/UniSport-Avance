from flask import Flask, jsonify, request
from flask_cors import CORS 
import mysql.connector
import requests
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

# ============================================================
# CIRCUIT BREAKER - Variables de estado
#
# El problema actual: si api-usuarios o api-transacciones se caen,
# el gateway sigue intentando llamarlos una y otra vez.
# Eso satura el sistema y hace que todo responda lento.
#
# Solución: el Circuit Breaker actúa como un interruptor eléctrico.
# Cuando detecta muchos fallos seguidos, "abre" el circuito y
# deja de intentar llamar al servicio caído.
# ============================================================

# Número de fallos consecutivos que toleramos antes de abrir el circuito
MAX_FALLOS = 3
TIEMPO_ESPERA = 30

# Estado de cada microservicio
# fallos          → cuántos fallos consecutivos lleva
# circuito_abierto→ False = CERRADO (normal) | True = ABIERTO (bloqueado)
estado_servicios = {
    "api-usuarios": {
        "fallos": 0,
        "circuito_abierto": False,
        "tiempo_apertura": None
    },
    "api-transacciones": {
        "fallos": 0,
        "circuito_abierto": False,
        "tiempo_apertura": None
    },
    "api-modules": {
        "fallos": 0,
        "circuito_abierto": False,
        "tiempo_apertura": None
    }
}

# ============================================================
# CIRCUIT BREAKER - Funciones de control
#
# Tres funciones que trabajan juntas:
#   registrar_fallo()       → cuando el servicio NO responde
#   registrar_exito()       → cuando el servicio SÍ responde
#   circuito_esta_abierto() → consulta si debemos bloquear
#
# Lógica:
#   - Cada fallo suma 1 al contador del servicio
#   - Si llega a MAX_FALLOS → abre el circuito (bloquea)
#   - Cuando el servicio vuelve → resetea todo
# ============================================================

def registrar_fallo(servicio):
    """
    Se llama cuando una petición falla.
    Suma 1 al contador. Si llega a MAX_FALLOS, abre el circuito
    y guarda el momento exacto en que se abrió.
    """
    estado_servicios[servicio]["fallos"] += 1
    fallos_actuales = estado_servicios[servicio]["fallos"]

    print(f"[CB] {servicio} - fallo #{fallos_actuales}", flush=True)

    if fallos_actuales >= MAX_FALLOS:
        estado_servicios[servicio]["circuito_abierto"] = True
        # Guardamos el momento en que se abrió para saber cuándo recuperar
        estado_servicios[servicio]["tiempo_apertura"]  = time.time()
        print(f"[CB] {servicio} - CIRCUITO ABIERTO. "
              f"Reintentará en {TIEMPO_ESPERA} segundos.", flush=True)


def registrar_exito(servicio):
    """
    Se llama cuando una petición tiene éxito.
    Resetea el contador, cierra el circuito y limpia el tiempo.
    """
    if estado_servicios[servicio]["fallos"] > 0:
        print(f"[CB] {servicio} - respondió bien. Circuito CERRADO.", flush=True)

    estado_servicios[servicio]["fallos"]           = 0
    estado_servicios[servicio]["circuito_abierto"] = False
    estado_servicios[servicio]["tiempo_apertura"]  = None


def circuito_esta_abierto(servicio):
    """
    Consulta si el circuito está abierto.
    Implementa 3 estados:

      CERRADO   → circuito_abierto = False → llamadas normales
      ABIERTO   → circuito_abierto = True, no ha pasado el tiempo → bloqueado
      HALF-OPEN → circuito_abierto = True, ya pasó el tiempo → dejamos pasar
                  una llamada de prueba para ver si el servicio volvió
    """
    cb = estado_servicios[servicio]

    # Estado CERRADO: todo normal
    if not cb["circuito_abierto"]:
        return False

    # Calculamos cuánto tiempo lleva abierto
    segundos_abierto = time.time() - cb["tiempo_apertura"]

    if segundos_abierto >= TIEMPO_ESPERA:
        # HALF-OPEN: ya esperamos suficiente, dejamos pasar una prueba
        print(f"[CB] {servicio} - HALF-OPEN: probando si se recuperó "
              f"({segundos_abierto:.0f}s abierto).", flush=True)
        cb["circuito_abierto"] = False
        return False

    # ABIERTO: todavía no cumple el tiempo, seguimos bloqueando
    restantes = TIEMPO_ESPERA - segundos_abierto
    print(f"[CB] {servicio} - ABIERTO, bloqueado. "
          f"Reintenta en {restantes:.0f}s.", flush=True)
    return True

# ============================================================
# CIRCUIT BREAKER - Función central de peticiones
#
# En vez de tener try/except repetido en cada endpoint,
# esta función centraliza todo el trabajo.
#
# Flujo:
#   1. Revisa si el circuito está abierto
#      → si está abierto: retorna error 503 inmediatamente
#        sin llamar al servicio, sin esperar ningún timeout
#      → si está cerrado: continúa
#   2. Intenta la petición HTTP
#      → si responde bien: llama registrar_exito() y retorna
#      → si falla:         llama registrar_fallo() y retorna 503
#
# Todos los endpoints usarán esta función en el próximo paso.
# ============================================================

def hacer_peticion(servicio, path, method="GET", data=None):
    """
    Hace una petición a un microservicio aplicando el Circuit Breaker.

    Parámetros:
      servicio → nombre del servicio (ej: "api-usuarios")
      path     → ruta dentro del servicio (ej: "/usuarios")
      method   → "GET" o "POST"
      data     → cuerpo JSON para POST (opcional)

    Retorna:
      (dict, int) → respuesta JSON y código HTTP
    """

    # --- PASO 1: revisar el circuito ---
    # Si está abierto, respondemos de una sin llamar al servicio
    if circuito_esta_abierto(servicio):
        print(f"[CB] {servicio} - circuito ABIERTO, petición bloqueada", flush=True)
        return {"error": f"Servicio {servicio} no disponible (circuit breaker abierto)"}, 503

    # --- PASO 2: construir la URL completa ---
    urls = {
        "api-usuarios":      "http://api-usuarios:5002",
        "api-transacciones": "http://api-transacciones:5001",
        "api-modules":       "http://api-modules:5003"
    }
    url = urls[servicio] + path

    # --- PASO 3: intentar la petición ---
    try:
        if method == "POST":
            respuesta = requests.post(url, json=data, timeout=5)
        else:
            respuesta = requests.get(url, timeout=5)

        # El servicio respondió bien
        registrar_exito(servicio)
        return respuesta.json(), respuesta.status_code

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # El servicio no respondió, registramos el fallo
        registrar_fallo(servicio)
        return {"error": "Servicio no disponible"}, 503

@app.route("/")
def get_info():
    data_tx, _ = hacer_peticion("api-transacciones", "/")
    data_us, _ = hacer_peticion("api-usuarios", "/")
    return jsonify({
        "api-transacciones": data_tx,
        "api-usuarios": data_us
    })


@app.route("/usuarios")
def get_usuarios():
    # Antes: try/except aquí directamente
    # Ahora: hacer_peticion() aplica el CB automáticamente
    data, status = hacer_peticion("api-usuarios", "/usuarios")
    return jsonify(data), status


@app.route("/usuario/<int:usuario_id>")
def get_usuario(usuario_id):
    data, status = hacer_peticion("api-usuarios", f"/usuario/{usuario_id}")
    return jsonify(data), status


@app.route("/transacciones")
def get_transacciones():
    data, status = hacer_peticion("api-transacciones", "/transacciones")
    return jsonify(data), status


@app.route("/transaccion/<int:transaccion_id>")
def get_transaccion(transaccion_id):
    data, status = hacer_peticion("api-transacciones", f"/transaccion/{transaccion_id}")
    return jsonify(data), status


@app.route("/transacciones/usuario/<int:usuario_id>")
def get_transacciones_usuario(usuario_id):
    data, status = hacer_peticion("api-transacciones", f"/transacciones/usuario/{usuario_id}")
    return jsonify(data), status


@app.route("/usuario/auth", methods=["POST"])
def auth():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
    resp, status = hacer_peticion("api-usuarios", "/auth", method="POST", data=data)
    return jsonify(resp), status


@app.route("/modules")
def modules():
    data, status = hacer_peticion("api-modules", "/modules")
    return jsonify(data), status


@app.route("/registro", methods=["POST"])
def registro():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
    resp, status = hacer_peticion("api-usuarios", "/registro", method="POST", data=data)
    return jsonify(resp), status

# ============================================================
# ENDPOINT DE MONITOREO - /estado
#
# Permite ver en el navegador el estado actual de todos
# los circuit breakers del sistema.
#
# Cómo usarlo: con Docker corriendo, abrir en el navegador
#   http://localhost:5000/estado
#
# Respuesta cuando todo está bien:
#   { "api-usuarios": { "estado": "CERRADO", "fallos": 0 } }
#
# Respuesta cuando un servicio está caído:
#   { "api-usuarios": { "estado": "ABIERTO", "recupera_en": "18s" } }
# ============================================================

@app.route("/estado")
def ver_estado():
    resultado = {}

    for nombre, cb in estado_servicios.items():

        if not cb["circuito_abierto"]:
            # Circuito cerrado: el servicio está respondiendo bien
            resultado[nombre] = {
                "estado":  "CERRADO",
                "fallos":  cb["fallos"],
                "mensaje": "El servicio está disponible"
            }
        else:
            # Circuito abierto: calculamos cuánto falta para recuperar
            segundos_abierto = time.time() - cb["tiempo_apertura"]
            restantes = max(0, TIEMPO_ESPERA - segundos_abierto)

            if restantes > 0:
                resultado[nombre] = {
                    "estado":      "ABIERTO",
                    "fallos":      cb["fallos"],
                    "recupera_en": f"{restantes:.0f} segundos",
                    "mensaje":     "Servicio bloqueado, esperando para reintentar"
                }
            else:
                resultado[nombre] = {
                    "estado":  "HALF-OPEN",
                    "fallos":  cb["fallos"],
                    "mensaje": "Probando si el servicio se recuperó"
                }

    return jsonify({
        "circuit_breakers": resultado,
        "configuracion": {
            "max_fallos":    MAX_FALLOS,
            "tiempo_espera": f"{TIEMPO_ESPERA} segundos"
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
