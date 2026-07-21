from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import get_settings

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title="Apollo-IO API",
        version="1.0.0",
        debug=settings.app.debug
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from backend.api.routes import router
    app.include_router(router)

    return app
