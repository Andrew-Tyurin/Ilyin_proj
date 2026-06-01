from typing import Annotated

from fastapi import APIRouter, Path

from app.api.v1.dependencies import WalletServiceDep, PayloadAccessToken
from app.api.v1.schemas import (
    CreateWalletSchema,
    ReadWalletSchema,
    ReadWalletsTotalBalanceSchema,
    JustCreatedWalletSchema
)
from app.custom_enum import CurrencyEnum
from app.domain.entities import Wallet

router = APIRouter()


@router.get("/balances")
async def get_total_balance(
        service: WalletServiceDep,
        payload: PayloadAccessToken,
        currency: CurrencyEnum = CurrencyEnum.RUB
) -> ReadWalletsTotalBalanceSchema:
    user_id = payload.sub
    return await service.get_total_balance(user_id, currency)


@router.get("/one/{wallet_name}")
async def get_wallet(
        service: WalletServiceDep,
        payload: PayloadAccessToken,
        wallet_name: Annotated[str, Path(min_length=1)],
) -> ReadWalletSchema:
    user_id = payload.sub
    return await service.get_wallet(user_id, wallet_name)


@router.get("/all")
async def get_wallets(
        service: WalletServiceDep,
        payload: PayloadAccessToken,
) -> list[ReadWalletSchema]:
    user_id = payload.sub
    return await service.get_wallets(user_id)


@router.post("", status_code=201)
async def create_wallet(
        service: WalletServiceDep,
        payload: PayloadAccessToken,
        wallet: CreateWalletSchema
) -> JustCreatedWalletSchema:
    user_id = payload.sub
    wallet = Wallet(user_id=user_id, name=wallet.name, currency=wallet.currency)
    created_wallet = await service.create_wallet(wallet)
    return {
        "message": f"wallet '{created_wallet.name}' created",
        "wallet": created_wallet
    }
