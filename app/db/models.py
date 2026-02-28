"""SQLAlchemy ORM 模型：请假单、报销单、Agent 审计日志。"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, DECIMAL
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LeaveRequest(Base):
    """请假申请表：员工、天数、原因、状态、创建时间。"""
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee = Column(String(128), nullable=False)   # 员工标识
    days = Column(Integer, nullable=False)          # 请假天数
    reason = Column(Text, nullable=True)            # 请假原因
    status = Column(String(32), nullable=False, default="pending")  # 审批状态
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class ExpenseRequest(Base):
    """报销申请表：员工、金额、分类、原因、状态、创建时间。"""
    __tablename__ = "expense_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee = Column(String(128), nullable=False)   # 员工标识
    amount = Column(DECIMAL(12, 2), nullable=False) # 报销金额
    category = Column(String(64), nullable=True)     # 费用分类
    reason = Column(Text, nullable=True)             # 报销事由
    status = Column(String(32), nullable=False, default="pending")  # 审批状态
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class AgentLog(Base):
    """Agent 调用审计日志：用户输入、命中技能、动作摘要、结果摘要、时间。"""
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_input = Column(Text, nullable=True)   # 用户原始输入
    skill = Column(String(64), nullable=True)   # 命中的技能名
    action = Column(Text, nullable=True)       # 中间步骤/动作摘要
    result = Column(Text, nullable=True)       # 输出结果摘要
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
