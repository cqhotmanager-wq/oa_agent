"""Expense skill tools."""
from langchain_core.tools import tool


def make_expense_tools(get_db_session):
    """工厂：创建报销相关工具."""

    @tool
    def submit_expense(employee: str, amount: float, category: str = "", reason: str = "") -> str:
        """提交报销申请。参数：employee 员工姓名, amount 报销金额（元）, category 类别（如差旅/餐饮）, reason 说明（可选）。"""
        db = next(get_db_session())
        from decimal import Decimal
        from app.services.db_service import ExpenseService
        req = ExpenseService.create(
            db,
            employee=employee,
            amount=Decimal(str(amount)),
            category=category or None,
            reason=reason or None,
        )
        return f"已提交报销申请，单号：{req.id}，{employee} 报销金额 {amount} 元，类别：{category or '-'}，状态：{req.status}。"

    @tool
    def query_expense(employee: str, limit: int = 10) -> str:
        """查询某员工的报销记录。参数：employee 员工姓名, limit 最多返回条数（默认10）。"""
        db = next(get_db_session())
        from app.services.db_service import ExpenseService
        rows = ExpenseService.list_by_employee(db, employee=employee, limit=limit)
        if not rows:
            return f"{employee} 暂无报销记录。"
        lines = [f"单号:{r.id} 金额:{r.amount} 类别:{r.category or '-'} 状态:{r.status} 时间:{r.created_at}" for r in rows]
        return "最近报销记录：\n" + "\n".join(lines)

    return [submit_expense, query_expense]
