# AI 电商客服与订单售后 Agent 平台 TASKS

## Phase 0：项目初始化

### 0.1 创建项目目录结构

任务内容：

- 创建 backend 和 frontend 目录
- 创建 docs 或保留根目录文档
- 初始化 README.md

验收标准：

- 项目目录清晰
- 根目录能看到 PRD.md、TDD.md、TASKS.md
- README.md 简要说明项目定位

### 0.2 初始化 Git 忽略规则

任务内容：

- 添加 Python、Node、SQLite、环境变量相关 .gitignore

验收标准：

- node_modules、__pycache__、.env、*.db 不会被提交

## Phase 1：后端基础

### 1.1 初始化 FastAPI 应用

任务内容：

- 创建 FastAPI app
- 添加 /api/health 接口
- 配置本地启动命令

验收标准：

- 后端可启动
- GET /api/health 返回 ok

### 1.2 配置后端基础依赖

任务内容：

- 添加 fastapi、uvicorn、sqlalchemy、pydantic、pytest 等依赖
- 明确依赖管理方式

验收标准：

- 一条命令可以安装依赖
- 一条命令可以启动服务

### 1.3 配置后端项目分层

任务内容：

- 创建 api、models、schemas、services、repositories、agent、rag、tests 目录

验收标准：

- 目录结构符合 TDD
- health 接口仍可运行

## Phase 2：数据库与 Demo 数据

### 2.1 配置 SQLite 和 SQLAlchemy

任务内容：

- 创建数据库连接
- 创建 Base 和 Session 管理

验收标准：

- 应用启动时能连接 SQLite
- 测试环境可使用独立数据库

### 2.2 创建核心 ORM 模型

任务内容：

- 创建 users、products、orders、sessions、messages
- 创建 knowledge_documents、knowledge_chunks
- 创建 agent_runs、agent_node_logs、reply_suggestions、review_tasks、tickets

验收标准：

- 数据库表可创建成功
- 字段覆盖 TDD 初稿

### 2.3 创建数据库初始化脚本

任务内容：

- 提供创建表命令
- 提供重置本地 Demo 数据命令

验收标准：

- 一条命令可初始化数据库
- 重复运行不会导致明显异常

### 2.4 编写 Demo Seed 数据

任务内容：

- 创建 Mock 用户
- 创建耳机、手机、键盘等商品
- 创建已签收、运输中、已退款等订单
- 创建售后政策知识文档

验收标准：

- 初始化后可查询到 Demo 数据
- 包含“耳机有杂音，可以退货吗”演示所需订单和政策

## Phase 3：基础 API

### 3.1 商品 API

任务内容：

- 实现商品列表、详情、新增、编辑接口

验收标准：

- GET /api/products 可返回商品列表
- GET /api/products/{id} 可返回商品详情
- pytest 覆盖列表和详情接口

### 3.2 订单 API

任务内容：

- 实现订单列表、详情、按订单号查询、按用户查询接口

验收标准：

- GET /api/orders 可返回订单列表
- GET /api/users/{user_id}/orders 可返回用户订单
- pytest 覆盖订单详情接口

### 3.3 会话和消息 API

任务内容：

- 实现会话列表、创建会话、会话详情
- 实现消息列表、发送消息

验收标准：

- 可以创建会话
- 可以向会话写入用户消息
- 可以读取会话消息列表

### 3.4 知识库 API

任务内容：

- 实现文档列表、新增、详情、编辑
- 实现 rebuild chunks
- 实现简单关键词检索

验收标准：

- 可以新增知识文档
- 可以生成 knowledge_chunks
- GET /api/knowledge/search 能返回相关 chunk

## Phase 4：Agent MVP

### 4.1 实现 Agent 运行数据结构

任务内容：

- 定义 Agent context
- 定义节点结果结构
- 定义统一节点日志记录方法

验收标准：

- 每次 Agent run 都能创建 agent_runs 记录
- 每个节点能写入 agent_node_logs

### 4.2 实现 receive_message 节点

任务内容：

- 根据 session_id 和 message_id 读取消息
- 读取最近会话上下文

验收标准：

- 输入有效 message_id 时返回消息内容和用户信息
- 失败时写入失败日志

### 4.3 实现 classify_intent 节点

