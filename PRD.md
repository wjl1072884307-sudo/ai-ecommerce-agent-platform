# AI 电商客服与订单售后 Agent 平台 PRD

## 1. 项目定位

本项目是一个面向简历和面试演示的前后端分离 AI 电商客服系统。它不对接真实淘宝、京东、拼多多平台，而是使用 Mock 商品、订单、物流、售后政策和客服会话数据，模拟真实电商售前、售中、售后客服场景。

项目重点不只是“聊天机器人”，而是展示一个 AI Agent 如何在业务系统中完成可追踪、可审核、可落库的客服辅助流程：

- 理解用户消息意图
- 查询商品、订单和物流数据
- 检索售后知识库
- 根据规则判断退货、退款、投诉等售后场景
- 识别高风险或需人工介入的问题
- 生成客服回复建议
- 创建人工审核任务或售后工单
- 保存 Agent 执行日志，支持前端查看每个节点的输入输出

适合写成简历项目类型：

- AI Agent 应用项目
- 电商客服 SaaS 后台项目
- RAG 知识库问答项目
- 售后工单流转系统
- FastAPI + Vue3 全栈项目
- 可观测 Agent 工作流平台

推荐简历描述方向：

> 基于 FastAPI、Vue3、SQLAlchemy 和 RAG 构建 AI 电商客服与订单售后 Agent 平台，支持用户咨询意图识别、订单查询、售后政策检索、退货退款规则判断、人工审核任务创建、工单管理和 Agent 节点级运行日志追踪。

## 2. 目标用户

- 电商平台客服主管
- 电商商家售后人员
- 客服质检与运营人员
- 面试官和项目评审者

## 3. 核心业务问题

传统客服系统存在以下问题：

- 售后规则多，客服新人容易判断错误
- 订单、商品、政策信息分散，处理效率低
- AI 回复不可追踪，难以解释为什么这样回复
- 高风险售后问题需要人工审核，但普通聊天机器人缺少任务流转能力
- 售后工单和客服会话割裂，难以复盘

本项目解决方式：

- 用 Agent 工作流串联消息理解、业务查询、知识库检索、规则判断和回复生成
- 用人工审核任务承接风险场景
- 用工单模块承接退货、退款、投诉等售后事项
- 用节点日志记录 Agent 每一步执行过程
- 用前端后台展示业务数据、审核任务、工单和运行日志

## 4. 核心业务流程

完整链路如下：

1. 用户在客服会话中发送消息，例如“我买的耳机有杂音，可以退货吗？”
2. 系统创建或更新会话，并保存用户消息。
3. Agent 接收消息，创建一次 agent_run。
4. classify_intent 节点识别消息意图，例如 return_request。
5. query_order 节点根据用户、订单号、商品关键词查询订单。
6. retrieve_knowledge 节点从售后政策知识库中检索相关内容。
7. check_policy 节点根据订单状态、签收时间、商品类目、政策规则判断是否符合退货条件。
8. risk_check 节点判断是否存在风险，例如高金额订单、超期退货、投诉、情绪激烈、重复申请。
9. generate_reply 节点生成客服回复建议。
10. 如果需要人工确认，create_review_task 节点创建审核任务。
11. 如果属于明确售后事项，create_ticket 节点创建售后工单。
12. 系统保存每个 Agent 节点日志。
13. 前端客服会话页展示用户消息、Agent 建议、审核状态和关联工单。
14. 人工审核页允许客服主管通过、驳回或修改回复建议。
15. 工单页跟踪退货、退款、投诉处理状态。

## 5. 角色与权限 MVP

MVP 阶段不做复杂登录权限，使用 Mock 用户和简单角色字段即可。

- customer：模拟买家
- agent：客服人员
- reviewer：审核人员或客服主管
- admin：后台管理员

后续可扩展登录、JWT、权限控制、操作审计。

## 6. 前端页面规划

### 6.1 首页 Dashboard

页面作用：

- 展示系统整体运营概览
- 让面试演示时第一屏就能看到项目价值

主要数据：

- 今日会话数
- 待审核任务数
- 待处理工单数
- Agent 平均处理耗时
- 常见意图分布
- 工单状态分布
- 最近 Agent 运行记录

调用 API：

- GET /api/dashboard/summary
- GET /api/dashboard/intent-stats
- GET /api/dashboard/ticket-stats
- GET /api/agent/runs

主要组件：

- 指标卡片
- ECharts 饼图或柱状图
- 最近运行记录表格

### 6.2 商品管理页

页面作用：

- 管理 Mock 商品数据
- 支持客服查询商品信息

主要数据：

- 商品名称
- SKU
- 类目
- 价格
- 库存
- 售后标签
- 状态

调用 API：

- GET /api/products
- GET /api/products/{product_id}
- POST /api/products
- PUT /api/products/{product_id}

主要组件：

- 商品表格
- 搜索框
- 商品详情抽屉
- 新增/编辑表单

### 6.3 订单管理页

页面作用：

- 查看用户订单、支付、物流和售后状态

主要数据：

- 订单号
- 用户
- 商品
- 金额
- 订单状态
- 支付状态
- 物流状态
- 签收时间
- 售后状态

