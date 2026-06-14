# AI 电商客服与订单售后 Agent 平台 TDD

## 1. 技术架构

### 1.1 后端技术栈

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- LangGraph 或普通 Python Pipeline
- Mock LLM
- 简单 RAG 检索
- pytest

### 1.2 前端技术栈

- Vue3
- Vite
- Naive UI
- Axios
- Vue Router
- ECharts

### 1.3 架构分层

后端建议分层：

- api：FastAPI 路由层
- schemas：Pydantic 请求和响应模型
- models：SQLAlchemy ORM 模型
- repositories：数据库访问封装
- services：业务服务
- agent：Agent 工作流节点和编排
- rag：知识库切分与检索
- mock_llm：Mock LLM 回复生成
- tests：pytest 测试

前端建议分层：

- router：页面路由
- api：Axios 请求封装
- stores：可选，状态管理
- layouts：后台布局
- views：页面
- components：业务组件
- charts：ECharts 图表组件
- types：接口类型

## 2. 模块拆分

### 2.1 用户消息模块

模块作用：

- 管理客服会话和消息
- 保存用户消息、客服回复、Agent 建议

输入数据：

- session_id
- sender_type
- message_content
- message_type

输出数据：

- 会话详情
- 消息列表
- 新消息记录

主要接口：

- GET /api/sessions
- GET /api/sessions/{session_id}
- POST /api/sessions
- GET /api/sessions/{session_id}/messages
- POST /api/sessions/{session_id}/messages

MVP 必做：是

### 2.2 商品模块

模块作用：

- 管理 Mock 商品数据
- 支持商品咨询、订单关联、售后规则判断

输入数据：

- 商品名称
- SKU
- 类目
- 售后标签

输出数据：

- 商品列表
- 商品详情

主要接口：

- GET /api/products
- GET /api/products/{product_id}
- POST /api/products
- PUT /api/products/{product_id}

MVP 必做：是，新增和编辑可后置

### 2.3 订单模块

模块作用：

- 管理 Mock 订单
- 支持订单查询、物流查询、退货退款判断

输入数据：

- order_id
- order_no
- user_id
- product_id

输出数据：

- 订单列表
- 订单详情
- 物流状态

主要接口：

- GET /api/orders
- GET /api/orders/{order_id}
- GET /api/orders/by-number/{order_no}
- GET /api/users/{user_id}/orders

MVP 必做：是

### 2.4 知识库模块

模块作用：

- 管理售后政策、物流说明、商品说明
- 支持简单 RAG 检索

输入数据：

- document title
- document type
- document content
- query

输出数据：

- 文档列表
- chunk 列表
- 检索结果

主要接口：

- GET /api/knowledge/documents
- POST /api/knowledge/documents
- PUT /api/knowledge/documents/{document_id}
- POST /api/knowledge/documents/{document_id}/rebuild-chunks
- GET /api/knowledge/search

MVP 必做：是，先做关键词检索即可

### 2.5 Agent 模块

模块作用：

- 编排意图识别、业务查询、知识检索、规则判断和回复生成
- 保存运行记录和节点日志

输入数据：

- session_id
- message_id
- user_id
- message_content

输出数据：

- agent_run
- intent
- reply_suggestion
- review_task
- ticket
- node_logs

主要接口：

- POST /api/agent/runs
- GET /api/agent/runs
- GET /api/agent/runs/{run_id}
- GET /api/agent/runs/{run_id}/node-logs

MVP 必做：是

### 2.6 售后规则模块

模块作用：

- 根据订单、商品、签收时间、售后政策判断是否满足退货退款条件

输入数据：

- order
- product
- intent
- policy_chunks

输出数据：

- policy_result
- allow_return
- allow_refund
- reason

主要接口：

- MVP 可作为内部 service，不单独暴露接口

MVP 必做：是

### 2.7 人工审核模块

模块作用：

- 管理高风险或需人工确认的回复建议

输入数据：

- agent_run_id
- reply_suggestion_id
- risk_reason
- reviewer action

输出数据：

- review_task
- review_result

主要接口：

