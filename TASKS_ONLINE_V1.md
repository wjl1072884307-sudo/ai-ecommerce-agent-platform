# ai-ecommerce-agent-platform V1.0 上线级优化任务文档

> **执行说明**：本文档用于指导后续 Codex 或工程师分阶段把当前项目从“面试演示级 Demo”优化为“可上线 MVP”。本轮只规划任务，不修改业务代码。后续实施时每个 Phase 必须可独立验收，禁止推倒重来，禁止破坏现有演示流程和已有 API。

## 1. 项目当前定位

`ai-ecommerce-agent-platform` 当前是一个电商客服与订单售后 Agent 平台的项目级 / 面试演示级项目，采用 FastAPI + SQLAlchemy + SQLite 后端、Vue3 + Vite + Naive UI 前端，围绕“用户消息进入客服会话后触发 Agent，Agent 查询订单、检索知识库、判断售后规则、生成回复建议、创建人工审核任务和售后工单，并记录节点日志”的完整链路展开。

当前项目已经具备清晰的业务闭环和可演示价值，但生产化能力不足。V1.0 的目标不是重构成大型 ToB 系统，而是在保留现有单体架构和 Mock 演示能力的前提下，补齐配置、数据库、认证权限、LLM 抽象、RAG 抽象、状态机、日志审计、前端登录适配、Docker 部署和文档体系，使其达到可上线 MVP 的工程质量。

## 2. 当前项目审查结论

### 2.1 已完成能力

- 后端 FastAPI 应用入口位于 `backend/app/main.py`，已按模块注册 products、orders、sessions、knowledge、agent、dashboard、review_tasks、tickets、health 路由。
- 数据库基础层位于 `backend/app/database.py`，已支持通过 `DATABASE_URL` 环境变量覆盖默认 SQLite 地址，并在 SQLite 场景下自动创建父目录。
- 数据模型位于 `backend/app/models/entities.py`，已覆盖用户、商品、订单、会话、消息、知识文档、知识 chunk、Agent Run、Agent Node Log、回复建议、审核任务、售后工单等核心实体。
- 演示数据初始化位于 `backend/scripts/init_db.py` 和 `backend/app/services/demo_seed.py`，支持 `--reset` 初始化本地 SQLite 并注入 Demo 数据。
- Agent Pipeline 位于 `backend/app/agent/pipeline.py`、`backend/app/agent/nodes.py`、`backend/app/agent/logger.py`、`backend/app/agent/types.py`，已形成 9 个节点：receive_message、classify_intent、query_order、retrieve_knowledge、check_policy、risk_check、generate_reply、create_review_task、create_ticket。
- Agent 节点日志已记录节点名称、输入、输出、状态、错误、开始结束时间和耗时，具备较好的可观测性雏形。
- 知识库模块已支持文档 CRUD、chunk 重建和关键词检索，接口位于 `backend/app/api/routes/knowledge.py`。
- 售后工单和审核任务已支持列表、详情、状态更新、审核通过/拒绝，接口位于 `backend/app/api/routes/tickets.py` 和 `backend/app/api/routes/review_tasks.py`。
- 前端已具备后台控制台结构，包含 Dashboard、商品、订单、会话、知识库、人工审核、售后工单、Agent 日志等页面，入口位于 `frontend/src/router/index.ts` 和 `frontend/src/layouts/AdminLayout.vue`。
- Axios 客户端位于 `frontend/src/api/client.ts`，已统一 baseURL 为 `/api` 并具备响应错误提示。
- 后端测试位于 `backend/tests/`，已覆盖健康检查、数据库、商品、订单、会话、知识库、Agent API、Agent 节点、业务逻辑、Dashboard、审核和工单等核心演示路径。
- 根目录已有 `README.md`、`PRD.md`、`TDD.md`、`TASKS.md`，以及 `docs/INTERVIEW_DEMO.md`。

### 2.2 距离可上线还缺少的能力

- 缺少统一配置模块，数据库、JWT、LLM、日志、CORS、环境标识等配置未集中管理。
- 缺少 `.env.example`，生产部署时无法明确必需环境变量。
- 数据库仍以 SQLite 和 `Base.metadata.create_all()` 为主，缺少 PostgreSQL 驱动、连接池配置、迁移方案和上线索引规划。
- 缺少登录、JWT、密码 hash、当前用户依赖和 RBAC 权限控制。
- `User` 模型没有 `password_hash` 字段，当前 `role` 更像演示属性而非真实权限体系。
- LLM 仍是硬编码规则和 Mock Pipeline，没有 Provider 抽象、超时、异常处理、失败兜底和真实 OpenAI-compatible 接入边界。
- RAG 检索逻辑直接写在路由和 Agent 节点中，没有 Retriever 抽象，暂不支持 embedding、向量库和引用来源结构化返回。
- Agent context 是 dataclass，缺少节点输入输出契约、失败降级策略和高风险动作约束。
- 工单状态更新没有状态机，任意字符串都可写入，没有状态流转校验、状态变更日志和并发领取/处理机制。
- 缺少系统日志、业务日志和审计日志，关键操作不可追踪。
- 前端没有登录页、token 注入、未登录跳转、角色菜单控制和按钮级权限控制。
- 缺少 Dockerfile、docker-compose、Nginx 反向代理和生产启动说明。
- README 和已有中文文档在当前 PowerShell 输出中出现乱码风险，需要统一 UTF-8 编码和文档可读性。

### 2.3 Demo 特征

- 默认 SQLite 本地数据库，生产可靠性、并发写入、备份恢复和连接管理不足。
- 通过 `scripts/init_db.py --reset` 直接 drop/create 表，适合演示，不适合线上迭代。
- Agent 的意图识别、政策判断、回复生成、关键词抽取均为硬编码规则。
- 客服、审核人等用户 ID 在前端存在硬编码，例如 `frontend/src/api/client.ts` 中审核接口默认 `reviewer_id = 3`。
- 无认证时所有接口可直接访问，不符合后台系统上线要求。
- 售后工单状态当前以 `open` 等简单值处理，与目标状态机不一致。
- 无真实 LLM Provider、无 token 统计、无成本控制。
- 无真实文档上传和向量检索流程。
- 缺少部署、监控、审计和安全边界。

### 2.4 可以保留的部分

