from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.api.v1.dependencies import OperationServiceDep, PayloadAccessToken
from app.api.v1.http_exception import wallet_not_found_id_404, wallet_not_valid_balance_400, wide_date_range_422
from app.api.v1.schemas import (
    CreateOperationSchema,
    ReadOperationsHistorySchema,
    CreateTransferWalletsShema,
    ReadTransferBetweenWalletsSchema,
    DateFromDateToSchema
)
from app.custom_enum import OperationOrderEnum, OperationTypeEnum
from app.domain.dto import WalletUpdateDTO
from app.domain.entities import Operation, WalletNotFoundError, WalletUpdateError, NoMoreThanDaysError

router = APIRouter()


@router.patch("/income")
async def add_income(
        service: OperationServiceDep,
        operation: CreateOperationSchema,
        payload: PayloadAccessToken,
) -> ReadOperationsHistorySchema:
    user_id = payload.sub
    operation_income = Operation(
        wallet_id=operation.wallet_id,
        amount=operation.amount,
        description=operation.description,
        type=OperationTypeEnum.INCOME
    )
    wallet_update = WalletUpdateDTO(id=operation.wallet_id, user_id=user_id)
    try:
        result = await service.add_income(operation_income, wallet_update)
    except WalletNotFoundError:
        raise wallet_not_found_id_404(operation.wallet_id)
    except WalletUpdateError:
        raise wallet_not_valid_balance_400(operation.wallet_id)
    return result


@router.patch("/expense")
async def add_expense(
        service: OperationServiceDep,
        operation: CreateOperationSchema,
        payload: PayloadAccessToken,
) -> ReadOperationsHistorySchema:
    user_id = payload.sub
    operation_expense = Operation(
        wallet_id=operation.wallet_id,
        amount=operation.amount,
        description=operation.description,
        type=OperationTypeEnum.EXPENSE
    )
    wallet_update = WalletUpdateDTO(id=operation.wallet_id, user_id=user_id)
    try:
        result = await service.add_expense(operation_expense, wallet_update)
    except WalletNotFoundError:
        raise wallet_not_found_id_404(operation.wallet_id)
    except WalletUpdateError:
        raise wallet_not_valid_balance_400(operation.wallet_id)
    return result


@router.patch("/transfer")
async def transfer_between_wallets(
        service: OperationServiceDep,
        payload: PayloadAccessToken,
        transfer_wallets: CreateTransferWalletsShema,
) -> ReadTransferBetweenWalletsSchema:
    user_id = payload.sub
    amount = transfer_wallets.amount
    from_wallet_update = WalletUpdateDTO(id=transfer_wallets.from_wallet_id, user_id=user_id)
    to_wallet_update = WalletUpdateDTO(id=transfer_wallets.to_wallet_id, user_id=user_id)
    try:
        results = await service.transfer_between_wallets(from_wallet_update, to_wallet_update, amount)
    except WalletNotFoundError as e:
        user_id_error = e.args[0]
        raise wallet_not_found_id_404(user_id_error)
    except WalletUpdateError as e:
        user_id_error = e.args[0]
        raise wallet_not_valid_balance_400(user_id_error)

    response_from_wallet, response_to_wallet = results
    return {"from_wallet": response_from_wallet, "to_wallet": response_to_wallet}


@router.get("/history")
async def get_operations_history(
        service: OperationServiceDep,
        payload: PayloadAccessToken,
        wallet_id: Annotated[int | None, Query(ge=1)] = None,
        order_by_data: Annotated[OperationOrderEnum, Query()] = OperationOrderEnum.DECREASE,
        limit: Annotated[int | None, Query(ge=1, le=30)] = 10,
        offset: Annotated[int | None, Query(ge=0)] = 0,
) -> list[ReadOperationsHistorySchema]:
    user_id = payload.sub
    try:
        result = await service.get_operations_history(user_id, wallet_id, order_by_data, limit, offset)
    except WalletNotFoundError:
        raise wallet_not_found_id_404(wallet_id)
    return result


@router.get("/download", response_class=StreamingResponse)
async def download_file_with_operations(
        service: OperationServiceDep,
        payload: PayloadAccessToken,
        date_obj: Annotated[DateFromDateToSchema, Query()]
) -> StreamingResponse:
    """
    # image:
    - ### from_date: 2026-01-01
    - ### from_to: 2026-02-01
    - ### timezone: Europe/Moscow
    """
    max_days = 365
    current_days = (date_obj.date_to - date_obj.date_from).days

    try:
        if current_days > max_days:
            raise NoMoreThanDaysError
    except NoMoreThanDaysError:
        raise wide_date_range_422(current_days, max_days)

    user_id = payload.sub
    user_name = payload.user_name
    result = await service.crete_file_containing_operations(user_id, user_name, **date_obj.model_dump())
    return StreamingResponse(
        result,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=operations.pdf"}
    )
