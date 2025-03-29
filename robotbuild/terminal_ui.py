"""
终端交互界面 - 提供命令行交互功能
"""
import sys
import time
from colorama import Fore, Style, init

from assistant import ChatAssistant
from config import TYPEWRITER_SPEED

# 初始化colorama - 支持终端颜色显示
init(autoreset=True)

class ChatTerminal:
    """增强的终端交互界面"""
    
    def __init__(self):
        """初始化终端界面"""
        self.assistant = ChatAssistant()
        # 定义可用命令
        self.commands = {
            "/help": self.show_help,
            "/quit": self.quit_chat,
            "/clear": self.clear_history,
            "/mode": self.switch_mode,
            "/save": self.save_history,
            "/load": self.load_history,
            "/status": self.show_status
        }
    
    def show_help(self, *args) -> str:
        """显示帮助信息
        
        Returns:
            帮助文本
        """
        help_text = f"""
{Fore.CYAN}===== 聊天助手命令帮助 =====
{Fore.GREEN}/help{Style.RESET_ALL}   - 显示此帮助信息
{Fore.GREEN}/quit{Style.RESET_ALL}   - 退出聊天
{Fore.GREEN}/clear{Style.RESET_ALL}  - 清除对话历史
{Fore.GREEN}/mode{Style.RESET_ALL}   - 切换对话模式（原生/LangChain）
{Fore.GREEN}/save{Style.RESET_ALL}   - 保存对话历史
{Fore.GREEN}/load{Style.RESET_ALL} [文件名] - 加载对话历史
{Fore.GREEN}/status{Style.RESET_ALL} - 显示当前状态
{Fore.CYAN}=========================={Style.RESET_ALL}
"""
        return help_text
    
    def quit_chat(self, *args) -> str:
        """退出聊天
        
        Returns:
            永不返回，直接退出程序
        """
        print(f"{Fore.YELLOW}感谢使用聊天助手，再见！")
        sys.exit(0)
    
    def clear_history(self, *args) -> str:
        """清除对话历史
        
        Returns:
            成功消息
        """
        self.assistant.clear_history()
        return "对话历史已清除"
    
    def switch_mode(self, *args) -> str:
        """切换对话模式
        
        Returns:
            模式切换结果
        """
        return self.assistant.switch_mode()
    
    def save_history(self, *args) -> str:
        """保存对话历史
        
        Returns:
            保存结果
        """
        return self.assistant.save_history()
    
    def load_history(self, *args) -> str:
        """加载对话历史
        
        Args:
            *args: 命令参数，第一个参数应为文件名
            
        Returns:
            加载结果
        """
        if len(args) < 1:
            return "错误：需要提供文件名。用法：/load [文件名]"
        return self.assistant.load_history(args[0])
    
    def show_status(self, *args) -> str:
        """显示当前状态
        
        Returns:
            状态信息
        """
        mode = "原生对话" if self.assistant.mode == "native" else "LangChain"
        msg_count = len(self.assistant.messages) if self.assistant.mode == "native" else \
                    len(self.assistant.memory.chat_memory.messages) // 2
        
        return f"""
{Fore.CYAN}===== 当前状态 =====
{Fore.GREEN}对话模式:{Style.RESET_ALL} {mode}
{Fore.GREEN}模型名称:{Style.RESET_ALL} {self.assistant.model_name}
{Fore.GREEN}消息数量:{Style.RESET_ALL} {msg_count}
{Fore.CYAN}================={Style.RESET_ALL}
"""
    
    def typewriter_effect(self, text):
        """打字机效果显示文本
        
        Args:
            text: 要显示的文本
        """
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(TYPEWRITER_SPEED)
        sys.stdout.write("\n")
    
    def run(self):
        """运行聊天终端"""
        # 显示欢迎信息
        self._show_welcome()
        
        # 主循环
        while True:
            # 获取用户输入
            user_input = input(f"{Fore.GREEN}您{Style.RESET_ALL} > ")
            
            # 处理命令或对话
            if user_input.startswith("/"):
                self._handle_command(user_input)
            else:
                self._handle_conversation(user_input)
    
    def _show_welcome(self):
        """显示欢迎信息"""
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}{'='*15} {Fore.YELLOW}豆包AI多轮对话系统 {Fore.CYAN}{'='*15}")
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.GREEN}输入 {Fore.YELLOW}/help{Fore.GREEN} 查看命令列表，输入 {Fore.YELLOW}/quit{Fore.GREEN} 退出程序")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    def _handle_command(self, user_input):
        """处理命令输入
        
        Args:
            user_input: 用户输入的命令
        """
        cmd_parts = user_input.split()
        cmd = cmd_parts[0]
        args = cmd_parts[1:] if len(cmd_parts) > 1 else []
        
        if cmd in self.commands:
            result = self.commands[cmd](*args)
            print(f"{Fore.YELLOW}系统{Style.RESET_ALL} > {result}")
        else:
            print(f"{Fore.YELLOW}系统{Style.RESET_ALL} > 未知命令: {cmd}。输入 /help 查看可用命令。")
    
    def _handle_conversation(self, user_input):
        """处理对话输入
        
        Args:
            user_input: 用户消息
        """
        print(f"{Fore.BLUE}AI{Style.RESET_ALL} > ", end="")
        try:
            response = self.assistant.get_response(user_input)
            self.typewriter_effect(response)
        except Exception as e:
            print(f"{Fore.RED}错误: {str(e)}{Style.RESET_ALL}")