- 保留当前 FastAPI 单体结构，不拆微服务。
- 保留当前 API 分组和 URL，新增认证时尽量兼容已有接口路径。
- 保留 SQLite 本地开发能力和现有 Demo seed 数据。
- 保留 Agent 9 节点主流程和节点日志表，后续在节点内部和边界抽象上增强。
- 保留当前关键词检索作为 V1.0 的 `KeywordRetriever`。
- 保留 Vue3 + Naive UI 后台结构，不一次性重写前端。
- 保留当前测试目录结构，在每个 Phase 增加或调整测试。

### 2.5 必须优先优化的部分

- 统一配置、环境变量和敏感信息管理。
- 可配置数据库和 PostgreSQL 支持。
- 认证、JWT、密码 hash 和基础 RBAC。
- LLM Provider 抽象和 Agent 失败兜底。
- Retriever 抽象，避免知识检索继续散落在路由和节点中。
- 工单状态机和状态变更日志。
- 关键业务审计日志。
- Docker Compose 一键启动。

### 2.6 暂时不要做的部分

- 不做微服务拆分。
- 不引入 Kubernetes。
- 不做多租户、多店铺、多渠道适配器。
- 不接真实淘宝、京东、抖音接口。
- 不直接上复杂工作流引擎。
- 不一开始引入完整 OpenTelemetry、Prometheus、Grafana 告警体系。
- 不把 RAG 一步升级到完整文档中台；V1.0 只做抽象和来源展示，embedding + pgvector 放到 V1.1。
- 不一次性大改前端交互和视觉，只做登录、权限、状态时间线、Agent 日志可读性增强。

## 3. V1.0 上线版目标

V1.0 上线版应达到以下标准：

- 本地开发仍可通过 SQLite + Demo 数据快速启动。
- 生产部署可通过 PostgreSQL + Docker Compose 一键启动。
- 所有敏感配置从环境变量读取，仓库不提交真实密钥。
- 后台接口默认需要登录，未登录返回 401，无权限返回 403。
- 具备 admin、reviewer、agent、viewer 四类基础角色。
- Agent 可继续使用 Mock，但已具备 OpenAI-compatible Provider 接入点。
- LLM 或单个节点失败时，Agent Run 能记录失败原因并返回可解释降级结果，不导致服务整体崩溃。
- RAG 检索通过 Retriever 抽象调用，关键词检索保留，后续可替换为向量检索。
- 工单状态流转受控，关键状态变更有日志。
- 关键操作有审计记录，线上问题可排查。
- 前端可登录、可携带 token、可根据角色控制菜单和按钮。
- README 和部署文档可指导新成员启动、演示和部署。

## 4. V1.0 不做事项

- 不做微服务、服务注册、服务网格。
- 不引入 Kubernetes。
- 不接真实电商平台开放接口。
- 不做多租户、租户级隔离、租户计费。
- 不做复杂客服排班、SLA 自动调度和企业 IM 集成。
- 不做真实支付、退款打款、赔偿执行、自动关闭工单等高风险动作。
- 不允许 AI 直接执行退款、赔偿、关闭工单、修改订单金额等动作。
- 不删除现有 Mock 数据和演示流程。
- 不破坏现有 API；如必须改变行为，使用兼容字段或新增接口。

## 5. 分阶段任务总览

| Phase | 名称 | 目标 | 独立验收结果 |
| --- | --- | --- | --- |
| Phase 1 | 生产环境配置 | 统一配置和环境变量 | 本地和生产配置可区分，敏感项不硬编码 |
| Phase 2 | 数据库升级 | 支持 PostgreSQL，保留 SQLite | 测试可用 SQLite，部署可用 PostgreSQL |
| Phase 3 | 认证与权限 | 登录、JWT、RBAC | 401/403 行为正确，不同角色访问受控 |
| Phase 4 | LLM Provider 抽象 | Mock 与 OpenAI-compatible 可插拔 | LLM 异常不会打崩 Agent |
| Phase 5 | RAG 检索优化 | Retriever 抽象和来源展示 | KeywordRetriever 可用，预留 VectorRetriever |
| Phase 6 | Agent Pipeline 优化 | 明确节点契约和高风险边界 | 节点日志更完整，高风险必须审核 |
| Phase 7 | 工单状态机 | 规范状态流转和并发处理 | 非法流转被拒绝，状态变更留痕 |
| Phase 8 | 日志与审计 | 系统、业务、Agent、审计日志 | 关键操作可追踪 |
| Phase 9 | 前端适配 | 登录、token、权限和展示增强 | 前端权限体验完整 |
| Phase 10 | Docker 部署 | 一键启动生产化 MVP | postgres/backend/frontend compose 可运行 |
| Phase 11 | 文档升级 | 完整上线和设计文档 | README 和专项文档可指导交付 |

---

## Phase 1：生产环境配置

### 目标

增加统一配置模块，让数据库地址、JWT 密钥、LLM 配置、日志等级、运行环境等均从环境变量读取，并明确开发环境和生产环境差异。

### 任务 1.1：新增统一配置模块

**涉及文件**

- 新增：`backend/app/core/config.py`
- 新增：`backend/app/core/__init__.py`
- 修改：`backend/app/database.py`
- 修改：`backend/app/main.py`
- 修改：`backend/requirements.txt`
- 新增测试：`backend/tests/test_config.py`

**实现说明**

- 引入 `pydantic-settings`。
- 定义 `Settings`，至少包含：
  - `APP_ENV`
  - `APP_NAME`
  - `DEBUG`
  - `DATABASE_URL`
  - `JWT_SECRET_KEY`
  - `JWT_ALGORITHM`
  - `JWT_EXPIRE_MINUTES`
  - `LLM_PROVIDER`
  - `LLM_BASE_URL`
  - `LLM_API_KEY`
  - `LLM_MODEL`
  - `LLM_TIMEOUT_SECONDS`
  - `LOG_LEVEL`
  - `BACKEND_CORS_ORIGINS`
- 提供 `get_settings()`，使用 `@lru_cache` 避免重复解析。
- `backend/app/database.py` 不再直接 `os.getenv("DATABASE_URL")`，改为读取 `settings.database_url`。
- `backend/app/main.py` 中 FastAPI title/version/debug/CORS 后续均从 settings 读取。

**验收标准**

