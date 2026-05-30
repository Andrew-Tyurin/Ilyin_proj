from fastapi import APIRouter

from app.api.v1.dependencies import WalletServiceDep, PayloadAccessToken
from app.api.v1.schemas import (
    CreateWalletSchema,
    ReadWalletsAllSchema,
    ReadWalletSchema,
    ReadWalletsTotalBalanceSchema
)
from app.custom_enum import CurrencyEnum

router = APIRouter()


@router.get("/balances")
async def get_balance(
        service: WalletServiceDep,
        payload: PayloadAccessToken,
        wallet_name: str | None = None,
        show_total_balance_in_currency: CurrencyEnum | None = None
) -> ReadWalletSchema | ReadWalletsTotalBalanceSchema:
    user_id = payload.get("sub")
    return await service.get_balance(user_id, wallet_name, show_total_balance_in_currency)


@router.get("/all")
async def get_wallets(
        service: WalletServiceDep,
        payload: PayloadAccessToken,
) -> ReadWalletsAllSchema:
    user_id = payload.get("sub")
    user_name = payload.get("user_name")
    wallets_user = await service.get_wallets(user_id)
    return {"user_id": user_id, "user_name": user_name, "wallets": wallets_user}


@router.post("", status_code=201)
async def create_wallet(
        service: WalletServiceDep,
        payload: PayloadAccessToken,
        wallet: CreateWalletSchema
):
    user_id = payload.get("sub")
    return await service.create_wallet(user_id, wallet.model_dump())
