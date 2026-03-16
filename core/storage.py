"""
Simple JSON-file storage for Agents and Evaluation reports.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from .models import Agent, EvaluationReport

STORAGE_ROOT = Path(__file__).resolve().parent.parent / "storage"
AGENTS_DIR = STORAGE_ROOT / "agents"
EVALS_DIR = STORAGE_ROOT / "evaluations"


def _ensure_dirs():
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    EVALS_DIR.mkdir(parents=True, exist_ok=True)


# ---- Agent CRUD ----

def save_agent(agent: Agent) -> Agent:
    _ensure_dirs()
    if not agent.id:
        agent.id = uuid.uuid4().hex[:12]
    path = AGENTS_DIR / f"{agent.id}.json"
    path.write_text(agent.model_dump_json(indent=2), encoding="utf-8")
    return agent


def load_agent(agent_id: str) -> Agent | None:
    path = AGENTS_DIR / f"{agent_id}.json"
    if not path.exists():
        return None
    return Agent.model_validate_json(path.read_text(encoding="utf-8"))


def list_agents() -> list[dict]:
    _ensure_dirs()
    results = []
    for p in sorted(AGENTS_DIR.glob("*.json")):
        try:
            agent = Agent.model_validate_json(p.read_text(encoding="utf-8"))
            results.append({
                "id": agent.id,
                "name": agent.name,
                "role_type": agent.role_type,
                "version": agent.version,
            })
        except Exception:
            continue
    return results


def delete_agent(agent_id: str) -> bool:
    path = AGENTS_DIR / f"{agent_id}.json"
    if path.exists():
        path.unlink()
        return True
    return False


# ---- Evaluation history ----

def save_evaluation(agent_id: str, report: EvaluationReport) -> str:
    _ensure_dirs()
    eval_id = f"{agent_id}_{int(time.time())}"
    path = EVALS_DIR / f"{eval_id}.json"
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return eval_id


def list_evaluations(agent_id: str) -> list[dict]:
    _ensure_dirs()
    results = []
    for p in sorted(EVALS_DIR.glob(f"{agent_id}_*.json")):
        try:
            report = EvaluationReport.model_validate_json(p.read_text(encoding="utf-8"))
            results.append({
                "eval_id": p.stem,
                "mode": report.mode.value,
                "score_static": report.score_static,
                "score_runtime": report.score_runtime,
                "passed": report.passed,
            })
        except Exception:
            continue
    return results
