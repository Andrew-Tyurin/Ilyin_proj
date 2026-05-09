from fastapi import APIRouter

from app.api.v1.dependencies import OperationServiceDep, PayloadAccessToken
from app.api.v1.schemas import OperationSchema

router = APIRouter()


@router.patch("/income")
async def add_income(
        service: OperationServiceDep,
        operation: OperationSchema,
        payload: PayloadAccessToken,
):
    user_id =  payload.get("sub")
    return await service.add_income(user_id, operation.model_dump())


@router.patch("/expense")
async def add_expense(
        service: OperationServiceDep,
        operation: OperationSchema,
        payload: PayloadAccessToken,
):
    user_id = payload.get("sub")
    return await service.add_expense(user_id, operation.model_dump())
