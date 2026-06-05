from abc import ABC, abstractmethod

from app.domain.dto import UserWithoutPasswDTO, TokenPayloadDTO, UserLifetimeTokenDTO


class InterfaceToken(ABC):
    @abstractmethod
    def encode_token(self, user: UserWithoutPasswDTO) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> TokenPayloadDTO:
        pass

    @abstractmethod
    def token_info_payload(self, token: str) -> UserLifetimeTokenDTO:
        pass
