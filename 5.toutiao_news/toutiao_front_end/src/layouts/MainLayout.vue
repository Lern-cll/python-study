<template>
  <div class="main-layout">
    <div class="main-content">
      <!-- router-view + keep-alive + key 组合：
           - keep-alive 按路由 meta.keepAlive 缓存组件，保留滚动位置 / 表单状态等，
             实现"用户访问哪里，再次进入还是在哪里"；
           - :key="route.fullPath" 强制每次切换重建组件实例，
             避免在某些边界条件下（如重复跳转同一 fullPath）路由切换后 router-view 空白；
           - 注意：keep-alive 只缓存 include 命中的页面（当前只有 Home），
             未命中的页面（如 NewsDetail）走 fallthrough 渲染、不缓存，行为不变。 -->
      <router-view v-slot="{ Component, route }">
        <keep-alive :include="cachedViews">
          <component :is="Component" :key="route.fullPath" />
        </keep-alive>
      </router-view>
    </div>
    <!-- 详情页等通过路由 meta.hideTabBar 隐藏底部 TabBar -->
    <div v-if="!hideTabBar" class="main-tabbar">
      <div
        v-for="tab in tabs"
        :key="tab.path"
        :class="['tab-item', { active: currentPath === tab.path }]"
        @click="handleTabClick(tab)"
      >
        <el-icon :size="22">
          <component :is="tab.icon" />
        </el-icon>
        <span class="tab-label">{{ tab.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HomeFilled, ChatDotRound, User } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 底部 Tab 配置：path 为跳转地址，icon 为图标组件，requiresAuth 表示是否需要登录
const tabs = [
  { path: '/home', label: '首页', icon: HomeFilled },
  { path: '/ai-chat', label: 'AI问答', icon: ChatDotRound },
  { path: '/mine', label: '我的', icon: User, requiresAuth: true }
]

// 当前路由路径（用于高亮当前 Tab）
const currentPath = computed(() => route.path)

// 需要被 keep-alive 缓存的组件名（取自路由的 name 字段 + meta.keepAlive）
const cachedViews = computed(() => {
  return router.getRoutes()
    .filter((r) => r.meta?.keepAlive && r.name)
    .map((r) => r.name)
})

// 详情页等子路由通过 meta.hideTabBar 隐藏底部 TabBar
const hideTabBar = computed(() => Boolean(route.meta?.hideTabBar))

/**
 * 点击底部 Tab：未登录且目标 Tab 需要登录则跳登录页，否则正常跳转
 * @param tab - 被点击的 Tab 配置对象
 */
const handleTabClick = (tab) => {
  if (tab.requiresAuth && !localStorage.getItem('toutiao_token')) {
    router.push('/login')
    return
  }
  router.push(tab.path)
}
</script>

<style lang="scss" scoped>
.main-layout {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;

  .main-content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
  }

  .main-tabbar {
    display: flex;
    justify-content: space-around;
    align-items: center;
    height: 50px;
    background: #fff;
    border-top: 1px solid #e8e8e8;
    padding-bottom: env(safe-area-inset-bottom);

    .tab-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      flex: 1;
      color: #999;
      cursor: pointer;
      transition: color 0.3s;

      &.active {
        color: #e63946;
      }

      .tab-label {
        font-size: 0.625rem;
        margin-top: 2px;
      }
    }
  }
}


</style>