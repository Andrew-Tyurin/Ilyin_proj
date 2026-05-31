from typing import Annotated

from fastapi import APIRouter, Path

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
async def get_total_balance(
        service: WalletServiceDep,
        payload: PayloadAccessToken,
        currency: CurrencyEnum = CurrencyEnum.RUB
) -> ReadWalletsTotalBalanceSchema:
    user_id = payload.get("sub")
    return await service.get_total_balance(user_id, currency)


@router.get("/one/{wallet_name}")
async def get_wallet(
        service: WalletServiceDep,
        payload: PayloadAccessToken,
        wallet_name: Annotated[str, Path(min_length=1)],
) -> ReadWalletSchema:
    user_id = payload.get("sub")
    return await service.get_wallet(user_id, wallet_name)


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
