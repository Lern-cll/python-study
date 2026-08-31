入口 main.py
 ├─ conf/            ← 配置、env、logger、MCP 配置
 ├─ controllers/     ← FastAPI Router 层（按域拆包）
 ├─ middleware/      ← 跨域上下文（HttpRequestContext）
 ├─ entitys/         ← Pydantic 入参/出参 DTO
 ├─ service/         ← 业务逻辑层（LLM Chain、Prompt、Agent）
 │   ├─ agent_execute/  ← LangChain Chain 编排
 │   ├─ robot/          ← 对话/Robot 业务流程
 │   ├─ prompt_service/ ← Prompt 模板驱动服务
 │   └─ quality_inspection/ ← 质检
 ├─ websocket_service/  ← WebSocket 消息中心
 ├─ mcp_client/        ← MCP 工具接入
 ├─ po/             ← SQLAlchemy ORM 持久化, models层
 ├─ async_task/     ← 异步任务
 ├─ utils/          ← 通用工具
 ├─ doc/            ← SQL 脚本、docker-compose、prompt markdown、法律 PDF
 └─ templates/      ← 简易前端（index.html + jQuery）