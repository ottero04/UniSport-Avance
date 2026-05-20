from flask import Flask, jsonify, request
from flask_cors import CORS 
import requests
import time

app = Flask(__name__)
CORS(app)

TIMEOUT = 5

# ============================================================
# CIRCUIT BREAKER - Variables de estado por servicio
# ============================================================

MAX_FALLOS    = 3    # fallos seguidos para abrir el circuito
TIEMPO_ESPERA = 30   # segundos antes de intentar recuperar

fallos_usuarios      = 0
fallos_transacciones = 0
fallos_modules       = 0

circuito_usuarios      = False
circuito_transacciones = False
circuito_modules       = False

estado_usuarios      = "CLOSED"
estado_transacciones = "CLOSED"
estado_modules       = "CLOSED"

tiempo_apertura_usuarios      = 0
tiempo_apertura_transacciones = 0
tiempo_apertura_modules       = 0


# ============================================================
# CIRCUIT BREAKER - Función central de peticiones
#
# Recibe el nombre del servicio y aplica el CB antes de llamar.
# Si el circuito está abierto, bloquea la llamada de inmediato.
# Si está en HALF-OPEN, deja pasar una petición de prueba.
# ============================================================

def hacer_peticion(servicio, path, method="GET", data=None):
    global fallos_usuarios, fallos_transacciones, fallos_modules
    global circuito_usuarios, circuito_transacciones, circuito_modules
    global estado_usuarios, estado_transacciones, estado_modules
    global tiempo_apertura_usuarios, tiempo_apertura_transacciones, tiempo_apertura_modules

    # Seleccionamos las variables del servicio correspondiente
    if servicio == "api-usuarios":
        url_base       = "http://api-usuarios:5002"
        fallos         = fallos_usuarios
        circuito       = circuito_usuarios
        estado         = estado_usuarios
        tiempo_apertura = tiempo_apertura_usuarios
    elif servicio == "api-transacciones":
        url_base       = "http://api-transacciones:5001"
        fallos         = fallos_transacciones
        circuito       = circuito_transacciones
        estado         = estado_transacciones
        tiempo_apertura = tiempo_apertura_transacciones
    else:
        url_base       = "http://api-modules:5003"
        fallos         = fallos_modules
        circuito       = circuito_modules
        estado         = estado_modules
        tiempo_apertura = tiempo_apertura_modules

    # --- VERIFICAR EL CIRCUITO ---
    if circuito:
        tiempo_actual = time.time()
        if tiempo_actual - tiempo_apertura >= TIEMPO_ESPERA:
            # HALF-OPEN: dejamos pasar una petición de prueba
            print(f"[GATEWAY] {servicio} en estado HALF-OPEN → probando reconexión", flush=True)
            if servicio == "api-usuarios":
                estado_usuarios = "HALF-OPEN"
                circuito_usuarios = False
            elif servicio == "api-transacciones":
                estado_transacciones = "HALF-OPEN"
                circuito_transacciones = False
            else:
                estado_modules = "HALF-OPEN"
                circuito_modules = False
        else:
            restante = int(TIEMPO_ESPERA - (tiempo_actual - tiempo_apertura))
            print(f"[GATEWAY] Circuito {servicio} ABIERTO → bloqueando llamada. Reintento en {restante}s", flush=True)
            return {
            "error": f"{servicio} no disponible temporalmente",
            "estado_circuito": "ABIERTO",
            "mensaje": f"El circuito está abierto. Reintentará en {restante}s"
        }, 503

    # --- HACER LA PETICIÓN ---
    url = url_base + path
    inicio = time.time()
    print(f"[GATEWAY] Consultando {servicio} → {method} {url}", flush=True)

    try:
        if method == "POST":
            resp = requests.post(url, json=data, timeout=TIMEOUT)
        else:
            resp = requests.get(url, timeout=TIMEOUT)

        fin = time.time()
        print(f"[GATEWAY] {servicio} funcionando correctamente - {resp.status_code}", flush=True)
        print(f"[INFO] Tiempo {servicio} {method}: {fin - inicio:.4f}s", flush=True)

        # Éxito: cerramos el circuito
        if servicio == "api-usuarios":
            if estado_usuarios == "HALF-OPEN":
                print(f"[GATEWAY] {servicio} recuperado → cerrando circuito", flush=True)
            fallos_usuarios = 0
            circuito_usuarios = False
            estado_usuarios = "CLOSED"
        elif servicio == "api-transacciones":
            if estado_transacciones == "HALF-OPEN":
                print(f"[GATEWAY] {servicio} recuperado → cerrando circuito", flush=True)
            fallos_transacciones = 0
            circuito_transacciones = False
            estado_transacciones = "CLOSED"
        else:
            if estado_modules == "HALF-OPEN":
                print(f"[GATEWAY] {servicio} recuperado → cerrando circuito", flush=True)
            fallos_modules = 0
            circuito_modules = False
            estado_modules = "CLOSED"

        return resp.json(), resp.status_code

    except requests.exceptions.Timeout:
        fin = time.time()
        print(f"[ERROR] Timeout en {servicio} - {fin - inicio:.4f}s", flush=True)
        _registrar_fallo(servicio)
        return {"error": f"Timeout en {servicio}"}, 504

    except requests.exceptions.ConnectionError:
        fin = time.time()
        print(f"[ERROR] {servicio} no disponible - {fin - inicio:.4f}s", flush=True)
        _registrar_fallo(servicio)
        return {"error": f"{servicio} no disponible"}, 503


