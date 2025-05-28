from typing import List, Tuple
import os

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.datatype.monitor import (
    Monitor,
    MonitorDetailMdl,
    MonitorListMdl,
    MonitorCreateMdl,
    MonitorUpdateMdl,
    MonitorDeleteMdl,
)
from app.initializer import g
from app.utils import db_async


def get_audio_file_path(audio_path: str) -> str:
    """获取音频文件的完整路径"""
    if not audio_path:
        return ""
    # 从项目根目录开始构建路径
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # 移除路径中的 static 前缀，因为 base_dir 已经包含了 static 目录
    if audio_path.startswith('static/'):
        audio_path = audio_path[7:]  # 移除 'static/' 前缀
    return os.path.join(base_dir, audio_path)


def delete_audio_file(audio_path: str) -> bool:
    """删除音频文件"""
    if not audio_path:
        return False
    
    try:
        full_path = get_audio_file_path(audio_path)
        g.logger.info(f"尝试删除音频文件，完整路径: {full_path}")
        
        if os.path.exists(full_path):
            os.remove(full_path)
            g.logger.info(f"成功删除音频文件: {full_path}")
            return True
        else:
            g.logger.warning(f"音频文件不存在: {full_path}")
            return False
    except Exception as e:
        g.logger.error(f"删除音频文件失败: {str(e)}, 路径: {full_path}")
        return False


class MonitorDetailBiz(MonitorDetailMdl):
    async def detail(self) -> dict:
        async with g.db_async_session() as session:
            data = await db_async.query_one(
                session=session,
                model=Monitor,
                fields=self.response_fields(),
                filter_by={"id": self.id},
            )
            return data


class MonitorListBiz(MonitorListMdl):
    async def lst(self) -> Tuple[List[dict], int]:
        async with g.db_async_session() as session:
            data = await db_async.query_all(
                session=session,
                model=Monitor,
                fields=self.response_fields(),
                page=self.page,
                size=self.size,
            )
            total = await db_async.query_total(session, Monitor)
            return data, total


class MonitorCreateBiz(MonitorCreateMdl):
    async def create(self) -> str:
        async with g.db_async_session() as session:
            monitor = Monitor(
                name=self.name,
                address=self.address,
                audio_path=self.audio_path,
            )
            session.add(monitor)
            await session.commit()
            return monitor.id


class MonitorUpdateBiz(MonitorUpdateMdl):
    async def update(self, monitor_id: str) -> List[str]:
        async with g.db_async_session() as session:
            # 获取旧的音频路径
            old_monitor = await db_async.query_one(
                session=session,
                model=Monitor,
                fields=["audio_path"],
                filter_by={"id": monitor_id},
            )
            
            update_data = {}
            if self.name is not None:
                update_data["name"] = self.name
            if self.address is not None:
                update_data["address"] = self.address
            if self.audio_path is not None:
                update_data["audio_path"] = self.audio_path
                # 如果更新了音频路径，删除旧文件
                if old_monitor and old_monitor.get("audio_path"):
                    delete_audio_file(old_monitor["audio_path"])
            
            if not update_data:
                return []
            
            stmt = (
                update(Monitor)
                .where(Monitor.id == monitor_id)
                .values(**update_data)
            )
            result = await session.execute(stmt)
            await session.commit()
            return [monitor_id] if result.rowcount > 0 else []


class MonitorDeleteBiz(MonitorDeleteMdl):
    async def delete(self, monitor_id: str) -> List[str]:
        async with g.db_async_session() as session:
            # 获取监控账户信息
            monitor = await db_async.query_one(
                session=session,
                model=Monitor,
                fields=["audio_path"],
                filter_by={"id": monitor_id},
            )
            
            # 删除数据库记录
            stmt = delete(Monitor).where(Monitor.id == monitor_id)
            result = await session.execute(stmt)
            await session.commit()
            
            # 如果删除成功且存在音频文件，则删除音频文件
            if result.rowcount > 0 and monitor and monitor.get("audio_path"):
                g.logger.info(f"准备删除监控账户 {monitor_id} 的音频文件: {monitor['audio_path']}")
                delete_audio_file(monitor["audio_path"])
            
            return [monitor_id] if result.rowcount > 0 else [] 