from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime
import os
import time

load_dotenv()

from routers import chat, upload, history

START_TIME = time.time()

app = FastAPI(
    title="RAG Chatbot API",
    description="Domain-specific RAG chatbot using Groq + Gemini + Supabase pgvector",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router,  prefix="/api/upload",  tags=["upload"])
app.include_router(chat.router,    prefix="/api/chat",    tags=["chat"])
app.include_router(history.router, prefix="/api/history", tags=["history"])


@app.get("/", tags=["root"])
def root():
    return {
        "status": "RAG Chatbot API is running",
        "docs": "/docs",
        "ping": "/ping",
    }


@app.get("/health", tags=["root"])
def health():
    return {"status": "ok"}


@app.api_route("/ping", methods=["GET", "HEAD"], tags=["uptime"])
def ping():
    """
    UptimeRobot keep-alive endpoint.

    Setup (free at uptimerobot.com):
      Monitor Type : HTTP(s)
      URL          : https://your-app.onrender.com/ping
      Interval     : Every 5 minutes
    """
    uptime_s = int(time.time() - START_TIME)
    h, rem   = divmod(uptime_s, 3600)
    m, s     = divmod(rem, 60)
    return {
        "ping": "pong",
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": {
            "seconds": uptime_s,
            "human":   f"{h}h {m}m {s}s",
        },
    }
