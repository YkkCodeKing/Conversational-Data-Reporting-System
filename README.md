# 基于Vue.js的对话式数据报表系统 (后端 API)

本项目是一个高性能、高并发、模块化设计的对话式数据报表系统后端服务。采用 Python 3.11+ 和 FastAPI 构建，全面遵循领域驱动设计 (DDD) 原理和 SOLID 面向对象设计准则，确保业务高内聚与低耦合。

## 🎯 系统架构与技术栈

### 技术栈选型 (严格依赖)
- **核心框架**: FastAPI 0.109.0, Uvicorn 0.27.0, Python 3.11+
- **数据库组件**: PostgreSQL 15 (通过 `asyncpg` 驱动), Redis 7, ChromaDB 0.4.22
- **ORM 与数据校验**: SQLAlchemy 2.0.25 (异步引擎支持), Alembic 1.13.1, Pydantic 2.5.3 (通过 `pydantic_settings` 管理环境)
- **AI 与大模型基座**: OpenAI 1.10.0 (无缝接入 DeepSeek 等 OAI 兼容接口模型，支持 SSE 流返回), LangChain 0.1.0
- **认证与周边库**: python-jose 3.3.0, passlib 1.7.4, httpx 0.26.0, pandas 2.2.0, loguru 0.7.2, celery 5.3.4

### 分层架构说明
为了实现 **高内聚与可拆分性**，后端强行划定了明确的五级依赖边界，上层只能依赖下层或平级接口：
1. **网关层 / 入口抽象** (`app/main.py`)
2. **路由聚合层** (`app/api/v1/router.py`)
3. **业务模块层 / 领域层** (`app/modules/`)：按业务拆分为 Auth, Chat, DataSource, Query, Chart, Insight, Report 七大模块，模块内部闭环管理 router, service, repository, models 和 schemas。
4. **共享基建层** (`app/shared/`)：提供大模型统一调用 (AI Client)、内存与 Redis 两级缓存 (Cache Manager)、数据库会话池 (DB Session) 等抽象能力。
5. **核心配置层** (`app/core/`)：掌控系统所有凭证、JWT 安全认证与中间件。

## 📁 目录结构

```text
backend/
├── app/
│   ├── core/                  # 核心配置与安全
│   │   ├── config.py          # pydantic_settings 环境配置管理
│   │   └── security.py        # JWT签发/验证、bcrypt密码哈希、get_current_user
│   ├── api/v1/                # 统一路由挂载
│   │   └── router.py          # 聚合全部7个领域模块路由
│   ├── models/                # 跨模块全局基础模型基类
│   │   └── base.py            # SQLAlchemy DeclarativeBase
│   ├── schemas/               # 跨模块通用 Pydantic 验证模型
│   ├── modules/               # 核心领域层 (Domain-Driven Design)
│   │   ├── auth/              # 用户认证领域 (注册/登录/JWT)
│   │   ├── chat/              # 对话交互领域 (多轮对话/SSE流式)
│   │   ├── datasource/        # 数据源管理领域 (多库接入/连接测试/Schema抓取)
│   │   ├── query/             # 数据查询领域 (NL2SQL/安全执行/历史记录)
│   │   ├── chart/             # 图表可视化领域 (LLM推荐图表/ECharts配置生成)
│   │   ├── insight/           # 智能洞察领域 (趋势分析/异常检测/关键发现)
│   │   └── report/            # 仪表盘报表领域 (组件编排/发布管理)
│   └── shared/                # 共享公共基础设施层 (Infrastructure)
│       ├── ai/                # LLM大模型统一调用防腐层 (DeepSeek/GPT)
│       ├── cache/             # L1内存+L2 Redis 两级缓存管理
│       ├── database/          # 异步引擎、Session管理、泛型Repository基类
│       ├── messaging/         # Celery 与消息队列抽象
│       └── utils/             # 无副作用通用纯函数辅助库
├── requirements.txt           # 项目包版本锁定
└── .env.example               # 配置模板
```

## 🧩 七大业务模块详解

### Auth — 用户认证与鉴权
提供用户注册（唯一性校验 + bcrypt 密码哈希）、JWT 令牌签发登录、Bearer Token 鉴权中间件，为其他模块的访问控制提供基础支撑。

### Chat — 对话交互服务
系统的核心交互入口。管理 `Conversation`（会话）与 `Message`（消息）的完整生命周期，支持多轮上下文对话。提供两种响应模式：**普通补全**（一次性返回完整结果）和 **SSE 流式补全**（逐块推送，适配前端打字机效果）。

### DataSource — 多数据源管理
管理外部数据库连接（PostgreSQL / MySQL / SQLite），支持连接可用性测试和目标库的 **Schema 元信息抓取**（表名 → 列名/类型），为 Query 模块的 NL2SQL 提供必要的结构上下文。

### Query — 自然语言数据查询 (NL2SQL)
系统的核心智能引擎。将用户的自然语言问题、目标数据库的 Schema 信息组装为 Prompt，调用 LLM 生成安全的 SELECT SQL，在目标数据源上执行并返回结构化结果。内置 SQL 安全校验（禁止写操作），全程结果持久化。

