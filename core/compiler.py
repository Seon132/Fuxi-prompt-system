"""
Prompt Compiler — transforms structured Agent data into a deployable system prompt.

Uses the Fuxi mother prompt as the base template and injects the agent's
four-layer content to produce a complete, role-specific system prompt.
"""

from __future__ import annotations

from .models import Agent
from .validator import validate


def compile_agent(agent: Agent) -> tuple[str, list[str]]:
    """
    Compile an Agent into a system prompt string.
    Returns (system_prompt, validation_warnings).
    """
    result = validate(agent)
    warnings = [i.message for i in result.issues if i.severity == "warning"]

    sections: list[str] = []

    # --- Header ---
    sections.append(f"# 系统提示词（{agent.name}｜基于伏羲四层双向贯通架构）\n")
    if agent.description:
        sections.append(f"{agent.description}\n")

    sections.append(
        "本角色基于伏羲认知架构母体生成，遵循四层双向贯通机制。"
        "固定原原则不可删除、不可替换、不可降级。\n"
    )

    # --- Experience Layer ---
    sections.append("---\n\n## 1. 经验层\n")
    sections.append("定位：现实输入、事实锚点与后续验证来源。\n")

    if agent.experience.direct:
        sections.append("### 直接经验\n")
        for node in agent.experience.direct:
            sections.append(_format_experience(node))

    if agent.experience.indirect:
        sections.append("### 间接经验\n")
        for node in agent.experience.indirect:
            sections.append(_format_experience(node))

    if agent.experience.reflective:
        sections.append("### 反思经验\n")
        for node in agent.experience.reflective:
            sections.append(_format_experience(node))

    # --- Knowledge Layer ---
    sections.append("---\n\n## 2. 知识层\n")
    sections.append("定位：经验可复用化与思维可落地化的中介层。\n")

    for level_name, nodes in [
        ("个体知识", agent.knowledge.individual),
        ("专业知识", agent.knowledge.professional),
        ("普遍知识", agent.knowledge.universal),
    ]:
        if nodes:
            sections.append(f"### {level_name}\n")
            for node in nodes:
                sections.append(_format_knowledge(node))

    # --- Thinking Layer ---
    sections.append("---\n\n## 3. 思维层\n")
    sections.append("定位：把原理转成可操作推理的处理层。\n")

    caps = [
        ("分析能力", agent.thinking.analysis),
        ("总结能力", agent.thinking.synthesis),
        ("洞察能力", agent.thinking.insight),
        ("批判性思维", agent.thinking.critical),
        ("反思能力", agent.thinking.reflection),
    ]
    for name, cap in caps:
        if cap:
            sections.append(f"### {name}\n")
            sections.append(f"- 定义：{cap.definition}\n")
            if cap.trigger:
                sections.append(f"- 触发条件：{cap.trigger}\n")
            if cap.steps:
                sections.append("- 执行步骤：\n")
                for i, step in enumerate(cap.steps, 1):
                    sections.append(f"  {i}. {step}\n")
            if cap.anti_pattern:
                sections.append(f"- 反模式警告：{cap.anti_pattern}\n")
            if cap.excellence_criteria:
                sections.append(f"- 高质量判据：{cap.excellence_criteria}\n")
            if cap.failure_pattern:
                sections.append(f"- 失败模式：{cap.failure_pattern}\n")
            if cap.principle_binding:
                sections.append(f"- 绑定原则：{', '.join(cap.principle_binding)}\n")
            sections.append("\n")

    if agent.thinking.additional:
        sections.append("### 补充能力\n")
        for cap in agent.thinking.additional:
            sections.append(f"- **{cap.name}**：{cap.definition}\n")

    # --- Philosophy Layer ---
    sections.append("---\n\n## 4. 哲学层\n")
    sections.append("### 固定原原则（不可删除/替换/降级）\n\n")

    principle_names = {
        "P1_essentialism": "本质主义",
        "P2_first_principles": "第一性原理",
        "P3_systematic_thinking": "体系性思维",
        "P4_dialectics": "辩证法",
        "P5_contradiction": "矛盾论",
        "P6_concrete_analysis": "具体问题具体分析",
        "P7_positivism": "实证主义",
        "P8_pragmatism": "实用主义",
    }
    for p in agent.philosophy.fixed_principles:
        label = principle_names.get(p, p)
        sections.append(f"- {label}\n")

    sections.append(f"\n强制闭环路径：`{agent.philosophy.p_loop}`\n")

    if agent.philosophy.extension_principles:
        sections.append("\n### 扩展原则\n")
        for ext in agent.philosophy.extension_principles:
            bound = ", ".join(ext.bound_to) if ext.bound_to else "未绑定"
            sections.append(f"- **{ext.name}**：{ext.description}（门控：{bound}）\n")

    # --- Expression Layer ---
    sections.append("---\n\n## 5. 外显要素层\n")
    expr = agent.expression
    sections.append(f"- 语气强度：{expr.speech_habits.tone_intensity}\n")
    sections.append(f"- 句式偏好：{expr.speech_habits.sentence_preference}\n")
    sections.append(f"- 用词风格：{expr.speech_habits.vocabulary_style}\n")
    sections.append(f"- 对话组织：{expr.dialogue_style.organization}\n")
    sections.append(f"- 互动方式：{expr.dialogue_style.interaction}\n")
    sections.append(f"- 冲突处理：{expr.dialogue_style.conflict_handling}\n")
    sections.append(f"- 解释深度：{expr.dialogue_style.explanation_depth}\n")
    if expr.target_audience:
        sections.append(f"- 目标受众：{expr.target_audience}\n")
    if expr.boundary_rules:
        sections.append(f"- 边界规则：{expr.boundary_rules}\n")

    # --- Connection Protocol ---
    sections.append(_connection_protocol())

    # --- Output Protocol ---
    sections.append(_output_protocol())

    prompt = "\n".join(sections)
    return prompt, warnings


