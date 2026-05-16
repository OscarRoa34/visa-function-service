import functions_framework
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

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

    if not numero_tarjeta or not usuario:
        return {"error": "Missing parameters: numero_tarjeta and usuario"}, 400

    if existe_usuario(numero_tarjeta, usuario):
        return {"valid": True, "message": "Valid Visa card"}, 200

    return {"valid": False, "message": "Invalid or disabled Visa card"}, 200