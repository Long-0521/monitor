from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from starlette.requests import Request

from app.api.exception import CustomException
from app.api.status import Status
from app.datatype.user import User
from app.initializer import g
from app.utils import db_async
from app.utils.auth import verify_jwt


class JWTUser(BaseModel):
    # 字段与User对齐
    id: str = None
    phone: str = None


class JWTAuthorizationCredentials(HTTPAuthorizationCredentials):
    user: JWTUser


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

    async def __call__(
            self, request: Request
    ) -> Optional[JWTAuthorizationCredentials]:
        # 检查是否是登录或注册接口
        if request.url.path in ["/api/v1/user/login", "/api/v1/user"] and request.method == "POST":
            return None
            
        authorization = request.headers.get("Authorization")
        if not authorization:
            if self.auto_error:
                raise CustomException(
                    msg="Not authenticated",
                    status=Status.UNAUTHORIZED_ERROR,
                )
            return None
            
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (scheme and credentials):
            if self.auto_error:
                raise CustomException(
                    msg="Invalid authentication credentials",
                    status=Status.UNAUTHORIZED_ERROR,
                )
            return None
            
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise CustomException(
                    msg="Invalid authentication credentials",
                    status=Status.UNAUTHORIZED_ERROR,
                )
            return None
            
        try:
            user = await self.verify_credentials(credentials)
            return JWTAuthorizationCredentials(scheme=scheme, credentials=credentials, user=user)
        except Exception as e:
            if self.auto_error:
                raise CustomException(
                    msg=str(e),
                    status=Status.UNAUTHORIZED_ERROR,
                )
            return None

    async def verify_credentials(self, credentials: str) -> JWTUser:
        playload = await self._verify_jwt(credentials)
        if playload is None:
            raise CustomException(status=Status.UNAUTHORIZED_ERROR)
        # 建议：jwt_key进行redis缓存
        async with g.db_async_session() as session:
            data = await db_async.query_one(
                session=session,
                model=User,
                fields=["jwt_key"],
                filter_by={"id": playload.get("id")}
            )
            if not data:
                raise CustomException(status=Status.UNAUTHORIZED_ERROR)
        # <<< 建议
        await self._verify_jwt(credentials, jwt_key=data.get("jwt_key"))
        return JWTUser(
            id=playload.get("id"),
            phone=playload.get("phone"),
        )

    @staticmethod
    async def _verify_jwt(token: str, jwt_key: str = None) -> dict:
        try:
            return verify_jwt(token=token, jwt_key=jwt_key)
        except Exception as e:
            raise CustomException(status=Status.UNAUTHORIZED_ERROR, msg=str(e))


def get_current_user(
        credentials: Optional[JWTAuthorizationCredentials] = Depends(JWTBearer(auto_error=False))
) -> Optional[JWTUser]:
    if not credentials:
        return None
    return credentials.user
