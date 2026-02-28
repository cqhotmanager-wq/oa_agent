"""用户意图路由：根据用户输入判断意图（请假 / 报销 / 知识库），支持关键词 fallback。"""
from typing import Literal

# 意图类型：leave 请假、expense 报销、knowledge 知识库、unknown 未识别
IntentType = Literal["leave", "expense", "knowledge", "unknown"]


# 关键词到意图的映射，用于无 LLM 时的规则路由
KEYWORD_INTENT = {
    "leave": ["请假", "休假", "年假", "事假", "病假", "几天假", "请假申请", "我要请假"],
    "expense": ["报销", "费用", "差旅", "发票", "金额", "报销申请", "我要报销"],
    "knowledge": ["制度", "规定", "政策", "流程", "怎么办理", "如何申请", "规章制度", "手册"],
}


def route_by_keywords(user_input: str) -> IntentType:
    """基于关键词的意图分类（fallback）：命中任一关键词即返回对应意图。"""
    if not user_input or not user_input.strip():
        return "unknown"
    text = user_input.strip()
    for intent, keywords in KEYWORD_INTENT.items():
        for kw in keywords:
            if kw in text:
                return intent
    return "unknown"


def route_intent(user_input: str, use_llm: bool = False) -> IntentType:
    """
    分类用户意图。use_llm=True 时可接入 LLM 分类；当前实现为关键词 fallback。
    """
    if use_llm:
        # 预留：可在此调用 LLM 做细粒度分类
        pass
    return route_by_keywords(user_input)
