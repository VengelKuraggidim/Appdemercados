#!/usr/bin/env python3
"""
Comparador de Preços - Main Entry Point
Starts the FastAPI server with scheduler
"""

import uvicorn
from app.api.main import app
from app.utils.scheduler import AlertScheduler
from app.models.database import init_db

# Initialize database
print("Inicializando banco de dados...")
init_db()

# Initialize and start scheduler
scheduler = AlertScheduler()
scheduler.start(interval_minutes=60)  # Check alerts every hour

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   🛒 COMPARADOR DE PREÇOS - API INICIADA 🛒  ║
    ╠═══════════════════════════════════════════════╣
    ║                                               ║
    ║  API:      http://localhost:8000              ║
    ║  Docs:     http://localhost:8000/docs         ║
    ║  Frontend: http://localhost:8000 (servir)     ║
    ║                                               ║
    ║  Supermercados Suportados:                    ║
    ║  • Carrefour                                  ║
    ║  • Pão de Açúcar                             ║
    ║  • Extra                                      ║
    ║  • Mercado Livre                              ║
    ║                                               ║
    ╚═══════════════════════════════════════════════╝
    """)

    try:
        uvicorn.run(
            "app.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nEncerrando servidor...")
        scheduler.stop()
