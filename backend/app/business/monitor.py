from typing import List, Tuple

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
            update_data = {}
            if self.name is not None:
                update_data["name"] = self.name
            if self.address is not None:
                update_data["address"] = self.address
            if self.audio_path is not None:
                update_data["audio_path"] = self.audio_path
            
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
            stmt = delete(Monitor).where(Monitor.id == monitor_id)
            result = await session.execute(stmt)
            await session.commit()
            return [monitor_id] if result.rowcount > 0 else [] 