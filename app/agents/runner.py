"""LangChain 工具调用 Agent：构建 AgentExecutor、执行一轮对话并返回输出。"""
from typing import Any, Callable, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

try:
    from config.settings import settings
except Exception:
    settings = None


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
) -> AgentExecutor:
    """根据工具列表和系统提示构建 LangChain AgentExecutor（工具调用 Agent）。"""
    llm = get_llm()
    # 对话模板：系统提示 + 可选历史 + 当前输入 + Agent 思考过程
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)


def run_agent(
    agent_executor: AgentExecutor,
    user_input: str,
    chat_history: Optional[List] = None,
) -> dict:
    """执行一轮 Agent 调用，返回 output 与 intermediate_steps；异常时返回错误信息。"""
    try:
        result = agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history or [],
        })
        return {"output": result.get("output", ""), "intermediate_steps": result.get("intermediate_steps", [])}
    except Exception as e:
        return {"output": f"处理失败: {str(e)}", "intermediate_steps": []}
