from typing import Optional
from pydantic import BaseModel
from openai import OpenAI
from fastapi.responses import JSONResponse
from langtrans.v1.configer import CustomKeyConfiger
from langtrans.v1.config import CONFIG_PATH

CONFIG_PATH = CONFIG_PATH

# class Context(BaseModel):
#     def __init__(self, api_key: str, base_url: str, **kwargs):
        # self.client = OpenAI(api_key=api_key, base_url=base_url)

class OpenAIChat:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        config = CustomKeyConfiger(CONFIG_PATH)
        print(f"config path: {config}")
        # 定义 API 密钥的优先级顺序
        api_key_priorities = [
            "OPENAI_API_KEY",
            "DEEPSEEK_API_KEY",
            "ANTHROPIC_API_KEY"
        ]
        
        # 如果没有提供 api_key，从配置中获取
        if api_key is None:
            for key_prefix in api_key_priorities:
                api_key = next((config.get_key(key) for key in config.keys if key.startswith(key_prefix)), None)
                if api_key:
                    break
            
            if api_key is None:
                raise ValueError("No valid API key found in configuration")
        
        # 如果没有提供 base_url，从配置中获取，或使用默认值
        if base_url is None:
            base_url = config.get_key("OPENAI_API_BASE") or config.get_key("DEEPSEEK_API_BASE") or "https://api.openai.com/v1"
        
        print(f"API key: {api_key}, Base URL: {base_url} ")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def chat(self, prompt: str, model: str = "qwen-max"):  # deepseek-chat
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        )
        
        return response.choices[0].message.content

# 使用示例
if __name__ == "__main__":
    try:
        chat = OpenAIChat()
        response = chat.chat("你好，请介绍一下你自己。")
        print(response)  # .body.decode()
    except Exception as e:
        print(f"Error: {str(e)}")