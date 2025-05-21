import requests
import json
from datetime import datetime

class PriceService:
    def __init__(self):
        self.url = 'http://www.xinfadi.com.cn/getPriceData.html'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }

    def get_price_data(self):
        try:
            with True:
                response = requests.post(url=self.url, headers=self.headers).json()
                return {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": response
                }
        except Exception as e:
            return {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }

price_service = PriceService() 