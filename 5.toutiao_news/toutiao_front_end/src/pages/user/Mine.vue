<template>
  <div class="mine-page">
    <!-- 顶部用户信息卡：未登录时显示默认头像和"未登录" -->
    <div class="user-header">
      <div class="user-info" @click="handleUserInfo">
        <div class="avatar">
          <img :src="userInfo?.avatar || defaultAvatar" alt="avatar" />
        </div>
        <div class="info">
          <div class="nickname">{{ userInfo?.nickname || userInfo?.username || '未登录' }}</div>
          <div class="desc">点击查看个人信息</div>
        </div>
        <el-icon><ArrowRight /></el-icon>
      </div>
    </div>

    <!-- 第一组菜单：我的收藏、浏览历史 -->
    <div class="menu-section">
      <div class="menu-item" @click="router.push('/favorites')">
        <el-icon><Star /></el-icon>
        <span>我的收藏</span>
        <el-icon><ArrowRight /></el-icon>
      </div>
      <div class="menu-item" @click="router.push('/history')">
        <el-icon><Clock /></el-icon>
        <span>浏览历史</span>
        <el-icon><ArrowRight /></el-icon>
      </div>
    </div>

    <!-- 第二组菜单：个人设置 -->
    <div class="menu-section">
      <div class="menu-item" @click="router.push('/user-info')">
        <el-icon><Setting /></el-icon>
        <span>个人设置</span>
        <el-icon><ArrowRight /></el-icon>
      </div>
    </div>

    <!-- 底部按钮：根据登录态切换「退出登录 / 登录注册」 -->
    <div class="logout-section" v-if="isLoggedIn">
      <el-button type="danger" plain class="logout-btn" @click="handleLogout">
        退出登录
      </el-button>
    </div>
    <div class="login-section" v-else>
      <el-button type="primary" class="login-btn" @click="router.push('/login')">
        登录 / 注册
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/pinia/userStore'
import { User, ArrowRight, Star, Clock, Setting } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import defaultAvatar from '@/assets/imgs/photo.jpeg'

const router = useRouter()
const userStore = useUserStore()

// 当前用户信息（来自 store）
const userInfo = computed(() => userStore.userInfo)
// 是否已登录
const isLoggedIn = computed(() => userStore.isLoggedIn)

/**
 * 点击用户信息卡：
 * - 未登录：跳登录页
 * - 已登录：先调 /user/info 拉取最新用户信息（保证展示的是后端最新数据），
 *          成功后再跳个人设置页；失败由响应拦截器统一处理（401 会清 token 并跳登录）
 */
const handleUserInfo = async () => {
  if (!isLoggedIn.value) {
    router.push('/login')
    return
  }
  try {
    await userStore.fetchUserInfo()
    router.push('/user-info')
  } catch (e) {
    // 401 等异常已在 axios 响应拦截器中统一处理（弹错误并跳登录）
  }
}

/**
 * 退出登录：二次确认后清空 store 状态并跳转登录页
 */
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    userStore.logout()
    router.push('/login')
  } catch (e) {
    // 取消操作
  }
}
</script>

<style lang="scss" scoped>
.mine-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 20px;

  .user-header {
    background: linear-gradient(135deg, #e63946 0%, #c62b36 100%);
    padding: 30px 15px;

    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;

      .avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .el-icon {
          color: #fff;
        }
      }

      .info {
        flex: 1;
        margin-left: 15px;

        .nickname {
          font-size: 1.125rem;
          font-weight: 600;
          color: #fff;
          margin-bottom: 5px;
        }

        .desc {
          font-size: 0.75rem;
          color: rgba(255, 255, 255, 0.8);
        }
      }

      .el-icon {
        color: rgba(255, 255, 255, 0.6);
      }
    }
  }

  .menu-section {
    background: #fff;
    margin-top: 10px;

    .menu-item {
      display: flex;
      align-items: center;
      padding: 15px;
      border-bottom: 1px solid #f0f0f0;
      cursor: pointer;

      &:last-child {
        border-bottom: none;
      }

      .el-icon:first-child {
        color: #666;
        margin-right: 12px;
      }

      span {
        flex: 1;
        font-size: 0.9375rem;
        color: #333;
      }

      .el-icon:last-child {
        color: #ccc;
      }
    }
  }

  .logout-section,
  .login-section {
    padding: 20px 15px;

    .logout-btn,
    .login-btn {
      width: 100%;
    }
  }
}
</style>