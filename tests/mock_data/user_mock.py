from tests.mock_data.base_mock import BaseDataclassMock


class CreateUserDataclassMock(BaseDataclassMock):
    user_name: str
    password: str


class ResultCreateUserDataclassMock(BaseDataclassMock):
    id: int
    user_name: str
    access_token: str


class ReadUserAuthorizationMock(ResultCreateUserDataclassMock):
    pass


class ReadUserDataclassMock(BaseDataclassMock):
    id: int
    user_name: str


class ReadPayloadUserJwtDataclassMock(BaseDataclassMock):
    id: int
    user_name: str
    expires_time_life: str
