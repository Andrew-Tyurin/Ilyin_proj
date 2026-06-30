import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request

from app.api.v1.router_operations import router as operation_router
from app.api.v1.router_users import router as user_router
from app.api.v1.router_wallets import router as wallet_router
from app.config_app import StartAppSettings
from app.infrastructure.sqlalchemy_db import async_create_table


@asynccontextmanager
async def lifespan(app: FastAPI):
    await async_create_table()
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time_response = time.perf_counter()
    response = await call_next(request)
    end_time_response = time.perf_counter() - start_time_response
    response.headers["X-Process-Time"] = str(round(end_time_response, 4))
    return response


app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(wallet_router, prefix="/api/v1/my/wallets", tags=["wallets"])
app.include_router(operation_router, prefix="/api/v1/my/wallets/operations", tags=["operations on wallets"])

# для локального использования app.mount оставляем
# from starlette.staticfiles import StaticFiles
# app.mount("/ui", StaticFiles(directory="static"), name="ui")

if __name__ == "__main__":
    uvicorn.run(
        app=StartAppSettings.app,
        host=StartAppSettings.host,
        port=StartAppSettings.port,
        reload=StartAppSettings.reload,
        workers=StartAppSettings.workers
    )
