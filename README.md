# AI 岗位 JD 分析器

## 项目简介

AI 岗位 JD 分析器是一个基于 FastAPI 和大模型 API 的岗位分析工具。用户输入 AI 相关岗位描述后，系统会自动提取岗位核心技能、加分项、学习建议和简历关键词，帮助求职者快速理解岗位要求。

本项目是 AI 智能体开发学习路线中的第一个实践项目，主要目标是熟悉 FastAPI 接口开发、大模型 API 调用、Prompt 设计和结构化 JSON 输出。

## 技术栈

- Python
- FastAPI
- Uvicorn
- Pydantic
- DeepSeek API
- python-dotenv

## 核心功能

- 支持输入岗位 JD
- 自动分析岗位核心技能
- 提取岗位加分项
- 生成学习建议
- 生成简历关键词
- 返回统一 JSON 格式
- 支持 FastAPI 自动接口文档

## 项目结构

```text
ai-jd-analyzer/
  app/
    main.py
    schemas.py
    services/
      llm_service.py
      prompt_service.py
  .env.example
  requirements.txt
  README.md



快速开始
1. 安装依赖
pip install -r requirements.txt
2. 配置环境变量
在项目根目录创建 .env 文件：
DEEPSEEK_API_KEY=你的DeepSeek_API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
如果你使用的是其他 DeepSeek 模型，只需要修改 DEEPSEEK_MODEL。
3. 启动项目
uvicorn app.main:app --reload --port 8001
4. 打开接口文档
浏览器访问：
http://127.0.0.1:8001/docs
接口说明
健康检查
GET /health
响应示例：
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
JD 分析
POST /analyze-jd
请求示例：
{
  "jd": "AI智能体开发工程师，要求熟悉Python、FastAPI、RAG、Agent、LangGraph，有大模型应用开发经验。"
}
响应示例：
{
  "code": 200,
  "message": "success",
  "data": {
    "core_skills": ["Python", "FastAPI", "RAG", "Agent", "LangGraph"],
    "bonus_skills": ["项目经验", "Prompt Engineering", "开源贡献"],
    "learning_plan": ["学习大模型API调用", "掌握RAG知识库开发", "学习Agent工具调用"],
    "resume_keywords": ["大模型应用开发", "智能体开发", "向量检索", "工具调用"],
    "summary": "该岗位偏向AI应用工程化，需要掌握Python后端、大模型调用、RAG和Agent开发。"
  }
}
实现流程
用户输入岗位JD
     ↓
FastAPI 接收请求
     ↓
Pydantic 校验参数
     ↓
构造 Prompt
     ↓
调用 DeepSeek API
     ↓
解析模型返回结果
     ↓
返回统一 JSON 响应
项目亮点
使用 FastAPI 构建后端接口，自动生成 Swagger 文档
使用 Pydantic 完成请求参数校验
通过 Prompt 约束模型输出结构化 JSON
使用 .env 管理 API Key，避免敏感信息写入代码
采用 service 层拆分模型调用和 Prompt 构造逻辑
当前不足
模型返回内容偶尔可能不是标准 JSON
暂未接入数据库保存历史记录
暂未提供前端页面
暂未支持多个岗位 JD 批量分析
后续优化
增加前端页面
增加历史分析记录
支持上传 PDF/Word 简历
对比简历和岗位 JD 的匹配度
接入 RAG，支持基于岗位库进行分析
使用 LangGraph 扩展为求职规划 Agent
学习收获
通过本项目，我熟悉了 FastAPI 的基础接口开发流程，掌握了大模型 API 的基本调用方式，并实践了 Prompt 设计、结构化输出和统一响应格式，为后续开发 RAG 知识库和 AI Agent 项目打下基础。
## 第2周：RAG 向量检索 Demo

本阶段使用 Chroma 实现本地向量数据库检索。流程为：准备文本 → 存入 Chroma collection → 用户提问 → 检索 TopK 相关文本。

核心文件：

- `app/rag/splitter.py`：文本切分模块
- `app/rag/vector_store_demo.py`：Chroma 向量检索 Demo

本地运行：

```bash
python app/rag/vector_store_demo.py
## RAG 基础模块

本项目新增 RAG 基础检索模块，支持文本切分、向量数据库存储和相似度检索。

### 实现流程

文本输入 → 文本切分 → 存入 Chroma → 用户提问 → 检索相关片段

### 核心文件

- `app/rag/splitter.py`：文本切分
- `app/rag/vector_store.py`：向量数据库存储和检索
- `app/rag/rag_demo.py`：完整演示流程

### 运行方式

```bash
python -m app.rag.rag_demo