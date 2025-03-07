from typing import List, Optional
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langtrans.v1.llms.base import OpenAIChat
from concurrent.futures import ThreadPoolExecutor
from langtrans.v1.configer import CustomKeyConfiger
from langtrans.v1.config import CONFIG_PATH

class TextMapReducer:
    def __init__(
        self,
        chunk_size: int = 4000,
        chunk_overlap: int = 200,
        model: Optional[str] = None,
        tiktoken_model: str = "cl100k_base",
        openai_api_key: Optional[str] = None,
        openai_base_url: Optional[str] = None,
        max_workers: int = 16
    ):
        """
        初始化文本Map-Reduce总结器
        """
        config = CustomKeyConfiger(CONFIG_PATH)
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model = model or config.get_key("DEFAULT_MODEL") or "qwen-max"  # deepseek-chat
        self.tiktoken_model = tiktoken_model
        self.client = OpenAIChat(api_key=openai_api_key, base_url=openai_base_url)
        self.max_workers = max_workers
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=self._num_tokens,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
    def _num_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        encoding = tiktoken.get_encoding(self.tiktoken_model)
        return len(encoding.encode(text))
    
    def _call_openai_api(self, prompt: str,print_token:bool=False) -> str:
        """调用OpenAI API进行总结"""
        try:
            response = self.client.chat(prompt, model=self.model)
            return response
        except Exception as e:
            print(f"调用OpenAI API时出错: {str(e)}")
            return ""

    def _map_chunk(self, chunk: str,min_tokens: int = 100) -> str:
        #Map阶段：对单个文本块进行总结
        prompt = f"""请对以下文本进行简洁的总结，捕捉主要内容和关键点：

{chunk}

总结要求：
1. 保留重要的事实和细节
2. 确保信息准确性
3. 使用清晰简洁的语言
4. 突出关键观点和主题
5. 不要输出多余的介绍信息
6. 必须使用中文进行总结
"""
        
        if self._num_tokens(chunk) < min_tokens:
            return chunk
        return self._call_openai_api(prompt)

    def _reduce_summaries(self, summaries: List[str]) -> str:
        """Reduce阶段：将多个总结合并成最终总结"""
        combined_summaries = "\n\n".join([f"总结{i+1}:\n{summary}" for i, summary in enumerate(summaries)])
        
        prompt = f"""请将以下多个文本总结合并成一个连贯的最终总结：

{combined_summaries}

合并要求：
1. 整合所有重要信息，避免重复
2. 保持逻辑顺序和连贯性
3. 突出主要观点和主题
4. 确保最终总结完整且易于理解
5. 不要输出多余的介绍信息 比如 综合总结、最终总结 之类的
6. 必须使用中文进行合并总结
"""
#请提供最终总结：       
        return self._call_openai_api(prompt,print_token=True)

    def summarize(self, text: str,print_map_result: bool = False) -> str:
        """
        使用Map-Reduce方法对文本进行总结
        
        Args:
            text: 需要总结的完整文本
            print_map_result: 是否打印Map阶段的结果
            
        Returns:
            str: 最终的总结文本
        """
        # 分割文本
        chunks = self.text_splitter.split_text(text)
        
        if not chunks:
            return ""
        
        # Map阶段：并行处理各个文本块
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            chunk_summaries = list(executor.map(self._map_chunk, chunks))
        if print_map_result:
            print("Map阶段结果:")
            for i, summary in enumerate(chunk_summaries):
                print(f"map{i}:\n{summary}")
        # 如果只有一个总结，直接返回
        if len(chunk_summaries) == 1:
            return chunk_summaries[0]
        
        # Reduce阶段：合并所有总结
        final_summary = self._reduce_summaries(chunk_summaries)
        
        return final_summary
    
    
# 使用示例
if __name__ == "__main__":
    import time
    start_time = time.time()
    with open("大叔合并5k.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    summarizer = TextMapReducer(
        chunk_size=3000,
        chunk_overlap=200
    )
    summary = summarizer.summarize(text,print_map_result=True)
    print("\n\n")
    print(summary)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Running time: {elapsed_time:.2f} seconds")