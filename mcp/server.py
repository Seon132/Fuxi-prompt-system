"""
Fuxi MCP Server — exposes Fuxi capabilities as MCP tools.

Usage:
  python -m mcp.server

Configure in Claude Desktop / Cursor MCP settings:
  {
    "mcpServers": {
      "fuxi": {
        "command": "python",
        "args": ["-m", "mcp.server"],
        "cwd": "/path/to/Fuxi-prompt-system"
      }
    }
  }
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False


if HAS_MCP:
    from core.compiler import compile_agent
    from core.evaluator import evaluate as run_evaluate
    from core.models import Agent, EvaluateRequest, EvaluationMode
    from core.validator import validate as run_validate
    from core.storage import save_agent, load_agent, list_agents

    server = Server("fuxi")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="fuxi_evaluate",
                description="评估一份系统提示词或 Agent 输出的质量。返回结构化评分报告（分项分数、总分、优缺点、修改建议）。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "system_prompt": {
                            "type": "string",
                            "description": "要评估的系统提示词文本",
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["static", "dynamic", "hybrid"],
                            "default": "static",
                        },
                        "conversation_log": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "对话记录（dynamic/hybrid 模式使用）",
                            "default": [],
                        },
                    },
                    "required": ["system_prompt"],
                },
            ),
            Tool(
                name="fuxi_compile",
                description="将四层结构化 Agent 数据编译为可部署的系统提示词。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent": {
                            "type": "object",
                            "description": "Agent 四层结构化数据（含 name, experience, knowledge, thinking, philosophy, expression）",
                        },
                    },
                    "required": ["agent"],
                },
            ),
            Tool(
                name="fuxi_validate",
                description="校验 Agent 数据是否符合伏羲四层架构规范。返回问题列表和各层质量分数。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent": {
                            "type": "object",
                            "description": "Agent 四层结构化数据",
                        },
                    },
                    "required": ["agent"],
                },
            ),
            Tool(
                name="fuxi_list_agents",
                description="列出所有已保存的 Agent。",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="fuxi_get_agent",
                description="获取某个 Agent 的完整数据和编译后的提示词。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string"},
                    },
                    "required": ["agent_id"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "fuxi_evaluate":
            req = EvaluateRequest(
                mode=EvaluationMode(arguments.get("mode", "static")),
                system_prompt=arguments.get("system_prompt", ""),
                conversation_log=arguments.get("conversation_log", []),
            )
            report = await run_evaluate(req)
            return [TextContent(
                type="text",
                text=report.model_dump_json(indent=2),
            )]

        elif name == "fuxi_compile":
            agent = Agent.model_validate(arguments["agent"])
            prompt, warnings = compile_agent(agent)
            result = {"system_prompt": prompt, "warnings": warnings}
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        elif name == "fuxi_validate":
            agent = Agent.model_validate(arguments["agent"])
            result = run_validate(agent)
            return [TextContent(type="text", text=result.model_dump_json(indent=2))]

        elif name == "fuxi_list_agents":
            agents = list_agents()
            return [TextContent(type="text", text=json.dumps(agents, ensure_ascii=False, indent=2))]

        elif name == "fuxi_get_agent":
            agent = load_agent(arguments["agent_id"])
            if not agent:
                return [TextContent(type="text", text=f"Agent '{arguments['agent_id']}' not found")]
            prompt, _ = compile_agent(agent)
            result = {"agent": agent.model_dump(), "system_prompt": prompt}
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream)

else:
    async def main():
        print("Error: MCP SDK not installed. Run: pip install mcp")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
