"""LangChain 工具调用 Agent：使用 LangGraph create_react_agent 构建并执行。"""
from typing import Any, List, Optional

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

try:
    from config.settings import settings
except Exception:
    settings = None

# 类型：create_react_agent 返回的图，用于 type hint
AgentGraph = Any


def get_llm():
    """获取 LLM：有配置则用 OpenAI 兼容接口，否则用 FakeListChatModel 便于本地测试。"""
    if settings and getattr(settings, "openai_api_key", None):
        return ChatOpenAI(
            model=settings.chat_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=0,
        )
    # 无 key 时用 mock，仅便于本地测试
    from langchain_community.chat_models import FakeListChatModel
    return FakeListChatModel(responses=["已收到您的请求。"])


def build_agent_executor(
    tools: List[BaseTool],
    system_message: str = "你是一个企业 OA 助手，根据用户意图调用工具完成请假、报销或知识库查询。",
) -> AgentGraph:
    """根据工具列表和系统提示构建 LangGraph ReAct Agent（工具调用）。"""
    llm = get_llm()
    graph = create_react_agent(llm, tools, prompt=system_message)
    return graph


def run_agent(
    agent_executor: AgentGraph,
    user_input: str,
    chat_history: Optional[List] = None,
) -> dict:
    """执行一轮 Agent 调用，返回 output 与 intermediate_steps；异常时返回错误信息。"""
    try:
        messages = list(chat_history) if chat_history else []
        messages.append(HumanMessage(content=user_input))
        result = agent_executor.invoke({"messages": messages})
        out_messages = result.get("messages", [])
        output = ""
        for msg in reversed(out_messages):
            if isinstance(msg, AIMessage) and msg.content:
                output = msg.content if isinstance(msg.content, str) else str(msg.content)
                break
        # 从 messages 中收集 tool 调用信息作为 intermediate_steps 的简化表示
        steps = [m for m in out_messages if hasattr(m, "tool_calls") and getattr(m, "tool_calls", None)]
        return {"output": output, "intermediate_steps": steps}
    except Exception as e:
        return {"output": f"处理失败: {str(e)}", "intermediate_steps": []}
