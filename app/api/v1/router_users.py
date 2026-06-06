from typing import Annotated

from fastapi import APIRouter, Query, Path

from app.api.v1.dependencies import UserServiceDep, TokenServiceDep, AccessToken
from app.api.v1.http_exception import user_not_found_404, user_already_exists_400, user_incorrect_data_400
from app.api.v1.schemas import BaseUserSchema, ReadUserSchema, ReadUserAndTokenSchema, ReadPayloadTokenSchema
from app.domain.entities import User, UserNotFoundError, UserIncorrectDataError, UserAlreadyExistsError

router = APIRouter()


@router.get("")
async def get_users(service: UserServiceDep, offset: Annotated[int | None, Query(ge=0)] = 0) -> list[ReadUserSchema]:
    return await service.get_users(offset)


@router.post("", status_code=201)
async def create_user(service: UserServiceDep, user: BaseUserSchema) -> ReadUserAndTokenSchema:
    user_dto = User(**user.model_dump())
    try:
        result = await service.create_user(user_dto)
    except UserAlreadyExistsError:
        raise user_already_exists_400(user.user_name)
    return result


@router.get("/{user_id}")
async def get_user(service: UserServiceDep, user_id: Annotated[int, Path(ge=1)]) -> ReadUserSchema:
    try:
        result = await service.get_user(user_id)
    except UserNotFoundError:
        raise user_not_found_404(user_id)
    return result


@router.post("/authorization")
async def authorization_user(service: UserServiceDep, user: BaseUserSchema) -> ReadUserAndTokenSchema:
    user_dto = User(**user.model_dump())
    try:
        result = await service.user_authorization(user_dto)
    except UserIncorrectDataError:
        raise user_incorrect_data_400()
    return result


@router.get("/authorization/my/token-info")
async def get_token_info(
        service: TokenServiceDep,
        token: AccessToken,
) -> ReadPayloadTokenSchema:
    return service.token_info_payload(token)
