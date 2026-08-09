<template>
  <!-- 单条浏览历史：左缩略图 + 右标题/描述/作者/浏览时间/阅读量 + 右侧「删除」按钮 -->
  <div class="history-item" @click="handleRowClick">
    <!-- 左侧缩略图 -->
    <div class="thumb" :class="{ 'is-loading': !imageLoaded }">
      <img
        v-show="imageLoaded"
        :src="item.image"
        :alt="item.title"
        @load="onImageLoad"
        @error="onImageError"
      />
      <!-- 加载占位 -->
      <div v-if="!imageLoaded" class="thumb-placeholder">
        <el-icon class="is-loading"><Loading /></el-icon>
      </div>
    </div>

    <!-- 右侧主体 -->
    <div class="body">
      <h3 class="title text-ellipsis-2">{{ item.title }}</h3>
      <p class="desc text-ellipsis-2">{{ item.description }}</p>
      <p class="author text-ellipsis-1">{{ item.author || '头条号' }}</p>
      <p class="meta">
        <span class="view-time">浏览时间：{{ formatViewTime(item.view_time) }}</span>
        <span class="views">
          <el-icon><View /></el-icon>
          {{ formatViews(item.views) }}
        </span>
      </p>
    </div>

    <!-- 右侧操作区：阻止冒泡，避免触发整行跳转 -->
    <div class="actions" @click.stop>
      <el-button text type="danger" size="small" @click="handleDeleteClick">
        删除
      </el-button>
    </div>
  </div>
</template>

<script setup>
// 单条浏览历史项
// 布局：左缩略图 + 右侧（标题/描述/作者/浏览时间/阅读量）+ 右侧「删除」按钮
// 交互：整行点击跳转新闻详情；删除按钮单独触发删除事件
import { ref } from 'vue'
import { View, Loading } from '@element-plus/icons-vue'

// 接收父组件传入的历史记录数据
const props = defineProps({
  // 单条历史记录（含 id/title/description/image/author/views/view_time）
  item: {
    type: Object,
    required: true
  }
})

// 向父组件抛出事件：click 跳转详情、delete 删除单条
const emit = defineEmits(['click', 'delete'])

// 缩略图是否已加载完成（用于占位图与真实图的切换）
const imageLoaded = ref(false)

// 图片加载成功：隐藏占位图、显示真实图
const onImageLoad = () => {
  imageLoaded.value = true
}

// 图片加载失败：同样隐藏占位图，避免无限 loading
const onImageError = () => {
  imageLoaded.value = true
}

// 整行点击：通知父组件跳转新闻详情
const handleRowClick = () => {
  emit('click')
}

// 删除按钮点击：通知父组件删除本条历史
const handleDeleteClick = () => {
  emit('delete')
}

// 格式化浏览时间为 yyyy-MM-dd HH:mm
// @param time - ISO 时间字符串
// @returns 格式化后的字符串；非法时间返回空
const formatViewTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  if (Number.isNaN(date.getTime())) return ''
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

// 格式化阅读量，超过 1 万显示为「X.X万」
// @param views - 原始阅读量
// @returns 数字或带「万」单位的字符串
const formatViews = (views) => {
  const n = Number(views) || 0
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`
  return n
}
</script>

<style lang="scss" scoped>
.history-item {
  display: flex;
  align-items: stretch;
  padding: 15px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  gap: 12px;

  // 左侧缩略图
  .thumb {
    width: 90px;
    height: 70px;
    border-radius: 6px;
    overflow: hidden;
    flex-shrink: 0;
    background: #f0f0f0;
    position: relative;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: opacity 0.3s ease;
    }

    // 图片加载占位
    .thumb-placeholder {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f0f0f0;
      color: #ccc;
      font-size: 20px;
    }
  }

  // 右侧主体
  .body {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;

    // 标题：2 行省略
    .title {
      font-size: 1rem;
      line-height: 1.4;
      color: #333;
      margin: 0 0 6px;
      font-weight: 600;
    }

    // 描述：2 行省略
    .desc {
      font-size: 0.8125rem;
      line-height: 1.4;
      color: #666;
      margin: 0 0 6px;
    }

    // 作者：单行省略
    .author {
      font-size: 0.8125rem;
      line-height: 1.4;
      color: #888;
      margin: 0 0 6px;
    }

    // 元信息行：浏览时间 + 阅读量
    .meta {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.75rem;
      color: #999;
      margin: 0;

      // 阅读量
      .views {
        display: flex;
        align-items: center;
        flex-shrink: 0;

        .el-icon {
          margin-right: 3px;
          font-size: 12px;
        }
      }
    }
  }

  // 右侧操作区
  .actions {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-left: 4px;
  }
}

// 单行省略
.text-ellipsis-1 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

// 两行省略
.text-ellipsis-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
