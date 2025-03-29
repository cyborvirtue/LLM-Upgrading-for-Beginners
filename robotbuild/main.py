"""
主程序入口 - 启动聊天终端
"""
from terminal_ui import ChatTerminal

def main():
    """程序入口函数"""
    # 创建并运行终端界面
    terminal = ChatTerminal()
    terminal.run()

if __name__ == "__main__":
    main()