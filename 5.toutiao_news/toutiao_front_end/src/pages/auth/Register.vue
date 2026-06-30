<template>
  <div class="register-page">
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
      <!-- 注册表单：用户名 / 密码 / 确认密码 -->
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
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请确认密码"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        <el-form-item>
          <BaseButton type="primary" :loading="loading" block @click="handleRegister">
            注册
          </BaseButton>
        </el-form-item>
      </el-form>
      <!-- 底部：跳转登录 -->
      <div class="footer">
        <span>已有账号？</span>
        <span class="link" @click="router.push('/login')">去登录</span>
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
// 表单数据：用户名、密码、确认密码
const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

/**
 * Element Plus 自定义校验器：确认密码必须与密码一致
 * @param rule - 校验规则（未使用）
 * @param value - 当前输入框的值（confirmPassword）
 * @param callback - 校验完成回调
 */
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 表单字段校验规则
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

/**
 * 提交注册：先校验表单 → 调 userStore.register → 成功跳转首页
 * 失败统一弹错误提示；表单校验失败由 el-form 自行展示
 */
const handleRegister = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    // 接口只接收 username/password，从表单中拆出 confirmPassword
    const { confirmPassword, ...registerData } = form
    await userStore.register(registerData)
    ElMessage.success('注册成功')
    router.replace('/home')
  } catch (e) {
    // el-form 校验失败回调 reject(false)，不需要提示错误
    if (e !== false) {
      ElMessage.error('注册失败')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.register-page {
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