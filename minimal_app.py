#!/usr/bin/env python3
"""
Versión simplificada de main.py para diagnóstico
"""

from fastapi import FastAPI

print("Creando app básica...")
app = FastAPI(
    title="Social Media Analytics API - Debug",
    description="Versión simplificada para diagnóstico",
    version="3.0.0-debug"
)

@app.get("/")
def root():
    return {"message": "API básica funcionando", "status": "debug"}

@app.get("/health")
def health():
    return {"status": "healthy"}

print("App básica creada exitosamente")

if __name__ == "__main__":
    import uvicorn
    print("Iniciando servidor básico...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
