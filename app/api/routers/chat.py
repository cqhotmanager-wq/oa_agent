"""聊天 API：接收用户消息，调用 Chat 服务并返回意图、回复、技能与日志 ID。"""
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.db.session import get_db
from app.services.chat_service import chat

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """聊天请求体：用户输入与是否使用 LLM 做意图路由。"""
    message: str
    use_llm_route: Optional[bool] = False


class ChatResponse(BaseModel):
    """聊天响应：意图类型、助手回复、命中技能名、审计日志 ID。"""
    intent: str
    output: str
    skill: str
    log_id: Optional[int] = None


@router.post("/chat", response_model=ChatResponse)
def post_chat(
    body: ChatRequest,
    db=Depends(get_db),
):
    """对话接口：传入 message，返回结构化结果（intent / output / skill / log_id）。"""
    # 将 FastAPI 的 get_db 生成器包装成 chat 服务所需的 callable
    def get_db_session():
        yield db
    result = chat(body.message, get_db_session, use_llm_route=body.use_llm_route or False)
    return ChatResponse(
        intent=result["intent"],
        output=result["output"],
        skill=result["skill"],
        log_id=result.get("log_id"),
    )
