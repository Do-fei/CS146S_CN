import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import get_engine
from .models import Base
from .routers import annotations, auth, books, jobs, sync
from .services.storage import ensure_dirs

logging.basicConfig(level=logging.INFO)

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    ensure_dirs()
    Base.metadata.create_all(bind=get_engine())
    logging.getLogger("one_paper_wok").info(
        "providers: ocr=%s llm=%s email=%s",
        settings.resolved_ocr_provider(),
        settings.resolved_llm_provider(),
        settings.resolved_email_provider(),
    )


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "providers": {
            "ocr": settings.resolved_ocr_provider(),
            "llm": settings.resolved_llm_provider(),
            "email": settings.resolved_email_provider(),
        },
    }


app.include_router(auth.router)
app.include_router(books.router)
app.include_router(jobs.router)
app.include_router(annotations.router)
app.include_router(sync.router)
