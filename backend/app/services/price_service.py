from datetime import datetime
from app.initializer import g
from app.datatype.monitor import Monitor
from app.utils import db_async
import asyncio
import threading
import time
import requests

RPC_URL = "http://15.235.226.149:9000"

class MonitorAccountThread(threading.Thread):
    def __init__(self, monitor, ws_manager):
        super().__init__()
        self.monitor = monitor
        self.ws_manager = ws_manager
        self.account_address = monitor['address']
        self.account_name = monitor['name']
        self.audio_path = monitor['audio_path']
        self.account_id = monitor['id']
        self.processed = set()
        self.first_run = True

    def run(self):
        while True:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "suix_queryTransactionBlocks",
                    "params": [
                        {
                            "filter": {"ToAddress": self.account_address},
                            "options": {"showEvents": True}
                        },
                        None,
                        1,
                        True
                    ]
                }
                response = requests.post(RPC_URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    new_transactions = [
                        tx for tx in data.get("result", {}).get("data", [])
                        if tx['digest'] not in self.processed
                    ]
                    for tx in new_transactions:
                        self.processed.add(tx['digest'])
                        time_str = datetime.fromtimestamp(
                            int(tx['timestampMs']) / 1000
                        ).strftime('%Y-%m-%d %H:%M:%S')
                        # 推送到 WebSocket
                        asyncio.run(self.ws_manager.broadcast_new_transaction({
                            "account_id": self.account_id,
                            "account_name": self.account_name,
                            "address": self.account_address,
                            "audio_path": self.audio_path,
                            "tx_time": time_str,
                            "tx_digest": tx['digest']
                        }))
                time.sleep(3)
            except Exception as e:
                print(f"监控账户 {self.account_name} 发生异常: {str(e)}")
                # 推送异常到前端
                try:
                    asyncio.run(self.ws_manager.broadcast_new_transaction({
                        "type": "error",
                        "account_name": self.account_name,
                        "error": str(e)
                    }))
                except Exception as push_err:
                    print(f"推送异常到前端失败: {push_err}")
                time.sleep(10)

class PriceService:
    def __init__(self, ws_manager):
        self.ws_manager = ws_manager
        self.threads = []

    async def start_monitoring(self):
        # 从数据库加载所有监控账户
        async with g.db_async_session() as session:
            monitors = await db_async.query_all(
                session=session,
                model=Monitor,
                fields=["id", "name", "address", "audio_path"]
            )
        # 启动每个账户的监控线程
        for monitor in monitors:
            t = MonitorAccountThread(monitor, self.ws_manager)
            t.daemon = True
            t.start()
            self.threads.append(t)

    async def get_monitor_data(self):
        """获取监控账户数据"""
        try:
            async with g.db_async_session() as session:
                monitors = await db_async.query_all(
                    session=session,
                    model=Monitor,
                    fields=["id", "name", "address", "audio_path"]
                )
                return monitors
        except Exception as e:
            g.logger.error(f"获取监控账户数据失败: {str(e)}")
            return []

    async def get_data(self):
        """只返回监控账户数据"""
        try:
            has_accounts = await self.has_monitor_accounts()
            if not has_accounts:
                result = {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": "未添加账户",
                    "monitor_data": []
                }
                print(f"[get_data] 返回结果: {result}")
                return result
            monitor_data = await self.get_monitor_data()
            result = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "monitor_data": monitor_data
            }
            print(f"[get_data] 返回结果: {result}")
            return result
        except Exception as e:
            g.logger.error(f"获取数据失败: {str(e)}")
            result = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "monitor_data": []
            }
            print(f"[get_data] 异常: {result}")
            return result

    async def has_monitor_accounts(self):
        """判断数据库中是否有监控账户"""
        try:
            async with g.db_async_session() as session:
                count = await db_async.query_total(session, Monitor)
                return count > 0
        except Exception as e:
            g.logger.error(f"检查监控账户失败: {str(e)}")
            return False

price_service = None  # 由 ws.py 初始化