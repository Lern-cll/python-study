# 浏览历史页面修复 Spec

## 背景与目标

浏览历史页 `http://localhost:3000/history` 目前缺少与首页、收藏页一致的下拉刷新和触底自动加载体验。同时列表项渲染逻辑依赖 `NewsItem`，但 mock 数据为平铺结构，导致渲染异常，且未按业务需求展示 `view_time` 字段。

本次修复目标：

1. 接入与 `FavoriteList.vue` 一致的下拉刷新 + 触底自动加载交互。
2. 独立渲染列表项，准确展示 `title / description / image / author / views / view_time`。
3. 单条删除 + 一键清空操作在移动端可正常使用。

## 范围

### 包含

- 新增 `src/pages/user/HistoryItem.vue` 单条渲染组件
- 重构 `src/pages/user/HistoryList.vue` 接入下拉刷新 + 触底自动加载
- 列表项使用 mock 数据 `src/mock/test.json` 的字段结构

### 不包含

- 不修改 `src/api/history.ts`
- 不修改 `src/components/NewsItem.vue`（首页/收藏页继续使用）
- 不引入新依赖（无 swr / vueuse / better-scroll 等）
- 不做"长按删除"、"按时间分组"、"失效链接置灰"等扩展
- 不做后端接口实现

## 用户场景

### 主场景

1. 用户登录后从「我的」页进入浏览历史页
2. 看到按时间倒序的历史记录列表
3. 列表顶部下拉可刷新，回到第一页
4. 列表滚到底部自动加载下一页
5. 点击单条进入对应新闻详情
6. 点击右侧「删除」移除单条历史
7. 点击 header「清空」二次确认后清空所有历史

### 边界场景

- 列表为空：显示「暂无浏览记录」空态
- `hasMore = false`：触底不再触发加载
- 接口失败：toast 提示，保留原列表
- 401 Token 过期：由 `request.ts` 拦截器跳登录页

## 功能清单

### HistoryList.vue 改造

- 新增滚动容器 `.news-scroll`，绑定 `@scroll @touchstart @touchmove @touchend`
- 新增下拉刷新头部 `.pull-refresh`，高度随 `pullDistance` 展开
- 新增触底自动加载，去重 + 500ms 节流
- `fetchList(reset)` 统一管理 list / page / total / hasMore
- header「清空」按钮在 `list.length > 0` 时显示
- 单条点击 → `router.push(/news/:item.id)`
- 单条删除 → `deleteHistory(id)` → 从 list 过滤
- 清空全部 → `ElMessageBox.confirm` → `clearHistory()` → `list = []`

### HistoryItem.vue 新增

- 布局：左缩略图 + 右标题/作者/浏览时间/阅读量 + 右侧「删除」按钮
- props：`item`（必传）
- emits：`click` / `delete`
- 内部实现：图片懒加载占位、`view_time` 友好时间格式化、`views` 万单位格式化

## 字段映射

| mock 字段 | HistoryItem 展示位置 |
|---|---|
| `image` | 左侧 90×70 圆角缩略图 |
| `title` | 标题，2 行省略 |
| `author` | 副标题，单行省略 |
| `view_time` | 元信息「浏览时间：YYYY-MM-DD HH:mm」 |
| `views` | 元信息阅读量（带 View 图标，≥1 万显示 X.X 万） |
| `id` | 整行点击跳转 / 右侧删除依据 |

不展示 `publishTime / categoryId`；`description` 展示为 2 行省略描述（与 NewsItem 一致）。

注：因 mock 数据平铺且字段名为 `description`（非 `desc`），HistoryItem 直接读取 `item.description`。

## 约束条件

- 风格与 `FavoriteList.vue` 一致（header、滚动容器、下拉刷新样式、间距）
- 阈值与 FavoriteList 保持一致：`threshold = 60`、`maxDistance = 100`、触底判定 `< 80`
- 不复用 `NewsItem.vue`，避免影响首页/收藏页现有展示
- 不引入 pinia store，历史数据为页面级状态
- `HistoryItem.vue` 内部不持有业务状态，仅做展示和事件转发

## 验收标准

1. 进入 `http://localhost:3000/history`，展示 mock 数据 3 条，每条含 title / description / image / author / views / view_time
2. 列表为空时显示「暂无浏览记录」空态
3. 顶部下拉 ≥60px 松手 → 触发刷新，列表回到第一页
4. 列表未到底部时滚动 → 不触发加载
5. `hasMore = false` 时触底不触发加载
6. 点击单条 → 跳转 `/news/:id` 详情页
7. 点击「删除」按钮 → 该条从列表中移除 + toast「删除成功」
8. 点击「删除」时不会触发整行跳转
9. 点击「清空」→ 二次确认 → 列表清空 + toast
10. `list.length === 0` 时「清空」按钮不显示
11. 接口失败时显示对应错误 toast，原列表保留
12. 401 Token 过期自动跳转登录

## 风险与开放问题

### 风险

- mock 数据量小（仅 3 条，`hasMore = false`），触底加载路径无法在本地充分验证。需通过后端真实接口或临时调整 mock 数据验证。
- 浏览器 DevTools 移动端模拟与真机滚动行为可能略有差异，下拉刷新手感需在真机复核。

### 开放问题

- 无新增开放问题。
