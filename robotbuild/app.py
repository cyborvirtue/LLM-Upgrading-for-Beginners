from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from assistant import ChatAssistant  # 导入你已有的ChatAssistant

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # 允许跨域请求

# 创建全局聊天助手实例
chat_assistant = ChatAssistant()

@app.route("/")
def index():
    """渲染主页"""
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    """处理聊天请求"""
    data = request.json
    user_input = data.get("message", "")
    
    if not user_input.strip():
        return jsonify({"error": "消息不能为空"}), 400
    
    # 检查是否是命令（以/开头）
    if user_input.startswith("/"):
        response = handle_command(user_input)
    else:
        # 获取AI回复
        try:
            response = chat_assistant.get_response(user_input)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return jsonify({
        "message": response,
        "mode": chat_assistant.mode
    })

def handle_command(command):
    """处理命令"""
    cmd_parts = command.split()
    cmd = cmd_parts[0]
    args = cmd_parts[1:] if len(cmd_parts) > 1 else []
    
    if cmd == "/clear":
        chat_assistant.clear_history()
        return "对话历史已清除"
    elif cmd == "/mode":
        return chat_assistant.switch_mode()
    elif cmd == "/status":
        mode = "原生对话" if chat_assistant.mode == "native" else "LangChain"
        msg_count = len(chat_assistant.messages) if chat_assistant.mode == "native" else \
                   len(chat_assistant.memory.chat_memory.messages) // 2
        return f"当前状态: 对话模式: {mode}, 模型: {chat_assistant.model_name}, 消息数: {msg_count}"
    else:
        return f"未知命令: {cmd}。可用命令: /clear, /mode, /status"

if __name__ == "__main__":
    app.run(debug=True, port=5000)