- `python -m pytest backend/tests/test_config.py -v` 通过。
- 不设置环境变量时仍默认使用本地 SQLite。
- 设置 `DATABASE_URL` 后数据库连接使用新地址。
- 仓库中没有真实 JWT 密钥或真实 LLM API Key。

### 任务 1.2：新增环境变量示例文件

**涉及文件**

- 新增：`.env.example`
- 新增：`backend/.env.example`
- 修改：`.gitignore`

**实现说明**

- `.env.example` 写明本地开发推荐配置。
- `backend/.env.example` 写明后端必需配置。
- `.gitignore` 确认忽略 `.env`、`backend/.env`、`*.db`、`backend/data/`。

**验收标准**

- 新成员可复制 `.env.example` 为 `.env` 并启动本地项目。
- 示例文件只包含占位值，不包含真实密钥。

### 风险点

- 配置命名如果过度复杂，会增加后续实现成本。
- `pydantic-settings` 版本需要与 Pydantic v2 兼容。

### 阶段完成后的能力提升

项目从硬编码和零散配置进入可部署配置模式，为数据库、认证、LLM、Docker 和生产环境奠定基础。

---

## Phase 2：数据库升级

### 目标

将 SQLite 改造成可配置数据库，生产支持 PostgreSQL，本地保留 SQLite；补齐高频查询索引和 Alembic 迁移规划。

### 任务 2.1：支持 PostgreSQL 驱动和连接配置

**涉及文件**

- 修改：`backend/requirements.txt`
- 修改：`backend/app/database.py`
- 修改：`backend/README.md`
- 新增测试：`backend/tests/test_database_url.py`

**实现说明**

- 增加 `psycopg[binary]` 或 `asyncpg`。当前 SQLAlchemy 代码是同步 Session，优先使用 `psycopg[binary]`，避免大范围改异步。
- `create_engine()` 根据数据库类型配置：
  - SQLite 保留 `check_same_thread=False`。
  - PostgreSQL 配置 `pool_pre_ping=True`、`pool_size`、`max_overflow`。
- 生产环境如果仍使用 SQLite，在启动时记录 warning。

**验收标准**

- SQLite 本地测试继续通过。
- 使用 PostgreSQL URL 时 engine 可创建，连接参数正确。
- 文档说明 PostgreSQL URL 示例。

### 任务 2.2：补齐索引规划

**涉及文件**

- 修改：`backend/app/models/entities.py`
- 新增或修改测试：`backend/tests/test_database.py`
- 文档记录：`DATABASE_DESIGN.md`（Phase 11 创建时补充）

**实现说明**

- 保留已有 `index=True` 字段。
- 明确高频查询字段：
  - `orders.user_id`
  - `orders.order_no`
  - `orders.order_status`
  - `orders.after_sale_status`
  - `messages.session_id`
  - `knowledge_chunks.document_id`
  - `agent_runs.session_id`
  - `agent_runs.message_id`
  - `agent_runs.status`
  - `agent_node_logs.run_id`
  - `review_tasks.status`
  - `review_tasks.risk_level`
  - `tickets.status`
  - `tickets.assignee_id`
  - `tickets.created_at`
- 复合索引后续可规划：
  - `(ticket.status, ticket.assignee_id)`
  - `(agent_node_logs.run_id, agent_node_logs.node_name)`
  - `(messages.session_id, messages.created_at)`

**验收标准**

- 数据库模型可正常 create_all。
- 高频查询字段有明确索引策略。
- 不为了索引做大规模模型重构。

### 任务 2.3：规划 Alembic 迁移

**涉及文件**

- 新增：`backend/alembic.ini`
- 新增：`backend/alembic/env.py`
- 新增目录：`backend/alembic/versions/`
- 修改：`backend/scripts/init_db.py`
- 新增文档：`DATABASE_DESIGN.md`（Phase 11）

**实现说明**

- V1.0 可以先引入 Alembic 基础结构，不要求历史迁移完整追溯。
- `scripts/init_db.py` 继续保留给本地 Demo 使用。
- 生产部署文档要求使用 Alembic，而不是 `create_all()`。
- 说明生产不建议只用 SQLite 的原因：
  - 并发写能力弱；
  - 缺少生产级连接池和权限管理；
  - 备份、恢复、监控和扩展能力有限；
  - 不适合多实例部署；
  - schema 迁移和锁表风险更难控制。

**验收标准**

- 本地 Demo 初始化命令仍可用。
- 生产文档明确数据库迁移命令。
- 不删除现有 SQLite 快速启动能力。

### 风险点

- 一次性引入 Alembic 并迁移已有数据可能影响演示数据库，V1.0 应优先支持新环境部署。
- PostgreSQL 与 SQLite 的日期、布尔值、大小写匹配行为可能不同，检索测试需要覆盖。

### 阶段完成后的能力提升

项目可从本地单文件数据库升级为生产可用 PostgreSQL，同时保持 Demo 快速运行能力。

---

## Phase 3：认证与权限

### 目标

新增登录接口、JWT、密码 hash 和基础 RBAC，角色至少包含 admin、reviewer、agent、viewer。

### 任务 3.1：扩展用户模型与认证依赖

**涉及文件**

- 修改：`backend/app/models/entities.py`
- 新增：`backend/app/core/security.py`
- 新增：`backend/app/api/deps.py`
- 新增：`backend/app/schemas/auth.py`
- 修改：`backend/app/schemas/__init__.py`
- 修改：`backend/requirements.txt`
- 新增测试：`backend/tests/test_auth.py`

**实现说明**

- `User` 增加 `password_hash` 字段。
- 使用 `passlib[bcrypt]` 或 `pwdlib` 进行密码 hash。
- 使用 `python-jose` 或 `PyJWT` 生成和校验 JWT。
- `get_current_user()` 从 Authorization Bearer token 解析用户。
- 未登录抛出 401。
- 用户不存在、禁用或 token 过期均返回 401。

**验收标准**

- 密码不会明文入库。
- 错误密码登录失败。
- token 过期或无效返回 401。

### 任务 3.2：新增登录和当前用户接口

**涉及文件**

- 新增：`backend/app/api/routes/auth.py`
- 修改：`backend/app/main.py`
- 修改：`backend/app/services/demo_seed.py`
- 新增测试：`backend/tests/test_auth_api.py`

