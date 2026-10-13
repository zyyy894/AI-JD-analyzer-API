# 用户权限改造

参考项目：

- [FastAPI 官方全栈模板](https://github.com/fastapi/full-stack-fastapi-template)：参考 `backend/app/core/security.py` 的 PyJWT、pwdlib 密码哈希，以及 `backend/app/api/deps.py` 的当前用户、账号状态和管理员检查。
- [FastAPI Users](https://github.com/fastapi-users/fastapi-users)：参考注册、登录与当前用户依赖。README 声明进入维护模式。本项目没有安装该框架。
- [fastapi-permissions](https://github.com/holgi/fastapi-permissions)：参考资源所有者权限控制，适配为 SQLite `user_id` 与 Chroma metadata 过滤。

本项目独立适配，没有直接复制第三方源码，保留 SQLite、Chroma、LangGraph 和原有前端。FastAPI Users 使用 MIT，fastapi-permissions 使用 Beer-Ware 许可证。

## 启动

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
```

已有环境只需安装 `-r requirements-auth.txt`。网页提供邮箱注册、登录和退出。密码使用 Argon2 哈希，兼容旧 bcrypt，注册密码长度为 8–128 个字符。

`.env` 支持 `AUTH_SECRET_KEY` 和 `ACCESS_TOKEN_EXPIRE_MINUTES`（默认 120 分钟）。密钥需至少 32 字节。未配置时进程生成随机密钥，重启后旧登录失效；多进程部署必须配置同一随机密钥。实际 `.env` 不应提交 Git。

## 管理员

公开注册只创建普通用户，忽略客户端角色，不根据邮箱自动提权。先注册，再在本机执行：

```powershell
.venv\Scripts\python.exe -m app.manage_users your-email@example.com --role admin
```

恢复普通用户使用 `--role user`。每次请求读取数据库角色与启用状态，变更下一次请求生效。

- `GET /auth/users`：仅管理员查看账号清单，不返回密码哈希。
- `PATCH /auth/users/{user_id}/active?active=false`：停用其他账号；`active=true` 启用。禁止修改自己的启用状态。
- `GET /auth/me`：当前账号。
- `POST /auth/login`：OAuth2 表单 `username`（邮箱）、`password`，返回顶层 `access_token` 和 `token_type`，兼容 Swagger Authorize。

管理员的文档、问答与 Agent 检索也只使用自己的资料，账号管理权限不会自动开放其他人的简历。

## 数据与限制

SQLite 为旧表添加可空的 `user_id` 和索引，不删除原记录。无归属旧数据与缺少 `user_id` metadata 的历史向量不会通过普通接口读取。需要使用旧资料时，请登录后重新上传。

上传、入库、问答和 Agent 使用认证依赖的用户 ID，忽略请求体伪造的身份。上传目录没有静态公开。前端用 sessionStorage，退出或收到 401 清理会话和展示数据，并拒绝旧会话延迟返回的响应。

退出只清理浏览器会话，复制的 Bearer token 到过期前仍有效；停用账号阻止后续请求。尚无邮件验证、密码找回、登录限流、刷新令牌、单个 token 撤销。上传大小限制、后台任务、OCR 和生产部署也需后续完善。

## 测试

```powershell
.venv\Scripts\python.exe -m pytest test_db.py -q
```

测试使用临时数据库，覆盖登录、匿名拒绝、非法与过期令牌、跨用户隔离、角色变更、停用账号、向量过滤和 Agent 身份传递。替换模型调用，不发送外部 AI 请求、不打印真实简历记录。
