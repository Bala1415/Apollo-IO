"""
Apollo-IO Backend Application Entry Point.
Exports the FastAPI app instance for ASGI servers like Uvicorn or Gunicorn.
"""
from backend.core.factory import create_app

app = create_app()
