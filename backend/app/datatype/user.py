import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column, BigInteger, String
from toollib.utils import now2timestamp

from app.datatype import DeclBase, filter_fields
from app.initializer import g


class User(DeclBase):
    __tablename__ = "user"

    id = Column(String(20), primary_key=True, default=g.snow_cli.gen_uid, comment="主键")
    phone = Column(String(15), unique=True, index=True, nullable=False, comment="手机号")
    password = Column(String(128), nullable=True, comment="密码")
    jwt_key = Column(String(128), nullable=True, comment="jwtKey")
    created_at = Column(BigInteger, default=now2timestamp, comment="创建时间")
    updated_at = Column(BigInteger, default=now2timestamp, onupdate=now2timestamp, comment="更新时间")


class UserDetailMdl(BaseModel):
    id: str = Field(...)
    phone: str = None
    created_at: int = None
    updated_at: int = None

    @classmethod
    def response_fields(cls):
        return filter_fields(
            cls,
            exclude=[]
        )


class UserListMdl(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1)
    id: str = None
    phone: str = None
    created_at: int = None
    updated_at: int = None

    @classmethod
    def response_fields(cls):
        return filter_fields(
            cls,
            exclude=[
                "page",
                "size",
            ]
        )


class UserCreateMdl(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    password: str = Field(...)

    @field_validator("password")
    def validate_password(cls, v):
        if not re.match(r"^\d{6,}$", v):
            raise ValueError("密码必须至少包含6位数字")
        return v


class UserUpdateMdl(BaseModel):
    pass


class UserDeleteMdl(BaseModel):
    pass


class UserLoginMdl(BaseModel):
    phone: str = Field(...)
    password: str = Field(...)


class UserTokenMdl(BaseModel):
    id: str = Field(...)
    exp_minutes: int = Field(24 * 60 * 30, ge=1)
