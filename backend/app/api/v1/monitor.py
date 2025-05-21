import traceback

from fastapi import APIRouter, Depends

from app.api.response import Response, response_docs
from app.api.status import Status
from app.business.monitor import (
    MonitorDetailBiz,
    MonitorListBiz,
    MonitorCreateBiz,
    MonitorUpdateBiz,
    MonitorDeleteBiz,
)
from app.initializer import g
from app.middleware.auth import JWTUser, get_current_user

monitor_router = APIRouter()


@monitor_router.get(
    path="/monitor/{monitor_id}",
    summary="monitorDetail",
    responses=response_docs(
        model=MonitorDetailBiz,
    ),
)
async def detail(
        monitor_id: str,
        current_user: JWTUser = Depends(get_current_user),
):
    try:
        monitor_biz = MonitorDetailBiz(id=monitor_id)
        data = await monitor_biz.detail()
        if not data:
            return Response.failure(msg="未匹配到记录", status=Status.RECORD_NOT_EXIST_ERROR)
    except Exception as e:
        g.logger.error(traceback.format_exc())
        return Response.failure(msg="monitorDetail失败", error=e)
    return Response.success(data=data)


@monitor_router.get(
    path="/monitor",
    summary="monitorList",
    responses=response_docs(
        model=MonitorListBiz,
        is_listwrap=True,
        listwrap_key="items",
        listwrap_key_extra={
            "total": "int",
        },
    ),
)
async def lst(
        page: int = 1,
        size: int = 10,
        current_user: JWTUser = Depends(get_current_user),
):
    try:
        monitor_biz = MonitorListBiz(page=page, size=size)
        data, total = await monitor_biz.lst()
    except Exception as e:
        g.logger.error(traceback.format_exc())
        return Response.failure(msg="monitorList失败", error=e)
    return Response.success(data={"items": data, "total": total})


@monitor_router.post(
    path="/monitor",
    summary="monitorCreate",
    responses=response_docs(data={
        "id": "str",
    }),
)
async def create(
        monitor_biz: MonitorCreateBiz,
        current_user: JWTUser = Depends(get_current_user),
):
    try:
        monitor_id = await monitor_biz.create()
    except Exception as e:
        g.logger.error(traceback.format_exc())
        return Response.failure(msg="monitorCreate失败", error=e)
    return Response.success(data={"id": monitor_id})


@monitor_router.put(
    path="/monitor/{monitor_id}",
    summary="monitorUpdate",
    responses=response_docs(data={
        "id": "str",
    }),
)
async def update(
        monitor_id: str,
        monitor_biz: MonitorUpdateBiz,
        current_user: JWTUser = Depends(get_current_user),
):
    try:
        updated_ids = await monitor_biz.update(monitor_id)
        if not updated_ids:
            return Response.failure(msg="未匹配到记录", status=Status.RECORD_NOT_EXIST_ERROR)
    except Exception as e:
        g.logger.error(traceback.format_exc())
        return Response.failure(msg="monitorUpdate失败", error=e)
    return Response.success(data={"id": monitor_id})


@monitor_router.delete(
    path="/monitor/{monitor_id}",
    summary="monitorDelete",
    responses=response_docs(data={
        "id": "str",
    }),
)
async def delete(
        monitor_id: str,
        current_user: JWTUser = Depends(get_current_user),
):
    try:
        monitor_biz = MonitorDeleteBiz()
        deleted_ids = await monitor_biz.delete(monitor_id)
        if not deleted_ids:
            return Response.failure(msg="未匹配到记录", status=Status.RECORD_NOT_EXIST_ERROR)
    except Exception as e:
        g.logger.error(traceback.format_exc())
        return Response.failure(msg="monitorDelete失败", error=e)
    return Response.success(data={"id": monitor_id}) 