**实现说明**

- 新增：
  - `POST /api/auth/login`
  - `GET /api/auth/me`
- Demo seed 增加默认账号：
  - `admin_demo / admin123456`
  - `reviewer_demo / reviewer123456`
  - `agent_demo / agent123456`
  - `viewer_demo / viewer123456`
- 保留 customer demo 用于业务数据，但后台登录角色以 admin/reviewer/agent/viewer 为主。

**验收标准**

- 默认账号可登录。
- `/api/auth/me` 返回当前用户 id、username、display_name、role、status。
- README 后续记录默认账号。

### 任务 3.3：增加 RBAC 权限控制

**涉及文件**

- 修改：`backend/app/api/deps.py`
- 修改：`backend/app/api/routes/products.py`
- 修改：`backend/app/api/routes/orders.py`
- 修改：`backend/app/api/routes/sessions.py`
- 修改：`backend/app/api/routes/knowledge.py`
- 修改：`backend/app/api/routes/agent.py`
- 修改：`backend/app/api/routes/review_tasks.py`
- 修改：`backend/app/api/routes/tickets.py`
- 修改：`backend/app/api/routes/dashboard.py`
- 新增测试：`backend/tests/test_rbac.py`

**实现说明**

- 定义权限矩阵：
  - `admin`：全部接口。
  - `reviewer`：审核任务、工单处理、Agent 日志、Dashboard 只读、会话只读。
  - `agent`：会话处理、触发 Agent、查看订单/商品/知识库、创建或处理分配给自己的工单。
  - `viewer`：Dashboard、商品、订单、会话、知识库、Agent 日志只读。
- 写操作统一要求 admin/reviewer/agent 中合适角色。
- 知识库修改仅 admin。
- 未登录返回 401，无权限返回 403。
- 为避免破坏健康检查，`GET /api/health` 保持公开。

**验收标准**

- 所有受保护接口无 token 返回 401。
- viewer 调用写接口返回 403。
- admin 可访问全部接口。
- 现有测试可通过补充测试 fixture 登录后继续验证。

### 风险点

- 直接保护所有接口会导致现有测试大量失败，需要先新增测试登录 helper，再逐步调整。
- 前端硬编码用户 ID 需要在 Phase 9 改为使用当前登录用户。

### 阶段完成后的能力提升

后台系统具备上线最基本的访问控制能力，避免所有接口裸奔。

---

## Phase 4：LLM Provider 抽象

### 目标

保留当前 Mock LLM 能力，新增 LLM Provider 抽象层，支持 MockProvider 和 OpenAI Compatible Provider，并处理超时、异常、失败兜底。

### 任务 4.1：定义 LLM Provider 接口

**涉及文件**

- 新增：`backend/app/llm/__init__.py`
- 新增：`backend/app/llm/types.py`
- 新增：`backend/app/llm/base.py`
- 新增：`backend/app/llm/mock_provider.py`
- 新增：`backend/app/llm/factory.py`
- 修改：`backend/app/core/config.py`
- 新增测试：`backend/tests/test_llm_provider.py`

**实现说明**

- 定义 `LLMMessage`、`LLMRequest`、`LLMResponse`、`LLMProvider`。
- `MockProvider` 返回稳定 mock 内容，便于测试和演示。
- `get_llm_provider(settings)` 根据 `LLM_PROVIDER` 返回 provider。
- 先不要求 Agent 全部改为 LLM，至少让 `generate_reply` 可通过 provider 生成或兜底。

**验收标准**

- `LLM_PROVIDER=mock` 时不需要网络和 API Key。
- MockProvider 返回稳定结果。
- Provider 工厂遇到未知 provider 返回清晰配置错误。

### 任务 4.2：新增 OpenAI Compatible Provider

**涉及文件**

- 新增：`backend/app/llm/openai_compatible_provider.py`
- 修改：`backend/requirements.txt`
- 修改：`backend/app/core/config.py`
- 新增测试：`backend/tests/test_openai_compatible_provider.py`

**实现说明**

- 支持 OpenAI-compatible chat completions 接口：
  - `base_url`
  - `api_key`
  - `model`
  - `timeout`
- 可使用 `httpx` 直接调用，避免引入过重 SDK。
- 兼容 DeepSeek、Qwen、OpenAI 兼容接口。
- 网络异常、超时、非 2xx、响应格式异常都转换为统一 `LLMProviderError`。

**验收标准**

- 使用 mock httpx transport 可测试成功响应。
- 超时和 500 响应不会抛出未处理异常。

### 任务 4.3：Agent 回复生成接入 Provider 兜底

**涉及文件**

- 修改：`backend/app/agent/nodes.py`
- 修改：`backend/app/agent/types.py`
- 新增测试：`backend/tests/test_agent_llm_fallback.py`

**实现说明**

- `generate_reply` 节点优先调用 LLM Provider。
- LLM 失败时使用当前规则模板生成兜底回复，并在节点输出中记录：
  - `llm_used`
  - `llm_provider`
  - `fallback_used`
  - `fallback_reason`
- LLM 失败不应导致整个 Agent 流程崩溃，除非数据库写入失败等系统错误。

**验收标准**

- MockProvider 正常时 Agent Run 成功。
- Provider 抛异常时 Agent Run 仍成功或至少返回可解释结果，节点日志记录 fallback。
- 高风险场景仍创建审核任务。

### 风险点

- 真实 LLM 接入可能引入网络不稳定和响应不可控，V1.0 测试必须默认使用 Mock。
- 不应让 LLM 决定高风险动作，只能生成建议。

### 阶段完成后的能力提升

项目从“硬编码回复 Demo”升级为“可插拔 LLM MVP”，同时保持无外部依赖的演示能力。

---

## Phase 5：RAG 检索优化

### 目标

保留当前关键词检索，将检索逻辑抽象成 Retriever，当前实现 KeywordRetriever，后续预留 VectorRetriever，并在回复中展示知识来源。

### 任务 5.1：新增 Retriever 抽象

**涉及文件**

- 新增：`backend/app/rag/types.py`
- 新增：`backend/app/rag/base.py`
- 新增：`backend/app/rag/keyword_retriever.py`
- 新增：`backend/app/rag/factory.py`
- 修改：`backend/app/core/config.py`
- 新增测试：`backend/tests/test_rag_retriever.py`

