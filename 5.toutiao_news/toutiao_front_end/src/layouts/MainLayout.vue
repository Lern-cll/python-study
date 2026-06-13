<template>
  <div class="main-layout">
    <div class="main-content">
      <router-view v-slot="{ Component, route }">
        <transition name="slide" mode="out-in">
          <keep-alive :include="cachedViews">
            <component :is="Component" :key="route.fullPath" />
          </keep-alive>
        </transition>
      </router-view>
    </div>
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

const tabs = [
  { path: '/home', label: '首页', icon: HomeFilled },
  { path: '/ai-chat', label: 'AI问答', icon: ChatDotRound },
  { path: '/mine', label: '我的', icon: User, requiresAuth: true }
]

const currentPath = computed(() => route.path)

// 需要被 keep-alive 缓存的组件名（取自路由的 name 字段）
const cachedViews = computed(() => {
  return router.getRoutes()
    .filter((r) => r.meta?.keepAlive && r.name)
    .map((r) => r.name)
})

// 详情页等子路由通过 meta.hideTabBar 隐藏底部 TabBar
const hideTabBar = computed(() => Boolean(route.meta?.hideTabBar))

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