- GET /api/review-tasks
- GET /api/review-tasks/{task_id}
- POST /api/review-tasks/{task_id}/approve
- POST /api/review-tasks/{task_id}/reject

MVP 必做：是

### 2.8 工单模块

模块作用：

- 管理退货、退款、投诉等售后事项

输入数据：

- ticket_type
- order_id
- user_id
- priority
- description

输出数据：

- ticket
- ticket status

主要接口：

- GET /api/tickets
- GET /api/tickets/{ticket_id}
- POST /api/tickets
- PUT /api/tickets/{ticket_id}
- POST /api/tickets/{ticket_id}/status

MVP 必做：是

### 2.9 日志模块

模块作用：

- 记录 Agent 运行和节点执行日志
- 支持故障排查和面试演示

输入数据：

- run_id
- node_name
- input_json
- output_json
- status
- error_message

输出数据：

- run list
- node logs

主要接口：

- GET /api/agent/runs
- GET /api/agent/runs/{run_id}/node-logs

MVP 必做：是

### 2.10 前端管理后台模块

模块作用：

- 提供业务数据管理、客服会话、审核、工单和日志查看界面

输入数据：

- 用户操作
- 筛选条件
- 表单数据

输出数据：

- 表格
- 表单
- 图表
- 工作流日志

MVP 必做：是

## 3. 数据库表设计初稿

### 3.1 users

作用：保存 Mock 用户和后台人员信息。

字段：

- id：主键
- username：用户名
- display_name：展示名
- role：角色，customer、agent、reviewer、admin
- phone：手机号
- email：邮箱
- status：状态，active、disabled
- created_at：创建时间
- updated_at：更新时间

### 3.2 products

作用：保存 Mock 商品信息。

字段：

- id：主键
- name：商品名称
- sku：SKU 编码
- category：商品类目
- description：商品描述
- price：价格
- stock：库存
- after_sale_policy：售后标签或简要规则
- status：状态，active、inactive
- created_at：创建时间
- updated_at：更新时间

### 3.3 orders

作用：保存 Mock 订单、支付、物流和售后状态。

字段：

- id：主键
- order_no：订单号
- user_id：用户 ID
- product_id：商品 ID
- quantity：购买数量
- total_amount：订单金额
- order_status：订单状态，pending、paid、shipped、delivered、closed
- payment_status：支付状态，unpaid、paid、refunded
- logistics_status：物流状态，pending、shipped、delivered
- tracking_no：物流单号
- paid_at：支付时间
- shipped_at：发货时间
- delivered_at：签收时间
- after_sale_status：售后状态，none、applying、processing、done、rejected
- created_at：创建时间
- updated_at：更新时间

### 3.4 sessions

作用：保存客服会话。

字段：

- id：主键
- user_id：用户 ID
- title：会话标题
- status：会话状态，open、pending、closed
- last_message_at：最后消息时间
- created_at：创建时间
- updated_at：更新时间

### 3.5 messages

作用：保存会话中的用户消息、客服消息和 Agent 消息。

字段：

- id：主键
- session_id：会话 ID
- sender_id：发送者 ID，可为空
- sender_type：customer、agent、system、ai
- content：消息内容
- message_type：text、system、suggestion
- metadata_json：扩展信息
- created_at：创建时间

### 3.6 knowledge_documents

作用：保存知识库原始文档。

字段：

- id：主键
- title：文档标题
- document_type：文档类型，policy、product、logistics、complaint
- content：文档内容
- status：状态，active、inactive
- created_at：创建时间
- updated_at：更新时间

### 3.7 knowledge_chunks

作用：保存知识文档切分后的片段。

字段：

- id：主键
- document_id：文档 ID
- chunk_index：片段序号
- content：片段内容
- keywords：关键词
- metadata_json：扩展信息
- created_at：创建时间

### 3.8 agent_runs

作用：保存一次 Agent 执行总记录。

字段：

- id：主键
- session_id：会话 ID
- message_id：触发消息 ID
- user_id：用户 ID
- intent：识别意图
- status：running、success、failed
- summary：运行摘要
- started_at：开始时间
- finished_at：结束时间
- error_message：错误信息
- created_at：创建时间

### 3.9 agent_node_logs

