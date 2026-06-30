from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.agent import router as agent_router
from app.api.routes.audit import router as audit_router
from app.api.routes.auth import router as auth_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.orders import router as orders_router
from app.api.routes.products import router as products_router
from app.api.routes.review_tasks import router as review_tasks_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.tickets import router as tickets_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.database import check_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    check_database_connection()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    app = FastAPI(
        title=settings.app_name,
        description="Backend API for AI ecommerce customer service and after-sales workflows.",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router, prefix="/api")
    app.include_router(auth_router, prefix="/api")
    app.include_router(products_router, prefix="/api")
    app.include_router(orders_router, prefix="/api")
    app.include_router(sessions_router, prefix="/api")
    app.include_router(knowledge_router, prefix="/api")
    app.include_router(agent_router, prefix="/api")
    app.include_router(audit_router, prefix="/api")
    app.include_router(dashboard_router, prefix="/api")
    app.include_router(review_tasks_router, prefix="/api")
    app.include_router(tickets_router, prefix="/api")
    return app


app = create_app()
