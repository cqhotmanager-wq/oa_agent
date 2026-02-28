"""数据库服务层：请假、报销、Agent 审计日志的增删查。"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session
from app.db.models import LeaveRequest, ExpenseRequest, AgentLog


class LeaveService:
    """请假单服务：创建、按 ID 查询、按员工列表。"""

    @staticmethod
    def create(
        db: Session,
        employee: str,
        days: int,
        reason: Optional[str] = None,
        status: str = "pending",
    ) -> LeaveRequest:
        """创建一条请假申请并提交。"""
        req = LeaveRequest(employee=employee, days=days, reason=reason, status=status)
        db.add(req)
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def get_by_id(db: Session, id: int) -> Optional[LeaveRequest]:
        """按主键 ID 查询请假单。"""
        return db.query(LeaveRequest).filter(LeaveRequest.id == id).first()

    @staticmethod
    def list_by_employee(db: Session, employee: str, limit: int = 50) -> List[LeaveRequest]:
        """按员工名查询其请假记录，按创建时间倒序，限制条数。"""
        return (
            db.query(LeaveRequest)
            .filter(LeaveRequest.employee == employee)
            .order_by(LeaveRequest.created_at.desc())
            .limit(limit)
            .all()
        )


class ExpenseService:
    """报销单服务：创建、按 ID 查询、按员工列表。"""

    @staticmethod
    def create(
        db: Session,
        employee: str,
        amount: Decimal,
        category: Optional[str] = None,
        reason: Optional[str] = None,
        status: str = "pending",
    ) -> ExpenseRequest:
        """创建一条报销申请并提交。"""
        req = ExpenseRequest(
            employee=employee,
            amount=amount,
            category=category,
            reason=reason,
            status=status,
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def get_by_id(db: Session, id: int) -> Optional[ExpenseRequest]:
        """按主键 ID 查询报销单。"""
        return db.query(ExpenseRequest).filter(ExpenseRequest.id == id).first()

    @staticmethod
    def list_by_employee(db: Session, employee: str, limit: int = 50) -> List[ExpenseRequest]:
        """按员工名查询其报销记录，按创建时间倒序，限制条数。"""
        return (
            db.query(ExpenseRequest)
            .filter(ExpenseRequest.employee == employee)
            .order_by(ExpenseRequest.created_at.desc())
            .limit(limit)
            .all()
        )


class AgentLogService:
    """Agent 审计日志服务：写入单条日志、按天数清理旧日志。"""

    @staticmethod
    def create(
        db: Session,
        user_input: Optional[str] = None,
        skill: Optional[str] = None,
        action: Optional[str] = None,
        result: Optional[str] = None,
    ) -> AgentLog:
        """写入一条 Agent 调用日志（用户输入、技能、动作、结果）。"""
        log = AgentLog(
            user_input=user_input,
            skill=skill,
            action=action,
            result=result,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def delete_older_than(db: Session, days: int = 90) -> int:
        """删除早于指定天数的日志，返回删除条数。用于定时清理。"""
        from datetime import timedelta
        from sqlalchemy import func
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = db.query(AgentLog).filter(AgentLog.created_at < cutoff).delete()
        db.commit()
        return deleted
