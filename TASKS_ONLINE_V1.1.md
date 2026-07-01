# ai-ecommerce-agent-platform V1.1 会话中心产品化任务文档

> 本文档用于指导 `ai-ecommerce-agent-platform` 在 V1.0 上线级 MVP 基础上，继续把当前偏 Demo/调试台形态的 Sessions 模块升级为更接近真实 ToB 客服系统的“会话中心”。本轮只做架构判断、产品结构和任务拆解，不要求立即改代码。

## 1. V1.1 核心判断

### 1.1 是否应该新增一个数据库？

结论：不建议新增第二个物理数据库。

原因：

- 当前系统已经有用户、订单、商品、会话、消息、Agent Run、审核任务、工单、审计日志等强关联数据。如果再为“会话中心”单独新增一个数据库，会让订单匹配、售后判断、工单创建、审计追踪和权限控制跨库化，复杂度明显上升。
- 会话数据和售后业务数据需要事务一致性。例如客户发起售后问题后，系统可能同时写入消息、Agent Run、回复建议、审核任务、工单和审计日志。放在同一个数据库内更容易保证一致性。
- 当前项目目标仍是在线 MVP 到 ToB 雏形，不是大规模多租户 IM 平台。此阶段应优先增强数据模型，而不是拆分数据库。
- 新增独立数据库会增加部署、备份、迁移、监控、权限管理和数据排查成本，不符合 V1.1 的阶段目标。

建议：

- 保持一个业务数据库。
- 在同一数据库中扩展会话中心相关表和字段。
- 继续支持本地 SQLite 演示和生产 PostgreSQL 部署。
- 后续如果进入高并发 IM 场景，再评估是否拆分消息存储、搜索索引或事件流。

### 1.2 是否应该以 customer_id 作为主键存储售后聊天内容？

结论：不应该。

原因：

- 一个客户会有多次会话，可能分别对应售前咨询、物流问题、退货退款、投诉、发票、质保等不同场景。`customer_id` 只能代表客户，不能代表某一次会话。
- 同一客户可能同时有多个订单、多个商品和多个售后工单，不能用客户 ID 直接承载聊天主线。
- 匿名客户、未登录客户、未购买客户没有稳定 customer_id，但仍然需要能咨询。
- 主键应该表达记录自身身份。会话应使用 `session_id` 或 `conversation_id` 作为主键，消息应使用 `message_id` 作为主键。

建议：

- `customers` 或现有 `users` 表用于客户身份。
- `customer_sessions` / `conversations` 表使用独立主键。
- `messages` 表使用独立主键，并通过 `session_id` 关联会话。
- `session.customer_id` 允许为空，用于匿名访客或未绑定客户。
- 匿名访客使用 `visitor_id`、`visitor_token`、`channel_user_id` 或临时会话标识。

### 1.3 如何支持无客户 ID 的客户咨询？

应支持。

无客户 ID 不代表不能咨询，只代表系统无法直接查询订单和售后历史。

建议流程：

1. 客户进入咨询入口并发送第一条消息。
2. 系统自动创建会话，不要求后台人员手动创建。
3. 如果客户未登录或无客户 ID，则创建匿名会话。
4. Agent 先判断咨询类型：
   - 售前咨询：回答商品、库存、规格、价格、发货、优惠等问题。
   - 疑似售后：提示需要订单号、手机号、购买账号或其他凭证。
   - 投诉/高风险：进入人工接管或创建待补充信息工单。
5. 如果客户没有购买记录但问出售后问题，可以返回 mock/引导式回复：
   - 说明需要订单信息才能继续处理真实售后。
   - 提供可准备的信息：订单号、购买时间、商品名称、问题照片/视频。
   - 对无法核验的退货退款请求，不直接承诺处理结果。

### 1.4 当前 Sessions 模块的问题

当前模块更像 Agent 调试台，不像真实会话中心。

主要问题：