任务内容：

- 先使用关键词规则识别意图
- 支持 return_request、refund_request、logistics_query、order_query、product_inquiry、complaint、other

验收标准：

- “可以退货吗”识别为 return_request
- “物流到哪了”识别为 logistics_query
- pytest 覆盖核心意图

### 4.4 实现 query_order 节点

任务内容：

- 按用户和消息关键词匹配订单
- 优先匹配商品名
- 没有商品名时取最近订单

验收标准：

- “耳机有杂音”能匹配到耳机订单
- 找不到订单时不会中断整个 Agent

### 4.5 实现 retrieve_knowledge 节点

任务内容：

- 根据用户消息和意图检索知识库 chunk
- 返回 top N 结果

验收标准：

- 退货问题能检索到退货政策
- 检索结果写入节点日志

### 4.6 实现 check_policy 节点

任务内容：

- 判断是否满足退货或退款条件
- 支持签收 7 天内、质量问题、超期等规则

验收标准：

- 耳机质量问题场景返回可申请退货
- 超过期限场景返回需要人工确认或不可直接退货

### 4.7 实现 risk_check 节点

任务内容：

- 根据意图、金额、投诉关键词、超期情况判断风险

验收标准：

- 退货申请 need_review = true
- 投诉消息 risk_level 至少为 medium

### 4.8 实现 generate_reply 节点

任务内容：

- 使用 Mock LLM 或模板生成回复建议
- 生成引用依据摘要

验收标准：

- 回复内容包含订单或售后政策相关信息
- 创建 reply_suggestions 记录

### 4.9 实现 create_review_task 节点

任务内容：

- 当 need_review = true 时创建审核任务

验收标准：

- 退货申请能创建 pending 审核任务
- 审核任务关联 reply_suggestion

### 4.10 实现 create_ticket 节点

任务内容：

- 对退货、退款、投诉等场景创建售后工单

验收标准：

- 退货申请能创建 return 类型工单
- 工单关联 session、order、run

### 4.11 实现 Agent 触发接口

任务内容：

- 实现 POST /api/agent/runs
- 串联所有 MVP 节点

验收标准：

- 传入 session_id 和 message_id 可完整运行 Agent
- 返回 reply_suggestion、review_task、ticket
- agent_runs 最终状态为 success

### 4.12 实现 Agent 日志接口

任务内容：

- 实现 Agent run 列表、详情、节点日志接口

验收标准：

- 前端可以查询到 Agent 执行链路
- 节点输入输出以 JSON 返回

## Phase 5：前端基础布局

### 5.1 初始化 Vue3 + Vite 项目

任务内容：

- 创建 Vue3 项目
- 安装 Naive UI、Axios、Vue Router、ECharts

验收标准：

- 前端可启动
- 默认页面能打开

### 5.2 创建后台布局

任务内容：

- 创建侧边栏、顶部栏、内容区
- 配置路由

验收标准：

- 可在页面间切换
- 包含 Dashboard、商品、订单、会话、知识库、审核、工单、日志菜单

### 5.3 封装 Axios API 客户端

任务内容：

- 设置 baseURL
- 封装基础请求方法
- 处理错误提示

验收标准：

- 页面可调用 /api/health
- 请求错误有 Naive UI 提示

## Phase 6：核心页面

### 6.1 Dashboard 页面

任务内容：

- 展示指标卡片
- 展示意图分布和工单状态图表
- 展示最近 Agent 运行记录

验收标准：

- 页面加载后可看到核心指标
- 图表能基于接口数据渲染

### 6.2 商品管理页

任务内容：

- 商品表格
- 搜索和详情抽屉

验收标准：

- 可查看商品列表
- 可查看商品详情

### 6.3 订单管理页

任务内容：

- 订单表格
- 订单详情抽屉
- 展示物流和售后状态

验收标准：

- 可查看订单列表
- 可查看订单详情

### 6.4 客服会话页

任务内容：

- 会话列表
- 消息窗口
- 用户消息输入框
- 触发 Agent 按钮
- 展示回复建议、审核任务和工单

验收标准：

- 可以发送“我买的耳机有杂音，可以退货吗？”
- 可以触发 Agent
- 页面展示回复建议、审核任务和工单信息

### 6.5 知识库管理页