作用：保存 Agent 每个节点的执行日志。

字段：

- id：主键
- run_id：Agent 运行 ID
- node_name：节点名称
- status：success、failed、skipped
- input_json：节点输入
- output_json：节点输出
- error_message：错误信息
- started_at：开始时间
- finished_at：结束时间
- duration_ms：耗时毫秒
- created_at：创建时间

### 3.10 reply_suggestions

作用：保存 Agent 生成的客服回复建议。

字段：

- id：主键
- run_id：Agent 运行 ID
- session_id：会话 ID
- message_id：用户消息 ID
- content：建议回复内容
- intent：意图
- confidence：置信度
- status：draft、pending_review、approved、rejected、sent
- source_summary：引用依据摘要
- created_at：创建时间
- updated_at：更新时间

### 3.11 review_tasks

作用：保存人工审核任务。

字段：

- id：主键
- run_id：Agent 运行 ID
- reply_suggestion_id：回复建议 ID
- task_type：reply_review、refund_review、complaint_review
- title：任务标题
- risk_level：low、medium、high
- risk_reason：风险原因
- status：pending、approved、rejected
- reviewer_id：审核人 ID
- review_comment：审核意见
- reviewed_at：审核时间
- created_at：创建时间
- updated_at：更新时间

### 3.12 tickets

作用：保存售后工单。

字段：

- id：主键
- ticket_no：工单编号
- ticket_type：return、refund、complaint、logistics、other
- user_id：用户 ID
- order_id：订单 ID
- session_id：会话 ID
- run_id：Agent 运行 ID
- title：工单标题
- description：工单描述
- priority：low、medium、high
- status：open、processing、resolved、closed
- assignee_id：处理人 ID
- resolution：处理结果
- created_at：创建时间
- updated_at：更新时间
- closed_at：关闭时间

## 4. API 接口规划

### 4.1 商品接口

GET /api/products

- 请求参数：keyword、category、status、page、page_size
- 返回数据：商品分页列表
- 用途：商品管理和商品查询

GET /api/products/{product_id}

- 请求参数：product_id
- 返回数据：商品详情
- 用途：查看商品详情

POST /api/products

- 请求参数：name、sku、category、price、stock、description、after_sale_policy
- 返回数据：新建商品
- 用途：新增 Mock 商品

PUT /api/products/{product_id}

- 请求参数：商品编辑字段
- 返回数据：更新后的商品
- 用途：编辑商品

### 4.2 订单接口

GET /api/orders

- 请求参数：keyword、user_id、status、page、page_size
- 返回数据：订单分页列表
- 用途：订单管理

GET /api/orders/{order_id}

- 请求参数：order_id
- 返回数据：订单详情，包含用户和商品信息
- 用途：查看订单详情

GET /api/orders/by-number/{order_no}

- 请求参数：order_no
- 返回数据：订单详情
- 用途：按订单号查询

GET /api/users/{user_id}/orders

- 请求参数：user_id
- 返回数据：用户订单列表
- 用途：Agent 查询用户订单

### 4.3 会话接口

GET /api/sessions

- 请求参数：status、user_id、page、page_size
- 返回数据：会话列表
- 用途：客服会话页左侧列表

POST /api/sessions

- 请求参数：user_id、title
- 返回数据：新建会话
- 用途：创建模拟客服会话

GET /api/sessions/{session_id}

- 请求参数：session_id
- 返回数据：会话详情
- 用途：查看当前会话

GET /api/sessions/{session_id}/messages

- 请求参数：session_id
- 返回数据：消息列表
- 用途：加载聊天记录

POST /api/sessions/{session_id}/messages

- 请求参数：sender_type、sender_id、content、message_type
- 返回数据：新消息
- 用途：发送用户消息或客服消息

### 4.4 Agent 接口

POST /api/agent/runs

- 请求参数：session_id、message_id
- 返回数据：run_id、intent、reply_suggestion、review_task、ticket
- 用途：触发 Agent 工作流

GET /api/agent/runs

- 请求参数：status、intent、page、page_size
- 返回数据：Agent 运行列表
- 用途：查看运行历史

