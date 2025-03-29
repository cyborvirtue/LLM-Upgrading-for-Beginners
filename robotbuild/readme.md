### 文件目录
robotbuild/
├── app.py                  # Flask应用入口点
├── config.py               # 配置文件 (API密钥和设置)
├── models.py               # LLM模型实现
├── assistant.py            # 聊天助手核心功能
├── requirements.txt        # 项目依赖
│
├── static/                 # 静态文件目录
│   ├── css/
│   │   └── style.css       # 样式表
│   ├── js/
│   │   └── chat.js         # 前端JavaScript
│   └── img/                # 图片资源 (可选)
│       └── favicon.ico     # 网站图标
│
├── templates/              # 模板目录
│   └── index.html          # 主HTML模板
│
├── terminal_ui.py          # 终端交互界面 (可选)
└── main.py                 # 终端程序入口 (可选)

### 运行应用

python app.py