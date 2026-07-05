import time
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from jwt.exceptions import InvalidTokenError

from app.config_app import JWTokenSettings
from app.contracts.token_interface import InterfaceToken
from app.domain.dto import UserWithoutPasswDTO, TokenPayloadDTO, UserLifetimeTokenDTO


class JWTokenImplementation(InterfaceToken):
    _secret_key: str = JWTokenSettings.secret_key
    _access_token_expire_minutes: int = JWTokenSettings.time_minutes
    _algorithm: str = JWTokenSettings.algorithm

    @property
    def raise_token_exception(self) -> HTTPException:
        return HTTPException(
            status_code=401,
            detail="access-token expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def encode_token(self, user: UserWithoutPasswDTO) -> str:
        expires_delta = timedelta(minutes=self._access_token_expire_minutes)
        issued_at = datetime.now(timezone.utc)
        expire = issued_at + expires_delta
        data = {
            "sub": str(user.id),
            "user_name": user.user_name,
            "exp": expire,
            "iat": issued_at
        }
        token = jwt.encode(data, self._secret_key, algorithm=self._algorithm)
        return token

    def decode_token(self, token: str) -> TokenPayloadDTO:
        keys_payload = ("sub", "user_name", "exp", "iat")
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            for key in keys_payload:
                value = payload.get(key)
                if value is None:
                    raise self.raise_token_exception
        except InvalidTokenError:
            raise self.raise_token_exception
        try:
            payload["sub"] = int(payload["sub"])
        except (ValueError, TypeError):
            raise self.raise_token_exception
        return TokenPayloadDTO(**payload)

    def token_info_payload(self, token: str) -> UserLifetimeTokenDTO:
        payload = self.decode_token(token)
        user_id = payload.sub
        user_name = payload.user_name
        exp = payload.exp
        current_time = time.time()
        lifetime = round(exp - current_time)
        return UserLifetimeTokenDTO(id=user_id, user_name=user_name, expires_time_life=lifetime)
