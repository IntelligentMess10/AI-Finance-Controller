from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.db.session import init_db, close_db
from backend.app.api import transactions
from backend.app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


settings = get_settings()

app = FastAPI(
    title=settings.app.name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import logging
    logging.error(f"Unhandled exception: {type(exc).__name__}: {exc}")
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )

app.include_router(transactions.router)
app.include_router(transactions.router_canonical)
app.include_router(transactions.router_reconciliation)
app.include_router(transactions.router_exceptions)
app.include_router(transactions.router_cash)
app.include_router(transactions.router_metrics)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.app.name}