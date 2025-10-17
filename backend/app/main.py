from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base 




from app.routes import ruta, citas 



app = FastAPI(
    title="Servicio de Autenticación y Citas",
    version="1.0.0",
)


origins = [
    "http://localhost",
    "http://localhost:3000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(ruta.router, prefix="/auth", tags=["Autenticación"])
app.include_router(citas.router, prefix="/citas", tags=["Citas Médicas"])


@app.get("/")
def read_root():
    """Ruta de salud simple para verificar que el servicio está activo."""
    return {"message": "¡Servicio de citas activo!"}