def _registrar_fallo(servicio):
    """Suma un fallo y abre el circuito si se llega al límite."""
    global fallos_usuarios, fallos_transacciones, fallos_modules
    global circuito_usuarios, circuito_transacciones, circuito_modules
    global estado_usuarios, estado_transacciones, estado_modules
    global tiempo_apertura_usuarios, tiempo_apertura_transacciones, tiempo_apertura_modules

    if servicio == "api-usuarios":
        fallos_usuarios += 1
        print(f"[ERROR] Fallo api-usuarios número {fallos_usuarios}", flush=True)
        if estado_usuarios == "HALF-OPEN":
            circuito_usuarios = True
            estado_usuarios = "OPEN"
            tiempo_apertura_usuarios = time.time()
            print(f"[GATEWAY] HALF-OPEN de api-usuarios falló → reabriendo circuito", flush=True)
        elif fallos_usuarios >= MAX_FALLOS:
            circuito_usuarios = True
            estado_usuarios = "OPEN"
            tiempo_apertura_usuarios = time.time()
            print(f"[GATEWAY] Circuito api-usuarios ABIERTO → servicio no disponible temporalmente", flush=True)

    elif servicio == "api-transacciones":
        fallos_transacciones += 1
        print(f"[ERROR] Fallo api-transacciones número {fallos_transacciones}", flush=True)
        if estado_transacciones == "HALF-OPEN":
            circuito_transacciones = True
            estado_transacciones = "OPEN"
            tiempo_apertura_transacciones = time.time()
            print(f"[GATEWAY] HALF-OPEN de api-transacciones falló → reabriendo circuito", flush=True)
        elif fallos_transacciones >= MAX_FALLOS:
            circuito_transacciones = True
            estado_transacciones = "OPEN"
            tiempo_apertura_transacciones = time.time()
            print(f"[GATEWAY] Circuito api-transacciones ABIERTO → servicio no disponible temporalmente", flush=True)

    else:
        fallos_modules += 1
        print(f"[ERROR] Fallo api-modules número {fallos_modules}", flush=True)
        if estado_modules == "HALF-OPEN":
            circuito_modules = True
            estado_modules = "OPEN"
            tiempo_apertura_modules = time.time()
            print(f"[GATEWAY] HALF-OPEN de api-modules falló → reabriendo circuito", flush=True)
        elif fallos_modules >= MAX_FALLOS:
            circuito_modules = True
            estado_modules = "OPEN"
            tiempo_apertura_modules = time.time()
            print(f"[GATEWAY] Circuito api-modules ABIERTO → servicio no disponible temporalmente", flush=True)


