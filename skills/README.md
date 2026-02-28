# Skills 目录规范

技能以**目录**为单位存放，目录名即技能 ID（**英文 + 短横线**，如 `leave`、`expense`、`your-skill-name`）。

## 标准目录结构

```
your-skill-name/           # 技能文件夹，名称即技能 ID（英文+短横线）
├── SKILL.md               # 核心：技能定义文件（必须）
├── scripts/               # 可选：存放可执行的脚本（.py, .sh, .js）
├── assets/                # 可选：存放模板、配置文件等资源
└── references/            # 可选：存放参考文档（用于该技能专属的向量检索）
```

| 路径 | 必须 | 说明 |
|------|------|------|
| **SKILL.md** | 是 | 技能定义与描述；可含 YAML frontmatter，见下文。技能名以目录名为准。 |
| **scripts/** | 否 | 可执行脚本（.py / .sh / .js）。工具入口：优先 `scripts/tools.py`，若无则使用根目录 `tools.py`。 |
| **assets/** | 否 | 模板、配置文件等静态资源。 |
| **references/** | 否 | 该技能专属参考文档。若在 SKILL.md 中配置 `rag_namespace`，仅在**使用该技能**时才会从向量数据库加载并检索此 namespace。 |

## SKILL.md 说明

- 支持 **YAML frontmatter**（`---` 包裹）+ 正文。
- 常用 frontmatter 字段：
  - `description`：简短描述
  - `namespace`：命名空间（默认取目录名）
  - `keywords`：关键词列表，用于意图路由
  - `rag_namespace`：可选；该技能专属向量索引的 namespace，仅在选用该技能时才会加载并检索

示例：

```yaml
---
description: 请假申请技能，支持提交请假、查询请假记录
namespace: leave
keywords:
  - 请假
  - 休假
  - 年假
rag_namespace: leave_refs   # 可选，对应 data/faiss 下 leave_refs 索引
---

# 请假 (leave)

技能正文说明……
```

## 工具加载顺序

- 若存在 `scripts/tools.py`，则从该文件加载工具（`make_xxx_tools(get_db_session)`）。
- 否则从根目录 `tools.py` 加载。
- 工具工厂需返回 LangChain Tools 列表。

## 向量库加载时机

向量数据库（FAISS）**仅在真正使用到需要 RAG 的能力时才加载**：

- 用户命中**知识库**意图 → 仅此时加入 default namespace 的 RAG 工具，检索时再加载。
- 某技能被选用且配置了 **rag_namespace** → 仅在该请求中加入该 namespace 的 RAG 工具，检索时再加载。
- 未识别意图 → 汇总所有技能工具，并为配置了 `rag_namespace` 的技能各加对应 RAG 工具，再外加 default。

应用启动时不会预加载任何 FAISS 索引；索引在 Agent 实际调用 RAG 工具时按 namespace 按需加载。
