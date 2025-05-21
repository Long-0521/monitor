"""
@author axiner
@version v1.0.0
@created 2024/7/29 22:22
@abstract main
@description
@history
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app import (
    router,
    middleware,
)
from app.initializer import g

# 确保在所有导入之前初始化
g.setup()

# 在初始化之后导入其他模块
from app.api.v1 import ws

# #
openapi_url = "/openapi.json"
docs_url = "/docs"
redoc_url = "/redoc"
if g.config.is_disable_docs is True:
    openapi_url, docs_url, redoc_url = None, None, None


@asynccontextmanager
async def lifespan(app_: FastAPI):
    g.logger.info(f"Application using config file '{g.config.yamlname}'")
    g.logger.info(f"Application name '{g.config.appname}'")
    g.logger.info(f"Application version '{g.config.appversion}'")
    # #
    g.logger.info("Application server running")
    yield
    g.logger.info("Application server shutdown")


app = FastAPI(
    title=g.config.appname,
    version=g.config.appversion,
    debug=g.config.debug,
    openapi_url=openapi_url,
    docs_url=docs_url,
    redoc_url=redoc_url,
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # 允许前端开发服务器的请求
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"],  # 允许前端访问所有响应头
)

# 挂载静态文件目录
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# #
router.register_routers(app)
middleware.register_middlewares(app)

# 包含WebSocket路由
app.include_router(ws.ws_router, prefix="/api/v1", tags=["websocket"])
