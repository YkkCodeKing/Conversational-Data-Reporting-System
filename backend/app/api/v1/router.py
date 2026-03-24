from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.chat.router import router as chat_router
from app.modules.datasource.router import router as datasource_router
from app.modules.query.router import router as query_router
from app.modules.chart.router import router as chart_router
from app.modules.insight.router import router as insight_router
from app.modules.report.router import router as report_router

api_router = APIRouter()

# 挂载所有领域模块路由
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(datasource_router)
api_router.include_router(query_router)
api_router.include_router(chart_router)
api_router.include_router(insight_router)
api_router.include_router(report_router)
