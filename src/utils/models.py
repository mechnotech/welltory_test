import datetime
from typing import Optional, List

import orjson
from pydantic import BaseModel, EmailStr
from typing_extensions import TypedDict


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode('utf-8')


class AdvancedJsonModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class OAuthProviderSet(AdvancedJsonModel):
    oauth_provider: str
    request_code: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None


class LoginSet(AdvancedJsonModel):
    login: str
    password: str


class XYParams(TypedDict):
    date: datetime.date
    value: float


class XYData(TypedDict):
    x_data_type: str
    y_data_type: str
    x: List[XYParams]
    y: List[XYParams]


class MedDataSet(AdvancedJsonModel):
    user_id: int
    data: XYData


class CorrSet(AdvancedJsonModel):
    x_data_type: str
    y_data_type: str
    user_id: int


class UserSet(LoginSet):
    email: EmailStr


class LogSet(AdvancedJsonModel):
    info: str
    status: str
    created_at: datetime.datetime
