<template>
  <div class="main-layout">
    <div class="main-content">
      <!-- router-view + transition + keep-alive 组合：
           transition 提供路由切换动画，keep-alive 缓存标记 keepAlive 的子路由 -->
      <router-view v-slot="{ Component, route }">
        <transition name="slide" mode="out-in">
          <keep-alive :include="cachedViews">
            <component :is="Component" :key="route.fullPath" />
          </keep-alive>
        </transition>
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

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s, opacity 0.3s;
}

.slide-enter-from {
  transform: translateX(30px);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(-30px);
  opacity: 0;
}
</style>