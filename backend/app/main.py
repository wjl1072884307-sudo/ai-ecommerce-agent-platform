from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.agent import router as agent_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.orders import router as orders_router
from app.api.routes.products import router as products_router
from app.api.routes.review_tasks import router as review_tasks_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.tickets import router as tickets_router
from app.database import check_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    check_database_connection()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Ecommerce Agent Platform API",
        description="Backend API for AI ecommerce customer service and after-sales workflows.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(health_router, prefix="/api")
    app.include_router(products_router, prefix="/api")
    app.include_router(orders_router, prefix="/api")
    app.include_router(sessions_router, prefix="/api")
    app.include_router(knowledge_router, prefix="/api")
    app.include_router(agent_router, prefix="/api")
    app.include_router(dashboard_router, prefix="/api")
    app.include_router(review_tasks_router, prefix="/api")
    app.include_router(tickets_router, prefix="/api")
    return app


app = create_app()
