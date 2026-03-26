# 灵机 (Lingji) — 角色生成元角色

灵机是伏羲框架下的**角色宪法工程师**——专门负责创建、评估、修订、归档 AI 角色的元角色。

## 与 Nagel 示例的区别

| 维度 | 托马斯·内格尔 | 灵机 |
|------|-------------|------|
| 角色类型 | 领域角色（哲学家） | 元角色（角色工程师） |
| 核心任务 | 心灵哲学与道德哲学讨论 | 创建、评估、修订其他角色 |
| 思维层重点 | 概念分析、视角转换、论证审查 | 任务解析、四层画像生成、类型辨识、评估放行、漂移纠偏 |
| 知识层重点 | 主观经验不可还原、道德实在论等哲学论题 | 角色类型矩阵、交付深度分层、评估-修订映射、回写分类规则 |

## 文件说明

- `agent.json` — 灵机的四层结构化数据，符合 `core/models.py` 的 Pydantic schema
- `compiled-prompt.md` — 由 `core/compiler.py` 编译生成的可部署系统提示词

## 使用方式

**验证 agent.json：**

```bash
python cli.py validate --input examples/lingji/agent.json
```

**编译为系统提示词：**

```bash
python cli.py compile --input examples/lingji/agent.json --output examples/lingji/compiled-prompt.md
```

**通过 API 编译：**

```bash
curl -X POST http://localhost:8000/api/v1/compile \
  -H "Content-Type: application/json" \
  -d '{"agent": '"$(cat examples/lingji/agent.json)"'}'
```

## 内容来源

灵机的四层数据完全从以下文档提炼：

- `docs/灵机/灵机-01-总纲与整合部署说明-V0.3.md` — 整体架构和工作优先级
- `docs/灵机/灵机-02-核心系统提示词-V0.1.md` — 四层最低要求、评估门槛、回写规则
- `docs/灵机/灵机-03-任务输入模板-V0.3.md` — 输入字段定义
- `docs/灵机/灵机-04-任务输出模板-V0.3.md` — 输出协议

## 验证结果

```json
{
  "valid": true,
  "quality_scores": {
    "experience_density": 1.0,
    "knowledge_density": 0.98,
    "thinking_executability": 1.0,
    "philosophy_completeness": 1.0
  }
}
```
