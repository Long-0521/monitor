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

from app import (
    router,
    middleware,
)
from app.initializer import g
from app.api.v1 import ws

g.setup()
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
    allow_origins=["*"],  # 在生产环境中应该设置具体的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# #
router.register_routers(app)
middleware.register_middlewares(app)

# 包含WebSocket路由
app.include_router(ws.ws_router, prefix="/api/v1", tags=["websocket"])
