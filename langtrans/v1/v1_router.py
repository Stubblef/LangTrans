import re, json, os, asyncio, time
from typing import List, Dict, Any, Union
from pydantic import BaseModel
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from langtrans.v1.llms.base import OpenAIChat
from langtrans.utils.logging_config import logger

# 创建路由器，移除prefix参数
v1_router = APIRouter()

# 用于存储日志的队列
log_messages = asyncio.Queue()

# SSE 推送日志消息
async def log_stream():
    while True:
        msg = await log_messages.get()
        yield f"data: {msg}\n\n"
        await asyncio.sleep(0.5)

chat = OpenAIChat()

@v1_router.get("/v1/logs/stream")
async def stream_logs():
    return StreamingResponse(log_stream(), media_type="text/event-stream")

@v1_router.post("/v1/test")
async def test(data: Dict[str, Any]):
    return JSONResponse(content=data)

# 添加更多路由...
