"""
聊天助手类 - 提供多轮对话和记忆功能
"""
import json
import os
from datetime import datetime
from typing import List, Dict
from openai import OpenAI
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from models import DoubaoLLM
from config import DOUBAO_BASE_URL, DOUBAO_MODEL, HISTORY_DIR, DEFAULT_MODE

class ChatAssistant:
    """整合多种对话模式的聊天助手"""
    
    def __init__(self, model_name=DOUBAO_MODEL):
        """初始化聊天助手
        
        Args:
            model_name: 模型名称
        """
        # 初始化LLM
        self.llm = DoubaoLLM()
        self.model_name = model_name
        self.client = OpenAI(
            base_url=DOUBAO_BASE_URL,
            api_key=os.environ.get("Doubao_API_KEY")
        )
        
        # 初始化LangChain会话
        self._setup_langchain()
        
        # 初始化原生对话历史
        self._setup_native()
        
        # 对话模式: "langchain" 或 "native"
        self.mode = DEFAULT_MODE
        
        # 确保对话历史目录存在
        os.makedirs(HISTORY_DIR, exist_ok=True)
    
    def _setup_langchain(self):
        """设置LangChain对话组件"""
        # 创建提示模板
        custom_prompt = PromptTemplate(
            input_variables=["history", "input"],
            template="""你是一个知识渊博、乐于助人的AI助手。

以下是你与用户的对话历史：
{history}

用户：{input}
AI助手："""
        )
        # 创建记忆组件
        self.memory = ConversationBufferMemory(ai_prefix="AI助手", human_prefix="用户")
        # 创建对话链
        self.conversation = ConversationChain(
            llm=self.llm,
            prompt=custom_prompt,
            memory=self.memory,
            verbose=False
        )
    
    def _setup_native(self):
        """设置原生对话组件"""
        self.messages = []
        self.add_message("system", "你是一个知识渊博、乐于助人的AI助手。提供准确、有用的信息，并保持礼貌和友好。")
    
    def add_message(self, role: str, content: str) -> None:
        """添加消息到原生对话历史
        
        Args:
            role: 消息角色 (user/assistant/system)
            content: 消息内容
        """
        self.messages.append({"role": role, "content": content})
    
    def get_native_response(self, user_input: str) -> str:
        """使用原生对话接口获取回复
        
        Args:
            user_input: 用户输入
            
        Returns:
            AI回复文本
        """
        self.add_message("user", user_input)
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages
        )
        response = completion.choices[0].message.content
        self.add_message("assistant", response)
        return response
    
    def get_langchain_response(self, user_input: str) -> str:
        """使用LangChain获取回复
        
        Args:
            user_input: 用户输入
            
        Returns:
            AI回复文本
        """
        return self.conversation.predict(input=user_input)
    
    def get_response(self, user_input: str) -> str:
        """根据当前模式获取回复
        
        Args:
            user_input: 用户输入
            
        Returns:
            AI回复文本
        """
        if self.mode == "native":
            return self.get_native_response(user_input)
        else:
            return self.get_langchain_response(user_input)
    
    def clear_history(self) -> None:
        """清空对话历史"""
        if self.mode == "native":
            # 保留system消息
            system_messages = [msg for msg in self.messages if msg["role"] == "system"]
            self.messages = system_messages
        else:
            self.memory.clear()
    
    def switch_mode(self) -> str:
        """切换对话模式
        
        Returns:
            提示消息
        """
        if self.mode == "langchain":
            self.mode = "native"
            return "已切换到原生对话模式"
        else:
            self.mode = "langchain"
            return "已切换到LangChain对话模式"
    
    def save_history(self) -> str:
        """保存对话历史到文件
        
        Returns:
            提示消息
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{HISTORY_DIR}/chat_{timestamp}.json"
        
        if self.mode == "native":
            self._save_native_history(filename)
        else:
            self._save_langchain_history(filename)
                
        return f"对话历史已保存到 {filename}"
    
    def _save_native_history(self, filename: str):
        """保存原生对话历史
        
        Args:
            filename: 保存的文件名
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)
    
    def _save_langchain_history(self, filename: str):
        """保存LangChain对话历史
        
        Args:
            filename: 保存的文件名
        """
        # 转换LangChain记忆格式为标准格式
        history = []
        for i, entry in enumerate(self.memory.chat_memory.messages):
            if i % 2 == 0:  # 用户消息
                history.append({"role": "user", "content": entry.content})
            else:  # AI消息
                history.append({"role": "assistant", "content": entry.content})
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def load_history(self, filename: str) -> str:
        """从文件加载对话历史
        
        Args:
            filename: 历史文件名
            
        Returns:
            提示消息
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # 清空当前历史
            self.clear_history()
            
            if self.mode == "native":
                self._load_native_history(history)
            else:
                self._load_langchain_history(history)
            
            return f"已加载对话历史，共 {len(history)} 条消息"
        except Exception as e:
            return f"加载对话历史失败: {str(e)}"
    
    def _load_native_history(self, history: List[Dict[str, str]]):
        """加载原生格式历史
        
        Args:
            history: 历史记录列表
        """
        # 添加所有消息到原生历史
        for msg in history:
            self.add_message(msg["role"], msg["content"])
    
    def _load_langchain_history(self, history: List[Dict[str, str]]):
        """加载LangChain格式历史
        
        Args:
            history: 历史记录列表
        """
        # 添加到LangChain记忆
        for msg in history:
            if msg["role"] == "user":
                self.memory.chat_memory.add_user_message(msg["content"])
            elif msg["role"] == "assistant":
                self.memory.chat_memory.add_ai_message(msg["content"])