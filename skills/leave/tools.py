"""Leave skill tools - 依赖注入 db session 在运行时由 skill engine 提供."""
from langchain_core.tools import tool


def make_leave_tools(get_db_session):
    """工厂：根据 get_db_session 创建带 DB 的 leave 工具."""

    @tool
    def submit_leave(employee: str, days: int, reason: str = "") -> str:
        """提交请假申请。参数：employee 员工姓名, days 请假天数, reason 请假原因（可选）。"""
        db = next(get_db_session())
        from app.services.db_service import LeaveService
        req = LeaveService.create(db, employee=employee, days=days, reason=reason or None)
        return f"已提交请假申请，单号：{req.id}，{employee} 请假 {days} 天，状态：{req.status}。"

    @tool
    def query_leave(employee: str, limit: int = 10) -> str:
        """查询某员工的请假记录。参数：employee 员工姓名, limit 最多返回条数（默认10）。"""
        db = next(get_db_session())
        from app.services.db_service import LeaveService
        rows = LeaveService.list_by_employee(db, employee=employee, limit=limit)
        if not rows:
            return f"{employee} 暂无请假记录。"
        lines = [f"单号:{r.id} 天数:{r.days} 原因:{r.reason or '-'} 状态:{r.status} 时间:{r.created_at}" for r in rows]
        return "最近请假记录：\n" + "\n".join(lines)

    return [submit_leave, query_leave]
