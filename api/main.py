"""
Fuxi Cognitive Framework — API Entry Point
"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from .routers import agents, compile, create_role, evaluate, validate  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Fuxi Cognitive Framework",
    description=(
        "伏羲认知框架 API —— 评估、编译、校验、创建 AI Agent 的四层认知架构服务。\n\n"
        "核心接口：evaluate / compile / validate / create-role / agents CRUD"
    ),
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(evaluate.router, prefix="/api/v1", tags=["evaluate"])
app.include_router(compile.router, prefix="/api/v1", tags=["compile"])
app.include_router(validate.router, prefix="/api/v1", tags=["validate"])
app.include_router(create_role.router, prefix="/api/v1", tags=["create-role"])
app.include_router(agents.router, prefix="/api/v1", tags=["agents"])


@app.get("/health")
async def health():
    return {"status": "ok", "framework": "fuxi", "version": "0.1.0"}
