# 安装指南

## 环境要求

- Python 3.8+
- MySQL 8.0+
- MongoDB 4.4+
- Redis 5.0+

## 安装步骤

### 1. 创建并激活虚拟环境

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/Mac:
```bash
python -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

或使用setup.py:
```bash
pip install -e .
```

### 3. 配置环境变量

复制环境变量示例文件：
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

编辑 `.env` 文件，配置数据库连接信息：
- MySQL连接信息
- MongoDB连接信息
- Redis连接信息
- 安全密钥等

### 4. 初始化数据库

确保MySQL、MongoDB和Redis服务已启动。

创建MySQL数据库：
```sql
CREATE DATABASE youth_companion CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 运行测试

```bash
pytest
```

### 6. 启动应用

```bash
python src/main.py
```

或使用uvicorn:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. 访问应用

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 常见问题

### 1. 数据库连接失败

检查数据库服务是否启动，配置信息是否正确。

### 2. 依赖安装失败

尝试升级pip:
```bash
pip install --upgrade pip
```

### 3. 端口被占用

修改启动端口或关闭占用端口的进程。

## 开发模式

启用调试模式，在 `.env` 中设置：
```
DEBUG=True
LOG_LEVEL=DEBUG
```

## 生产部署

生产环境建议：
1. 设置 `DEBUG=False`
2. 使用强密码和密钥
3. 配置HTTPS
4. 使用进程管理器（如Supervisor、systemd）
5. 配置反向代理（如Nginx）
6. 启用日志轮转
7. 配置监控和告警
