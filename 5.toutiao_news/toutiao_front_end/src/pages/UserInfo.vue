<template>
  <div class="user-info-page">
    <div class="header">
      <el-icon @click="router.back()"><ArrowLeft /></el-icon>
      <span>个人信息</span>
    </div>
    <div class="content">
      <el-form label-position="top">
        <el-form-item label="头像">
          <div class="avatar-upload">
            <div class="avatar-preview">
              <img v-if="form.avatar" :src="form.avatar" alt="avatar" />
              <el-icon v-else :size="40"><User /></el-icon>
            </div>
            <el-button size="small">更换头像</el-button>
          </div>
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" block @click="handleSave">
            保存修改
          </el-button>
        </el-form-item>
      </el-form>

      <div class="divider"></div>

      <div class="password-section">
        <h3>修改密码</h3>
        <el-form label-position="top">
          <el-form-item label="旧密码">
            <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入旧密码" show-password />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="warning" :loading="passwordSaving" block @click="handleChangePassword">
              修改密码
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/pinia/userStore'
import { ArrowLeft, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const saving = ref(false)
const passwordSaving = ref(false)
const form = reactive({
  nickname: '',
  email: '',
  phone: '',
  avatar: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: ''
})

onMounted(() => {
  if (userStore.userInfo) {
    Object.assign(form, userStore.userInfo)
  }
})

const handleSave = async () => {
  try {
    saving.value = true
    await userStore.updateUserInfo(form)
    ElMessage.success('修改成功')
  } catch (e) {
    ElMessage.error('修改失败')
  } finally {
    saving.value = false
  }
}

const handleChangePassword = async () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    passwordSaving.value = true
    await userStore.changePassword(passwordForm)
    ElMessage.success('密码修改成功')
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
  } catch (e) {
    ElMessage.error('密码修改失败')
  } finally {
    passwordSaving.value = false
  }
}
</script>

<style lang="scss" scoped>
.user-info-page {
  min-height: 100vh;
  background: #f5f5f5;

  .header {
    display: flex;
    align-items: center;
    padding: 12px 15px;
    background: #fff;
    border-bottom: 1px solid #f0f0f0;

    .el-icon {
      font-size: 20px;
      cursor: pointer;
    }

    span {
      flex: 1;
      text-align: center;
      font-size: 1rem;
      font-weight: 600;
    }
  }

  .content {
    padding: 15px;

    .el-form {
      background: #fff;
      padding: 15px;
      border-radius: 8px;

      :deep(.el-form-item) {
        margin-bottom: 20px;
      }
    }

    .avatar-upload {
      display: flex;
      align-items: center;
      gap: 15px;

      .avatar-preview {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: #f0f0f0;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
      }
    }

    .divider {
      height: 10px;
    }

    .password-section {
      background: #fff;
      padding: 15px;
      border-radius: 8px;

      h3 {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 15px;
      }
    }
  }
}
</style>