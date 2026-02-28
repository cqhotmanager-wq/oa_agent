"""APScheduler 定时任务：扫描 skills、更新 FAISS 索引、清理过期 Agent 日志。"""
import logging
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


def job_scan_skills():
    """定时任务：扫描 skills 目录，便于热加载或统计当前技能列表。"""
    try:
        from app.services.skill_engine import scan_skills
        skills = scan_skills(None)
        logger.info("Scheduled job: scan_skills, found %s skills", list(skills.keys()))
    except Exception as e:
        logger.exception("job_scan_skills failed: %s", e)


def job_update_faiss():
    """定时任务：重新解析 policies 目录下 PDF 并更新 FAISS 向量库。"""
    try:
        from app.rag.ingest import ingest_all_namespaces
        result = ingest_all_namespaces(["default"])
        logger.info("Scheduled job: update FAISS, result=%s", result)
    except Exception as e:
        logger.exception("job_update_faiss failed: %s", e)


def job_clean_logs():
    """定时任务：删除 90 天前的 Agent 审计日志，控制表体积。"""
    try:
        from app.db.session import SessionLocal
        from app.services.db_service import AgentLogService
        db = SessionLocal()
        try:
            deleted = AgentLogService.delete_older_than(db, days=90)
            logger.info("Scheduled job: clean_logs, deleted=%s", deleted)
        finally:
            db.close()
    except Exception as e:
        logger.exception("job_clean_logs failed: %s", e)


def get_scheduler() -> BackgroundScheduler:
    """创建后台调度器并注册三个定时任务：2:00 扫技能、3:00 更新 FAISS、4:00 清日志。"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_scan_skills, CronTrigger(hour=2, minute=0), id="scan_skills")
    scheduler.add_job(job_update_faiss, CronTrigger(hour=3, minute=0), id="update_faiss")
    scheduler.add_job(job_clean_logs, CronTrigger(hour=4, minute=0), id="clean_logs")
    return scheduler


_scheduler: BackgroundScheduler = None


def start_scheduler():
    """启动全局后台调度器（仅启动一次）。"""
    global _scheduler
    if _scheduler is None:
        _scheduler = get_scheduler()
        _scheduler.start()
        logger.info("APScheduler started.")
    return _scheduler


def stop_scheduler():
    """关闭全局调度器并置空，供应用退出时调用。"""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("APScheduler stopped.")
