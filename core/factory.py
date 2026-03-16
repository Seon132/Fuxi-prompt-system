"""
Role Factory — automated Agent creation engine.

Given a role name/type, uses LLM to research, generate four-layer data,
compile, and optionally evaluate in a loop.
"""

from __future__ import annotations

from .compiler import compile_agent
from .evaluator import evaluate
from .llm import chat, load_prompt
from .models import (
    Agent,
    EvaluateRequest,
    EvaluationMode,
    EvaluationReport,
)
from .validator import validate

import json
import re


class CreateRoleRequest:
    def __init__(
        self,
        role_name: str,
        role_type: str = "",
        description: str = "",
        materials: str = "",
        auto_evaluate: bool = True,
        max_iterations: int = 2,
    ):
        self.role_name = role_name
        self.role_type = role_type
        self.description = description
        self.materials = materials
        self.auto_evaluate = auto_evaluate
        self.max_iterations = max_iterations


class CreateRoleResult:
    def __init__(
        self,
        agent: Agent,
        system_prompt: str,
        evaluation_report: EvaluationReport | None,
        iterations: int,
        status: str,
    ):
        self.agent = agent
        self.system_prompt = system_prompt
        self.evaluation_report = evaluation_report
        self.iterations = iterations
        self.status = status


async def create_role(req: CreateRoleRequest) -> CreateRoleResult:
    factory_prompt = load_prompt("factory")

    user_msg = _build_creation_prompt(req)
    raw_agent_json = await chat(
        system=factory_prompt + "\n\n" + _agent_schema_instruction(),
        user=user_msg,
        temperature=0.4,
    )

    agent = _parse_agent(raw_agent_json, req)
    system_prompt, _ = compile_agent(agent)

    evaluation_report = None
    iterations = 1
    status = "created"

    if req.auto_evaluate:
        for i in range(req.max_iterations):
            iterations = i + 1
            eval_req = EvaluateRequest(
                mode=EvaluationMode.static,
                system_prompt=system_prompt,
            )
            evaluation_report = await evaluate(eval_req)

            if evaluation_report.score_static and evaluation_report.score_static >= 70:
                status = "passed_static_evaluation"
                break

            if i < req.max_iterations - 1:
                agent = await _refine_agent(agent, evaluation_report)
                system_prompt, _ = compile_agent(agent)
                status = "iterating"
        else:
            status = "needs_manual_review"

    return CreateRoleResult(
        agent=agent,
        system_prompt=system_prompt,
        evaluation_report=evaluation_report,
        iterations=iterations,
        status=status,
    )


def _build_creation_prompt(req: CreateRoleRequest) -> str:
    parts = [
        f"请为以下角色生成完整的四层结构化数据：",
        f"角色名称：{req.role_name}",
    ]
    if req.role_type:
        parts.append(f"角色类型：{req.role_type}")
    if req.description:
        parts.append(f"角色描述：{req.description}")
    if req.materials:
        parts.append(f"参考资料：\n{req.materials}")

    parts.append(
        "\n请按照伏羲四层架构的要求，生成完整的角色数据。"
        "经验层必须补厚（尤其间接经验），知识层必须有定义/作用/误读/边界，"
        "思维层必须写成可执行程序（含触发条件、步骤、反模式、失败模式），"
        "哲学层必须保留全部固定原原则并添加角色特有的扩展原则。"
    )
    return "\n".join(parts)


def _agent_schema_instruction() -> str:
    return """
你必须输出一个 JSON 对象（用 ```json 包裹），严格遵循以下结构：
{
  "name": "角色名",
  "role_type": "philosopher|writer|scientist|...",
  "description": "一句话描述",
  "experience": {
    "direct": [{"id": "e1", "claim": "...", "evidence": "...", "context": "...", "experience_type": "direct", "confidence": 0.9}],
    "indirect": [{"id": "e2", "claim": "...", "evidence": "...", "context": "...", "experience_type": "indirect", "source_medium": "...", "confidence": 0.8}],
    "reflective": [{"id": "e3", "claim": "...", "evidence": "...", "context": "...", "experience_type": "reflective", "lesson": "...", "confidence": 0.7}]
  },
  "knowledge": {
    "individual": [...],
    "professional": [{"id": "k1", "statement": "...", "definition": "...", "role_in_system": "...", "boundary": "...", "common_misreading": "...", "counter_case": "...", "level": "professional", "knowledge_type": "conceptual", "confidence": 0.9}],
    "universal": [...]
  },
  "thinking": {
    "analysis": {"id": "t1", "name": "...", "definition": "...", "trigger": "...", "steps": ["..."], "anti_pattern": "...", "excellence_criteria": "...", "failure_pattern": "...", "principle_binding": ["P1_essentialism"]},
    "synthesis": {...},
    "insight": {...},
    "critical": {...},
    "reflection": {...}
  },
  "philosophy": {
    "fixed_principles": ["P1_essentialism","P2_first_principles","P3_systematic_thinking","P4_dialectics","P5_contradiction","P6_concrete_analysis","P7_positivism","P8_pragmatism"],
    "extension_principles": [{"id": "ext1", "name": "...", "description": "...", "bound_to": ["P1_essentialism"], "scope": "..."}]
  },
  "expression": {
    "speech_habits": {"tone_intensity": "...", "sentence_preference": "...", "vocabulary_style": "...", "rhythm": "..."},
    "dialogue_style": {"organization": "...", "interaction": "...", "conflict_handling": "...", "explanation_depth": "..."},
    "personality": {"introversion_extroversion": 0.5, "rationality": 0.7, "idealism_pragmatism": 0.5, "altruism": 0.5, "sharpness": 0.5},
    "target_audience": "...",
    "boundary_rules": "..."
  }
}

要求：
1. 经验层每个类别至少 2 条
2. 知识层至少 3 条专业知识
3. 思维层 5 个能力全部填写
4. 扩展原则至少 2 条，每条必须绑定固定原原则
"""


def _parse_agent(raw: str, req: CreateRoleRequest) -> Agent:
    json_match = re.search(r"```json\s*\n(.*?)\n\s*```", raw, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            return Agent.model_validate(data)
        except Exception:
            pass

    return Agent(
        name=req.role_name,
        role_type=req.role_type,
        description=req.description or f"由伏羲角色工厂自动生成的{req.role_name}角色",
    )


async def _refine_agent(agent: Agent, report: EvaluationReport) -> Agent:
    """Ask LLM to refine the agent based on evaluation feedback."""
    suggestions = "\n".join(f"- {s}" for s in report.suggestions) if report.suggestions else "无具体建议"
    weaknesses = "\n".join(f"- {w}" for w in report.weaknesses) if report.weaknesses else "无"

    user_msg = (
        f"以下是当前角色 {agent.name} 的评估反馈：\n\n"
        f"静态评分：{report.score_static}\n"
        f"薄弱项：\n{weaknesses}\n\n"
        f"修改建议：\n{suggestions}\n\n"
        f"当前角色数据：\n```json\n{agent.model_dump_json(indent=2)}\n```\n\n"
        f"请根据评估反馈修改角色数据，输出完整的修订后 JSON（用 ```json 包裹）。"
    )

    raw = await chat(
        system=_agent_schema_instruction(),
        user=user_msg,
        temperature=0.3,
    )

    json_match = re.search(r"```json\s*\n(.*?)\n\s*```", raw, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            refined = Agent.model_validate(data)
            refined.id = agent.id
            refined.version = agent.version + 1
            return refined
        except Exception:
            pass

    return agent
