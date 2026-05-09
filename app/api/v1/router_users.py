from typing import Annotated

from fastapi import APIRouter, Query, Path

from app.api.v1.dependencies import UserServiceDep, TokenServiceDep, AccessToken
from app.api.v1.schemas import BaseUserSchema, ReadUserSchema, ReadUserAndTokenSchema, ReadPayloadTokenSchema

router = APIRouter()


@router.get("")
async def get_users(service: UserServiceDep, offset: Annotated[int | None, Query(ge=0)] = 0) -> list[ReadUserSchema]:
    return await service.get_users(offset)


@router.post("")
async def create_user(service: UserServiceDep, user: BaseUserSchema) -> ReadUserAndTokenSchema:
    return await service.create_user(user.model_dump())


@router.get("/{user_id}")
async def get_user(service: UserServiceDep, user_id: Annotated[int, Path(ge=1)]) -> ReadUserSchema:
    return await service.get_user(user_id)


@router.post("/authorization")
async def user_authorization(service: UserServiceDep, user: BaseUserSchema) -> ReadUserAndTokenSchema:
    return await service.user_authorization(user.model_dump())


@router.get("/authorization/my/token-info")
async def get_token_info(
        service: TokenServiceDep,
        token: AccessToken,
) -> ReadPayloadTokenSchema:
    return service.token_info_payload(token)