调用 API：

- GET /api/orders
- GET /api/orders/{order_id}
- GET /api/orders/by-number/{order_no}

主要组件：

- 订单表格
- 订单详情抽屉
- 物流时间线
- 售后状态标签

### 6.4 客服会话页

页面作用：

- 模拟真实客服工作台
- 支持输入用户消息并触发 Agent
- 展示回复建议、审核任务和工单

主要数据：

- 会话列表
- 消息记录
- 用户消息
- Agent 回复建议
- 意图识别结果
- 关联订单
- 关联审核任务
- 关联售后工单

调用 API：

- GET /api/sessions
- GET /api/sessions/{session_id}
- GET /api/sessions/{session_id}/messages
- POST /api/sessions/{session_id}/messages
- POST /api/agent/runs
- GET /api/agent/runs/{run_id}

主要组件：

- 左侧会话列表
- 中间聊天窗口
- 右侧订单/知识/工单信息面板
- 回复建议卡片
- 运行状态步骤条

### 6.5 知识库管理页

页面作用：

- 管理售后政策、商品说明、物流说明、投诉处理规范等知识文档

主要数据：

- 文档标题
- 文档类型
- 文档内容
- chunk 数量
- 启用状态
- 创建时间

调用 API：

- GET /api/knowledge/documents
- GET /api/knowledge/documents/{document_id}
- POST /api/knowledge/documents
- PUT /api/knowledge/documents/{document_id}
- POST /api/knowledge/documents/{document_id}/rebuild-chunks
- GET /api/knowledge/search

主要组件：

- 文档列表
- 文档编辑器
- Chunk 预览
- 检索测试框

### 6.6 人工审核页

页面作用：

- 处理需要人工确认的回复建议或售后决策

主要数据：

- 审核任务标题
- 用户消息
- Agent 建议
- 风险原因
- 审核状态
- 审核人
- 审核意见

调用 API：

- GET /api/review-tasks
- GET /api/review-tasks/{task_id}
- POST /api/review-tasks/{task_id}/approve
- POST /api/review-tasks/{task_id}/reject

主要组件：

- 审核任务表格
- 审核详情抽屉
- 通过/驳回按钮
- 回复建议编辑框

### 6.7 售后工单页

页面作用：

- 跟踪退货、退款、投诉等售后事项

主要数据：

- 工单编号
- 工单类型
- 关联订单
- 用户
- 状态
- 优先级
- 处理人
- 创建时间
- 最新处理备注

调用 API：

- GET /api/tickets
- GET /api/tickets/{ticket_id}
- POST /api/tickets
- PUT /api/tickets/{ticket_id}
- POST /api/tickets/{ticket_id}/status

主要组件：

- 工单表格
- 状态筛选
- 工单详情抽屉
- 处理记录时间线

### 6.8 Agent 运行日志页

页面作用：

- 展示每次 Agent 执行的节点链路
- 让项目具备可解释性和工程深度

主要数据：

- run_id
- 会话
- 用户消息
- 意图
- 运行状态
- 开始时间
- 结束时间
- 每个节点输入输出
- 错误信息

调用 API：

- GET /api/agent/runs
- GET /api/agent/runs/{run_id}
- GET /api/agent/runs/{run_id}/node-logs

主要组件：

- 运行记录表格
- 节点步骤条
- JSON 输入输出查看器
- 错误信息面板

## 7. MVP 范围

第一版目标：做小但完整，能演示一条从用户消息到 Agent 判断、回复建议、审核任务和工单的业务链路。

MVP 必做功能：

- Mock 用户、商品、订单、知识库数据
- 会话和消息保存
- Agent MVP 工作流
- 意图识别：商品咨询、订单查询、物流查询、退货申请、退款申请、投诉
- 简单知识库检索
- 售后规则判断
- 风险判断
- 回复建议生成
- 人工审核任务创建
- 售后工单创建
- Agent 运行日志保存
- 前端 Dashboard、客服会话、人工审核、工单、运行日志页面

MVP 演示场景：

用户输入：

> 我买的耳机有杂音，可以退货吗？

系统流程：

1. 保存用户消息
2. 识别意图为退货申请
3. 查询用户最近购买的耳机订单
4. 检索“7 天无理由退货”和“质量问题退货”政策
5. 判断签收时间、商品状态和售后规则
6. 识别为质量问题售后，建议可申请退货
7. 因涉及退货和可能退款，创建人工审核任务
8. 创建售后工单
9. 生成客服回复建议
10. 前端展示 Agent 结果、审核任务、工单和节点日志

## 8. 非 MVP 加分项

- 接入真实 LLM Provider，并保留 Mock LLM fallback
- 使用 LangGraph 实现可视化或可配置工作流
- 向量数据库替代 SQLite 简单检索
- RAG 引用来源高亮
- 客服质检评分
- 多轮对话上下文记忆
- 用户画像和风险标签
- 工单 SLA 超时提醒
- JWT 登录与 RBAC 权限
- Docker Compose 一键启动
- OpenAPI 文档截图写入 README

