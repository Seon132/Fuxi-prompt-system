from fastapi import APIRouter

from core.models import ValidateRequest, ValidateResponse
from core.validator import validate

router = APIRouter()


@router.post("/validate", response_model=ValidateResponse)
async def validate_endpoint(req: ValidateRequest):
    """
    校验 Agent 数据是否符合伏羲四层架构规范。
    返回是否合法、问题列表与各层质量分数。
    """
    result = validate(req.agent)
    return ValidateResponse(result=result)
