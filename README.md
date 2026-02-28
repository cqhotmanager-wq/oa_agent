# 企业 OA 智能 Agent 系统

基于 FastAPI + LangChain（Tool Calling / Agent）+ OpenAI + FAISS + MySQL 的企业 OA 智能助手，支持请假、报销与规章制度知识库问答。

## 技术栈

- **Web**: FastAPI
- **Agent**: LangChain（Tool Calling / AgentExecutor）
- **LLM**: OpenAI API
- **向量库**: FAISS（多 namespace）
- **数据库**: MySQL + SQLAlchemy ORM
- **定时任务**: APScheduler
- **测试**: pytest

## 项目结构

```
oa_agent/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── scheduler.py         # 定时任务
│   ├── api/routers/         # 路由（chat、意图分类）
│   ├── services/            # 业务（skill_engine、chat_service、db_service）
│   ├── agents/              # LangChain Agent 执行
│   ├── tools/               # RAG 等通用工具
│   ├── rag/                 # PDF 解析、FAISS、ingest
│   └── db/                  # 模型、session
├── config/
│   └── settings.py         # 配置（Pydantic Settings）
├── skills/                  # 动态技能目录（目录名即能力名）
│   ├── leave/
│   │   ├── SKILL.md        # 技能描述（替代原 config.yaml）
│   │   └── tools.py        # 请假工具
│   └── expense/
│       ├── SKILL.md
│       └── tools.py
├── policies/                # 规章制度 PDF
├── scripts/
│   └── init_db.sql         # MySQL 初始化
├── tests/                   # pytest
├── pyproject.toml          # 项目与依赖（uv 推荐，唯一依赖定义）
├── uv.lock                  # uv 锁文件（uv sync 生成，部署时用此锁定版本）
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 使用 uv 管理项目（推荐）

本项目使用 [uv](https://docs.astral.sh/uv/) 管理依赖与虚拟环境。**使用 UV 部署后不再需要 `requirements.txt`**，依赖以 `pyproject.toml` 与 `uv.lock` 为准。

### 安装 uv

```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 创建虚拟环境并安装依赖

```bash
cd oa_agent

# 使用 .python-version 指定 Python 版本（当前 3.11），创建 venv 并安装依赖
uv sync

# 仅安装生产依赖（不含 dev）
uv sync --no-dev
```

### 常用命令

```bash
# 安装依赖（与 lock 一致）
uv sync

# 添加新依赖
uv add <package>

# 添加开发依赖
uv add --dev <package>

# 运行应用
uv run python run.py
# 或
uv run uvicorn app.main:app --reload --port 8000

# 运行测试
uv run pytest

# 进入虚拟环境 shell（可选）
uv run python -c "import fastapi; print(fastapi.__file__)"
```

首次执行 `uv sync` 会生成 `uv.lock`，建议提交到仓库以保证环境一致。部署时执行 `uv sync --no-dev` 即可，无需 `requirements.txt`。

---

## 快速开始（pip 方式，可选）

若不使用 uv，仍可用 pip + `requirements.txt` 安装依赖（需自行从 `pyproject.toml` 导出或维护 `requirements.txt`）。

### 1. 环境

- Python 3.10+
- MySQL 8（或使用 SQLite 本地测试）

### 2. 配置

复制 `.env.example` 为 `.env`，按需填写：

```bash
cp .env.example .env
```

主要项：`OPENAI_API_KEY`、`MYSQL_*`（若用 MySQL）。

### 3. 数据库初始化（MySQL）

```bash
mysql -u root -p < scripts/init_db.sql
```

或使用 SQLite（无需 MySQL）时，应用启动时会自动建表。

### 4. 运行

```bash
# 开发
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或
python -m app.main
```

- 健康检查: http://localhost:8000/health  
- 对话接口: `POST /api/chat`，Body: `{"message": "我要请假3天", "use_llm_route": false}`  

## 功能说明

### 意图路由

- **请假**：关键词如「请假、休假、年假、事假、病假」→ 使用 `leave` 技能。
- **报销**：关键词如「报销、费用、差旅、发票」→ 使用 `expense` 技能。
- **知识库**：关键词如「制度、规定、政策、流程」→ 使用 RAG 检索 `policies` 下 PDF。

支持关键词 fallback；可扩展为 LLM 分类（`use_llm_route=true`）。

### 技能（Skill）

- 在 `skills/` 下每个子目录为一技能，**目录名描述能力**；目录内为 `SKILL.md` + 可选 `tools.py`。
- `SKILL.md`：技能描述，可含 YAML frontmatter（`description`、`namespace`、`keywords`）；技能名以目录名为准。
- `tools.py`：提供 `make_xxx_tools(get_db_session)`，返回 LangChain Tools 列表。
- 定时任务每天扫描 `skills/`，实现热加载能力。

### RAG

- 将 `policies/` 下 PDF 解析、分块、向量化后写入 FAISS。
- 按 namespace 隔离（如 `default`、按制度类型等）。
- 查询时返回 top-k 相关片段。

### 定时任务（APScheduler）

- 每天 2:00 扫描 skills。
- 每天 3:00 更新 FAISS（重新解析 policies）。
- 每天 4:00 清理 90 天前的 `agent_logs`。

## 测试

```bash
pytest
# 指定文件
pytest tests/test_intent_router.py tests/test_api.py -v
```

- `test_skill_engine.py`：技能加载。
- `test_intent_router.py`：意图分类。
- `test_rag.py`：RAG 分块与检索。
- `test_leave_tool.py`：请假服务与“已提交”结果。
- `test_api.py`：/health、/api/chat。

## Docker（可选）

```bash
docker-compose up -d
```

- 服务端口 8000；MySQL 3306；需在 `.env` 或 `docker-compose` 中配置 `OPENAI_API_KEY` 和数据库连接。

## 生产建议

- 配置文件驱动（`.env` / `config/settings.py`）。
- 技能通过 `skills/` 动态扩展，无需改主代码。
- RAG 使用 namespace 隔离不同制度/文档集。
- MySQL 持久化业务与审计日志；异常处理与单元测试已做基础覆盖。

## License

MIT
