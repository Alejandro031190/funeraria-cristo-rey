from fastapi import APIRouter

router = APIRouter(
    prefix="/contratos",
    tags=["Contratos"]
)

@router.get("/")
def obtener_contratos():
    return {"mensaje": "Aquí iría la lista de contratos"}