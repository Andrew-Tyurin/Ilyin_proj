import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.api.v1.router_operations import router as operation_router
from app.api.v1.router_users import router as user_router
from app.api.v1.router_wallets import router as wallet_router

app = FastAPI()
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(wallet_router, prefix="/api/v1/my/wallets", tags=["wallets"])
app.include_router(operation_router, prefix="/api/v1/my/wallets/operations", tags=["operations on wallets"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
