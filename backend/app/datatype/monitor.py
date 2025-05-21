from typing import Literal
from pydantic import BaseModel, Field
from sqlalchemy import Column, BigInteger, String
from toollib.utils import now2timestamp

from app.datatype import DeclBase, filter_fields
from app.initializer import g


class Monitor(DeclBase):
    __tablename__ = "monitor"

    id = Column(String(20), primary_key=True, default=g.snow_cli.gen_uid, comment="主键")
    name = Column(String(100), nullable=False, comment="监控名称")
    address = Column(String(200), nullable=False, comment="监控地址")
    audio_path = Column(String(200), nullable=True, comment="音频路径")
    created_at = Column(BigInteger, default=now2timestamp, comment="创建时间")
    updated_at = Column(BigInteger, default=now2timestamp, onupdate=now2timestamp, comment="更新时间")


class MonitorDetailMdl(BaseModel):
    id: str = Field(...)
    name: str = None
    address: str = None
    audio_path: str = None
    created_at: int = None
    updated_at: int = None

    @classmethod
    def response_fields(cls):
        return filter_fields(
            cls,
            exclude=[]
        )


class MonitorListMdl(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1)
    id: str = None
    name: str = None
    address: str = None
    audio_path: str = None
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


class MonitorCreateMdl(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=200)
    audio_path: str = Field(None, max_length=200)


class MonitorUpdateMdl(BaseModel):
    name: str = Field(None, min_length=1, max_length=100)
    address: str = Field(None, min_length=1, max_length=200)
    audio_path: str = Field(None, max_length=200)


class MonitorDeleteMdl(BaseModel):
    pass 