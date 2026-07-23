"""
backend/main.py

FastAPI entry point for AI Study Buddy.

Endpoints:
    POST /api/summarize     — upload PDF → summary, topics, definitions
    POST /api/quiz          — summary + topics → interactive quiz
    POST /api/study-plan    — topics + days  → study schedule
    GET  /api/health        — liveness check
"""

from __future__ import annotations

import logging
from typing import Any

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.agents.quiz_generator import generate_quiz
from backend.agents.study_planner import study_planner_agent
from backend.agents.summarizer import summarization_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Study Buddy API", version="1.0.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8130", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _blank_state() -> dict[str, Any]:
    """Return a fully-populated blank StudyState dict (satisfies TypedDict)."""
    return {
        "pdf_bytes": b"",
        "pdf_path": "",
        "raw_text": "",
        "study_days": 5,
        "difficulty": "medium",
        "summary": "",
        "key_topics": [],
        "definitions": [],
        "quiz": [],
        "study_plan": [],
        "blocked": False,
        "security_reason": "",
        "execution_logs": [],
    }


def _security_obj(result: dict[str, Any]) -> dict[str, Any]:
    reason = result.get("security_reason", "")
    warnings = [reason] if reason else []
    risk = "High" if result.get("blocked") else ("Medium" if warnings else "Low")
    return {"is_safe": not result.get("blocked", False), "risk_level": risk, "warnings": warnings}


# ── POST /api/summarize ───────────────────────────────────────────────────────
@app.post("/api/summarize")
async def summarize(
    file: UploadFile = File(..., description="PDF study material"),
) -> dict[str, Any]:
    """
    Accepts a PDF and runs only the Summarization Agent.
    Returns summary, key topics, and definitions.
    """
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    logger.info("Summarizing '%s'", file.filename)

    state = {**_blank_state(), "pdf_bytes": pdf_bytes}

    try:
        result = summarization_agent(state)
    except Exception as exc:
        logger.exception("Summarizer failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Summarization failed: {exc}") from exc

    if result.get("blocked"):
        raise HTTPException(
            status_code=422,
            detail=result.get("security_reason", "Document blocked by security layer."),
        )

    return {
        "file_name": file.filename,
        "summary": result.get("summary", ""),
        "key_topics": result.get("key_topics", []),
        "definitions": result.get("definitions", []),
        "security": _security_obj(result),
    }


# ── POST /api/quiz ────────────────────────────────────────────────────────────
class QuizRequest(BaseModel):
    summary: str
    key_topics: list[str]
    num_mcq: int = Field(default=3, ge=1, le=10)
    num_short: int = Field(default=2, ge=0, le=5)
    difficulty: str = "medium"


@app.post("/api/quiz")
def quiz_endpoint(body: QuizRequest) -> dict[str, Any]:
    """
    Accepts summary + topics + config and runs the Quiz Generator Agent.
    Returns an interactive quiz with MCQ and/or short-answer questions.
    """
    logger.info("Generating quiz | mcq=%d short=%d difficulty=%s", body.num_mcq, body.num_short, body.difficulty)

    try:
        result = generate_quiz(
            summary=body.summary,
            key_topics=body.key_topics,
            num_mcq=body.num_mcq,
            num_short=body.num_short,
            difficulty=body.difficulty,
        )
    except Exception as exc:
        logger.exception("Quiz generator failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {exc}") from exc

    return {"quiz": result.get("quiz", [])}


# ── POST /api/study-plan ──────────────────────────────────────────────────────
class PlanRequest(BaseModel):
    key_topics: list[str]
    study_days: int = Field(default=5, ge=1, le=30)


@app.post("/api/study-plan")
def study_plan_endpoint(body: PlanRequest) -> dict[str, Any]:
    """
    Accepts topics + study days and runs the Study Planner Agent.
    Returns a day-by-day study schedule with spaced repetition.
    """
    logger.info("Generating study plan | days=%d topics=%d", body.study_days, len(body.key_topics))

    state = {**_blank_state(), "key_topics": body.key_topics, "study_days": body.study_days}

    try:
        result = study_planner_agent(state)
    except Exception as exc:
        logger.exception("Study planner failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Study plan generation failed: {exc}") from exc

    return {"study_plan": result.get("study_plan", [])}


# ── GET /api/health ───────────────────────────────────────────────────────────
@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8080, reload=True)
