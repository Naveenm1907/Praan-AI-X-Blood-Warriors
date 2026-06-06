from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import patient, blood_bank, donor, voice, workflow

app = FastAPI(
    title="PRAAN AI API",
    description="AI-Powered Blood Coordination for Thalassemia Fighters",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient.router, prefix="/api")
app.include_router(blood_bank.router, prefix="/api")
app.include_router(donor.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(workflow.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "PRAAN AI", "mode": "mock"}
