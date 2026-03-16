from pydantic import BaseModel, Field
from fastapi import APIRouter

from core.factory import CreateRoleRequest, create_role
from core.storage import save_agent, save_evaluation

router = APIRouter()


class CreateRoleAPIRequest(BaseModel):
    role_name: str
    role_type: str = ""
    description: str = ""
    materials: str = Field(default="", description="可选的参考资料文本")
    auto_evaluate: bool = True
    max_iterations: int = Field(default=2, ge=1, le=5)


@router.post("/create-role")
async def create_role_endpoint(req: CreateRoleAPIRequest):
    """
    自动化角色创建：输入角色名 → 自动完成研究、四层画像生成、编译、评估全流程。
    若 auto_evaluate=true，会自动迭代优化直到通过静态评估或达到最大迭代次数。
    """
    result = await create_role(CreateRoleRequest(
        role_name=req.role_name,
        role_type=req.role_type,
        description=req.description,
        materials=req.materials,
        auto_evaluate=req.auto_evaluate,
        max_iterations=req.max_iterations,
    ))

    saved = save_agent(result.agent)

    if result.evaluation_report:
        save_evaluation(saved.id, result.evaluation_report)

    resp = {
        "agent": saved.model_dump(),
        "system_prompt": result.system_prompt,
        "iterations": result.iterations,
        "status": result.status,
    }
    if result.evaluation_report:
        resp["evaluation_report"] = result.evaluation_report.model_dump()

    return resp
