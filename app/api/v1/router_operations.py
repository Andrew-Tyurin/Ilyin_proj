from typing import Annotated

from fastapi import APIRouter, Query

from app.api.v1.dependencies import OperationServiceDep, PayloadAccessToken
from app.api.v1.schemas import OperationSchema
from app.custom_enum import OperationOrderEnum

router = APIRouter()


@router.patch("/income")
async def add_income(
        service: OperationServiceDep,
        operation: OperationSchema,
        payload: PayloadAccessToken,
):
    user_id = payload.get("sub")
    return await service.add_income(user_id, operation.model_dump())


@router.patch("/expense")
async def add_expense(
        service: OperationServiceDep,
        operation: OperationSchema,
        payload: PayloadAccessToken,
):
    user_id = payload.get("sub")
    return await service.add_expense(user_id, operation.model_dump())


@router.get("/operations-history")
async def get_operations_history(
        service: OperationServiceDep,
        payload: PayloadAccessToken,
        wallet_id: Annotated[int | None, Query(ge=1)] = None,
        order_by_data: Annotated[OperationOrderEnum, Query()] = OperationOrderEnum.DECREASE,
        limit: Annotated[int | None, Query(ge=1)] = None,
):
    user_id = payload.get("sub")
    return await service.get_operations_history(user_id, wallet_id, order_by_data, limit)
