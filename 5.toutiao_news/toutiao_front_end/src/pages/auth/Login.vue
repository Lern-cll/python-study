<template>
  <div class="login-page">
    <div class="header">
      <el-icon @click="router.back()"><ArrowLeft /></el-icon>
    </div>
    <div class="form-container">
      <h1 class="title">登录</h1>
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

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    await userStore.login(form)
    ElMessage.success('登录成功')
    const redirect = router.currentRoute.value.query.redirect || '/home'
    router.replace(redirect)
  } catch (e) {
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
  background: #fff;

  .header {
    padding: 12px 15px;

    .el-icon {
      font-size: 20px;
      cursor: pointer;
    }
  }

  .form-container {
    padding: 40px 30px;

    .title {
      font-size: 1.5rem;
      font-weight: 700;
      color: #333;
      margin-bottom: 30px;
    }

    .el-form {
      :deep(.el-form-item) {
        margin-bottom: 20px;
      }

      :deep(.el-input) {
        .el-input__wrapper {
          padding: 12px 15px;
        }
      }
    }

    .footer {
      text-align: center;
      font-size: 0.875rem;
      color: #999;
      margin-top: 20px;

      .link {
        color: #e63946;
        margin-left: 5px;
        cursor: pointer;
      }
    }
  }
}
</style>