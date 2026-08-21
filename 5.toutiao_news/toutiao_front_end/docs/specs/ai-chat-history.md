# AI 问答历史会话 Spec

## 背景与目标

当前 `/ai-chat` 页面存在以下问题：

1. 切到其它底部 tab 再切回 AI 问答，本次对话内容丢失（AiChat 组件被卸载重建，messages 仅在页面 local state）。
2. 没有"会话历史"概念，无法回看之前与 AI 聊过的话题、也无法在历史会话基础上继续问。
3. 用户每次只能在一个"匿名会话"里聊天，无法在多个话题间切换。

本次目标：

1. **pinia 持久化当前会话**：把 messages 从页面 local state 移到 pinia store，切 tab 不丢。
2. **后端持久化历史会话**：新建 `ai_chat_session` 表 + 5 个 REST 接口，按用户存储完整消息数组。
3. **侧边栏历史抽屉**：在 AiChat 页面加左侧抽屉，展示历史会话列表，支持搜索（title + messages 全文）、查看详情、继续对话、删除单条。
4. **"+ 新会话"按钮**：在输入区右下角加圆形 Plus 按钮，点击清空当前 pinia 状态、开始新会话。

## 范围

### 包含

**后端（`toutiao_back_end`）**
- 新增 `models/ai_chat_session.py`（SQLAlchemy ORM 模型）
- 新增 `schemas/ai_chat.py`（Pydantic 请求/响应模型）
- 新增 `crud/ai_chat.py`（CRUD 函数）
- 新增 `routers/ai_chat.py`（5 个 REST 路由）
- 在 `main.py` 中 `app.include_router(ai_chat.router)`
- 更新 `物料文件/database.sql`（新增 DDL）
- 更新 `物料文件/API接口规范文档.md`（新增"AI 问答会话模块"章节）

**前端（`toutiao_front_end`）**
- 新增 `src/pinia/aiChatStore.ts`（Pinia store）
- 新增 `src/api/aiChat.ts`（5 个 REST 接口封装）
- 扩展 `src/api/ai.ts`（保留 `chat()`，不与新 store 冲突）
- 重构 `src/pages/ai/AiChat.vue`（接入 store、加抽屉、加 + 按钮）
- 修改 `src/router/index.ts`（`/ai-chat` 路由 `requiresAuth: true`）

### 不包含

- localStorage 草稿兜底（pinia + 后端已覆盖崩溃恢复场景）
- 会话重命名（手动改 title）
- AI 自动总结标题
- 软删除 / `is_deleted` 字段
- 列表项 active 状态高亮
- 流式输出（保留现有非流式 `chat()` 调用）
- 消息按 token 数截断
- 列表项置顶 / 收藏
- 跨设备实时同步（依赖后端 GET 拉取即可）

## 用户场景

### 主场景

1. 用户登录后进入 AI 问答页
2. 输入"红烧肉的做法是什么" → 点发送 → AI 回复 → 此时 `POST /api/ai-chat/sessions` 落库
3. 继续问"不放酱油可以吗" → AI 回复 → 此时 `PUT /api/ai-chat/sessions/:id` 更新
4. 切到"首页"tab 再切回 AI 问答 → 历史对话仍在（pinia 持久化）
5. 点击标题右侧的 Memo 图标 → 左侧滑出抽屉，展示历史会话列表（按 updated_at 倒序）
6. 在抽屉搜索框输入"红烧肉" → 列表过滤为最多 5 条匹配项（命中 title 或 messages 任意一条）
7. 点击某条历史会话 → 抽屉关闭，对话区加载完整 messages，可以继续问（下次 AI 回成功 → 更新该会话）
8. 在某条历史项上左滑 / 长按 → 弹出确认 → 删除该条 → 列表移除该项

### 边界场景

- 切 tab 时 AI 仍在思考（isTyping=true）→ 切回后状态保留，继续等待
- 切 tab 时 AI 失败未入库 → 切回后 pinia 仍有该轮消息（不丢），下次发送时按"未入库会话"逻辑处理（见约束条件）
- 抽屉打开时点列表项 → 自动关闭抽屉再加载
- 抽屉打开时点 + 按钮（如果未来扩展到此）→ 关闭抽屉 + 清空 pinia（v1 不在抽屉加 + 按钮，仅在输入区有 +）
- 侧边栏搜索关键词为空 → 走普通列表（分页 10 条 / 页），不走搜索接口
- 侧边栏搜索接口失败 → toast 提示，列表保留原数据
- 用户未登录访问 `/ai-chat` → 跳登录页（`requiresAuth: true` + router guard）
- 后端接口 401 → `request.ts` 拦截器跳登录页

