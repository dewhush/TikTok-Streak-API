"""
TikTok Streak API
==================
REST API for controlling the TikTok Streak Bot.

Created by: dewhush

Endpoints:
    GET  /              - Welcome message
    GET  /health        - Health check
    GET  /status        - Detailed status
    POST /v1/streak     - Run streak bot
    GET  /v1/contacts   - List all contacts
    POST /v1/contacts   - Add a contact
    DELETE /v1/contacts/{nickname} - Remove a contact

Usage:
    uvicorn api:app --host 0.0.0.0 --port 8000
    
Docs:
    http://localhost:8000/docs
"""

import os
import sys
import json
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess

from config import (
    APP_NAME,
    APP_ENV,
    API_KEY,
    CONTACTS_FILE,
    SCHEDULE_TIME,
    STREAK_MESSAGE,
    HEADLESS_MODE,
    HOST,
    PORT,
)

# =============================================================================
# ASCII Art Banner
# =============================================================================
BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗             ║
║   ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝             ║
║      ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝              ║
║      ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗              ║
║      ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗             ║
║      ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝             ║
║                                                              ║
║   ███████╗████████╗██████╗ ███████╗ █████╗ ██╗  ██╗          ║
║   ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗██║ ██╔╝          ║
║   ███████╗   ██║   ██████╔╝█████╗  ███████║█████╔╝           ║
║   ╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██╔═██╗           ║
║   ███████║   ██║   ██║  ██║███████╗██║  ██║██║  ██╗          ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝          ║
║                                                              ║
║              █████╗ ██████╗ ██╗                              ║
║             ██╔══██╗██╔══██╗██║                              ║
║             ███████║██████╔╝██║                              ║
║             ██╔══██║██╔═══╝ ██║                              ║
║             ██║  ██║██║     ██║                              ║
║             ╚═╝  ╚═╝╚═╝     ╚═╝                              ║
║                                                              ║
║                  Created by: dewhush                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

print(BANNER)

# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title=APP_NAME,
    description="REST API for controlling TikTok Streak Bot. Created by dewhush.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Models
# =============================================================================

class ContactRequest(BaseModel):
    nickname: str


class RunRequest(BaseModel):
    message: Optional[str] = None


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


# =============================================================================
# Authentication
# =============================================================================

async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key from X-API-Key header."""
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API key not configured. Set API_KEY in .env file."
        )
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    return x_api_key


# =============================================================================
# Helper Functions
# =============================================================================

def load_contacts():
    """Load contacts from JSON file."""
    if not os.path.exists(CONTACTS_FILE):
        return []
    
    try:
        with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('contacts', [])
    except Exception:
        return []


def save_contacts(contacts):
    """Save contacts to JSON file."""
    try:
        with open(CONTACTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"contacts": contacts}, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False


def run_streak_bot(custom_message: str = None):
    """Run the streak bot in background."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bot_script = os.path.join(script_dir, 'streak_bot.py')
    
    cmd = [sys.executable, bot_script, '--now']
    if custom_message:
        cmd.extend(['--message', custom_message])
    
    try:
        subprocess.Popen(
            cmd,
            cwd=script_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception as e:
        print(f"Error running bot: {e}")
        return False


# =============================================================================
# API Endpoints - General
# =============================================================================

@app.get("/", tags=["General"])
async def root():
    """API root - welcome message."""
    return {
        "name": APP_NAME,
        "version": "1.0.0",
        "environment": APP_ENV,
        "creator": "dewhush",
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health",
            "status": "GET /status",
            "run_streak": "POST /v1/streak",
            "list_contacts": "GET /v1/contacts",
            "add_contact": "POST /v1/contacts",
            "remove_contact": "DELETE /v1/contacts/{nickname}"
        }
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Health check for monitoring tools."""
    return {"status": "healthy"}


@app.get("/status", tags=["General"])
async def get_status():
    """Get detailed server status."""
    contacts = load_contacts()
    
    return {
        "app_name": APP_NAME,
        "version": "1.0.0",
        "environment": APP_ENV,
        "python_version": sys.version,
        "schedule_time": SCHEDULE_TIME,
        "headless_mode": HEADLESS_MODE,
        "contacts_count": len(contacts),
        "server_time": datetime.now().isoformat(),
        "creator": "dewhush"
    }


# =============================================================================
# API Endpoints - V1
# =============================================================================

@app.post("/v1/streak", tags=["Bot"], response_model=ApiResponse)
async def run_streak(
    background_tasks: BackgroundTasks,
    request: RunRequest = None,
    api_key: str = Depends(verify_api_key)
):
    """
    Run the streak bot.
    
    The bot runs in the background, so this endpoint returns immediately.
    Check Telegram notifications for results.
    
    **Requires X-API-Key header.**
    """
    custom_message = request.message if request else None
    
    # Run bot in background
    background_tasks.add_task(run_streak_bot, custom_message)
    
    return ApiResponse(
        success=True,
        message="Streak bot started in background",
        data={
            "custom_message": custom_message or STREAK_MESSAGE,
            "started_at": datetime.now().isoformat()
        }
    )


@app.get("/v1/contacts", tags=["Contacts"], response_model=ApiResponse)
async def list_contacts(api_key: str = Depends(verify_api_key)):
    """
    Get all contacts.
    
    **Requires X-API-Key header.**
    """
    contacts = load_contacts()
    
    return ApiResponse(
        success=True,
        message=f"Found {len(contacts)} contacts",
        data={
            "contacts": contacts,
            "count": len(contacts)
        }
    )


@app.post("/v1/contacts", tags=["Contacts"], response_model=ApiResponse)
async def add_contact(request: ContactRequest, api_key: str = Depends(verify_api_key)):
    """
    Add a new contact.
    
    **Requires X-API-Key header.**
    """
    nickname = request.nickname.strip()
    
    if not nickname:
        raise HTTPException(status_code=400, detail="Nickname cannot be empty")
    
    contacts = load_contacts()
    
    # Check if already exists (case-insensitive)
    if nickname.lower() in [c.lower() for c in contacts]:
        raise HTTPException(status_code=409, detail=f"Contact '{nickname}' already exists")
    
    contacts.append(nickname)
    
    if save_contacts(contacts):
        return ApiResponse(
            success=True,
            message=f"Contact '{nickname}' added successfully",
            data={
                "nickname": nickname,
                "total_contacts": len(contacts)
            }
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to save contact")


@app.delete("/v1/contacts/{nickname}", tags=["Contacts"], response_model=ApiResponse)
async def remove_contact(nickname: str, api_key: str = Depends(verify_api_key)):
    """
    Remove a contact by nickname.
    
    **Requires X-API-Key header.**
    """
    contacts = load_contacts()
    original_count = len(contacts)
    
    # Remove case-insensitive
    contacts = [c for c in contacts if c.lower() != nickname.lower()]
    
    if len(contacts) == original_count:
        raise HTTPException(status_code=404, detail=f"Contact '{nickname}' not found")
    
    if save_contacts(contacts):
        return ApiResponse(
            success=True,
            message=f"Contact '{nickname}' removed successfully",
            data={
                "nickname": nickname,
                "remaining_contacts": len(contacts)
            }
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to save changes")


# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle all unhandled exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": str(exc),
            "data": None
        }
    )


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    print(f"\n🚀 Starting {APP_NAME} on http://{HOST}:{PORT}")
    print(f"📚 Swagger docs: http://{HOST}:{PORT}/docs")
    print(f"📖 ReDoc: http://{HOST}:{PORT}/redoc\n")
    uvicorn.run("api:app", host=HOST, port=PORT, reload=(APP_ENV == "development"))
