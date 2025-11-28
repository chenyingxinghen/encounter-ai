# 青春伴行平台 (Youth Companion Platform)

基于AI技术的大学生深度社交匹配系统

## 项目结构

```
.
├── src/                    # 源代码目录
│   ├── api/               # API接口层
│   ├── database/          # 数据库连接
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务
│   ├── utils/             # 工具函数
│   ├── config.py          # 配置管理
│   └── main.py            # 应用入口
├── tests/                 # 测试目录
├── logs/                  # 日志目录
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量示例
└── README.md             # 项目说明
```

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv venv
```

### 2. 激活虚拟环境

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

### 5. 运行应用

```bash
python src/main.py
```

或使用uvicorn:

```bash
uvicorn src.main:app --reload
```

应用将在 http://localhost:8000 启动

## 开发指南

### 运行测试

```bash
pytest
```

### 代码覆盖率

```bash
pytest --cov=src --cov-report=html
```

## 技术栈

- **Web框架**: FastAPI
- **数据库**: MySQL, MongoDB, Redis
- **AI模型**: BERT, ChatGLM
- **测试**: pytest, hypothesis

## 许可证

MIT License
