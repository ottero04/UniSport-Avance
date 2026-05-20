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