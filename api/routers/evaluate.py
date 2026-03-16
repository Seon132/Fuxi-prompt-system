from fastapi import APIRouter

from core.evaluator import evaluate as run_evaluate
from core.models import EvaluateRequest, EvaluateResponse

router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_endpoint(req: EvaluateRequest):
    """
    评估一份系统提示词（static）、一次对话输出（dynamic）或两者兼有（hybrid）。
    返回结构化评分报告，包含分项分数、总分、评级、优缺点与修改建议。
    """
    report = await run_evaluate(req)
    return EvaluateResponse(report=report)
