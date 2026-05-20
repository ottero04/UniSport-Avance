from flask import Flask, jsonify, request
from flask_cors import CORS 
import requests
import logging
import time

# ─── Logs estructurados ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [gateway] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ─── Circuit Breaker - Estado global por servicio ─────────────────────────────
MAX_FALLOS    = 3       # Fallos consecutivos para abrir el circuito
TIEMPO_ESPERA = 30      # Segundos antes de intentar recuperación (half-open)

circuitos = {
    "api-usuarios": {
        "fallos":          0,
        "circuito_abierto": False,
        "tiempo_apertura": None,
        "url_base":        "http://api-usuarios:5002"
    },
    "api-transacciones": {
        "fallos":          0,
        "circuito_abierto": False,
        "tiempo_apertura": None,
        "url_base":        "http://api-transacciones:5001"
    },
    "api-modules": {
        "fallos":          0,
        "circuito_abierto": False,
        "tiempo_apertura": None,
        "url_base":        "http://api-modules:5003"
    },
}


def circuit_breaker_check(servicio: str) -> tuple[bool, str]:
    """
    Verifica el estado del circuit breaker para un servicio.
    Retorna (puede_llamar: bool, motivo: str)
    """
    cb = circuitos[servicio]
    if cb["circuito_abierto"]:
        elapsed = time.time() - cb["tiempo_apertura"]
        if elapsed > TIEMPO_ESPERA:
            logger.info(f"[CB] {servicio} - Half-open: intentando recuperación después de {elapsed:.1f}s")
            cb["circuito_abierto"] = False
            cb["fallos"] = 0
            cb["tiempo_apertura"] = None
            return True, "half-open"
        else:
            logger.warning(f"[CB] {servicio} - Circuito ABIERTO - bloqueando llamada ({elapsed:.1f}s / {TIEMPO_ESPERA}s)")
            return False, "abierto"
    return True, "cerrado"


def circuit_breaker_fallo(servicio: str):
    """Registra un fallo y abre el circuito si se supera el umbral."""
    cb = circuitos[servicio]
    cb["fallos"] += 1
    logger.warning(f"[CB] {servicio} - Fallo #{cb['fallos']}")
    if cb["fallos"] >= MAX_FALLOS:
        cb["circuito_abierto"] = True
        cb["tiempo_apertura"] = time.time()
        logger.error(f"[CB] {servicio} - Circuito ABIERTO tras {cb['fallos']} fallos consecutivos")


def circuit_breaker_exito(servicio: str):
    """Registra un éxito y cierra el circuito."""
    cb = circuitos[servicio]
    if cb["fallos"] > 0 or cb["circuito_abierto"]:
        logger.info(f"[CB] {servicio} - Recuperado. Circuito CERRADO")
    cb["fallos"] = 0
    cb["circuito_abierto"] = False
    cb["tiempo_apertura"] = None


def hacer_peticion(servicio: str, path: str, method: str = "GET", data=None, timeout: int = 5):
    """
    Realiza una petición HTTP con Circuit Breaker integrado.
    Retorna (response_json, status_code)
    """
    puede_llamar, estado = circuit_breaker_check(servicio)
    if not puede_llamar:
        return {"error": f"Servicio {servicio} temporalmente bloqueado (circuit breaker abierto)"}, 503

    url = circuitos[servicio]["url_base"] + path
    inicio = time.time()
    logger.info(f"[GATEWAY] {method} {url}")

    try:
        if method == "POST":
            resp = requests.post(url, json=data, timeout=timeout)
        else:
            resp = requests.get(url, timeout=timeout)

        fin = time.time()
        logger.info(f"[GATEWAY] {method} {url} -> {resp.status_code} ({fin - inicio:.4f}s)")
        circuit_breaker_exito(servicio)
        return resp.json(), resp.status_code

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        fin = time.time()
        logger.error(f"[GATEWAY] {method} {url} -> ERROR ({fin - inicio:.4f}s) - {type(e).__name__}")
        circuit_breaker_fallo(servicio)
        return {"error": "Servicio no disponible"}, 503


# ─── Endpoint de estado del sistema (monitoreo) ───────────────────────────────

@app.route("/estado")
def estado_sistema():
    """Muestra el estado de todos los circuitos y health de cada servicio."""
    logger.info("GET /estado - Consultando estado del sistema")
    inicio = time.time()
    estado = {}

    for nombre, cb in circuitos.items():
        # Determinar estado del circuito
        if cb["circuito_abierto"]:
            elapsed = time.time() - cb["tiempo_apertura"]
            estado_cb = "ABIERTO"
            segundos_restantes = max(0, TIEMPO_ESPERA - elapsed)
        else:
            estado_cb = "CERRADO"
            segundos_restantes = None

        # Intentar health check directo (sin pasar por el CB para monitoreo)
        try:
            health_resp = requests.get(
                cb["url_base"] + "/health", timeout=2
            )
            health_data = health_resp.json()
            health_ok = health_resp.status_code == 200
        except Exception:
            health_data = {"status": "sin respuesta"}
            health_ok = False

        estado[nombre] = {
            "circuit_breaker": estado_cb,
            "fallos_actuales": cb["fallos"],
            "max_fallos": MAX_FALLOS,
            "tiempo_espera_s": TIEMPO_ESPERA,