任务内容：

- 文档列表
- 文档详情
- 检索测试

验收标准：

- 可以查看知识文档
- 输入退货相关问题能返回 chunk

### 6.6 人工审核页

任务内容：

- 审核任务列表
- 审核详情
- 通过和驳回操作

验收标准：

- 可以看到 Agent 创建的审核任务
- 可以通过或驳回任务

### 6.7 售后工单页

任务内容：

- 工单列表
- 工单详情
- 状态流转

验收标准：

- 可以看到 Agent 创建的退货工单
- 可以更新工单状态

### 6.8 Agent 运行日志页

任务内容：

- Agent run 表格
- 节点步骤条
- 节点输入输出 JSON 查看器

验收标准：

- 可以查看一次 Agent 的完整执行链路
- 节点日志包含输入、输出、状态和错误信息

## Phase 7：测试与文档

### 7.1 补充后端单元测试

任务内容：

- 覆盖意图识别、知识库检索、售后规则、风险判断

验收标准：

- pytest 可运行
- 核心业务逻辑有测试

### 7.2 补充 API 测试

任务内容：

- 覆盖商品、订单、会话、Agent、审核、工单接口

验收标准：

- 核心接口测试通过
- Agent MVP 集成测试通过

### 7.3 编写 README

任务内容：

- 项目介绍
- 技术栈
- 启动方式
- 演示流程
- API 文档入口
- 截图占位

验收标准：

- 新人按 README 可以启动项目
- 面试官能快速理解项目亮点

### 7.4 编写面试演示脚本

任务内容：

- 准备 3 分钟演示流程
- 准备技术亮点说明
- 准备常见追问答案

验收标准：

- 可以按脚本完成端到端演示

## Phase 8：优化与加分项

### 8.1 替换为 LangGraph 工作流

任务内容：

- 将 Python Pipeline 改造为 LangGraph
- 保留原节点日志能力

验收标准：

- Agent 行为不回退
- 节点仍可追踪

### 8.2 接入真实 LLM

任务内容：

- 增加 LLM Provider 抽象
- 支持 Mock LLM 和真实 LLM 切换

验收标准：

- 默认仍可离线演示
- 配置 API Key 后可使用真实模型

### 8.3 增强 RAG 检索

任务内容：

- 引入 embedding
- 支持向量检索
- 回复中展示引用来源

验收标准：

- 检索结果比关键词更稳定
- 前端可展示引用文档

### 8.4 增加登录和权限

任务内容：

- 添加 JWT 登录
- 添加角色权限控制

验收标准：

- customer、agent、reviewer、admin 权限不同
- 审核接口只有 reviewer 或 admin 可操作

### 8.5 Docker Compose 一键启动

任务内容：

- 编写后端 Dockerfile
- 编写前端 Dockerfile
- 编写 docker-compose.yml

验收标准：

- 一条命令启动前后端

## 推荐开发顺序

不要一次性生成整个项目。建议按以下顺序逐步交给 Codex 实现，每一步完成后都运行验证：

1. 创建后端 FastAPI 最小应用，只实现 /api/health。
2. 配置 SQLAlchemy 和 SQLite，创建最小数据库连接。
3. 创建 ORM 模型和初始化数据库脚本。
4. 编写 Demo seed 数据，确保有耳机订单和退货政策。
5. 实现商品和订单查询 API，并用 pytest 验证。
6. 实现会话和消息 API，能保存用户输入。
7. 实现知识库文档、chunk 和关键词检索 API。
8. 实现 Agent Pipeline 的前三个节点：receive_message、classify_intent、query_order。
9. 继续实现 retrieve_knowledge、check_policy、risk_check。
10. 实现 generate_reply、create_review_task、create_ticket。
11. 实现 POST /api/agent/runs，跑通完整 MVP 链路。
12. 实现 Agent 运行日志查询接口。
13. 初始化 Vue3 前端，完成后台布局和路由。
14. 做客服会话页，优先打通发送消息和触发 Agent。
15. 做人工审核页、工单页和 Agent 日志页。
16. 补 Dashboard、商品页、订单页和知识库页。
17. 补充测试、README 和面试演示脚本。
18. 再考虑 LangGraph、真实 LLM、向量检索、权限和 Docker。

