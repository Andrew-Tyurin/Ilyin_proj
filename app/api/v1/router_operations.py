from typing import Annotated

from fastapi import APIRouter, Query

from app.api.v1.dependencies import OperationServiceDep, PayloadAccessToken
from app.api.v1.schemas import (
    CreateOperationSchema,
    ReadOperationsHistoryShema,
    CreateTransferWalletsShema,
    ReadTransferBetweenWalletsShema
)
from app.custom_enum import OperationOrderEnum

router = APIRouter()


@router.patch("/income")
async def add_income(
        service: OperationServiceDep,
        operation: CreateOperationSchema,
        payload: PayloadAccessToken,
) -> ReadOperationsHistoryShema:
    user_id = payload.get("sub")
    return await service.add_income(user_id, operation.model_dump())


@router.patch("/expense")
async def add_expense(
        service: OperationServiceDep,
        operation: CreateOperationSchema,
        payload: PayloadAccessToken,
) -> ReadOperationsHistoryShema:
    user_id = payload.get("sub")
    return await service.add_expense(user_id, operation.model_dump())


@router.patch("/transfer")
async def transfer_between_wallets(
        service: OperationServiceDep,
        payload: PayloadAccessToken,
        transfer_wallets: CreateTransferWalletsShema,
) -> ReadTransferBetweenWalletsShema:
    user_id = payload.get("sub")
    from_wallet, to_wallet = await service.transfer_between_wallets(user_id, transfer_wallets.model_dump())
    return ReadTransferBetweenWalletsShema(
        from_wallet=ReadOperationsHistoryShema(**from_wallet),
        to_wallet=ReadOperationsHistoryShema(**to_wallet),
    )


@router.get("/history")
async def get_operations_history(
        service: OperationServiceDep,
        payload: PayloadAccessToken,
        wallet_id: Annotated[int | None, Query(ge=1)] = None,
        order_by_data: Annotated[OperationOrderEnum, Query()] = OperationOrderEnum.DECREASE,
        limit: Annotated[int | None, Query(ge=1)] = None,
) -> list[ReadOperationsHistoryShema]:
    user_id = payload.get("sub")
    return await service.get_operations_history(user_id, wallet_id, order_by_data, limit)
