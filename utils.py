import os
import shutil
from datetime import datetime

# === FORMATO DE NÚMEROS Y FECHAS ===
def formato_moneda(valor):
    """Devuelve el valor con formato de moneda."""
    try:
        return f"${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "$0.00"

def fecha_hoy():
    """Devuelve la fecha actual en formato dd/mm/yyyy."""
    return datetime.now().strftime("%d/%m/%Y")


# === CÁLCULOS DE ABONOS Y SALDOS ===
def calcular_nuevo_saldo(saldo_actual, abono):
    """Calcula el nuevo saldo después de un abono."""
    nuevo_saldo = saldo_actual - abono
    return max(nuevo_saldo, 0)  # Evita que el saldo sea negativo


# === RESPALDO DE BASE DE DATOS ===
def backup_db(db_path="cristo_rey.db", backup_folder="backups"):
    """Crea una copia de seguridad de la base de datos."""
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{fecha}.db"
    backup_path = os.path.join(backup_folder, backup_name)

    shutil.copy2(db_path, backup_path)
    return backup_path