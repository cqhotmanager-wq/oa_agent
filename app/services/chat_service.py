"""Chat 服务：意图路由 -> 选择技能 -> 构建 Agent -> 执行并写日志."""
from typing import Any, Callable, Dict, Generator, List, Optional

from app.agents.runner import build_agent_executor, run_agent
from app.api.routers.intent_router import route_intent, IntentType
from app.services.skill_engine import scan_skills
from app.tools.rag_tool import make_rag_tool


def get_db_session_generator(get_db) -> Generator:
    """将 FastAPI 依赖 get_db（生成器）包装成 skill engine 所需的 callable。"""
    def _gen():
        yield from get_db()
    return _gen


def collect_tools_for_intent(
    intent: IntentType,
    get_db_session: Callable,
) -> List[Any]:
    """
    根据意图收集工具列表：leave -> leave tools; expense -> expense tools; knowledge -> RAG tool.
    可扩展：同时加入 RAG（如 knowledge 或所有意图都带 RAG）。
    """
    skills = scan_skills(get_db_session)
    tools = []
    if intent == "leave":
        if "leave" in skills:
            data = skills["leave"]
            tools.extend(data["tools"])
            # 仅在使用该技能时才加载该技能专属的向量 namespace（若配置了 rag_namespace）
            rag_ns = data["config"].get("rag_namespace")
            if rag_ns:
                tools.append(make_rag_tool(namespace=rag_ns))
    elif intent == "expense":
        if "expense" in skills:
            data = skills["expense"]
            tools.extend(data["tools"])
            rag_ns = data["config"].get("rag_namespace")
            if rag_ns:
                tools.append(make_rag_tool(namespace=rag_ns))
    elif intent == "knowledge":
        # 知识库意图：仅使用 RAG 检索工具（此时才加载向量库）
        tools.append(make_rag_tool(namespace="default"))
    else:
        # 未识别意图：汇总所有技能工具并加上 RAG
        for name, data in skills.items():
            tools.extend(data["tools"])
            rag_ns = data["config"].get("rag_namespace")
            if rag_ns:
                tools.append(make_rag_tool(namespace=rag_ns))
        tools.append(make_rag_tool(namespace="default"))
    return tools


def chat(
    user_input: str,
    get_db_session: Callable,
    use_llm_route: bool = False,
) -> Dict[str, Any]:
    """
    主流程：路由 -> 收集工具 -> 执行 agent -> 写 agent_logs。
    返回 {"intent": str, "output": str, "skill": str, "log_id": int | None}。
    """
    intent = route_intent(user_input, use_llm=use_llm_route)
    tools = collect_tools_for_intent(intent, get_db_session)
    skill_name = intent if intent != "unknown" else "general"
    if not tools:
        return {
            "intent": intent,
            "output": "暂无可用的处理能力，请稍后再试或联系管理员。",
            "skill": skill_name,
            "log_id": None,
        }
    agent_executor = build_agent_executor(tools)
    result = run_agent(agent_executor, user_input)
    output = result.get("output", "")
    # 写入审计日志（用户输入、技能、动作、结果）
    log_id = None
    try:
        db = next(get_db_session())
        from app.services.db_service import AgentLogService
        log_entry = AgentLogService.create(
            db,
            user_input=user_input,
            skill=skill_name,
            action=str(result.get("intermediate_steps", []))[:2000],
            result=output[:2000],
        )
        log_id = log_entry.id
        db.close()
    except Exception:
        pass
    return {
        "intent": intent,
        "output": output,
        "skill": skill_name,
        "log_id": log_id,
    }
