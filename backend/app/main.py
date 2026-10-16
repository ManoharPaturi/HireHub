from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import SessionLocal, init_tables
from app.db.init_db import init_db
from app.routers import auth, students, internships, applications, notifications, messages, recruiter, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables (MySQL) and seed demo data on startup.
    init_tables()
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description="HireHub — Full-stack Internship Portal (Student & Recruiter REST APIs)",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "online", "service": settings.PROJECT_NAME, "version": "2.0.0", "docs": "/docs"}


app.include_router(auth.router)
app.include_router(students.router)
app.include_router(internships.router)
app.include_router(applications.router)
app.include_router(notifications.router)
app.include_router(messages.router)
app.include_router(recruiter.router)
app.include_router(admin.router)
