"""
Evaluation Engine — calls LLM with the evaluator prompt to produce
structured evaluation reports.
"""

from __future__ import annotations

import json
import re

from .llm import chat, load_prompt
from .models import (
    AuditScores,
    DynamicSubscores,
    EvaluateRequest,
    EvaluationMode,
    EvaluationReport,
    StaticSubscores,
    dynamic_rating,
    static_rating,
)


async def evaluate(req: EvaluateRequest) -> EvaluationReport:
    mode = _resolve_mode(req)
    evaluator_system = load_prompt("evaluator")
    user_message = _build_user_message(req, mode)

    raw = await chat(
        system=evaluator_system,
        user=user_message,
        temperature=0.2,
    )

    report = _parse_report(raw, mode)
    return report


def _resolve_mode(req: EvaluateRequest) -> EvaluationMode:
    has_prompt = bool(req.system_prompt)
    has_log = bool(req.conversation_log)
    if has_prompt and has_log:
        return EvaluationMode.hybrid
    if has_log:
        return EvaluationMode.dynamic
    return EvaluationMode.static


def _build_user_message(req: EvaluateRequest, mode: EvaluationMode) -> str:
    parts = [
        "请按四层架构动态熵机制 V2 评估以下对象。",
        "",
        f"[评估模式]\n{mode.value}",
    ]

    if req.system_prompt:
        parts.append(f"\n[system_prompt]\n{req.system_prompt}")

    if req.conversation_log:
        log_text = json.dumps(req.conversation_log, ensure_ascii=False, indent=2)
        parts.append(f"\n[conversation_log]\n{log_text}")

    if req.candidate_output:
        parts.append(f"\n[candidate_output]\n{req.candidate_output}")

    parts.append(
        "\n\n请严格按照你的输出格式要求输出完整评估报告。"
        "在报告末尾，额外输出一个 JSON 块（用 ```json 包裹），"
        "包含以下字段以方便程序解析：\n"
        "{\n"
        '  "mode": "static|dynamic|hybrid",\n'
        '  "static_subscores": { "S_order": 0.xx, "S_edge": ..., "S_core": ..., '
        '"S_combo": ..., "S_closure": ..., "S_rule": ..., '
        '"S_philosophy_constitution": ... },\n'
        '  "score_static": xx.x,\n'
        '  "dynamic_subscores": { "S_order_dyn": ..., "S_edge_dyn": ..., '
        '"S_combo_dyn": ..., "S_valid": ..., "S_control": ..., '
        '"S_writeback": ..., "S_revise": ..., '
        '"S_philosophy_enforce": ... },\n'
        '  "score_runtime": xx.x,\n'
        '  "audit": { "Consistency": ..., "EvidenceCov": ..., "GoalFit": ..., '
        '"EntropyExcess": ..., "RuleViolation": ..., "UnsafeRisk": ... },\n'
        '  "j_t": 0.xx,\n'
        '  "passed": true|false,\n'
        '  "strengths": ["...", "..."],\n'
        '  "weaknesses": ["...", "..."],\n'
        '  "suggestions": ["...", "..."]\n'
        "}\n"
        "对于当前模式不适用的字段，设为 null。"
    )
    return "\n".join(parts)


def _parse_report(raw: str, mode: EvaluationMode) -> EvaluationReport:
    """Extract the structured JSON from the LLM response, fall back to defaults."""
    json_match = re.search(r"```json\s*\n(.*?)\n\s*```", raw, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            return _build_report_from_json(data, mode)
        except (json.JSONDecodeError, KeyError):
            pass

    return EvaluationReport(
        mode=mode,
        strengths=["（LLM 返回未能解析为结构化数据，请查看原始输出）"],
        suggestions=[raw[:2000]],
    )


def _build_report_from_json(data: dict, mode: EvaluationMode) -> EvaluationReport:
    report = EvaluationReport(mode=mode)

    if data.get("static_subscores"):
        ss = StaticSubscores(**data["static_subscores"])
        report.static_subscores = ss
        report.score_static = data.get("score_static") or ss.total()
        report.static_rating = static_rating(report.score_static)

    if data.get("dynamic_subscores"):
        ds = DynamicSubscores(**data["dynamic_subscores"])
        report.dynamic_subscores = ds
        report.score_runtime = data.get("score_runtime") or ds.total()
        report.dynamic_rating = dynamic_rating(report.score_runtime)

    if data.get("audit"):
        audit = AuditScores(**data["audit"])
        report.audit = audit
        runtime = report.score_runtime or 0.0
        report.j_t = data.get("j_t") or audit.j_t(runtime)
        report.forced_reject_reasons = audit.forced_reject()

    report.passed = data.get("passed", False)
    if report.forced_reject_reasons:
        report.passed = False

    report.strengths = data.get("strengths", [])
    report.weaknesses = data.get("weaknesses", [])
    report.suggestions = data.get("suggestions", [])

    return report
