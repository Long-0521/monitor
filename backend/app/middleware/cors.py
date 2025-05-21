from fastapi.middleware.cors import CORSMiddleware


class Cors:
    middleware_class = CORSMiddleware
    allow_origins = [
        "http://localhost:8000",
        "http://localhost:3000",  # React 开发服务器
        "http://127.0.0.1:3000",  # React 开发服务器（备用地址）
        "http://127.0.0.1:8000",  # 后端服务器（备用地址）
    ]
    allow_credentials = True
    allow_methods = ["*"]  # 允许所有 HTTP 方法
    allow_headers = ["*"]  # 允许所有请求头
