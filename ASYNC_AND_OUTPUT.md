# 异步任务与结构化输出

## 异步任务

新增接口：

- `POST /analyze-jd/async`：提交 JD 分析任务。
- `POST /agent/run/async`：提交 Agent 任务。
- `GET /tasks/{task_id}`：查询任务状态和结果。

任务状态为 `pending`、`running`、`succeeded` 或 `failed`。任务和结果写入 SQLite，并按 `user_id` 隔离；管理员可以查看任务，但不会改变任务执行身份。

当前使用 FastAPI `BackgroundTasks`，适合本地学习、演示和单进程部署。进程异常退出时，正在执行的任务不会自动恢复。生产环境应将 `run_task` 替换为 Celery、RQ 或其他持久化队列，并增加重试、超时和幂等键。

## 结构化输出

## 简历与 JD 匹配

- `POST /match-resume-jd`：上传 `resume`（PDF、DOCX、TXT 或 MD）并提交 `job_description` 表单字段。
- `POST /match-resume-jd/async`：异步提交，使用 `GET /tasks/{task_id}` 查询。

结果包含 `match_score`、`matching_skills`、`missing_skills`、`strengths`、`gaps`、`recommendations` 和 `summary`。匹配文件只在处理期间保存，完成后删除；上传大小受 `MAX_UPLOAD_SIZE_BYTES` 限制。

`POST /analyze-jd` 和异步 JD 任务都要求模型返回以下 JSON 字段：

```json
{
  "core_skills": ["Python"],
  "bonus_skills": ["Docker"],
  "learning_plan": ["完成一个 RAG 项目"],
  "resume_keywords": ["FastAPI"],
  "summary": "岗位总结"
}
```

服务会去除 Markdown JSON 代码围栏，然后使用 Pydantic `JDAnalyzeResult` 验证字段、类型和必填项。同步接口验证失败返回 HTTP 502；异步任务验证失败会变为 `failed`，错误写入任务状态，不会伪装成成功结果。
