from typing import Annotated

from fastapi import APIRouter, Query

from app.api.v1.dependencies import OperationServiceDep, PayloadAccessToken
from app.api.v1.schemas import (
    CreateOperationSchema,
    ReadOperationsHistoryShema,
    CreateTransferWalletsShema,
    ReadTransferBetweenWalletsShema
)
from app.custom_enum import OperationOrderEnum, OperationTypeEnum
from app.domain.dto import WalletUpdateDTO
from app.domain.entities import Operation

router = APIRouter()


@router.patch("/income")
async def add_income(
        service: OperationServiceDep,
        operation: CreateOperationSchema,
        payload: PayloadAccessToken,
) -> ReadOperationsHistoryShema:
    user_id = payload.sub
    operation_income = Operation(
        wallet_id=operation.wallet_id,
        amount=operation.amount,
        description=operation.description,
        type=OperationTypeEnum.INCOME
    )
    wallet_update = WalletUpdateDTO(id=operation.wallet_id, user_id=user_id)
    return await service.add_income(operation_income, wallet_update)


@router.patch("/expense")
async def add_expense(
        service: OperationServiceDep,
        operation: CreateOperationSchema,
        payload: PayloadAccessToken,
) -> ReadOperationsHistoryShema:
    user_id = payload.sub
    operation_expense = Operation(
        wallet_id=operation.wallet_id,
        amount=operation.amount,
        description=operation.description,
        type=OperationTypeEnum.EXPENSE
    )
    wallet_update = WalletUpdateDTO(id=operation.wallet_id, user_id=user_id)
    return await service.add_expense(operation_expense, wallet_update)


@router.patch("/transfer")
async def transfer_between_wallets(
        service: OperationServiceDep,
        payload: PayloadAccessToken,
        transfer_wallets: CreateTransferWalletsShema,
) -> ReadTransferBetweenWalletsShema:
    user_id = payload.sub
    amount = transfer_wallets.amount
    from_wallet_update = WalletUpdateDTO(id=transfer_wallets.from_wallet_id, user_id=user_id)
    to_wallet_update = WalletUpdateDTO(id=transfer_wallets.to_wallet_id, user_id=user_id)
    results = await service.transfer_between_wallets(from_wallet_update, to_wallet_update, amount)
    response_from_wallet, response_to_wallet = results
    return {"from_wallet": response_from_wallet, "to_wallet": response_to_wallet}


@router.get("/history")
async def get_operations_history(
        service: OperationServiceDep,
        payload: PayloadAccessToken,
        wallet_id: Annotated[int | None, Query(ge=1)] = None,
        order_by_data: Annotated[OperationOrderEnum, Query()] = OperationOrderEnum.DECREASE,
        limit: Annotated[int | None, Query(ge=1)] = None,
) -> list[ReadOperationsHistoryShema]:
    user_id = payload.sub
    return await service.get_operations_history(user_id, wallet_id, order_by_data, limit)