GET /api/agent/runs/{run_id}

- 请求参数：run_id
- 返回数据：运行详情
- 用途：查看一次 Agent 执行结果

GET /api/agent/runs/{run_id}/node-logs

- 请求参数：run_id
- 返回数据：节点日志列表
- 用途：查看 Agent 节点级输入输出

### 4.5 知识库接口

GET /api/knowledge/documents

- 请求参数：keyword、document_type、status、page、page_size
- 返回数据：文档列表
- 用途：知识库管理

POST /api/knowledge/documents

- 请求参数：title、document_type、content
- 返回数据：新建文档
- 用途：添加政策或说明文档

GET /api/knowledge/documents/{document_id}

- 请求参数：document_id
- 返回数据：文档详情和 chunks
- 用途：查看知识文档

PUT /api/knowledge/documents/{document_id}

- 请求参数：文档编辑字段
- 返回数据：更新后的文档
- 用途：编辑知识文档

POST /api/knowledge/documents/{document_id}/rebuild-chunks

- 请求参数：document_id
- 返回数据：chunk 数量
- 用途：重新切分知识库

GET /api/knowledge/search

- 请求参数：query、document_type、limit
- 返回数据：相关 chunk 列表
- 用途：检索测试和 Agent RAG

### 4.6 审核接口

GET /api/review-tasks

- 请求参数：status、risk_level、page、page_size
- 返回数据：审核任务列表
- 用途：人工审核页

GET /api/review-tasks/{task_id}

- 请求参数：task_id
- 返回数据：审核任务详情
- 用途：查看审核详情

POST /api/review-tasks/{task_id}/approve

- 请求参数：reviewer_id、review_comment、final_reply
- 返回数据：审核结果
- 用途：通过审核

POST /api/review-tasks/{task_id}/reject

- 请求参数：reviewer_id、review_comment
- 返回数据：审核结果
- 用途：驳回审核

### 4.7 工单接口

GET /api/tickets

- 请求参数：status、ticket_type、priority、page、page_size
- 返回数据：工单列表
- 用途：售后工单管理

GET /api/tickets/{ticket_id}

- 请求参数：ticket_id
- 返回数据：工单详情
- 用途：查看工单详情

POST /api/tickets

- 请求参数：ticket_type、user_id、order_id、title、description、priority
- 返回数据：新建工单
- 用途：人工创建工单

PUT /api/tickets/{ticket_id}

- 请求参数：工单编辑字段
- 返回数据：更新后的工单
- 用途：编辑工单

POST /api/tickets/{ticket_id}/status

- 请求参数：status、resolution
- 返回数据：更新后的工单
- 用途：流转工单状态

### 4.8 Dashboard 接口

GET /api/dashboard/summary

- 请求参数：无或 date_range
- 返回数据：会话数、待审核数、待处理工单数、Agent 成功率
- 用途：首页指标卡片

GET /api/dashboard/intent-stats

- 请求参数：date_range
- 返回数据：意图分布
- 用途：意图统计图

GET /api/dashboard/ticket-stats

- 请求参数：date_range
- 返回数据：工单状态和类型统计
- 用途：工单统计图

## 5. Agent 工作流设计

### 5.1 receive_message

节点作用：读取用户消息和会话上下文。

输入：

- session_id
- message_id

输出：

- user_id
- message_content
- recent_messages

失败情况：

- message_id 不存在
- session_id 不存在

是否记录日志：是

### 5.2 classify_intent

节点作用：识别用户意图。

输入：

- message_content
- recent_messages

输出：

- intent
- confidence
- extracted_entities

失败情况：

- 无法识别意图时返回 other

是否记录日志：是

MVP 意图：

- product_inquiry
- order_query
- logistics_query
- return_request
- refund_request
- complaint
- other

### 5.3 query_order

节点作用：根据用户、订单号、商品关键词查询订单。

输入：

- user_id
- intent
- extracted_entities
- message_content

输出：

- matched_order
- matched_product
- match_reason

失败情况：

- 找不到订单
- 匹配到多个订单，需要人工确认

是否记录日志：是

### 5.4 retrieve_knowledge

节点作用：检索售后政策、物流说明或商品知识。