def _format_experience(node) -> str:
    lines = [f"- **{node.id}**：{node.claim}\n"]
    if node.evidence:
        lines.append(f"  - 证据：{node.evidence}\n")
    if node.context:
        lines.append(f"  - 情境：{node.context}\n")
    if node.lesson:
        lines.append(f"  - 沉淀：{node.lesson}\n")
    return "".join(lines)


def _format_knowledge(node) -> str:
    lines = [f"- **{node.id}**：{node.statement}\n"]
    if node.definition:
        lines.append(f"  - 定义：{node.definition}\n")
    if node.role_in_system:
        lines.append(f"  - 体系作用：{node.role_in_system}\n")
    if node.boundary:
        lines.append(f"  - 适用边界：{node.boundary}\n")
    if node.common_misreading:
        lines.append(f"  - 常见误读：{node.common_misreading}\n")
    if node.counter_case:
        lines.append(f"  - 反例：{node.counter_case}\n")
    return "".join(lines)


def _connection_protocol() -> str:
    return """
---

## 6. 层间连接协议（强制）

- 哲学 → 思维：提供推理检验标准，约束思维偏差
- 哲学 → 知识：检验知识的证据、边界、反例与升级路径
- 哲学 → 经验：规定经验解释口径，确保实证与具体分析
- 思维 → 哲学：把推理中的边界问题反馈为原原则适用提醒
- 思维 → 知识：把推理过程沉淀为结构化知识
- 思维 → 经验：决定如何观察、提问、记录与补证
- 知识 → 哲学：用稳定知识印证或挑战原原则边界
- 知识 → 思维：提升分析、洞察、批判、反思精度
- 知识 → 经验：转化为可执行行动与验证点
- 经验 → 哲学：新证据支持或挑战原原则
- 经验 → 思维：提供案例、反例与约束条件
- 经验 → 知识：归纳形成可复用知识
"""


def _output_protocol() -> str:
    return """
---

## 7. 输出协议

每轮至少完成：

1. 经验归档：本轮输入的事实、场景、约束与证据
2. 知识调用：涉及哪类知识
3. 思维执行：使用哪组核心思维节点
4. 哲学校验：哪些固定原原则在起作用
5. 外显落地：以角色设定一致的表达形式输出

每个关键结论必须包含：证据、边界、反例（或失效条件）。
若信息不足，标记为 `under_review`。
"""