**实现说明**

- 定义 `RetrievalQuery`、`RetrievedChunk`、`Retriever`。
- `KeywordRetriever` 复用现有 `KnowledgeChunk` + `KnowledgeDocument` 查询逻辑。
- 返回结果包含：
  - `chunk_id`
  - `document_id`
  - `document_title`
  - `document_type`
  - `content`
  - `score`
  - `metadata`
- `score` 在关键词阶段可使用简单命中次数或固定值。

**验收标准**

- 关键词检索结果与现有 `/api/knowledge/search` 基本一致。
- 检索逻辑不再重复散落在 Agent 节点和路由中。

### 任务 5.2：路由和 Agent 节点接入 Retriever

**涉及文件**

- 修改：`backend/app/api/routes/knowledge.py`
- 修改：`backend/app/agent/nodes.py`
- 修改：`backend/app/schemas/knowledge.py`
- 修改：`backend/app/schemas/agent.py`
- 新增或修改测试：`backend/tests/test_knowledge_api.py`、`backend/tests/test_agent_nodes.py`

**实现说明**

- `/api/knowledge/search` 调用 `KeywordRetriever`。
- `retrieve_knowledge` 节点调用 Retriever。
- `ReplySuggestion.source_summary` 继续保留，同时节点输出增加结构化 sources。
- 前端后续可展示 `document_title` 和 `chunk_id`。

**验收标准**

- 搜索接口返回知识来源。
- Agent 日志中能看到检索 query、命中 chunk 和来源文档。

### 任务 5.3：预留 VectorRetriever 升级说明

**涉及文件**

- 新增：`backend/app/rag/vector_retriever.py`
- 新增文档：`RAG_UPGRADE_PLAN.md`（Phase 11）

**实现说明**

- `VectorRetriever` 可先抛出明确的 `NotImplementedError` 或返回配置错误，不能静默失败。
- 文档说明 V1.1 如何升级：
  - 文档上传；
  - chunk 切分；
  - embedding 生成；
  - pgvector 存储；
  - hybrid search；
  - 引用来源展示。

**验收标准**

- 配置为 vector 但未实现时返回清晰错误。
- 不影响 keyword 默认检索。

### 风险点

- 不要在 V1.0 直接引入完整向量化链路，避免超出 MVP 范围。
- 检索来源字段需要兼容前端现有类型。

### 阶段完成后的能力提升

项目具备 RAG 可扩展边界，后续从关键词升级到向量检索时不会重写 Agent。

---

## Phase 6：Agent Pipeline 优化

### 目标

梳理每个 Agent 节点输入输出，明确 context 传递方式，增强节点日志，确保高风险场景必须转人工审核，禁止 AI 直接执行高风险动作。

### 任务 6.1：定义节点契约和 context 快照

**涉及文件**

- 修改：`backend/app/agent/types.py`
- 修改：`backend/app/agent/pipeline.py`
- 修改：`backend/app/agent/logger.py`
- 新增文档：`AGENT_WORKFLOW.md`（Phase 11）
- 新增测试：`backend/tests/test_agent_context_contract.py`

**实现说明**

- 为 `AgentContext` 增加结构化字段：
  - `sources`
  - `llm_result`
  - `fallback_reason`
  - `risk_actions`
- 为 `NodeResult` 明确允许状态：`success`、`skipped`、`failed`。
- `_context_snapshot()` 补齐关键上下文字段，但避免记录敏感信息和超长内容。
- 约定每个节点输入输出在 `AGENT_WORKFLOW.md` 中记录。

**验收标准**

- 每个节点日志都有输入、输出、状态、错误、耗时。
- 日志不会包含 JWT、API Key、密码 hash。

### 任务 6.2：高风险动作控制

**涉及文件**

- 修改：`backend/app/agent/nodes.py`
- 新增：`backend/app/agent/policies.py`
- 新增测试：`backend/tests/test_agent_risk_policy.py`

**实现说明**

- 定义高风险动作：
  - refund
  - compensation
  - close_ticket
  - modify_order_amount
  - approve_after_sale
- Agent 只能生成建议、创建审核任务、创建工单。
- 对退款、赔偿、关闭工单等动作，节点输出必须标记 `requires_human_review=True`。
- `risk_check` 必须覆盖投诉、高金额订单、超售后期、退款/退货请求。

**验收标准**

- 高风险场景一定创建 `ReviewTask`。
- Agent 不会直接修改订单退款状态或关闭工单。
- 测试覆盖至少退款、投诉、高金额订单三类风险。

### 任务 6.3：Agent 失败结果标准化

**涉及文件**

- 修改：`backend/app/agent/pipeline.py`
- 修改：`backend/app/api/routes/agent.py`
- 修改：`backend/app/schemas/agent.py`
- 新增测试：`backend/tests/test_agent_failure_response.py`

**实现说明**

- Agent Run 失败时返回统一结构：
  - `run.status = failed`
  - `run.error_message`
  - `failed_node`
  - `partial_context`
- API 不应返回 500，除非系统级不可恢复错误。
- 节点失败仍应写入 AgentNodeLog。

**验收标准**

- 输入不存在 message 时返回可解释失败结果。
- 节点异常被 logger 捕获并记录。

### 风险点

- 如果把所有失败都吞掉，会掩盖系统错误；需要区分业务失败和系统异常。
- context 日志要控制大小，避免大文本导致数据库膨胀。

### 阶段完成后的能力提升

Agent 从“演示脚本链路”升级为“可观测、可降级、可审计的业务流程”。

---

## Phase 7：工单状态机

### 目标

规范工单状态，状态至少包括 pending、processing、waiting_customer、resolved、closed、cancelled；明确允许流转，禁止非法流转，每次变更记录日志，并防止两个客服同时处理同一个工单。

### 任务 7.1：定义状态机

**涉及文件**

- 新增：`backend/app/tickets/state_machine.py`
- 新增：`backend/app/tickets/__init__.py`
- 修改：`backend/app/models/entities.py`
- 修改：`backend/app/schemas/ticket.py`
- 修改：`backend/app/api/routes/tickets.py`
- 新增测试：`backend/tests/test_ticket_state_machine.py`

**实现说明**

