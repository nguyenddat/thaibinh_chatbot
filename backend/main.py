from typing import * 

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from database import get_db
from routes import chat_route, procedure_route, geometry_route
from services import ProcedureService
from utils.retriever import retriever

def get_application() -> FastAPI:
    application = FastAPI()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Preload procedures
    ProcedureService.preloadProcedure()
    retriever.build()

    # Add routes
    application.include_router(chat_route.router, prefix="/api/chat", tags=["Chat"])
    application.include_router(procedure_route.router, prefix="/api/procedure", tags=["Procedure"])
    application.include_router(geometry_route.router, prefix="/api/geometry", tags=["Geometry"])

    frontend_dir = Path(__file__).resolve().parent / "frontend"
    if frontend_dir.exists():
        application.mount("/ui", StaticFiles(directory=frontend_dir, html=True), name="frontend")

        @application.get("/", response_class=HTMLResponse)
        async def serve_frontend() -> str:
            return (frontend_dir / "index.html").read_text(encoding="utf-8")

    return application


app = get_application()