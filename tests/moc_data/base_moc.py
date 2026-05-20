from dataclasses import dataclass, asdict


class DataclassMeta(type):
    def __new__(metacls, *args, **kwargs):
        cls = super().__new__(metacls, *args, **kwargs)
        return dataclass(cls)


class BaseDataclassMoc(metaclass=DataclassMeta):
    def model_dump(self) -> dict:
        return asdict(self)
