import traceback
import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

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

# 音频文件保存目录
AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# 允许的音频文件类型
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mp4": ".m4a",
    "audio/aac": ".aac",
}

# 最大文件大小（10MB）
MAX_FILE_SIZE = 10 * 1024 * 1024


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


@monitor_router.post("/monitor/upload-audio", summary="上传音频文件")
async def upload_audio(
    file: UploadFile = File(...),
    current_user: JWTUser = Depends(get_current_user)
):
    """
    上传音频文件
    - 支持的文件类型：mp3, wav, m4a, aac
    - 返回：音频文件的相对路径，用于创建 monitor 时使用
    """
    try:
        # 检查文件类型
        if file.content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型。支持的类型：{', '.join(ALLOWED_AUDIO_TYPES.keys())}"
            )

        # 读取文件内容
        content = await file.read()

        # 生成安全的文件名
        ext = ALLOWED_AUDIO_TYPES[file.content_type]
        safe_filename = f"{g.snow_cli.gen_uid()}{ext}"
        save_path = os.path.join(AUDIO_DIR, safe_filename)

        # 保存文件
        with open(save_path, "wb") as f:
            f.write(content)

        # 返回相对路径
        rel_path = f"static/audio/{safe_filename}"
        return Response.success(data={"audio_path": rel_path})

    except HTTPException as e:
        return Response.failure(msg=str(e.detail), status=e.status_code)
    except Exception as e:
        g.logger.error(traceback.format_exc())
        return Response.failure(msg="音频上传失败", error=e) 