### Chart — 图表可视化配置
将 Query 返回的数据交给 LLM，由 AI 自动推荐最合适的图表类型（柱状图/折线图/饼图/散点图等），并生成前端可直接渲染的 **ECharts 兼容 JSON 配置**。内置 JSON 解析降级方案。

### Insight — 智能数据洞察
对查询结果调用 LLM 进行深度分析，输出结构化的洞察报告，包含：数据总体概述、关键发现列表（趋势/异常/分布特征）、可行的业务行动建议。

### Report — 仪表盘大屏聚合
将 Chart 图表、Insight 洞察、自由文本等组件项组装为完整的仪表盘报表，支持布局配置、组件排序、报表的发布与取消发布管理。

## 🔗 业务数据流

```
用户提问 → Chat(对话) → Query(NL2SQL) → 目标数据库执行
                                ↓
                        Chart(图表配置) ←→ Insight(智能洞察)
                                ↓
                        Report(仪表盘组装) → 前端渲染
```

## 📡 API 接口总览 (27 个端点)

| 模块 | 端点 | 说明 |
|------|------|------|
| **Auth** | `POST /auth/register` | 用户注册 |
| | `POST /auth/login` | 用户登录，返回 JWT |
| | `GET /auth/me` | 获取当前用户信息 |
| **Chat** | `POST /chat/completions` | 非流式对话补全 |
| | `POST /chat/completions/stream` | SSE 流式对话补全 |
| **DataSource** | `POST /datasource/` | 创建数据源 |
| | `GET /datasource/` | 数据源列表 |
| | `GET /datasource/{id}` | 数据源详情 |
| | `DELETE /datasource/{id}` | 删除数据源 |
| | `POST /datasource/{id}/test` | 测试连接 |
| **Query** | `POST /query/execute` | 自然语言查询执行 |
| | `GET /query/history` | 查询历史 |
| **Chart** | `POST /chart/generate` | 生成图表配置 |
| | `GET /chart/{id}` | 图表详情 |
| | `GET /chart/` | 图表列表 |
| **Insight** | `POST /insight/generate` | 生成数据洞察 |
| | `GET /insight/{id}` | 洞察详情 |
| | `GET /insight/` | 洞察列表 |
| **Report** | `POST /report/` | 创建报表 |
| | `GET /report/` | 报表列表 |
| | `GET /report/{id}` | 报表详情(含组件) |
| | `PUT /report/{id}` | 更新报表 |
| | `DELETE /report/{id}` | 删除报表 |
| | `POST /report/{id}/items` | 添加组件项 |
| | `POST /report/{id}/publish` | 发布报表 |
| | `POST /report/{id}/unpublish` | 取消发布 |
| **Health** | `GET /health` | 健康检查 |

## 🚀 核心特性

- **高度解耦的 AI 基建**: 基于抽象工厂模式的 `BaseLLMClient`，目前原生接入 **DeepSeek** (基于 OpenAI SDK) 并支持灵活扩展或切换其他模型，提供异步并行处理与 SSE 流式对话。
- **NL2SQL 智能查询引擎**: 自动抓取目标库 Schema → 组装上下文 → LLM 生成安全 SQL → 执行并持久化，全链路自动化。
- **两级全异步缓存系统**: L1 进程内存字典零网络开销极速访问，L2 Redis 持久态跨实例共享。
- **现代化异步与类型提示**: 基于 `asyncpg` + SQLAlchemy 2.0 异步引擎的全链路异步 IO，Pydantic 2 严格类型安全校验。
- **DDD 领域解耦**: 七大模块各自闭环管理 `Router → Service → Repository → Models`，满足单一职责与开闭原则。
- **JWT 无状态认证**: `security.py` 提供密码哈希 + Token 签发 + `get_current_user` 依赖注入，一行代码即可为任意路由增加鉴权。

## 🛠️ 安装与运行指南

### 1. 基础环境准备
1. 确保安装了 **Python 3.11** 及其以上版本。
2. 确保在本地或远端具有运行中的 **PostgreSQL 15** 以及 **Redis 7**。

### 2. 初始化项目依赖
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Mac/Linux 系统
# .\venv\Scripts\activate   # Windows 系统

# 安装严格约束版本号的核心包
pip install -r requirements.txt
```

### 3. 环境配置
将源码中自带的 `.env.example` 复制一份并重命名为 `.env`：
```bash
cp .env.example .env
```
随后编辑 `.env` 文件，填入可用的数据库凭证、Redis URL 以及 DeepSeek (或相关大模型) 的 API Key。

### 4. 启动后端服务器
项目利用 Uvicorn 搭载 FastAPI 提供异步事件循环 HTTP 服务：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 接口调试 (Swagger UI)
在浏览器访问接口自描述文档页：
[http://localhost:8000/docs](http://localhost:8000/docs)
您可以直接在此界面对不同领域的模块（如 `/api/v1/chat/completions`）进行免客户端的调用请求测试。
