from abc import ABC, abstractmethod


class AbstractTokenService(ABC):
    @abstractmethod
    def encode_token(self, user: dict):
        pass

    @abstractmethod
    def decode_token(self, token: str):
        pass

    @abstractmethod
    def token_info_payload(self, token: str):
        pass
