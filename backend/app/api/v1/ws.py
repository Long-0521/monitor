from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
from app.services.price_service import PriceService

ws_router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def broadcast_new_transaction(self, tx_data):
        message = json.dumps({"type": "new_transaction", "data": tx_data})
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()
price_service = PriceService(manager)

@ws_router.on_event("startup")
async def startup_event():
    await price_service.start_monitoring()

@ws_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 你可以定时推送所有监控账户的快照（可选）
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)