from pwdlib import PasswordHash

from app.infrastructure.patterns.singleton import SingletonMeta


class HashArgon2(metaclass=SingletonMeta):
    _hash = PasswordHash.recommended()

    @property
    def hashing_algorithm(self) -> str:
        return self._hash.current_hasher.__class__.__name__

    def hash(self, value: str) -> str | bytes:
        return self._hash.hash(value)

    def verify(self, value: str, hash_value: str | bytes) -> bool:
        return self._hash.verify(value, hash_value)
