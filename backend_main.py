from fastapi import FastAPI
from routers import contratos

app = FastAPI()

# Registrar el router de contratos
app.include_router(contratos.router)

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido al backend de Funeraria Cristo Rey"}