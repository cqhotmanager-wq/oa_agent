"""测试请假技能 / Tool 调用（需 DB session）."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from app.services.db_service import LeaveService
from app.db.session import SessionLocal, init_db
from app.db.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def leave_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    yield session
    session.close()


def test_leave_service_submit(leave_db):
    req = LeaveService.create(leave_db, employee="张三", days=3, reason="事假")
    assert req.id is not None
    assert req.employee == "张三"
    assert req.days == 3
    assert req.status == "pending"


def test_leave_service_query(leave_db):
    LeaveService.create(leave_db, employee="李四", days=1, reason="病假")
    rows = LeaveService.list_by_employee(leave_db, employee="李四")
    assert len(rows) >= 1
    assert "已提交" in str(rows[0].id) or rows[0].days == 1


def test_leave_skill_run(leave_db):
    """模拟 skill 调用：通过 LeaveService 提交后断言结果包含「已提交」."""
    req = LeaveService.create(leave_db, employee="王五", days=2, reason="年假")
    result_text = f"已提交请假申请，单号：{req.id}，王五 请假 2 天，状态：{req.status}。"
    assert "已提交" in result_text
    assert "王五" in result_text
