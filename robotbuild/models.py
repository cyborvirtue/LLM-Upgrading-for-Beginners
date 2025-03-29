"""
LLM模型类 - 为LangChain框架定义豆包AI接口
"""
from typing import Any
from langchain.llms.base import LLM
from openai import OpenAI
import os
from config import DOUBAO_BASE_URL, DOUBAO_MODEL

class DoubaoLLM(LLM):
    """豆包AI LLM 封装类 - 用于LangChain集成"""
    
    model_name: str = DOUBAO_MODEL
    
    def __init__(self):
        """初始化DoubaoLLM实例"""
        super().__init__()
        self._client = OpenAI(
            base_url=DOUBAO_BASE_URL,
            api_key=os.environ.get("Doubao_API_KEY")
        )
    
    @property
    def client(self) -> Any:
        """获取API客户端"""
        return self._client

    @client.setter
    def client(self, value: Any):
        """设置API客户端"""
        self._client = value

    def _call(self, prompt: str, **kwargs) -> str:
        """调用LLM生成回复
        
        Args:
            prompt: 用户输入提示
            **kwargs: 其他参数
            
        Returns:
            生成的响应文本
        """
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content

    @property
    def _llm_type(self) -> str:
        """返回LLM类型标识"""
        return "doubao"