import json
import threading
import time
from string import digits

import requests
import os
import subprocess

from datetime import datetime, timedelta, timezone

# 使用Windows媒体播放器播放音频，避免playsound问题

RPC_URL = "http://15.235.226.149:9000"


class AccountMonitor(threading.Thread):
    def __init__(self, account_name, config, warning_audio):  # 新增警告音频参数
        super().__init__()
        self.warning_audio = warning_audio  # 新增属性
        self.account_name = account_name
        self.audio_path = config['audio']
        self.account_address = config['url'].split('=')[-1]  # 从配置中提取地址
        self.start_time = int(time.time() * 1000)
        self.processed = set()
        self.first_run = True

    def _play_sound(self, audio_path):

        if audio_path and os.path.exists(audio_path):
            try:
                # 修改为直接启动独立进程播放，避免音频重叠
                subprocess.Popen(
                    f'start /B wmplayer "{audio_path}" /play /close',
                    shell=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True
            except Exception as e:
                print(f"播放音频失败: {audio_path}, 错误: {str(e)}")
                return False
        else:
            print(f"音频文件不存在: {audio_path}")
            return False

    def run(self):
        while True:
            try:

                payload = {
                    "jsonrpc": "2.0",
                    "id":2,
                    "method": "suix_queryTransactionBlocks",
                    "params": [
                        {
                            "filter": {"ToAddress": self.account_address},  # 查询发送到该地址的交易
                            "options": {
                                "showEvents": True  # 直接获取交易事件
                            }
                        },
                        None,
                        1,  # 查询 1 条最新记录
                        True
                    ]
                }

                response = requests.post(RPC_URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    # print(json.dumps(data, indent=2))  # 格式化输出 JSON

                    # 首次运行显示最近交易时间
                    if self.first_run:
                        events = data.get("result", {}).get("data", [])
                        # print(events)
                        if events:
                            latest_time = datetime.fromtimestamp(
                                int(events[0]['timestampMs']) / 1000
                            ).strftime('%Y-%m-%d %H:%M:%S')

                            # digest = events[0]['digest']  # 原变量名 digits 有拼写错误
                            # print(f"交易哈希: {digest}")
                            print(f"\n📌 {self.account_name} 最近交易时间：{latest_time}")
                        self.first_run = False

                    # 处理新交易
                    new_transactions = [
                        tx for tx in data.get("result", {}).get("data", [])
                        # 修复字段层级 (原数据直接包含 digest)
                        if int(tx['timestampMs']) > self.start_time
                           and tx['digest'] not in self.processed  # 移除 id 层级
                    ]

                    for tx in new_transactions:
                        print(f"音频路径: {self.audio_path}")
                        self._play_sound(self.audio_path)
                        # 修复字段记录方式
                        self.processed.add(tx['digest'])  # 直接使用 digest
                        time_str = datetime.fromtimestamp(
                            int(tx['timestampMs']) / 1000
                        ).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"\n🐍{self.account_name} 新交易")
                        print(f"时间: {time_str}")
                        print(f"交易哈希: {tx['digest']}")  # 直接使用 digest

                time.sleep(3)  # 每3秒查询一次

            except Exception as e:
                # 播放警告声音
                if self.warning_audio:
                    self._play_sound(self.warning_audio)
                print(f"❌ {self.account_name} 监控异常: {str(e)}")
                time.sleep(10)


if __name__ == '__main__':
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'accounts.json')  # 修改文件名

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            accounts = config_data['accounts']
            warning_audio = config_data.get('warning', {}).get('audio')

        print("Sui交易监控系统启动")
        monitors = []

        for acc_name, cfg in accounts.items():
            monitor = AccountMonitor(acc_name, cfg, warning_audio)
            monitor.daemon = True
            monitor.start()
            monitors.append(monitor)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n停止监控程序...")
    except FileNotFoundError:
        print(f"配置文件不存在: {config_path}")
    except json.JSONDecodeError:
        print(f"配置文件格式错误: {config_path}")
    except Exception as e:
        print(f"启动失败: {str(e)}")