- 状态集合：
  - `pending`
  - `processing`
  - `waiting_customer`
  - `resolved`
  - `closed`
  - `cancelled`
- 允许流转：
  - `pending -> processing`
  - `pending -> cancelled`
  - `processing -> waiting_customer`
  - `processing -> resolved`
  - `processing -> cancelled`
  - `waiting_customer -> processing`
  - `waiting_customer -> resolved`
  - `resolved -> closed`
  - `resolved -> processing`
- 禁止 `closed` 和 `cancelled` 再流转，除非 admin 使用后续专门 reopen 接口，V1.0 暂不做 reopen。
- 兼容旧数据：`open` 可在迁移或读取时转换为 `pending`。

**验收标准**

- 非法状态流转返回 400。
- 合法状态流转成功。
- 新创建工单默认 `pending`。

### 任务 7.2：记录状态变更日志

**涉及文件**

- 修改：`backend/app/models/entities.py`
- 新增：`TicketStatusLog` 模型
- 新增：`backend/app/schemas/ticket_log.py`
- 修改：`backend/app/schemas/__init__.py`
- 修改：`backend/app/api/routes/tickets.py`
- 新增测试：`backend/tests/test_ticket_status_logs.py`

**实现说明**

- `TicketStatusLog` 字段：
  - `id`
  - `ticket_id`
  - `from_status`
  - `to_status`
  - `operator_id`
  - `reason`
  - `created_at`
- 状态变更接口要求传入 reason 或 review_comment。
- 新增 `GET /api/tickets/{ticket_id}/status-logs`。

**验收标准**

- 每次状态变更都生成一条日志。
- 工单详情可查询状态时间线。

### 任务 7.3：防止并发处理

**涉及文件**

- 修改：`backend/app/models/entities.py`
- 修改：`backend/app/api/routes/tickets.py`
- 新增测试：`backend/tests/test_ticket_assignment.py`

**实现说明**

- 增加领取接口：
  - `POST /api/tickets/{ticket_id}/claim`
- 未分配工单可被当前 agent/reviewer 领取，设置 `assignee_id` 并从 `pending` 转为 `processing`。
- 已分配给其他人的工单，非 admin 不允许领取或处理，返回 409 或 403。
- PostgreSQL 后续可使用行级锁；V1.0 同步 SQLAlchemy 可先用事务和条件更新规划。

**验收标准**

- 两个客服同时领取同一工单时只有一个成功。
- 非 assignee 更新工单状态返回 403。

### 风险点

- SQLite 对并发锁支持有限，生产并发验证以 PostgreSQL 为准。
- 旧状态 `open` 与新状态需兼容迁移。

### 阶段完成后的能力提升

售后工单从简单字段更新升级为可控业务状态流，减少线上误操作和并发冲突。

---

## Phase 8：日志与审计

### 目标

增加系统日志、业务日志、Agent 执行日志和审计日志，覆盖登录、审核、工单状态变更、知识库修改、Agent 触发等关键操作。

### 任务 8.1：系统日志配置

**涉及文件**

- 新增：`backend/app/core/logging.py`
- 修改：`backend/app/main.py`
- 修改：`backend/app/core/config.py`
- 新增测试：`backend/tests/test_logging_config.py`

**实现说明**

- 根据 `LOG_LEVEL` 配置 Python logging。
- 日志格式至少包含时间、等级、模块、message。
- 生产环境建议 JSON 日志，V1.0 可以先支持普通格式并预留 JSON formatter。

**验收标准**

- 启动时日志等级来自环境变量。
- health check 不产生异常日志。

### 任务 8.2：新增审计日志模型与服务

**涉及文件**

- 修改：`backend/app/models/entities.py`
- 新增：`backend/app/audit/__init__.py`
- 新增：`backend/app/audit/service.py`
- 新增：`backend/app/schemas/audit.py`
- 新增：`backend/app/api/routes/audit.py`
- 修改：`backend/app/main.py`
- 新增测试：`backend/tests/test_audit_log.py`

**实现说明**

- `AuditLog` 字段：
  - `id`
  - `operator_id`
  - `operator_role`
  - `action`
  - `resource_type`
  - `resource_id`
  - `request_id`
  - `ip_address`
  - `user_agent`
  - `before_json`
  - `after_json`
  - `created_at`
- 提供 `record_audit_log()` 服务函数。
- 新增 admin 可查询审计日志接口。

**验收标准**

- 登录成功/失败、审核通过/拒绝、工单状态变更、知识库创建/修改、Agent 触发均可记录审计。
- viewer 不能查看审计日志。

### 任务 8.3：关键业务操作接入审计

**涉及文件**

- 修改：`backend/app/api/routes/auth.py`
- 修改：`backend/app/api/routes/review_tasks.py`
- 修改：`backend/app/api/routes/tickets.py`
- 修改：`backend/app/api/routes/knowledge.py`
- 修改：`backend/app/api/routes/agent.py`
- 新增测试：`backend/tests/test_business_audit_integration.py`

**实现说明**

- 对关键操作记录：
  - `auth.login.success`
  - `auth.login.failed`
  - `review.approve`
  - `review.reject`
  - `ticket.status_changed`
  - `ticket.claimed`
  - `knowledge.created`
  - `knowledge.updated`
  - `agent.run_triggered`
- 审计失败不应影响主流程，但必须记录系统 warning。

**验收标准**

- 每类关键操作至少有一条测试验证审计记录。
- 审计日志不记录明文密码和 token。

### 风险点

- 过度记录 input/output 会产生敏感信息风险，需要明确脱敏策略。
- 审计日志表增长较快，V2.0 再规划归档和检索优化。

### 阶段完成后的能力提升

线上关键操作可追踪，具备基本排查、问责和合规雏形。

---

## Phase 9：前端适配

### 目标

增加登录页，Axios 自动携带 token，未登录跳转登录页，根据角色控制菜单和按钮，增强工单详情状态时间线和 Agent 日志展示。

### 任务 9.1：新增登录和认证状态

**涉及文件**

- 新增：`frontend/src/views/LoginView.vue`
- 新增：`frontend/src/stores/auth.ts` 或 `frontend/src/auth/session.ts`
- 修改：`frontend/src/api/client.ts`
- 修改：`frontend/src/router/index.ts`
- 修改：`frontend/src/App.vue`

**实现说明**