- 需要手动创建会话，不符合真实客户主动咨询流程。
- 新建会话弹窗要求填写标题和首条消息，偏后台测试，不偏客户入口。
- 售前咨询和已购售后没有明确分流。
- Agent 回复已经进入聊天窗口后，右侧如果继续重复显示回复正文，价值较低。
- 右侧更应该展示 Agent 决策依据、订单上下文、知识库来源、风险判断和工单状态。
- 会话类型、处理状态、是否需要人工、是否绑定订单等信息没有成为会话列表的一等筛选条件。

## 2. V1.1 目标

将当前 Sessions 模块升级为“会话中心”，目标是：

- 客户发送第一条消息后自动创建会话。
- 支持匿名访客、未购买客户、已购买客户。
- 支持售前咨询与售后服务统一入口、自动分类、可筛选管理。
- Agent 回复进入真实聊天记录。
- Agent 根据客户输入语言回复，而不是根据后台 UI 语言回复。
- 右侧面板从“重复展示 Agent 回复”升级为“上下文与决策面板”。
- 售后问题尽量绑定订单；无法绑定时进入信息补充或 mock 引导。
- 人工审核、工单、风险状态可以从会话中心直接观察。

## 3. 推荐信息架构

### 3.1 左侧：会话队列

功能：

- 展示所有会话。
- 支持按类型筛选：
  - 全部
  - 售前
  - 售后
  - 物流
  - 投诉
  - 发票
  - 待人工
  - 已关闭
- 支持搜索：
  - 用户名
  - 客户 ID
  - 访客 ID
  - 订单号
  - 商品名
  - 会话标题
  - 会话摘要
- 会话卡片应展示：
  - 会话标题或自动摘要
  - 会话类型
  - 客户/访客标识
  - 订单绑定状态
  - 处理状态
  - 最新消息时间
  - 是否需要人工介入

### 3.2 中间：真实聊天窗口

功能：

- 展示客户消息、Agent 回复、人工客服回复。
- Agent 回复持久化为消息记录。
- 输入框用于客服测试、人工客服回复或 Demo 触发 Agent。
- Enter 发送，Shift + Enter 换行。
- Agent 回复语言应跟随客户输入语言。
- UI 切换中英文只影响后台界面文案，不强制翻译客户消息和 Agent 回复历史。

消息类型建议：

- `customer`
- `agent`
- `human_agent`
- `system`

消息子类型建议：

- `text`
- `agent_reply`
- `handoff_notice`
- `order_bind_request`
- `ticket_created`
- `review_required`

### 3.3 右侧：上下文与决策面板

右侧不应重复聊天正文，而应展示 Agent 为什么这样处理。

建议展示：

- 客户信息：
  - customer_id
  - visitor_id
  - 是否匿名
  - 是否已购买
- 订单上下文：
  - 匹配订单
  - 商品
  - 支付状态
  - 物流状态
  - 售后状态
- Agent 判断：
  - 会话类型
  - 意图
  - 置信度
  - 风险等级
  - 是否需要人工审核
  - 是否需要补充订单信息
- RAG / 知识库来源：
  - 命中文档
  - 命中片段
  - 来源摘要
- 工单与审核：
  - 审核任务状态
  - 工单号
  - 工单类型
  - 工单状态
  - 负责人
- 技术诊断：
  - LLM Provider
  - 是否 fallback
  - Agent Run ID
  - 节点日志入口

### 3.4 新建会话入口

新建会话不应作为主流程。

建议调整为：

- 主流程：客户发送消息后自动创建会话。
- 后台保留入口：命名为“模拟客户咨询”或“创建测试会话”。
- 测试入口可以选择：
  - 匿名访客
  - 已购客户
  - 售前咨询
  - 售后问题
  - 绑定某个订单
  - 不绑定订单

## 4. 推荐数据模型方向

### 4.1 不新增物理数据库，扩展现有数据库

建议在现有数据库中扩展以下概念。

### 4.2 客户与访客

可选方案：

- 方案 A：扩展现有 `users` 表，增加 `user_type` 区分后台用户、客户、访客。
- 方案 B：新增 `customers` 表，后台用户继续使用 `users`。

V1.1 推荐方案 B。

原因：

- 后台登录用户和电商客户是两类身份。
- 后台用户有角色权限，例如 admin/reviewer/agent/viewer。
- 客户侧身份更关注手机号、邮箱、会员等级、购买记录、渠道用户 ID。
- 分表能避免 RBAC 与客户资料混在一起。

