from dataclasses import dataclass


@dataclass
class UserWithoutPasswDTO:
    id: int
    user_name: str


@dataclass
class UserAuthorizationDTO:
    id: int
    user_name: str
    access_token: str


@dataclass
class TokenPayloadDTO:
    exp: int
    iat: int
    sub: int
    user_name: str


@dataclass
class UserLifetimeTokenDTO:
    id: int
    user_name: str
    expires_time_life: int