## 功能清单

### 后端

#### DDL（`database.sql` 新增）

```sql
CREATE TABLE IF NOT EXISTS `ai_chat_session` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NOT NULL,
  `title` VARCHAR(255) NOT NULL DEFAULT '',
  `model` VARCHAR(64) NOT NULL DEFAULT '',
  `messages` JSON NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_ai_chat_session_user_idx` (`user_id` ASC),
  INDEX `idx_user_updated` (`user_id` ASC, `updated_at` DESC),
  CONSTRAINT `fk_ai_chat_session_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI 会话表';
```

#### 5 个 REST 接口

所有接口都 `Depends(get_current_user)`，前缀 `/api/ai-chat`。

| 方法 | 路径 | 入参（Body / Query） | 出参 data |
|---|---|---|---|
| POST | `/sessions` | Body: `{model, messages: [{role, content}], title?}` | `{id, title, model, messages, createdAt, updatedAt}` |
| PUT | `/sessions/{id}` | Body: `{model, messages, title?}` | `{id, title, model, messages, createdAt, updatedAt}` |
| GET | `/sessions` | Query: `page=1&pageSize=10&keyword=`（keyword 缺省时走普通列表） | `{list:[{id,title,model,updatedAt,messageCount}], total, hasMore}` |
| GET | `/sessions/search` | Query: `keyword=&limit=5`（limit 上限 5） | `{list:[{id,title,updatedAt}], total}` |
| GET | `/sessions/{id}` | — | `{id, title, model, messages, createdAt, updatedAt}` |
| DELETE | `/sessions/{id}` | — | `{deletedCount}` |

> 备注：搜索接口 `limit` 上限硬编码为 5；普通列表 `pageSize` 默认 10，最大 100。`title` 在创建时由首条 user 消息截取 30 字符生成（前端已生成，后端不二次加工）。

### 前端

#### `aiChatStore`（新增）

状态：
- `messages: {type: 'user'|'ai', content: string}[]`
- `currentSessionId: number | null`（null 表示"未入库的新会话"）
- `isTyping: boolean`
- `drawerOpen: boolean`
- `searchKeyword: string`
- `sessionList: {id, title, model, updatedAt, messageCount}[]`
- `searchResults: {id, title, updatedAt}[]`
- `sessionListLoading: boolean`

action：
- `send(text)`：调 `chat()` → 成功后视 `currentSessionId` 是否为 null 决定 POST 或 PUT → 更新 messages、刷新 updatedAt
- `newChat()`：清空 messages、currentSessionId、searchKeyword
- `loadSession(id)`：GET `/sessions/:id` → 写入 messages + currentSessionId
- `deleteSession(id)`：DELETE → 从 sessionList 过滤
- `openDrawer()` / `closeDrawer()`：控制 drawerOpen
- `fetchSessionList(reset)`：GET `/sessions?page=&pageSize=`（普通列表）
- `searchSessions(keyword)`：GET `/sessions/search?keyword=&limit=5`（搜索列表）

#### AiChat.vue 重构

- 输入框右侧加 `<el-button circle><Plus/></el-button>` → 点击 `newChat()`
- 标题右侧加 `<el-icon @click="toggleDrawer"><Memo v-if="!drawerOpen"/><Close v-else/></el-icon>` → 切换 `drawerOpen`
- 抽屉内容：
  - 搜索框 `el-input`（v-model="searchKeyword"，@input 防抖 300ms 触发 `searchSessions`）
  - `searchKeyword` 为空 → 渲染 `sessionList`（v-infinite-scroll 触底加载更多）
  - `searchKeyword` 非空 → 渲染 `searchResults`（最多 5 条，不再分页）
  - 列表项：左滑/长按 → 弹 `ElMessageBox.confirm` → 确认后 `deleteSession(id)`
- 抽屉外层：80% 宽度、白色背景、右侧遮罩点击关闭

#### router/index.ts

