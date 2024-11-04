from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
from typing import List, Optional
import asyncpg
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solo estos orígenes
    allow_credentials=True,  # Permitir el uso de cookies de autenticación
    allow_methods=["*"],     # Permitir todos los métodos HTTP
    allow_headers=["*"],     # Permitir todos los headers
)

DATABASE_URL = "postgresql://old:old@localhost/ContactWebDB"  # Cambia esto según tu configuración



class SalaDeTrabajo(BaseModel):
    id: int
    nombre: str
    descripcion: str
    capacidad: int
    lider_proyecto: str

async def get_connection():
    return await asyncpg.connect(DATABASE_URL)

@app.post("/salas/", response_model=SalaDeTrabajo)
async def crear_sala(sala: SalaDeTrabajo):
    print("Datos recibidos:", sala)  # Log para ver los datos que llegan
    conn = await get_connection()
    query = "INSERT INTO salas_de_trabajo (nombre, descripcion, capacidad, lider_proyecto) VALUES ($1, $2, $3, $4) RETURNING id;"
    sala_id = await conn.fetchval(query, sala.nombre, sala.descripcion, sala.capacidad, sala.lider_proyecto)
    sala.id = sala_id
    await conn.close()
    return sala

@app.put("/salas/{sala_id}", response_model=SalaDeTrabajo)
async def actualizar_sala(sala_id: int, sala: SalaDeTrabajo):
    conn = await get_connection()
    query = """
    UPDATE salas_de_trabajo
    SET nombre = $1, descripcion = $2, capacidad = $3, lider_proyecto = $4
    WHERE id = $5;
    """
    result = await conn.execute(query, sala.nombre, sala.descripcion, sala.capacidad, sala.lider_proyecto, sala_id)
    await conn.close()
    
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    
    sala.id = sala_id  # Asegúrate de que el ID se mantenga
    return sala


@app.get("/salas/", response_model=List[SalaDeTrabajo])
async def listar_salas():
    conn = await get_connection()
    query = "SELECT * FROM salas_de_trabajo;"
    salas = await conn.fetch(query)
    await conn.close()
    return [SalaDeTrabajo(**sala) for sala in salas]

@app.get("/salas/{sala_id}", response_model=SalaDeTrabajo)
async def obtener_sala(sala_id: int):
    conn = await get_connection()
    query = "SELECT * FROM salas_de_trabajo WHERE id = $1;"
    sala = await conn.fetchrow(query, sala_id)
    await conn.close()
    if sala is None:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    return SalaDeTrabajo(**sala)



@app.delete("/salas/{sala_id}")
async def eliminar_sala(sala_id: int):
    conn = await get_connection()
    query = "DELETE FROM salas_de_trabajo WHERE id = $1;"
    result = await conn.execute(query, sala_id)
    if result == "DELETE 0":
        await conn.close()
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    await conn.close()
    return {"detail": "Sala eliminada"}



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)