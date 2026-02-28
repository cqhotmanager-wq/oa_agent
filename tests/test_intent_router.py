"""测试意图路由."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from app.api.routers.intent_router import route_by_keywords, route_intent, IntentType


@pytest.mark.parametrize("text,expected", [
    ("我要请假3天", "leave"),
    ("请假申请", "leave"),
    ("报销差旅费", "expense"),
    ("报销100元", "expense"),
    ("公司制度在哪里看", "knowledge"),
    ("规章制度", "knowledge"),
    ("你好", "unknown"),
])
def test_route_by_keywords(text: str, expected: IntentType):
    assert route_by_keywords(text) == expected


def test_route_intent():
    assert route_intent("请假3天") == "leave"
    assert route_intent("报销500") == "expense"
    assert route_intent("制度流程") == "knowledge"
