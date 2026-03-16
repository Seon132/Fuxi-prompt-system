"""
Four-layer structure validator.

Checks whether an Agent's data meets the density and quality requirements
defined in the Fuxi specification. This is a rule-based validator (no LLM).
"""

from __future__ import annotations

from .models import Agent, ValidationIssue, ValidationResult


def validate(agent: Agent) -> ValidationResult:
    issues: list[ValidationIssue] = []
    scores: dict[str, float] = {}

    # --- Experience Layer ---
    exp = agent.experience
    all_exp = exp.direct + exp.indirect + exp.reflective
    if not all_exp:
        issues.append(ValidationIssue(
            layer="experience", severity="error",
            message="经验层为空，至少需要提供一条经验节点",
        ))
        scores["experience_density"] = 0.0
    else:
        density = 0.0
        for node in all_exp:
            node_score = 1.0
            if not node.evidence:
                node_score -= 0.3
                issues.append(ValidationIssue(
                    layer="experience", severity="warning",
                    message=f"经验 '{node.id}' 缺少证据字段",
                ))
            if not node.context:
                node_score -= 0.2
            density += max(node_score, 0.0)
        scores["experience_density"] = round(density / len(all_exp), 2)

        if not exp.indirect:
            issues.append(ValidationIssue(
                layer="experience", severity="warning",
                message="缺少间接经验，建议补充阅读/课程/案例等来源",
            ))

    # --- Knowledge Layer ---
    know = agent.knowledge
    all_know = know.individual + know.professional + know.universal
    if not all_know:
        issues.append(ValidationIssue(
            layer="knowledge", severity="error",
            message="知识层为空，至少需要提供一条知识节点",
        ))
        scores["knowledge_density"] = 0.0
    else:
        density = 0.0
        for node in all_know:
            node_score = 1.0
            if not node.definition:
                node_score -= 0.25
                issues.append(ValidationIssue(
                    layer="knowledge", severity="warning",
                    message=f"知识 '{node.id}' 缺少定义",
                ))
            if not node.boundary:
                node_score -= 0.25
                issues.append(ValidationIssue(
                    layer="knowledge", severity="warning",
                    message=f"知识 '{node.id}' 缺少适用边界",
                ))
            if not node.common_misreading:
                node_score -= 0.15
            if not node.role_in_system:
                node_score -= 0.15
            density += max(node_score, 0.0)
        scores["knowledge_density"] = round(density / len(all_know), 2)

    # --- Thinking Layer ---
    think = agent.thinking
    caps = [
        ("analysis", think.analysis),
        ("synthesis", think.synthesis),
        ("insight", think.insight),
        ("critical", think.critical),
        ("reflection", think.reflection),
    ]
    present = [(name, cap) for name, cap in caps if cap is not None]

    if len(present) < 2:
        issues.append(ValidationIssue(
            layer="thinking", severity="error",
            message=f"思维层只有 {len(present)} 个能力，至少需要 2 个核心能力（分析/批判/反思）",
        ))
        scores["thinking_executability"] = 0.0
    else:
        density = 0.0
        for name, cap in present:
            node_score = 1.0
            if not cap.steps:
                node_score -= 0.3
                issues.append(ValidationIssue(
                    layer="thinking", severity="warning",
                    message=f"思维能力 '{name}' 缺少执行步骤，无法作为可执行程序",
                ))
            if not cap.anti_pattern:
                node_score -= 0.2
            if not cap.failure_pattern:
                node_score -= 0.2
            if not cap.excellence_criteria:
                node_score -= 0.15
            density += max(node_score, 0.0)
        scores["thinking_executability"] = round(density / len(present), 2)

    # --- Philosophy Layer ---
    phil = agent.philosophy
    missing_fixed = [p for p in [
        "P1_essentialism", "P2_first_principles", "P3_systematic_thinking",
        "P4_dialectics", "P5_contradiction", "P6_concrete_analysis",
        "P7_positivism", "P8_pragmatism",
    ] if p not in phil.fixed_principles]

    if missing_fixed:
        issues.append(ValidationIssue(
            layer="philosophy", severity="error",
            message=f"固定原原则缺失: {', '.join(missing_fixed)}（不可删除/替换/降级）",
        ))
        scores["philosophy_completeness"] = round(
            1.0 - len(missing_fixed) / 8.0, 2,
        )
    else:
        scores["philosophy_completeness"] = 1.0

    for ext in phil.extension_principles:
        if not ext.bound_to:
            issues.append(ValidationIssue(
                layer="philosophy", severity="warning",
                message=f"扩展原则 '{ext.name}' 未绑定固定原原则门控",
            ))

    # --- Expression Layer ---
    expr = agent.expression
    if not expr.target_audience:
        issues.append(ValidationIssue(
            layer="expression", severity="info",
            message="建议指定目标受众（target_audience）以提升风格匹配度",
        ))

    # --- Overall ---
    has_errors = any(i.severity == "error" for i in issues)

    return ValidationResult(
        valid=not has_errors,
        issues=issues,
        quality_scores=scores,
    )
