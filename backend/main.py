from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from database import init_db
from routes import patient, blood_bank, donor, voice, workflow, agent, tasks, whatsapp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    logger.info("Starting PRAAN AI Backend...")
    logger.info("Initializing database tables...")
    init_db()
    logger.info("Database initialization complete")
    yield
    # Shutdown
    logger.info("Shutting down PRAAN AI Backend...")


app = FastAPI(
    title="PRAAN AI API",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(patient.router, prefix="/api/patient", tags=["patient"])
app.include_router(blood_bank.router, prefix="/api/blood-bank", tags=["blood-bank"])
app.include_router(donor.router, prefix="/api/donor", tags=["donor"])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(workflow.router, prefix="/api/workflow", tags=["workflow"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(whatsapp.router, tags=["whatsapp"])


@app.get("/")
def root():
    return {"message": "PRAAN AI API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