- 不强制引入 Pinia；当前项目未使用状态管理，V1.0 可用轻量 `auth/session.ts` 管理 token 和 currentUser。
- `apiClient` 请求拦截器自动添加 `Authorization: Bearer <token>`。
- 响应 401 自动清理 token 并跳转 `/login`。
- 登录成功后跳转 Dashboard。

**验收标准**

- 未登录访问 `/dashboard` 自动跳转 `/login`。
- 登录后刷新页面仍可从 localStorage 恢复 token 并请求 `/api/auth/me`。
- 退出登录后不能访问后台页面。

### 任务 9.2：角色菜单和按钮权限

**涉及文件**

- 修改：`frontend/src/layouts/AdminLayout.vue`
- 修改：`frontend/src/router/index.ts`
- 修改：`frontend/src/views/KnowledgeView.vue`
- 修改：`frontend/src/views/ReviewTasksView.vue`
- 修改：`frontend/src/views/TicketsView.vue`
- 修改：`frontend/src/views/SessionsView.vue`

**实现说明**

- 路由 meta 增加 `roles`。
- 菜单根据当前用户 role 过滤。
- 按钮级控制：
  - viewer 隐藏写操作；
  - reviewer 可审核、处理工单；
  - agent 可触发 Agent、处理自己的工单；
  - admin 可全部操作。
- 权限控制只是前端体验，后端 RBAC 才是安全边界。

**验收标准**

- viewer 看不到新增/编辑/审核/状态变更按钮。
- reviewer 可以看到审核入口。
- admin 可以看到全部菜单和按钮。

### 任务 9.3：工单状态时间线

**涉及文件**

- 修改：`frontend/src/api/client.ts`
- 修改：`frontend/src/views/TicketsView.vue`
- 可选新增：`frontend/src/views/components/TicketStatusTimeline.vue`

**实现说明**

- 接入 `GET /api/tickets/{ticket_id}/status-logs`。
- 工单详情或展开区域展示状态时间线。
- 状态更新使用新状态集合。

**验收标准**

- 工单状态变更后前端能看到时间线。
- 非法状态操作前端不展示，后端仍负责拦截。

### 任务 9.4：Agent 日志展示增强

**涉及文件**

- 修改：`frontend/src/views/AgentLogsView.vue`
- 修改：`frontend/src/api/client.ts`

**实现说明**

- 按节点顺序展示节点名称、状态、耗时、错误、输入输出。
- JSON 输入输出提供折叠展示。
- 对 fallback、sources、高风险审核标记做明显展示。

**验收标准**

- 一次 Agent Run 的节点链路可快速看懂。
- 节点失败时前端能看到失败节点和错误原因。

### 风险点

- 当前前端中文文本在终端输出存在乱码风险，修改时统一 UTF-8。
- 不要一次性重做视觉，只做上线必需功能。

### 阶段完成后的能力提升

前端从无鉴权演示后台升级为具备基础登录、权限和可观测展示的 MVP 控制台。

---

## Phase 10：Docker 部署

### 目标

新增 Docker 化部署，服务至少包含 postgres、backend、frontend，前端使用 Nginx 托管，`/api` 反向代理后端，一条命令启动项目，提供 `/api/health` 健康检查。

### 任务 10.1：后端 Dockerfile

**涉及文件**

- 新增：`backend/Dockerfile`
- 新增：`backend/.dockerignore`
- 修改：`backend/README.md`

**实现说明**

- 使用 Python slim 镜像。
- 安装 `requirements.txt`。
- 运行 `uvicorn app.main:app --host 0.0.0.0 --port 8000`。
- 通过环境变量注入配置。

**验收标准**

- `docker build -t ai-ecommerce-agent-backend ./backend` 成功。
- 容器启动后 `/api/health` 返回 `{"status":"ok"}`。

### 任务 10.2：前端 Dockerfile 和 Nginx 配置

**涉及文件**

- 新增：`frontend/Dockerfile`
- 新增：`frontend/.dockerignore`
- 新增：`frontend/nginx.conf`

**实现说明**

- 使用 Node 镜像构建 Vite 静态文件。
- 使用 Nginx 托管 dist。
- Nginx 将 `/api` 反向代理到 backend。
- 支持 Vue Router history fallback。

**验收标准**

- `docker build -t ai-ecommerce-agent-frontend ./frontend` 成功。
- 前端容器访问 `/dashboard` 不 404。
- `/api/health` 经 Nginx 代理可访问后端。

### 任务 10.3：docker-compose 一键启动

**涉及文件**

- 新增：`docker-compose.yml`
- 新增：`.env.example`
- 修改：`README.md`
- 新增文档：`DEPLOYMENT.md`（Phase 11）

**实现说明**

- 服务：
  - `postgres`
  - `backend`
  - `frontend`
- postgres 使用 volume 持久化。
- backend 依赖 postgres，读取 `DATABASE_URL=postgresql+psycopg://...`。
- frontend 暴露 80 或 8080。
- 初始数据库可通过 `docker compose exec backend python scripts/init_db.py --reset` 或启动脚本处理。V1.0 建议文档命令显式初始化，避免容器每次启动误 reset。

**验收标准**

- `docker compose up -d` 可启动三项服务。
- 初始化数据库后可登录默认账号。
- 前端页面可访问 Dashboard。

### 风险点

- 自动初始化数据库如果处理不当会误删数据，生产环境禁止自动 `--reset`。
- Compose 健康检查需要等待 postgres ready，避免 backend 过早启动失败。

### 阶段完成后的能力提升

项目具备可复现部署方式，新环境可以一条命令启动 MVP。

---

## Phase 11：文档升级

### 目标

优化 README，新增部署、升级、API、数据库、Agent 工作流和 RAG 升级文档，使项目可交付、可演示、可继续迭代。

### 任务 11.1：优化 README

**涉及文件**

- 修改：`README.md`

**实现说明**

README 必须包含：

- 项目定位；
- 架构图，可用 Mermaid；
- 技术栈；
- 本地启动步骤；
- Docker 启动步骤；
- 默认账号；
- 演示流程；
- 核心 API；
- 测试命令；
- 目录结构；
- 后续规划。

**验收标准**

- 新成员只看 README 能本地启动并完成演示。
- 中文在常见编辑器和终端中为 UTF-8 可读。

