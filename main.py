import functions_framework
import psycopg
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "visa.log")

def log(nivel: str, mensaje: str, extra: dict = {}):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entrada = {
        "timestamp": datetime.now().isoformat(),
        "servicio": "visa",
        "nivel": nivel,
        "mensaje": mensaje,
        **extra
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entrada) + "\n")

def get_connection():
    return psycopg.connect(DATABASE_URL)

def existe_usuario(numero_tarjeta: str, usuario: str) -> bool:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM clientes_visa
            WHERE numero_tarjeta = %s
              AND usuario = %s
            """,
            (numero_tarjeta, usuario)
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()

@functions_framework.http
def validar_visa(request):
    numero_tarjeta = request.args.get("numero_tarjeta")
    usuario = request.args.get("usuario")

    log("INFO", "Validation request received", {"usuario": usuario, "numero_tarjeta": numero_tarjeta})

    if not numero_tarjeta or not usuario:
        log("ERROR", "Missing parameters", {})
        return {"error": "Missing parameters: numero_tarjeta and usuario"}, 400

    if existe_usuario(numero_tarjeta, usuario):
        log("INFO", "Valid card", {"usuario": usuario})
        return {"valid": True, "message": "Valid Visa card"}, 200

    log("ERROR", "Card not found", {"usuario": usuario})
    return {"valid": False, "message": "Invalid or disabled Visa card"}, 200