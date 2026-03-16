from fastapi import APIRouter, HTTPException

from core.compiler import compile_agent
from core.models import Agent
from core.storage import delete_agent, list_agents, load_agent, save_agent, list_evaluations

router = APIRouter()


@router.get("/agents")
async def get_agents():
    """获取所有已保存的 Agent 列表。"""
    return {"agents": list_agents()}


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """获取某个 Agent 的完整数据（四层结构 + 编译后提示词 + 评估历史）。"""
    agent = load_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    system_prompt, _ = compile_agent(agent)
    evals = list_evaluations(agent_id)

    return {
        "agent": agent.model_dump(),
        "system_prompt": system_prompt,
        "evaluation_history": evals,
    }


@router.put("/agents/{agent_id}")
async def update_agent(agent_id: str, agent: Agent):
    """更新 Agent 数据。自动触发重新编译。"""
    existing = load_agent(agent_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    agent.id = agent_id
    agent.version = existing.version + 1
    saved = save_agent(agent)
    system_prompt, warnings = compile_agent(saved)

    return {
        "agent": saved.model_dump(),
        "system_prompt": system_prompt,
        "validation_warnings": warnings,
        "version": saved.version,
    }


@router.delete("/agents/{agent_id}")
async def remove_agent(agent_id: str):
    """删除一个 Agent。"""
    if not delete_agent(agent_id):
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return {"deleted": agent_id}


@router.post("/agents")
async def create_agent(agent: Agent):
    """手动创建并保存一个 Agent（不经过角色工厂）。"""
    saved = save_agent(agent)
    system_prompt, warnings = compile_agent(saved)
    return {
        "agent": saved.model_dump(),
        "system_prompt": system_prompt,
        "validation_warnings": warnings,
    }