输入：

- intent
- message_content
- matched_product

输出：

- related_chunks
- source_documents

失败情况：

- 无相关知识，返回空列表

是否记录日志：是

### 5.5 check_policy

节点作用：根据订单、商品和知识库内容判断售后规则。

输入：

- intent
- matched_order
- matched_product
- related_chunks

输出：

- policy_result
- allow_return
- allow_refund
- reason
- need_ticket

失败情况：

- 订单缺少签收时间
- 缺少相关售后政策

是否记录日志：是

### 5.6 risk_check

节点作用：判断是否需要人工审核。

输入：

- intent
- policy_result
- matched_order
- message_content

输出：

- risk_level
- need_review
- risk_reasons

失败情况：

- 风险规则异常时默认 need_review = true

是否记录日志：是

MVP 风险规则：

- 退款或退货申请需要审核
- 投诉类消息需要审核
- 订单金额大于指定阈值需要审核
- 超过售后期限但用户仍要求售后需要审核
- 消息包含强烈负面情绪关键词需要审核

### 5.7 generate_reply

节点作用：生成客服回复建议。

输入：

- intent
- matched_order
- related_chunks
- policy_result
- risk_result

输出：

- reply_content
- confidence
- source_summary

失败情况：

- Mock LLM 异常时返回模板回复

是否记录日志：是

### 5.8 create_review_task

节点作用：当 need_review 为 true 时创建人工审核任务。

输入：

- run_id
- reply_suggestion_id
- risk_result
- policy_result

输出：

- review_task

失败情况：

- reply_suggestion_id 不存在

是否记录日志：是

### 5.9 create_ticket

节点作用：当需要售后流转时创建工单。

输入：

- run_id
- session_id
- user_id
- matched_order
- intent
- policy_result

输出：

- ticket

失败情况：

- 订单缺失时创建未关联订单的工单，标记为需要人工补充

是否记录日志：是

### 5.10 save_run_log

节点作用：结束 Agent run，更新状态和摘要。

输入：

- run_id
- all_node_results

输出：

- final_run_status
- summary

失败情况：

- 保存失败时记录 error_message

是否记录日志：是

## 6. Agent 编排建议

MVP 推荐先使用普通 Python Pipeline 实现：

1. 每个节点是一个独立函数或类方法
2. 用上下文字典 context 在节点间传递数据
3. 每个节点前后统一调用 log_node_start 和 log_node_end
4. 节点异常统一捕获，写入 agent_node_logs
5. MVP 稳定后再替换或扩展为 LangGraph

推荐执行顺序：

receive_message -> classify_intent -> query_order -> retrieve_knowledge -> check_policy -> risk_check -> generate_reply -> create_review_task -> create_ticket -> save_run_log

## 7. 测试策略

### 7.1 后端单元测试

- 意图识别测试
- 知识库检索测试
- 售后规则判断测试
- 风险判断测试
- Mock LLM 回复生成测试

### 7.2 后端接口测试

- 商品列表接口
- 订单详情接口
- 会话消息接口
- Agent run 接口
- 审核任务接口
- 工单接口

### 7.3 MVP 集成测试

测试输入：

> 我买的耳机有杂音，可以退货吗？

验收结果：

- 创建用户消息
- 创建 agent_run
- intent = return_request
- 查询到耳机订单
- 检索到售后政策
- 创建 reply_suggestion
- 创建 review_task
- 创建 ticket
- 写入 agent_node_logs

## 8. 推荐开发顺序

1. 初始化后端 FastAPI 项目，提供健康检查接口
2. 初始化前端 Vue3 项目，提供后台基础布局
3. 建立数据库模型和 SQLite 连接
4. 编写 seed 脚本，生成 Mock 用户、商品、订单和知识库
5. 实现商品、订单、会话、消息基础 API
6. 实现知识库文档和简单关键词检索
7. 实现 Agent Pipeline MVP
8. 实现审核任务和工单 API
9. 实现 Dashboard 汇总 API
10. 前端接入商品、订单、会话、审核、工单、日志页面
11. 补充 pytest 测试
12. 编写 README 和面试演示脚本

