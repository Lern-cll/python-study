<template>
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

const userStore = useUserStore()

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