# ============================================================
# ENDPOINTS PRINCIPALES
# ============================================================

@app.route("/")
def home():
    return jsonify({
        "mensaje": "API Gateway UniSport funcionando",
        "servicios": [
            "api-usuarios",
            "api-transacciones",
            "api-modules"
        ]
    })


@app.route("/usuarios")
def get_usuarios():
    print("[GATEWAY] Consultando servicio api-usuarios", flush=True)
    data, status = hacer_peticion("api-usuarios", "/usuarios")
    return jsonify(data), status


@app.route("/usuario/<int:usuario_id>")
def get_usuario(usuario_id):
    print(f"[GATEWAY] Consultando usuario {usuario_id}", flush=True)
    data, status = hacer_peticion("api-usuarios", f"/usuario/{usuario_id}")
    return jsonify(data), status


@app.route("/transacciones")
def get_transacciones():
    print("[GATEWAY] Consultando servicio api-transacciones", flush=True)
    data, status = hacer_peticion("api-transacciones", "/transacciones")
    return jsonify(data), status


@app.route("/transaccion/<int:transaccion_id>")
def get_transaccion(transaccion_id):
    print(f"[GATEWAY] Consultando transaccion {transaccion_id}", flush=True)
    data, status = hacer_peticion("api-transacciones", f"/transaccion/{transaccion_id}")
    return jsonify(data), status


@app.route("/transacciones/usuario/<int:usuario_id>")
def get_transacciones_usuario(usuario_id):
    print(f"[GATEWAY] Consultando transacciones del usuario {usuario_id}", flush=True)
    data, status = hacer_peticion("api-transacciones", f"/transacciones/usuario/{usuario_id}")
    return jsonify(data), status


@app.route("/usuario/auth", methods=["POST"])
def auth():
    print("[GATEWAY] Autenticando usuario", flush=True)
    body = request.get_json()
    if body is None:
        return jsonify({"error": "Invalid JSON"}), 400
    data, status = hacer_peticion("api-usuarios", "/auth", method="POST", data=body)
    return jsonify(data), status


@app.route("/modules")
def modules():
    print("[GATEWAY] Consultando servicio api-modules", flush=True)
    data, status = hacer_peticion("api-modules", "/modules")
    return jsonify(data), status


@app.route("/registro", methods=["POST"])
def registro():
    print("[GATEWAY] Registrando usuario", flush=True)
    body = request.get_json()
    if body is None:
        return jsonify({"error": "Invalid JSON"}), 400
    data, status = hacer_peticion("api-usuarios", "/registro", method="POST", data=body)
    return jsonify(data), status


# ============================================================
# ENDPOINTS DE MONITOREO - Estado individual por servicio
# ============================================================

@app.route("/estado/usuarios")
def estado_usuarios_service():
    inicio = time.time()
    print("[MONITOREO] Consultando estado del servicio de usuarios", flush=True)
    try:
        response = requests.get("http://api-usuarios:5002/health", timeout=2)
        fin = time.time()
        print("[MONITOREO] Servicio de usuarios funcionando correctamente - 200", flush=True)
        print(f"[INFO] Tiempo estado usuarios: {fin - inicio:.4f}s", flush=True)
        return jsonify(response.json())
    except:
        print(f"[ERROR] Estado del servicio de usuarios → no disponible", flush=True)
        return jsonify({
            "status": "down",
            "circuit_breaker": estado_usuarios,
            "fallos": fallos_usuarios
        }), 503


