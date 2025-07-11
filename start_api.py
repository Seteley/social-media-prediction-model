#!/usr/bin/env python3
"""
Script para iniciar la API FastAPI
"""

import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
