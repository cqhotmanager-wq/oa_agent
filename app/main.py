"""FastAPI 应用入口：创建应用、生命周期、中间件与路由注册。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import chat
from app.db.session import init_db

# 从配置读取应用名，失败则使用默认名
try:
    from config.settings import settings
    APP_NAME = settings.app_name
except Exception:
    APP_NAME = "OA Agent"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库与定时任务，关闭时停止定时任务。"""
    # 启动时：创建数据库表
    try:
        init_db()
    except Exception:
        pass
    # 启动时：启动后台定时任务（扫描技能、更新 FAISS、清理日志）
    try:
        from app.scheduler import start_scheduler
        start_scheduler()
    except Exception:
        pass
    yield
    # 关闭时：停止定时任务
    try:
        from app.scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass


app = FastAPI(title=APP_NAME, lifespan=lifespan)
# 跨域中间件，允许任意来源（可按需收紧）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册聊天相关 API 路由
app.include_router(chat.router)


@app.get("/health")
def health():
    """健康检查接口，用于探活与负载均衡。"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
