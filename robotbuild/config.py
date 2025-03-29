"""
配置文件 - 包含API密钥和系统设置
"""
import os

# 豆包AI API设置
DOUBAO_API_KEY = 'your_api_key'
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DOUBAO_MODEL = "doubao-1-5-lite-32k-250115"

# 设置API密钥环境变量
os.environ["Doubao_API_KEY"] = DOUBAO_API_KEY

# 系统设置
HISTORY_DIR = "chat_history"
DEFAULT_MODE = "langchain"  # 'langchain' 或 'native'

# 终端UI设置
TYPEWRITER_SPEED = 0.005  # 打字机效果速度（秒/字符）