from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
from datetime import datetime
from app.services.price_service import price_service

ws_router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # 存储所有活跃的WebSocket连接
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@ws_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 获取价格数据
            price_data = price_service.get_price_data()
            # 发送消息
            await manager.send_personal_message(json.dumps(price_data), websocket)
            # 等待10秒
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        manager.disconnect(websocket) 