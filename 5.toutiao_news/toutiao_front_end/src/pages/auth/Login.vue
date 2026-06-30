<template>
  <div class="login-page">
    <!-- 顶部：返回箭头 -->
    <div class="header">
      <el-icon @click="router.back()"><ArrowLeft /></el-icon>
    </div>
    <div class="form-container">
      <!-- 品牌区：Logo + 应用名 -->
      <div class="brand">
        <div class="avatar">
          <img :src="defaultAvatar" alt="avatar" />
        </div>
        <h1 class="title">新闻资讯</h1>
      </div>
      <!-- 登录表单：用户名 / 密码 -->
      <el-form ref="formRef" :model="form" :rules="rules">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        <el-form-item>
          <BaseButton type="primary" :loading="loading" block @click="handleLogin">
            登录
          </BaseButton>
        </el-form-item>
      </el-form>
      <!-- 测试账号提示 -->
      <div class="test-account">
        <p>测试账号：admin</p>
        <p>测试密码：123456</p>
      </div>
      <!-- 底部：跳转注册 -->
      <div class="footer">
        <span>还没有账号？</span>
        <span class="link" @click="router.push('/register')">立即注册</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/pinia/userStore'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import BaseButton from '@/components/BaseButton.vue'
import defaultAvatar from '@/assets/imgs/photo.jpeg'

const router = useRouter()
const userStore = useUserStore()

// 表单实例引用（用于调用 validate 进行校验）
const formRef = ref(null)
// 提交按钮的 loading 状态
const loading = ref(false)
// 表单数据：用户名、密码
const form = reactive({
  username: '',
  password: ''
})

// 表单字段校验规则
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

/**
 * 提交登录：先校验表单 → 调 userStore.login → 成功后跳 redirect 或首页
 * redirect 来源：路由守卫在拦截未登录访问时写入 query.redirect
 */
const handleLogin = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    await userStore.login(form)
    ElMessage.success('登录成功')
    const redirect = router.currentRoute.value.query.redirect || '/home'
    router.replace(redirect)
  } catch (e) {
    // el-form 校验失败回调 reject(false)，不弹错误
    if (e !== false) {
      ElMessage.error('登录失败')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: #f5f5f5;

  .header {
    background: linear-gradient(135deg, #e63946 0%, #c62b36 100%);
    padding: 12px 15px;

    .el-icon {
      font-size: 20px;
      color: #fff;
      cursor: pointer;
    }
  }

  .form-container {
    padding: 30px 30px 20px;

    .brand {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 24px;

      .avatar {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        overflow: hidden;
        border: 3px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 4px 12px rgba(230, 57, 70, 0.3);

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
      }

      .title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #333;
        margin-top: 12px;
        margin-bottom: 0;
      }
    }

    .el-form {
      :deep(.el-form-item) {
        margin-bottom: 16px;
      }

      :deep(.el-input) {
        .el-input__wrapper {
          padding: 10px 15px;
          background: #fff;
          border-radius: 8px;
        }
      }

      :deep(.el-button) {
        height: 44px;
        font-size: 1rem;
        border-radius: 22px;
      }
    }

    .test-account {
      text-align: center;
      font-size: 0.8125rem;
      color: #999;
      margin: 16px 0 12px;

      p {
        margin: 4px 0;
      }
    }

    .footer {
      text-align: center;
      font-size: 0.875rem;
      color: #999;

      .link {
        color: #e63946;
        margin-left: 5px;
        cursor: pointer;
      }
    }
  }
}
</style>