建议字段：

- `customers.id`
- `customers.external_customer_id`
- `customers.name`
- `customers.phone`
- `customers.email`
- `customers.status`
- `customers.created_at`
- `customers.updated_at`

匿名访客不一定需要单独落 `customers`，可以在会话表中保存 `visitor_id`。

### 4.3 会话表

当前 `sessions` 表可以扩展，或迁移为更清晰的 `conversations` 命名。

V1.1 可以先保留现有表名，避免破坏现有 API。

建议新增或规划字段：

- `customer_id`：可空，关联客户。
- `visitor_id`：可空，匿名访客标识。
- `channel`：来源渠道，例如 web、admin_demo、mock、api。
- `conversation_type`：会话类型。
- `intent`：最近一次识别意图。
- `status`：open、pending_human、resolved、closed。
- `priority`：low、medium、high。
- `bound_order_id`：可空，当前主绑定订单。
- `bound_product_id`：可空，当前主绑定商品。
- `requires_human`：是否需要人工。
- `summary`：会话摘要。
- `last_message_at`：最新消息时间。

### 4.4 消息表

继续以 `messages.id` 作为主键。

建议增强字段：

- `sender_type`：customer、agent、human_agent、system。
- `message_type`：text、agent_reply、handoff_notice、ticket_created 等。
- `language`：zh、en、unknown。
- `metadata_json`：保存 run_id、reply_suggestion_id、risk_level、source 等轻量信息。

### 4.5 会话上下文表

是否新增独立表可以分阶段。

V1.1 推荐先不强制新增复杂上下文表，优先把关键上下文字段落在 session、agent_run、ticket、review_task 现有结构里。

后续如果右侧决策面板需要保存历史快照，再新增：

- `conversation_context_snapshots`
- `conversation_order_links`
- `conversation_tags`

## 5. Agent 行为调整原则

### 5.1 自动创建会话

新增客户入口 API 时，不要求前端先创建会话。

建议流程：

1. 前端发送第一条客户消息。
2. 后端判断是否已有 session。
3. 如果没有，则自动创建 session。
4. 保存客户消息。
5. 触发 Agent。
6. 保存 Agent 回复。
7. 返回会话、消息和决策上下文。

### 5.2 售前与售后分类

Agent 应先判断会话大类：

- pre_sales
- after_sales
- logistics
- complaint
- invoice
- other

然后再判断细分意图：

- product_inquiry
- order_query
- return_request
- refund_request
- exchange_request
- logistics_query
- complaint
- invoice_request

### 5.3 已购客户售后

如果有 customer_id 或订单号：

- 查询客户订单。
- 匹配订单和商品。
- 判断售后规则。
- 判断风险等级。
- 必要时创建审核任务或工单。
- 给出具体回复。

### 5.4 未购买或匿名客户咨询

如果没有 customer_id：

- 售前问题正常回答。
- 售后问题不直接承诺退款、退货、换货。
- 引导客户提供订单号、手机号、购买账号、商品信息。
- 可以生成 mock 回复用于 Demo，但必须明确这是“需要补充订单信息”的处理。

### 5.5 回复语言

Agent 回复语言必须跟随客户最近一条消息的语言。

规则：

- 中文输入，中文回复。
- 英文输入，英文回复。
- 中英混合时，优先使用客户主要语言。
- UI 语言切换不影响历史聊天内容和 Agent 回复语言。

## 6. V1.1 Phase 拆解

### Phase 1：会话中心产品模型确认

目标：

- 明确会话中心不是 Agent 调试台。
- 明确售前、售后、匿名访客、已购客户的统一入口设计。
- 明确不新增物理数据库，只扩展现有数据库模型。

交付：

- 更新产品说明。
- 更新数据库设计草案。
- 明确 session、message、customer、visitor 的边界。

验收：

- 文档中明确说明 customer_id 不是会话主键。
- 文档中明确说明匿名访客如何进入咨询流程。
- 文档中明确说明右侧面板的新定位。

### Phase 2：会话数据模型升级

目标：

