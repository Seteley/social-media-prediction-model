#!/usr/bin/env python3
"""
Script para probar la API de regresión
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Iniciando API de Social Media Analytics...")
    print("📊 Endpoints disponibles:")
    print("   • /docs - Documentación interactiva")
    print("   • /clustering - API de clustering")
    print("   • /regression - API de regresión")
    print("\n🌐 Servidor iniciando en: http://localhost:8000")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
