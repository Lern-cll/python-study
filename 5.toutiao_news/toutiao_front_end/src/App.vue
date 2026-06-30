<template>
  <!-- 顶层 router-view：负责在路由切换时播放淡入淡出动画 -->
  <router-view v-slot="{ Component, route }">
    <transition name="fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/pinia/userStore'
import { getToken, isTokenExpired } from '@/utils/auth'

// 全局唯一的用户 Store 实例
const userStore = useUserStore()

/**
 * 应用挂载后：若本地存在有效 Token，则静默拉取最新用户信息
 * 用于实现「刷新页面保持登录态」
 */
onMounted(() => {
  // 初始化用户状态
  const token = getToken()
  if (token && !isTokenExpired()) {
    userStore.fetchUserInfo()
  }
})
</script>

<style lang="scss">
#app {
  width: 100%;
  height: 100%;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>