- 扩展会话表字段。
- 新增 customers 表或等价客户模型。
- 支持匿名 visitor_id。

建议涉及文件：

- `backend/app/models/entities.py`
- `backend/app/schemas/session.py`
- `backend/app/api/routes/sessions.py`
- `backend/app/services/demo_seed.py`
- `DATABASE_DESIGN.md`

验收：

- 一个 customer 可以拥有多个 session。
- 一个 session 可以没有 customer_id。
- session 能标记 conversation_type、status、requires_human、bound_order_id。

### Phase 3：客户入口 API

目标：

- 提供“发送第一条消息自动创建会话”的 API。
- 不再要求真实客户先手动创建会话。

建议 API：

- `POST /api/conversations/messages`
- 或兼容现有路径新增 `POST /api/sessions/customer-message`

请求可包含：

- `session_id`
- `customer_id`
- `visitor_id`
- `content`
- `channel`
- `order_no`

行为：

- 有 session_id：追加消息。
- 无 session_id：自动创建会话并追加消息。
- 根据需要触发 Agent。

验收：

- 匿名客户可发起咨询。
- 已购客户可发起售后。
- 首条消息后自动生成会话。

### Phase 4：Agent 分类与语言策略

目标：

- Agent 先判断售前/售后/物流/投诉/发票等会话类型。
- Agent 回复语言跟随客户输入语言。

建议涉及文件：

- `backend/app/agent/types.py`
- `backend/app/agent/nodes.py`
- `backend/app/agent/pipeline.py`
- `backend/tests/test_agent_*`

验收：

- 中文售后问题返回中文回复。
- 英文售后问题返回英文回复。
- 售前问题不会强行进入售后工单。
- 未绑定订单的售后问题会要求补充订单信息。

### Phase 5：右侧上下文与决策面板

目标：

- 右侧不再重复展示 Agent 回复正文。
- 改为展示客户、订单、商品、知识库、风险、审核、工单、Agent 运行上下文。

建议涉及文件：

- `frontend/src/views/SessionsView.vue`
- `frontend/src/api/client.ts`
- `backend/app/schemas/agent.py`
- `backend/app/api/routes/agent.py`

验收：

- 聊天正文只在中间聊天窗口展示。
- 右侧展示 Agent 判断依据。
- 可看到是否需要人工、是否创建工单、命中哪些知识库。

### Phase 6：会话队列筛选与搜索

目标：

- 左侧从简单列表升级为会话队列。

筛选项：

- 全部
- 售前
- 售后
- 物流
- 投诉
- 发票
- 待人工
- 已关闭

搜索项：

- 客户
- 访客
- 订单号
- 商品
- 会话标题
- 摘要

验收：

- 不同类型会话可以筛选。
- 待人工会话可以快速定位。
- 匿名会话和客户会话都能展示。

### Phase 7：新建会话入口降级为测试入口

目标：

- 当前“新建会话”不作为主流程。
- 改名为“模拟客户咨询”或“创建测试会话”。

验收：

- 真实业务路径不依赖手动新建会话。
- Demo 仍可通过测试入口快速创建场景。
- 测试入口可以选择匿名/已购、售前/售后、是否绑定订单。

## 7. 非目标

V1.1 暂不做：

- 不拆分第二个物理数据库。
- 不引入独立 IM 服务。
- 不接入真实淘宝、京东、抖音订单系统。
- 不做多租户隔离。
- 不允许 AI 自动执行真实退款、赔付、关闭工单等高风险动作。
- 不做复杂客服排班。
- 不做真实短信、邮件、Telegram、Discord 等渠道接入。

## 8. 推荐最终形态

V1.1 后，会话中心应表现为：

- 客户直接发起咨询，而不是后台人员先创建会话。
- 系统自动识别售前或售后。
- 有购买记录则进入订单售后判断。
- 没有购买记录则进入售前回答或售后信息补充引导。
- Agent 回复进入聊天记录。
- 右侧展示上下文和决策依据。
- 人工审核与工单状态能从会话中心直接观察。

这会让项目从“可演示 Agent Pipeline”进一步升级为“接近真实客服工作台的在线 MVP”。
