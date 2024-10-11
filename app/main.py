import os
import sys

print("Current working directory:", os.getcwd())
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Project root:", project_root)
sys.path.insert(0, project_root)
print("Updated sys.path:", sys.path)

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from app.endpoints import gmail_webhook, digitization, email_automation, auth, assistant, cover_pages, email_templates, files, roster, stats, user_settings
from app.core.config import settings
from app.utils.authenticate import authenticate
from app.services.drive_service import build_drive_service
from app.services.gmail_service import build_gmail_service
from contextlib import asynccontextmanager
from dev.start_ngrok import start_ngrok
import uvicorn



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize services, database connections, etc.
    yield
    # Clean up resources, close connections, etc.


app = FastAPI(
    title= settings.PROJECT_NAME,
    version= settings.PROJECT_VERSION,
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Include routers
app.include_router(gmail_webhook.router, prefix="/api/webhook", tags=["webhook"])
app.include_router(digitization.router, prefix="/api/digitization", tags=["digitization"])
app.include_router(email_automation.router, prefix="/api/email-automation", tags=["email-automation"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user_settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["assistant"])
app.include_router(cover_pages.router, prefix="/api/cover-pages", tags=["cover-pages"])
app.include_router(email_templates.router, prefix="/api/email-templates", tags=["email-templates"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(roster.router, prefix="/api/roster", tags=["roster"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])




if __name__ == "__main__":
    start_ngrok()
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)