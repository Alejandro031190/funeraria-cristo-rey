# database.py
import json
import os
from datetime import datetime
from shutil import copy2

DB_FILE = "contratos.json"
BACKUP_DIR = "backups"


def _crear_base_si_no_existe():
    if not os.path.exists(DB_FILE):
        data = {"contratos": [], "abonos": []}
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


def cargar_datos():
    _crear_base_si_no_existe()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_datos(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def generar_id(lista, campo="id"):
    if not lista:
        return 1
    return max(item.get(campo, 0) for item in lista) + 1


# -----------------------------
# CONTRATOS
# -----------------------------
def guardar_contrato(nombre, cedula, direccion, telefono, plan, mensualidad, fecha_inicio, afiliados, id_manual=None):
    data = cargar_datos()
    contratos = data["contratos"]

    if id_manual is not None:
        if any(c["id"] == id_manual for c in contratos):
            raise ValueError(f"El ID {id_manual} ya existe.")
        contrato_id = id_manual
    else:
        contrato_id = generar_id(contratos)

    contrato = {
        "id": contrato_id,
        "nombre": nombre,
        "cedula": cedula,
        "direccion": direccion,
        "telefono": telefono,
        "plan": plan,
        "mensualidad": float(mensualidad),
        "fecha_inicio": fecha_inicio,
        "estado": "Activo",
        "afiliados": afiliados  # lista de dicts {nombre, apellido, parentesco, telefono}
    }

    contratos.append(contrato)
    guardar_datos(data)
    backup_db()  # respaldo automático
    return contrato_id


def obtener_contratos(estado=None):
    data = cargar_datos()
    contratos = data["contratos"]
    if estado:
        return [c for c in contratos if c["estado"] == estado]
    return contratos


def obtener_contrato_por_id(contrato_id):
    contratos = cargar_datos()["contratos"]
    return next((c for c in contratos if c["id"] == contrato_id), None)


def buscar_contrato_por_cedula(cedula):
    contratos = cargar_datos()["contratos"]
    return [c for c in contratos if c["cedula"] == cedula]


def editar_contrato(contrato_id, nuevos_datos):
    data = cargar_datos()
    updated = False
    for c in data["contratos"]:
        if c["id"] == contrato_id:
            c.update(nuevos_datos)
            updated = True
            break
    if updated:
        guardar_datos(data)
        backup_db()
    else:
        raise ValueError("Contrato no encontrado")


def cambiar_estado(contrato_id, nuevo_estado):
    data = cargar_datos()
    for c in data["contratos"]:
        if c["id"] == contrato_id:
            c["estado"] = nuevo_estado
            guardar_datos(data)
            backup_db()
            return
    raise ValueError("Contrato no encontrado")


# -----------------------------
# ABONOS
# -----------------------------
def agregar_abono(contrato_id, monto, observacion=""):
    data = cargar_datos()
    abonos = data["abonos"]
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo = {
        "id": generar_id(abonos),
        "contrato_id": contrato_id,
        "fecha": fecha_actual,
        "monto": float(monto),
        "observacion": observacion
    }
    abonos.append(nuevo)
    guardar_datos(data)
    backup_db()
    return nuevo["id"]


def obtener_abonos(contrato_id=None, cedula=None):
    data = cargar_datos()
    abonos = data["abonos"]
    if contrato_id:
        return [a for a in abonos if a["contrato_id"] == contrato_id]
    if cedula:
        contratos = data["contratos"]
        contrato = next((c for c in contratos if c["cedula"] == cedula), None)
        if contrato:
            return [a for a in abonos if a["contrato_id"] == contrato["id"]]
        return []
    return abonos


# -----------------------------
# BACKUP
# -----------------------------
def backup_db():
    if not os.path.exists(DB_FILE):
        return None
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(BACKUP_DIR, f"backup_CristoRey_{fecha}.json")
    copy2(DB_FILE, destino)
    return os.path.abspath(destino)


# Initialization: ensure DB exists
_crear_base_si_no_existe()
