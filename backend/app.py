"""Naveen Kumar Electrical Works — API."""

from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
DATA = ROOT / "data"
DB_PATH = DATA / "leads.db"
PHONE_RE = re.compile(r"^[+\d][\d\s\-()]{8,18}$")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "naveen-admin-2026")

SHOP = {
    "name": "Naveen Kumar Electrical Works",
    "name_ta": "நவீன் குமார் எலக்ட்ரிக்கல் வொர்க்ஸ்",
    "tagline": "Your Ride... Our Power.",
    "tagline_ta": "உங்கள் வாகனம்… எங்கள் சக்தி",
    "owner": "Naveen Kumar",
    "phone": "+91 80986 73590",
    "whatsapp": "918098673590",
    "address": "GM Theatre Back Side, Indhira Nagar, Dharmapuri–Harur Road, Dharmapuri, Tamil Nadu 636701",
    "address_ta": "தர்மபுரி — GM Theatre பின்புறம்",
    "vehicles": ["Bus", "Travels", "Car", "Tata Ace", "Pickup"],
    "services": [
        {"id": "lighting", "en": "Lighting / LED upgrades", "ta": "லைட்டிங்"},
        {"id": "dc", "en": "All DC work", "ta": "DC வேலைகள்"},
        {"id": "ceiling", "en": "Trending ceiling lights (vehicle & home)", "ta": "சீலிங் லைட்"},
        {"id": "audio", "en": "Audio systems", "ta": "ஆடியோ"},
    ],
}


def get_db() -> sqlite3.Connection:
    DATA.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            vehicle TEXT,
            service TEXT,
            message TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


app = FastAPI(title="Naveen Kumar Electrical Works API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class LeadIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    phone: str = Field(..., min_length=10, max_length=20)
    vehicle: str = Field(default="", max_length=40)
    service: str = Field(default="", max_length=60)
    message: str = Field(default="", max_length=500)


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "shop": SHOP["name"]}


@app.get("/api/shop")
def shop() -> dict:
    return SHOP


@app.post("/api/leads")
def create_lead(payload: LeadIn) -> dict:
    if not PHONE_RE.match(payload.phone.strip()):
        raise HTTPException(status_code=422, detail="Enter a valid phone number")
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    try:
        cur = conn.execute(
            """
            INSERT INTO leads (name, phone, vehicle, service, message, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.name.strip(),
                payload.phone.strip(),
                payload.vehicle.strip(),
                payload.service.strip(),
                payload.message.strip(),
                now,
            ),
        )
        conn.commit()
        lead_id = cur.lastrowid
    finally:
        conn.close()
    wa = (
        f"https://wa.me/{SHOP['whatsapp']}"
        f"?text=Vanakkam%20{payload.name}%20-%20{payload.phone}"
    )
    return {"ok": True, "id": lead_id, "whatsapp": wa}


def _require_admin(token: str | None) -> None:
    if not token or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Admin token required")


@app.get("/api/leads")
def list_leads(x_admin_token: str | None = Header(default=None)) -> dict:
    _require_admin(x_admin_token)
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT id, name, phone, vehicle, service, message, created_at "
            "FROM leads ORDER BY id DESC LIMIT 100"
        ).fetchall()
        return {"leads": [dict(r) for r in rows]}
    finally:
        conn.close()


if FRONTEND.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND / "assets"), name="assets")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(FRONTEND / "index.html")

    @app.get("/admin")
    def admin() -> FileResponse:
        return FileResponse(FRONTEND / "admin.html")
