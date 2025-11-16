from typing import * 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import get_db
from routes import chat_route, procedure_route
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
    return application


app = get_application()