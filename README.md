# Fuxi 伏羲认知框架

> We seek the meaning of AI.

伏羲是一个**可分发的 AI 认知操作协议**——文档与代码的组合体。它不是工具（MCP），不是静态指令（Skill），而是一套让 AI 获得**结构化思考、自我评估与持续进化**能力的框架。

## 核心接口

| 接口 | 功能 |
|------|------|
| `POST /evaluate` | 对系统提示词或 Agent 输出做结构化评分（静态/动态/混合） |
| `POST /compile` | 将四层结构化数据编译为可部署的系统提示词 |
| `POST /validate` | 检查 Agent 数据是否符合四层架构规范 |
| `POST /create-role` | 输入角色名 → 自动完成研究、画像、编译、评估全流程 |
| `GET/POST/PUT/DELETE /agents` | Agent 的增删改查、版本管理与评估历史 |

## 四种使用方式

### 1. API 服务

```bash
pip install -r requirements.txt
cp .env.example .env   # 填入 LLM API Key
python cli.py server --reload
# → http://localhost:8000/docs  查看交互式 API 文档
```

### 2. 命令行 CLI

```bash
# 校验 Agent 数据
python cli.py validate --input examples/nagel/agent.json

# 编译 Agent 为系统提示词
python cli.py compile --input examples/nagel/agent.json --output output.md

# 评估系统提示词
python cli.py evaluate --input some-prompt.md --mode static

# 管理 Agent
python cli.py agents list
python cli.py agents get nagel_001
```

### 3. MCP 接入（Cursor / Claude Desktop）

在 MCP 配置中添加：

```json
{
  "mcpServers": {
    "fuxi": {
      "command": "python3",
      "args": ["-m", "mcp.server"],
      "cwd": "/path/to/Fuxi-prompt-system"
    }
  }
}
```

提供的 MCP 工具：`fuxi_evaluate` / `fuxi_compile` / `fuxi_validate` / `fuxi_list_agents` / `fuxi_get_agent`

### 4. 直接使用 Prompt

不想跑代码？把 `prompts/` 目录里的文件直接复制到任何 AI 平台也能用：

- `prompts/mother.md` — 伏羲母体认知架构
- `prompts/evaluator.md` — 四层架构评估器
- `prompts/factory.md` — 角色创建工作流

## 项目结构

```
├── api/                # API 服务（FastAPI）
│   ├── main.py         # 入口
│   └── routers/        # 路由
│       ├── evaluate.py
│       ├── compile.py
│       ├── validate.py
│       ├── create_role.py
│       └── agents.py
├── core/               # 伏羲内核（纯逻辑，不依赖 HTTP）
│   ├── models.py       # 数据模型
│   ├── evaluator.py    # 评估引擎
│   ├── compiler.py     # Prompt 编译器
│   ├── validator.py    # 四层数据校验器
│   ├── factory.py      # 角色工厂引擎
│   ├── storage.py      # JSON 文件存储
│   └── llm.py          # LLM 调用封装
├── prompts/            # Prompt 资产（可直接跨平台使用）
├── mcp/                # MCP Server
├── cli.py              # 命令行工具
├── examples/           # 示例 Agent
│   └── nagel/          # 托马斯·内格尔完整示例
├── storage/            # 运行时数据存储
└── docs/               # 理论文档
    ├── papers/         # 论文 02-07
    ├── discussions/    # 自我/非我讨论三轮
    └── math/           # 数学形式化
```

## 架构设计

`core/` 是纯逻辑层，不依赖任何接入方式。API、MCP、CLI 都是 `core/` 的包装层，共享同一个内核。

```
任何平台 / MCP Client / 开发者代码 / CLI
          ↓
    API 接口层（FastAPI）/ MCP Server / CLI
          ↓
    伏羲内核（core/）
    ├── evaluator  评估引擎
    ├── compiler   Prompt 编译器
    ├── validator  四层校验器
    ├── factory    角色工厂
    └── storage    持久化
          ↓
    Prompt 资产（prompts/）+ LLM API
```

## 快速体验

```bash
# 1. 校验内格尔示例
python cli.py validate --input examples/nagel/agent.json
# → Status: VALID
# → Quality scores: experience_density=1.0, knowledge_density=0.97, ...

# 2. 编译为系统提示词
python cli.py compile --input examples/nagel/agent.json
# → 输出完整的、可直接部署的系统提示词

# 3. 启动 API，打开 /docs 查看所有接口
python cli.py server --reload
```

## 理论基础

详见 `docs/` 目录，涵盖：

- 四层双向贯通认知架构
- 动态熵机制与评估数学
- 自我与非我统一智能模型
- 三阶段演化模型
- 从系统提示词到认知操作协议
