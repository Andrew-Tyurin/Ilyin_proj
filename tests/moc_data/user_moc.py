from tests.moc_data.base_moc import BaseDataclassMoc


class CreateUserDataclassMoc(BaseDataclassMoc):
    user_name: str
    password: str


class ResultCreateUserDataclassMoc(BaseDataclassMoc):
    id: int
    user_name: str
    access_token: str


class ReadUserAuthorizationMoc(ResultCreateUserDataclassMoc):
    pass


class ReadUserDataclassMoc(BaseDataclassMoc):
    id: int
    user_name: str


class ReadPayloadUserJwtDataclassMoc(BaseDataclassMoc):
    id: int
    user_name: str
    expires_time_life: str
