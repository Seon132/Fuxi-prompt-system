"""
Fuxi Cognitive Framework — Data Models

Defines the four-layer Agent structure, evaluation reports,
and all request/response schemas used across the framework.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Experience Layer
# ---------------------------------------------------------------------------

class ExperienceType(str, Enum):
    direct = "direct"
    indirect = "indirect"
    reflective = "reflective"


class ExperienceNode(BaseModel):
    id: str
    claim: str = Field(..., description="核心主张/事实陈述")
    evidence: str = Field(default="", description="支撑证据")
    context: str = Field(default="", description="情境说明")
    experience_type: ExperienceType
    source_domain: str = Field(default="", description="来源领域")
    source_role: str = Field(default="", description="来源角色")
    source_medium: str = Field(default="", description="来源媒介（书籍/访谈/课程等）")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    lesson: str = Field(default="", description="沉淀的教训/模式（反思经验用）")


class ExperienceLayer(BaseModel):
    direct: list[ExperienceNode] = Field(default_factory=list)
    indirect: list[ExperienceNode] = Field(default_factory=list)
    reflective: list[ExperienceNode] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Knowledge Layer
# ---------------------------------------------------------------------------

class KnowledgeLevel(str, Enum):
    individual = "individual"
    professional = "professional"
    universal = "universal"


class KnowledgeType(str, Enum):
    conceptual = "conceptual"
    procedural = "procedural"
    causal = "causal"
    evaluative = "evaluative"


class KnowledgeNode(BaseModel):
    id: str
    statement: str = Field(..., description="知识主张")
    definition: str = Field(default="", description="概念定义")
    role_in_system: str = Field(default="", description="在体系中的作用")
    common_misreading: str = Field(default="", description="常见误读")
    boundary: str = Field(default="", description="适用边界")
    counter_case: str = Field(default="", description="反例/失效条件")
    level: KnowledgeLevel
    knowledge_type: KnowledgeType = KnowledgeType.conceptual
    derived_from: str = Field(default="", description="来源经验 ID")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class KnowledgeLayer(BaseModel):
    individual: list[KnowledgeNode] = Field(default_factory=list)
    professional: list[KnowledgeNode] = Field(default_factory=list)
    universal: list[KnowledgeNode] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Thinking Layer
# ---------------------------------------------------------------------------

class ThinkingCapability(BaseModel):
    id: str
    name: str
    definition: str = Field(default="", description="能力定义")
    trigger: str = Field(default="", description="触发条件")
    steps: list[str] = Field(default_factory=list, description="执行步骤")
    anti_pattern: str = Field(default="", description="常见反模式")
    excellence_criteria: str = Field(default="", description="高质量判据")
    failure_pattern: str = Field(default="", description="失败模式")
    principle_binding: list[str] = Field(
        default_factory=list,
        description="绑定的哲学原则（如 P1, P3）",
    )


class ThinkingLayer(BaseModel):
    analysis: Optional[ThinkingCapability] = None
    synthesis: Optional[ThinkingCapability] = None
    insight: Optional[ThinkingCapability] = None
    critical: Optional[ThinkingCapability] = None
    reflection: Optional[ThinkingCapability] = None
    additional: list[ThinkingCapability] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Philosophy Layer
# ---------------------------------------------------------------------------

FIXED_PRINCIPLES = [
    "P1_essentialism",
    "P2_first_principles",
    "P3_systematic_thinking",
    "P4_dialectics",
    "P5_contradiction",
    "P6_concrete_analysis",
    "P7_positivism",
    "P8_pragmatism",
]


class ExtensionPrinciple(BaseModel):
    id: str
    name: str
    description: str = Field(default="", description="原则内容")
    bound_to: list[str] = Field(
        default_factory=list,
        description="受哪些固定原原则门控",
    )
    scope: str = Field(default="", description="适用范围")


class PhilosophyLayer(BaseModel):
    fixed_principles: list[str] = Field(
        default_factory=lambda: list(FIXED_PRINCIPLES),
        description="固定原原则集（不可删除/替换/降级）",
    )
    extension_principles: list[ExtensionPrinciple] = Field(default_factory=list)
    p_loop: str = Field(
        default="experience -> knowledge -> thinking -> philosophy -> thinking -> knowledge -> experience",
        description="体系性思维闭环路径",
    )


# ---------------------------------------------------------------------------
# Expression Layer
# ---------------------------------------------------------------------------

class SpeechHabits(BaseModel):
    tone_intensity: str = Field(default="neutral", description="语气强度：温和/中性/犀利")
    sentence_preference: str = Field(default="mixed", description="句式偏好：短句/长句/条列")
    vocabulary_style: str = Field(default="professional", description="用词风格")
    rhythm: str = Field(default="steady", description="节奏控制")


class DialogueStyle(BaseModel):
    organization: str = Field(default="conclusion_first", description="组织方式")
    interaction: str = Field(default="guided", description="互动方式")
    conflict_handling: str = Field(default="principle_first", description="冲突处理")
    explanation_depth: str = Field(default="standard", description="解释深度")


class PersonalityAxes(BaseModel):
    introversion_extroversion: float = Field(default=0.5, ge=0.0, le=1.0)
    rationality: float = Field(default=0.7, ge=0.0, le=1.0)
    idealism_pragmatism: float = Field(default=0.5, ge=0.0, le=1.0)
    altruism: float = Field(default=0.5, ge=0.0, le=1.0)
    sharpness: float = Field(default=0.5, ge=0.0, le=1.0)


class ExpressionLayer(BaseModel):
    speech_habits: SpeechHabits = Field(default_factory=SpeechHabits)
    dialogue_style: DialogueStyle = Field(default_factory=DialogueStyle)
    personality: PersonalityAxes = Field(default_factory=PersonalityAxes)
    target_audience: str = Field(default="")
    boundary_rules: str = Field(default="")


# ---------------------------------------------------------------------------
# Agent (complete four-layer structure)
# ---------------------------------------------------------------------------

class Agent(BaseModel):
    id: str = Field(default="")
    name: str
    role_type: str = Field(default="", description="角色类型（philosopher/writer/scientist 等）")
    description: str = Field(default="")
    experience: ExperienceLayer = Field(default_factory=ExperienceLayer)
    knowledge: KnowledgeLayer = Field(default_factory=KnowledgeLayer)
    thinking: ThinkingLayer = Field(default_factory=ThinkingLayer)
    philosophy: PhilosophyLayer = Field(default_factory=PhilosophyLayer)
    expression: ExpressionLayer = Field(default_factory=ExpressionLayer)
    version: int = Field(default=1)


# ---------------------------------------------------------------------------
# Evaluation Models
# ---------------------------------------------------------------------------

class EvaluationMode(str, Enum):
    static = "static"
    dynamic = "dynamic"
    hybrid = "hybrid"


class StaticSubscores(BaseModel):
    S_order: float = Field(0.0, ge=0.0, le=1.0, description="四层顺序与稳定性")
    S_edge: float = Field(0.0, ge=0.0, le=1.0, description="层间连接协议")
    S_core: float = Field(0.0, ge=0.0, le=1.0, description="层内核心/次级/边缘区分")
    S_combo: float = Field(0.0, ge=0.0, le=1.0, description="多节点协同与冲突处理")
    S_closure: float = Field(0.0, ge=0.0, le=1.0, description="闭环回写与反馈更新")
    S_rule: float = Field(0.0, ge=0.0, le=1.0, description="证据/边界/反例/降级/审核规则")
    S_philosophy_constitution: float = Field(0.0, ge=0.0, le=1.0, description="固定原原则与闭环完整性")

    def total(self) -> float:
        return 100 * (
            0.12 * self.S_order
            + 0.16 * self.S_edge
            + 0.16 * self.S_core
            + 0.12 * self.S_combo
            + 0.12 * self.S_closure
            + 0.12 * self.S_rule
            + 0.20 * self.S_philosophy_constitution
        )


class DynamicSubscores(BaseModel):
    S_order_dyn: float = Field(0.0, ge=0.0, le=1.0)
    S_edge_dyn: float = Field(0.0, ge=0.0, le=1.0)
    S_combo_dyn: float = Field(0.0, ge=0.0, le=1.0)
    S_valid: float = Field(0.0, ge=0.0, le=1.0)
    S_control: float = Field(0.0, ge=0.0, le=1.0)
    S_writeback: float = Field(0.0, ge=0.0, le=1.0)
    S_revise: float = Field(0.0, ge=0.0, le=1.0)
    S_philosophy_enforce: float = Field(0.0, ge=0.0, le=1.0)

    def total(self) -> float:
        return 100 * (
            0.12 * self.S_order_dyn
            + 0.12 * self.S_edge_dyn
            + 0.16 * self.S_combo_dyn
            + 0.18 * self.S_valid
            + 0.10 * self.S_control
            + 0.10 * self.S_writeback
            + 0.10 * self.S_revise
            + 0.12 * self.S_philosophy_enforce
        )


class AuditScores(BaseModel):
    """J_t output-gate scores."""
    Consistency: float = Field(0.0, ge=0.0, le=1.0)
    EvidenceCov: float = Field(0.0, ge=0.0, le=1.0)
    GoalFit: float = Field(0.0, ge=0.0, le=1.0)
    EntropyExcess: float = Field(0.0, ge=0.0, le=1.0)
    RuleViolation: float = Field(0.0, ge=0.0, le=1.0)
    UnsafeRisk: float = Field(0.0, ge=0.0, le=1.0)

    def j_t(self, score_runtime: float) -> float:
        norm = score_runtime / 100.0
        return (
            0.30 * norm
            + 0.15 * self.Consistency
            + 0.15 * self.EvidenceCov
            + 0.15 * self.GoalFit
            - 0.10 * self.EntropyExcess
            - 0.10 * self.RuleViolation
            - 0.05 * self.UnsafeRisk
        )

    def forced_reject(self) -> list[str]:
        reasons = []
        if self.RuleViolation >= 0.30:
            reasons.append("RuleViolation >= 0.30")
        if self.UnsafeRisk >= 0.25:
            reasons.append("UnsafeRisk >= 0.25")
        if self.EvidenceCov < 0.50:
            reasons.append("EvidenceCov < 0.50")
        if self.GoalFit < 0.60:
            reasons.append("GoalFit < 0.60")
        return reasons


def static_rating(score: float) -> str:
    if score >= 85:
        return "优秀，可部署"
    if score >= 70:
        return "良好，可试运行"
    if score >= 60:
        return "及格，结构偏弱"
    return "不建议部署"


def dynamic_rating(score: float) -> str:
    if score >= 85:
        return "高质量输出"
    if score >= 70:
        return "可接受输出"
    if score >= 60:
        return "低质量但可修复"
    return "不达标，触发重排"


class EvaluationReport(BaseModel):
    mode: EvaluationMode
    static_subscores: Optional[StaticSubscores] = None
    score_static: Optional[float] = None
    static_rating: Optional[str] = None
    dynamic_subscores: Optional[DynamicSubscores] = None
    score_runtime: Optional[float] = None
    dynamic_rating: Optional[str] = None
    audit: Optional[AuditScores] = None
    j_t: Optional[float] = None
    passed: bool = False
    forced_reject_reasons: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    extension_principle_notes: str = Field(default="")
    audit_notes: str = Field(default="")


# ---------------------------------------------------------------------------
# Validation Models
# ---------------------------------------------------------------------------

class ValidationIssue(BaseModel):
    layer: str
    severity: str = Field(description="error | warning | info")
    message: str


class ValidationResult(BaseModel):
    valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    quality_scores: dict[str, float] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# API Request / Response schemas
# ---------------------------------------------------------------------------

class EvaluateRequest(BaseModel):
    mode: EvaluationMode = EvaluationMode.static
    system_prompt: str = Field(default="", description="要评估的系统提示词（static/hybrid）")
    conversation_log: list[dict] = Field(default_factory=list, description="对话记录（dynamic/hybrid）")
    candidate_output: str = Field(default="", description="候选输出（dynamic 可选）")


class EvaluateResponse(BaseModel):
    report: EvaluationReport


class CompileRequest(BaseModel):
    agent: Agent


class CompileResponse(BaseModel):
    system_prompt: str
    validation_warnings: list[str] = Field(default_factory=list)


class ValidateRequest(BaseModel):
    agent: Agent


class ValidateResponse(BaseModel):
    result: ValidationResult
