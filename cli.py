#!/usr/bin/env python3
"""
Fuxi CLI — command-line interface for the Fuxi Cognitive Framework.

Usage:
  python cli.py evaluate --input prompt.md --mode static
  python cli.py compile  --input agent.json --output prompt.md
  python cli.py validate --input agent.json
  python cli.py agents   list
  python cli.py agents   get <id>
  python cli.py server   [--port 8000]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from core.models import Agent, EvaluateRequest, EvaluationMode
from core.compiler import compile_agent
from core.validator import validate
from core.storage import list_agents, load_agent


def cmd_evaluate(args):
    from core.evaluator import evaluate as run_evaluate

    content = Path(args.input).read_text(encoding="utf-8")
    req = EvaluateRequest(
        mode=EvaluationMode(args.mode),
        system_prompt=content if args.mode in ("static", "hybrid") else "",
    )
    report = asyncio.run(run_evaluate(req))

    if args.json:
        print(report.model_dump_json(indent=2))
    else:
        _print_report(report)


def cmd_compile(args):
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    agent = Agent.model_validate(data)
    prompt, warnings = compile_agent(agent)

    if args.output:
        Path(args.output).write_text(prompt, encoding="utf-8")
        print(f"Compiled prompt written to {args.output}")
    else:
        print(prompt)

    if warnings:
        print(f"\n--- {len(warnings)} warnings ---", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)


def cmd_validate(args):
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    agent = Agent.model_validate(data)
    result = validate(agent)

    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        status = "VALID" if result.valid else "INVALID"
        print(f"Status: {status}")
        print(f"Quality scores: {result.quality_scores}")
        if result.issues:
            print(f"\nIssues ({len(result.issues)}):")
            for issue in result.issues:
                print(f"  [{issue.severity}] {issue.layer}: {issue.message}")


def cmd_agents(args):
    if args.action == "list":
        agents = list_agents()
        if not agents:
            print("No agents found.")
            return
        for a in agents:
            print(f"  {a['id']}  {a['name']}  (v{a['version']}, {a['role_type'] or 'generic'})")

    elif args.action == "get":
        if not args.agent_id:
            print("Error: agent_id required", file=sys.stderr)
            sys.exit(1)
        agent = load_agent(args.agent_id)
        if not agent:
            print(f"Agent '{args.agent_id}' not found", file=sys.stderr)
            sys.exit(1)
        print(agent.model_dump_json(indent=2))


def cmd_server(args):
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


def _print_report(report):
    print(f"Mode: {report.mode.value}")
    if report.score_static is not None:
        print(f"Static Score: {report.score_static:.1f} ({report.static_rating})")
    if report.score_runtime is not None:
        print(f"Dynamic Score: {report.score_runtime:.1f} ({report.dynamic_rating})")
    if report.j_t is not None:
        print(f"J_t: {report.j_t:.3f}")
    print(f"Passed: {report.passed}")

    if report.strengths:
        print("\nStrengths:")
        for s in report.strengths:
            print(f"  + {s}")
    if report.weaknesses:
        print("\nWeaknesses:")
        for w in report.weaknesses:
            print(f"  - {w}")
    if report.suggestions:
        print("\nSuggestions:")
        for s in report.suggestions:
            print(f"  > {s}")


def main():
    parser = argparse.ArgumentParser(
        prog="fuxi",
        description="Fuxi Cognitive Framework CLI",
    )
    sub = parser.add_subparsers(dest="command")

    # evaluate
    p_eval = sub.add_parser("evaluate", help="评估系统提示词或对话输出")
    p_eval.add_argument("--input", "-i", required=True, help="输入文件路径")
    p_eval.add_argument("--mode", "-m", default="static", choices=["static", "dynamic", "hybrid"])
    p_eval.add_argument("--json", action="store_true", help="输出 JSON 格式")

    # compile
    p_comp = sub.add_parser("compile", help="编译 Agent JSON 为系统提示词")
    p_comp.add_argument("--input", "-i", required=True, help="Agent JSON 文件路径")
    p_comp.add_argument("--output", "-o", default="", help="输出文件路径（默认 stdout）")

    # validate
    p_val = sub.add_parser("validate", help="校验 Agent 数据")
    p_val.add_argument("--input", "-i", required=True, help="Agent JSON 文件路径")
    p_val.add_argument("--json", action="store_true", help="输出 JSON 格式")

    # agents
    p_agents = sub.add_parser("agents", help="管理已保存的 Agent")
    p_agents.add_argument("action", choices=["list", "get"])
    p_agents.add_argument("agent_id", nargs="?", default="")

    # server
    p_server = sub.add_parser("server", help="启动 API 服务")
    p_server.add_argument("--host", default="0.0.0.0")
    p_server.add_argument("--port", "-p", type=int, default=8000)
    p_server.add_argument("--reload", action="store_true")

    args = parser.parse_args()

    if args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "compile":
        cmd_compile(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "agents":
        cmd_agents(args)
    elif args.command == "server":
        cmd_server(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
