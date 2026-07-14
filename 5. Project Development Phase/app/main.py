import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from fastapi import APIRouter

# include routers (registered below)
from .routers import qa as qa_router
from .routers import explain as explain_router
from .routers import quiz as quiz_router
from .routers import summarize as summarize_router
from .routers import roadmap as roadmap_router
from .services.lamini_service import LaminiServiceError, get_lamini_service


tags_metadata = [
    {"name": "Landing", "description": "Website landing page and introductory content."},
    {"name": "Health", "description": "Health check and operational status endpoints."},
]

logger = logging.getLogger("edu_genie")
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="EduGenie",
    description="AI powered learning assistant foundation built with FastAPI and modern web technologies.",
    version="0.1.0",
    openapi_tags=tags_metadata,
    contact={"name": "EduGenie Team", "email": "support@edugenie.example"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Register feature routers
app.include_router(qa_router.router, prefix="", tags=["QA"])
app.include_router(explain_router.router, prefix="", tags=["Explain"])
app.include_router(quiz_router.router, prefix="", tags=["Quiz"])
app.include_router(summarize_router.router, prefix="", tags=["Summarize"])
app.include_router(roadmap_router.router, prefix="", tags=["Roadmap"])


@app.on_event("startup")
def preload_local_fallback() -> None:
    """Load the cached fallback before requests can hit the 15-second UI limit."""
    try:
        get_lamini_service()._load_model()
    except LaminiServiceError:
        # Gemini remains available when local initialization cannot complete;
        # the service will report a normal API error if fallback is required.
        logger.exception("Local LaMini fallback could not be preloaded")


@app.get("/", tags=["Landing"])
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": "EduGenie",
            "description": "A modern learning assistant foundation for education products.",
        },
    )


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "message": "EduGenie is healthy and ready to serve requests.",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning("HTTP exception: %s", exc)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error: %s", exc)
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
