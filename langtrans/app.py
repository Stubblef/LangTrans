from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests, json, os
from contextlib import asynccontextmanager
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi import File, UploadFile, HTTPException

from langtrans.v1.llms.base import OpenAIChat
from langtrans.map_reduce import TextMapReducer

summarizer = TextMapReducer(
        chunk_size=3000,
        chunk_overlap=200
    )

# 修改导入方式
from langtrans.v1.v1_router import v1_router
from langtrans.utils.logging_config import logger
chat = OpenAIChat()

SUMM_PROMPT = "你是一个专业的文本总结助手。请对给定的文本进行精确的总结,保留关键信息。"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Application is starting up")
    try:
        yield
    except Exception as e:
        logger.exception(e)
        raise 
    finally:
        logger.debug("Application is shutting down")
        import gc
        gc.collect()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom exception handler
@app.exception_handler(Exception)
async def exception_handler(request, exc):
    logger.error(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )

# Add custom route handler
class CustomRoute(APIRoute):
    async def handle(self, request):
        try:
            return await super().handle(request)
        except Exception as e:
            logger.error(f"Error: {e}")
            raise e


# 添加聊天路由
class ChatMessage(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(message: ChatMessage):
    try:
        # 这里可以添加实际的聊天逻辑
        # return {"reply": f"收到您的消息：{message.message}"} # 测试用
        # res = chat.chat(message.message) # 调用OpenAI API
        
        token_length = summarizer._num_tokens(message.message) # 检查文本长度
        logger.debug(f"文本长度: {token_length}")
        
        if 100 < token_length < 300_000:
            res = chat.chat(SUMM_PROMPT +"```" + message.message + "```")
            return {"reply": res}
        
        
        # 使用Map-Reduce总结器   
        summary = summarizer.summarize(message.message,print_map_result=True)
        if summary == message.message:
            res = chat.chat(message.message)
            return {"reply": res}
        else:
            return {"reply": summary}        
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# 添加文件上传路由
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    prompt: str = Form(...)
):
    """
    上传文件
    要求： 仅支持txt文件
    """
    # try:
    contents = await file.read()
    text = contents.decode()
    token_length = summarizer._num_tokens(text) # 检查文本长度
    logger.debug(f"文本长度: {token_length}")
    if 100 < token_length < 300_000:
        res = chat.chat(SUMM_PROMPT +"```" + text + "```" + prompt)
        logger.debug("直接调用OpenAI API")
        return {"filename": file.filename, "summary": res}
    
    # 使用Map-Reduce总结器处理文件内容和提示
    if prompt:
        modified_prompt = f"{prompt}\n\n文件内容:\n{text}"
        summary = summarizer.summarize(modified_prompt, print_map_result=True)
    else:
        summary = summarizer.summarize(text, print_map_result=True)
        
    return {
        "filename": file.filename,
        "summary": summary
    }
    # except Exception as e:
    #     logger.error(f"Upload error: {e}")
    #     raise HTTPException(status_code=500, detail="Upload failed")

app.router.route_class = CustomRoute

# 修改路由包含方式
app.include_router(v1_router)

app.mount("/", StaticFiles(directory="../static", html=True), name="static")