@app.route("/estado/transacciones")
def estado_transacciones_service():
    
    inicio = time.time()
    print("[MONITOREO] Consultando estado del servicio de transacciones", flush=True)
    try:
        response = requests.get("http://api-transacciones:5001/health", timeout=2)
        fin = time.time()
        print("[MONITOREO] Servicio de transacciones funcionando correctamente - 200", flush=True)
        print(f"[INFO] Tiempo estado transacciones: {fin - inicio:.4f}s", flush=True)
        return jsonify(response.json())
    except:
        
        print(f"[ERROR] Estado del servicio de transacciones → no disponible - fallos: {fallos_transacciones}", flush=True)
        return jsonify({
            "status": "down",
            "fallos": fallos_transacciones
        }), 503


@app.route("/estado/modules")
def estado_modules_service():
    
    inicio = time.time()
    print("[MONITOREO] Consultando estado del servicio de modules", flush=True)
    try:
        response = requests.get("http://api-modules:5003/health", timeout=2)
        fin = time.time()
        print("[MONITOREO] Servicio de modules funcionando correctamente - 200", flush=True)
        print(f"[INFO] Tiempo estado modules: {fin - inicio:.4f}s", flush=True)
        return jsonify(response.json())
    except:
        
        print(f"[ERROR] Estado del servicio de modules → no disponible - fallos: {fallos_modules}", flush=True)
        return jsonify({
            "status": "down",
            "fallos": fallos_modules
        }), 503


@app.route("/monitoreo")
def monitoreo():
    print("[MONITOREO] Consultando estado general de los microservicios", flush=True)
    estados = {}
    try:
        estados["api-usuarios"] = requests.get("http://gateway:5000/estado/usuarios", timeout=2).json()
    except:
        estados["api-usuarios"] = {"status": "down"}
    try:
        estados["api-transacciones"] = requests.get("http://gateway:5000/estado/transacciones", timeout=2).json()
    except:
        estados["api-transacciones"] = {"status": "down"}
    try:
        estados["api-modules"] = requests.get("http://gateway:5000/estado/modules", timeout=2).json()
    except:
        estados["api-modules"] = {"status": "down"}

    print("[MONITOREO] Monitoreo general completado", flush=True)
    return jsonify(estados)


@app.route("/estado")
def estado_circuitos():
    return jsonify({
        "circuitos": {
            "api-usuarios": {
                "estado":               estado_usuarios,
                "fallos_acumulados":    fallos_usuarios,
                "max_fallos":           MAX_FALLOS,
                "tiempo_espera_segundos": TIEMPO_ESPERA
            },
            "api-transacciones": {
                "estado":               estado_transacciones,
                "fallos_acumulados":    fallos_transacciones,
                "max_fallos":           MAX_FALLOS,
                "tiempo_espera_segundos": TIEMPO_ESPERA
            },
            "api-modules": {
                "estado":               estado_modules,
                "fallos_acumulados":    fallos_modules,
                "max_fallos":           MAX_FALLOS,
                "tiempo_espera_segundos": TIEMPO_ESPERA
            }
        }
    })

@app.route("/resumen")
def resumen():
    print("[RESUMEN] Consultando información general del sistema", flush=True)
    datos = {}

    try:
        response = requests.get("http://api-usuarios:5002/usuarios", timeout=3)
        datos["Servicio de usuarios"] = response.json()
    except:
        datos["Servicio de usuarios"] = {"error": "api-usuarios no disponible"}

    try:
        response = requests.get("http://api-transacciones:5001/transacciones", timeout=3)
        datos["Servicio de transacciones"] = response.json()
    except:
        datos["Servicio de transacciones"] = {"error": "api-transacciones no disponible"}

    try:
        response = requests.get("http://api-modules:5003/modules", timeout=3)
        datos["Servicio de modules"] = response.json()
    except:
        datos["Servicio de modules"] = {"error": "api-modules no disponible"}

    print("[RESUMEN] Consulta general completada", flush=True)
    return jsonify(datos)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)