### 任务 11.2：新增部署文档

**涉及文件**

- 新增：`DEPLOYMENT.md`

**实现说明**

内容包括：

- 环境变量说明；
- Docker Compose 部署；
- PostgreSQL 初始化；
- Alembic 迁移命令；
- 健康检查；
- 日志查看；
- 生产安全检查清单；
- 常见故障排查。

**验收标准**

- 按文档可在新机器启动服务。
- 明确生产禁止使用默认 JWT secret。

### 任务 11.3：新增上线升级计划

**涉及文件**

- 新增：`ONLINE_UPGRADE_PLAN.md`

**实现说明**

- 记录 V1.0 Phase 1-11 的执行顺序。
- 每个阶段包含改造范围、回滚方式、验收命令。
- 明确不要一次性合并所有改造。

**验收标准**

- 后续 Codex 可按文档逐阶段实施。

### 任务 11.4：新增 API 设计文档

**涉及文件**

- 新增：`API_DESIGN.md`

**实现说明**

- 列出当前 API 分组。
- 标注公开接口、登录接口、受保护接口。
- 标注角色权限。
- 标注关键错误码：400、401、403、404、409、500。

**验收标准**

- 前后端对接口权限和错误码有统一认知。

### 任务 11.5：新增数据库设计文档

**涉及文件**

- 新增：`DATABASE_DESIGN.md`

**实现说明**

- 描述核心表和关系。
- 记录索引策略。
- 记录 SQLite 与 PostgreSQL 使用边界。
- 记录 Alembic 迁移策略。

**验收标准**

- 数据库结构和上线注意事项清晰。

### 任务 11.6：新增 Agent 工作流文档

**涉及文件**

- 新增：`AGENT_WORKFLOW.md`

**实现说明**

- 描述 9 个节点输入输出。
- 描述 context 字段传递。
- 描述节点日志。
- 描述失败兜底。
- 描述高风险人工审核规则。

**验收标准**

- 新工程师可根据文档理解 Agent 执行链路。

### 任务 11.7：新增 RAG 升级计划

**涉及文件**

- 新增：`RAG_UPGRADE_PLAN.md`

**实现说明**

- 记录 V1.0 KeywordRetriever。
- 规划 V1.1 embedding + pgvector：
  - 文档上传；
  - chunk 切分；
  - embedding；
  - 向量表；
  - 检索召回；
  - 引用来源；
  - 评估指标。

**验收标准**

- 后续升级 RAG 不需要重新梳理方向。

### 风险点

- 文档如果只写概念会无法指导实现，必须绑定文件和验收标准。
- 当前已有 README 中文输出疑似编码不一致，文档升级时统一为 UTF-8。

### 阶段完成后的能力提升

项目从“能跑 Demo”升级为“可交付、可部署、可维护、可继续迭代”的 MVP 工程。

---

## 6. 后续优化路线

### V1.1：RAG 与 Agent 观测增强

- RAG 从关键词检索升级到 embedding + pgvector。
- 增加文档上传、chunk 切分、向量化、引用来源。
- 增加 LLM token 统计，包括 prompt tokens、completion tokens、total tokens、估算成本。
- 增加 Agent 运行回放，按时间线重放每个节点输入、输出、状态、耗时。
- 增加客服回复质量评估，例如准确性、政策一致性、语气、是否需要人工审核。
- 增加知识库命中率、无答案率、人工改写率等指标。

### V2.0：ToB 基础能力

- 多租户。
- 多店铺。
- 多渠道适配器。
- 租户级知识库。
- 租户级 Agent 配置。
- 操作审计增强。
- SLA 超时提醒。
- 企业私有化部署方案。
- 更细粒度的数据权限隔离。
- 客服分配、工单协作和团队视图。

### V3.0：ToB SaaS 化

- ToB SaaS 化。
- 套餐计费。
- 模型额度控制。
- 企业配置中心。
- 数据权限隔离。
- 监控告警。
- 自动化质检。
- 运营报表。
- 多模型路由与成本优化。
- 企业级 SSO、审计导出和合规配置。

## 7. 当前结构与预期不一致处及调整建议

- 当前 `README.md`、前端部分中文文案、后端 seed 文案在 PowerShell 输出中出现乱码。建议后续统一检查文件编码为 UTF-8，并避免在不同编码终端下保存文件。
- 当前 `backend/app/rag/` 只有包目录但没有实际 Retriever 实现。建议 Phase 5 在该目录内补齐抽象，而不是继续把检索逻辑写在路由和 Agent 节点中。
- 当前 `backend/app/repositories/` 为空。V1.0 暂不强制引入 repository 层，避免无意义分层；只有当某个模型查询逻辑明显重复时再逐步抽取。
- 当前用户模型已有 `role`，但没有认证字段。建议在 Phase 3 复用 `User.role`，新增 `password_hash`，不另建复杂权限表。
- 当前工单状态默认是 `open`，目标状态机要求 `pending` 等状态。建议通过兼容迁移处理旧值，不直接删除旧演示数据。
- 当前 Agent `run.user_id` 初始化为 `0`，后续应在 `receive_message` 后写入真实用户 ID；如果 message/session 不存在，失败结果应明确说明。
- 当前前端未使用状态管理库。V1.0 不必为了 auth 引入 Pinia，可先用轻量 session 模块；如果后续状态复杂再引入。

## 8. 推荐实施顺序和验收节奏

1. Phase 1 和 Phase 2 优先完成，保证配置和数据库基础稳定。
2. Phase 3 完成后再做 Phase 9 的前端登录和权限，否则前端无法真实联调。
3. Phase 4、Phase 5、Phase 6 可连续实施，因为它们都围绕 Agent 可上线能力。
4. Phase 7、Phase 8 处理业务安全和追踪能力，适合在 Agent 边界稳定后实施。
5. Phase 10、Phase 11 作为交付收口，但 Docker 和部署文档可以在 Phase 1 后提前草拟。

每个 Phase 的最低验收要求：

- 后端：`cd backend && python -m pytest`
- 前端：`cd frontend && npm run build`
- 文档：确认新增/修改文档为 UTF-8，且命令可执行。
- 演示：保留原始 Demo 流程，即会话触发 Agent、生成回复建议、创建审核任务、创建售后工单、查看 Agent 节点日志。

