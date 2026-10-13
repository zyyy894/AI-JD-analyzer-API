# 部署到其他主机

## 1. 复制项目

复制 `app/`、`frontend/`、`scripts/`、`requirements.txt`、`.env.example`，以及需要保留的数据目录：

- `data/`：SQLite 数据库和问答历史
- `chroma_db/`：知识库向量数据
- `uploads/`：已上传的原始文件
- `logs/`：运行日志

不要复制 `.venv/`、`__pycache__/` 或 `.pytest_cache/`。虚拟环境必须在目标主机重新创建。

## 2. 创建环境

在目标主机安装 Python 3.10 或更高版本，然后在项目根目录执行：

```powershell
py -3.10 -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. 配置大模型

复制 `.env.example` 为 `.env`，填写真实配置：

```dotenv
DEEPSEEK_API_KEY=真实API密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=当前账号可用的模型名称
```

不要提交或公开 `.env`。

## 4. 启动

局域网使用：

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

也可以执行项目根目录的 `run_server.bat`。不要在正式运行时添加 `--reload`。

## 5. 访问和防火墙

在服务器上放行 TCP 8001：

```powershell
New-NetFirewallRule -DisplayName "AI JD Analyzer 8001" -Direction Inbound -Protocol TCP -LocalPort 8001 -Action Allow
```

其他主机访问：

```text
http://服务器局域网IP:8001/
```

验证接口：

```text
http://服务器局域网IP:8001/health
http://服务器局域网IP:8001/docs
```

应用现在会把运行数据和 `.env` 按项目根目录定位，不依赖启动命令的当前目录。