```ts
{
  path: '/ai-chat',
  name: 'AiChat',
  component: AiChat,
  meta: { title: 'AI问答', requiresAuth: true }
}
```

## 约束条件

- 风格与现有 `HistoryList.vue` / `FavoriteList.vue` 一致（按钮、抽屉、消息框样式 token）
- 后端响应必须包 `{code, message, data}` 格式（与现有约定一致）
- messages 在 DB 中只存 `[{role, content}]`（不含 system），system prompt 由前端每次发送时组装
- `title` 在 POST 入库时由前端生成（首条 user 消息 `.slice(0, 30)`），后端不二次加工
- PUT 接口语义为"全量覆盖"：客户端始终发送完整 messages 数组，后端直接覆盖
- API base path 一律走 `/api/ai-chat/...`，不与 `/qwen` 千问代理混用
- 千问调用仍走前端 `/qwen` 代理（API key 仍在前端），后端不中转
- 错误统一通过 `request.ts` 拦截器 toast；401 跳登录页
- 不复用 `NewsItem.vue` / `FavoriteItem.vue`，列表项独立渲染（数据 schema 完全不同）
- 抽屉组件用 Element Plus `<el-drawer>`，自定义 `direction="ltr"` + `size="80%"` + `with-header="false"`

## 验收标准

### 后端

1. `database.sql` 新增 DDL 执行成功，表存在
2. `POST /api/ai-chat/sessions` 成功创建一条记录，返回 `id` 与 `createdAt`
3. `PUT /api/ai-chat/sessions/:id` 成功覆盖 messages，`updatedAt` 自动刷新
4. `GET /api/ai-chat/sessions` 返回按 `updated_at desc` 排序的列表，分页参数正确
5. `GET /api/ai-chat/sessions/search?keyword=红烧肉` 返回 ≤5 条命中（命中 title 或 messages）
6. `GET /api/ai-chat/sessions/:id` 返回完整会话
7. `DELETE /api/ai-chat/sessions/:id` 删除成功，再次 GET 返回 404
8. 所有接口未带 Authorization → 返回 401

### 前端

1. 进入 `/ai-chat`，未登录被跳转到 `/login`
2. 登录后进入，发消息并等 AI 回复 → 浏览器 DevTools Network 看到 `POST /api/ai-chat/sessions`
3. 继续发第二条 → AI 回复 → Network 看到 `PUT /api/ai-chat/sessions/:id`
4. 切到首页 tab 再切回 AI 问答 → messages 仍在（pinia 持久化）
5. 点击标题右侧 Memo 图标 → 抽屉从左侧滑入，列表展示历史会话
6. 在搜索框输入"红烧" → 列表立即过滤为 ≤5 条匹配项
7. 清空搜索框 → 列表恢复为分页列表，可下拉/触底加载更多
8. 点击列表某项 → 抽屉关闭，对话区加载该会话 messages，可继续问（下次 AI 回复后 PUT 到该 id）
9. 在某项上长按（或左滑）→ 弹"确定删除？" → 确认后该条从列表消失
10. 点击输入区右侧 + 圆按钮 → messages 清空、currentSessionId=null，可开始新会话
11. 抽屉打开时点击右侧遮罩 → 抽屉关闭
12. 抽屉打开时再次点击 Memo/Close 图标 → 抽屉关闭
13. AI 接口失败 → toast 提示，pinia 中保留用户已发的消息（不丢）

### API 文档

1. `物料文件/API接口规范文档.md` 新增"AI 问答会话模块"章节，含 6 个接口的完整文档（参考现有 favorite / history 章节格式）

## 风险与开放问题

### 风险

- messages JSON 字段大小：长对话（百轮以上）可能导致单行 TEXT 较大（但 TEXT 上限 64KB 远超日常单会话 10~30 轮消息体量，足够）
- 千问 API key 仍在前端：本期不变，与现有 AiChat.vue 一致
- 搜索 JSON LIKE 性能：MySQL JSON 路径模糊匹配在表行数 > 1000 后会变慢；目前单用户历史 < 200 条，可接受；后续可加 FULLTEXT 索引或迁移到 ES
- 抽屉使用 `<el-drawer>`：在移动端 webview 中的滑动体验与原生 drawer 有差异，需真机验证

### 开放问题

- 无新增开放问题。