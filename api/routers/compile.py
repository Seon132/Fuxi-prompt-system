from fastapi import APIRouter

from core.compiler import compile_agent
from core.models import CompileRequest, CompileResponse

router = APIRouter()


@router.post("/compile", response_model=CompileResponse)
async def compile_endpoint(req: CompileRequest):
    """
    将四层结构化 Agent 数据编译为可部署的系统提示词。
    同时返回校验警告（如有）。
    """
    system_prompt, warnings = compile_agent(req.agent)
    return CompileResponse(
        system_prompt=system_prompt,
        validation_warnings=warnings,
    )
