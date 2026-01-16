"""
TikTok Streak API
==================
REST API for controlling the TikTok Streak Bot.

Endpoints:
    POST /api/run              - Run streak bot
    GET  /api/contacts         - List all contacts
    POST /api/contacts         - Add a contact
    DELETE /api/contacts/{nickname} - Remove a contact
    GET  /api/status           - Get bot status

Usage:
    uvicorn api:app --host 0.0.0.0 --port 8000
    
Docs:
    http://localhost:8000/docs
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import (
    CONTACTS_FILE,
    SCHEDULE_TIME,
    STREAK_MESSAGE,
    HEADLESS_MODE,
)

# =============================================================================
# Configuration
# =============================================================================

# API Key for authentication - CHANGE THIS!
API_KEY = os.environ.get("TIKTOK_API_KEY", "your-secret-api-key-here")

# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="TikTok Streak API",
    description="REST API for controlling TikTok Streak Bot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
    """Verify API key from header."""
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
    except:
        return []


def save_contacts(contacts):
    """Save contacts to JSON file."""
    try:
        with open(CONTACTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"contacts": contacts}, f, indent=4, ensure_ascii=False)
        return True
    except:
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
# API Endpoints
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """API root - welcome message."""
    return {
        "name": "TikTok Streak API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "POST /api/run",
            "GET /api/contacts",
            "POST /api/contacts",
            "DELETE /api/contacts/{nickname}",
            "GET /api/status"
        ]
    }


@app.get("/api/status", tags=["Status"], response_model=ApiResponse)
async def get_status(api_key: str = Depends(verify_api_key)):
    """Get bot status and configuration."""
    contacts = load_contacts()
    
    return ApiResponse(
        success=True,
        message="Status retrieved successfully",
        data={
            "schedule_time": SCHEDULE_TIME,
            "streak_message": STREAK_MESSAGE,
            "contacts_count": len(contacts),
            "headless_mode": HEADLESS_MODE,
            "server_time": datetime.now().isoformat()
        }
    )


@app.get("/api/contacts", tags=["Contacts"], response_model=ApiResponse)
async def list_contacts(api_key: str = Depends(verify_api_key)):
    """Get all contacts."""
    contacts = load_contacts()
    
    return ApiResponse(
        success=True,
        message=f"Found {len(contacts)} contacts",
        data={
            "contacts": contacts,
            "count": len(contacts)
        }
    )


@app.post("/api/contacts", tags=["Contacts"], response_model=ApiResponse)
async def add_contact(request: ContactRequest, api_key: str = Depends(verify_api_key)):
    """Add a new contact."""
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


@app.delete("/api/contacts/{nickname}", tags=["Contacts"], response_model=ApiResponse)
async def remove_contact(nickname: str, api_key: str = Depends(verify_api_key)):
    """Remove a contact by nickname."""
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


@app.post("/api/run", tags=["Bot"], response_model=ApiResponse)
async def run_bot(
    background_tasks: BackgroundTasks,
    request: RunRequest = None,
    api_key: str = Depends(verify_api_key)
):
    """
    Run the streak bot.
    
    The bot runs in the background, so this endpoint returns immediately.
    Check Telegram notifications for results.
    """
    custom_message = request.message if request else None
    
    # Run bot in background
    background_tasks.add_task(run_streak_bot, custom_message)
    
    return ApiResponse(
        success=True,
        message="Streak bot started in background",
        data={
            "custom_message": custom_message,
            "started_at": datetime.now().isoformat()
        }
    )


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
    uvicorn.run(app, host="0.0.0.0", port=8000)
