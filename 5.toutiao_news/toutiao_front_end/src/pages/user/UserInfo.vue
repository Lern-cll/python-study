<template>
  <div class="user-info-page">
    <!-- 顶部：返回 + 标题 -->
    <div class="header">
      <el-icon @click="router.back()"><ArrowLeft /></el-icon>
      <span>个人信息</span>
    </div>

    <!-- 基础信息列表 -->
    <div class="list-section">
      <div class="list-item" @click="showAvatarPicker = true">
        <span class="label">头像</span>
        <div class="value avatar-value">
          <img :src="form.avatar || defaultAvatar" alt="avatar" class="avatar-img" />
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
      <div class="list-item">
        <span class="label">用户名</span>
        <span class="value">{{ form.username || userInfo?.username || '-' }}</span>
      </div>
      <div class="list-item" @click="openNicknameEdit">
        <span class="label">昵称</span>
        <span class="value editable">
          {{ form.nickname || '测试用户' }}
          <el-icon><ArrowRight /></el-icon>
        </span>
      </div>
      <div class="list-item">
        <span class="label">性别</span>
        <span class="value">{{ genderLabel }}</span>
      </div>
      <div class="list-item">
        <span class="label">账号ID</span>
        <span class="value id-value">ID: {{ form.id || userInfo?.id || '-' }}</span>
      </div>
      <div class="list-item" @click="showBioEdit = true">
        <span class="label">个人简介</span>
        <span class="value editable">
          {{ form.bio || '这个人很懒，什么都没写' }}
          <el-icon><ArrowRight /></el-icon>
        </span>
      </div>
    </div>

    <!-- 安全设置：修改密码 -->
    <div class="list-section">
      <div class="list-item" @click="showPasswordDialog = true">
        <span class="label">修改密码</span>
        <span class="value editable">
          <el-icon><ArrowRight /></el-icon>
        </span>
      </div>
    </div>

    <!-- 昵称编辑弹窗 -->
    <el-dialog v-model="showNicknameEdit" title="编辑昵称" width="300px">
      <el-input v-model="tempNickname" placeholder="请输入昵称" />
      <template #footer>
        <el-button @click="showNicknameEdit = false">取消</el-button>
        <el-button type="primary" @click="saveNickname">确定</el-button>
      </template>
    </el-dialog>

    <!-- 简介编辑弹窗 -->
    <el-dialog v-model="showBioEdit" title="编辑个人简介" width="300px">
      <el-input v-model="tempBio" placeholder="请输入个人简介" />
      <template #footer>
        <el-button @click="showBioEdit = false">取消</el-button>
        <el-button type="primary" @click="saveBio">确定</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="300px">
      <el-form label-position="top">
        <el-form-item label="旧密码">
          <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入旧密码" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="passwordSaving" @click="handleChangePassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/pinia/userStore'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import defaultAvatar from '@/assets/imgs/photo.jpeg'

const router = useRouter()
const userStore = useUserStore()

// 当前登录用户信息（来自 store）
const userInfo = computed(() => userStore.userInfo)

// 修改昵称时的 loading
const saving = ref(false)
// 修改密码时的 loading
const passwordSaving = ref(false)
// 昵称编辑弹窗显隐
const showNicknameEdit = ref(false)
// 简介编辑弹窗显隐
const showBioEdit = ref(false)
// 修改密码弹窗显隐
const showPasswordDialog = ref(false)
// 头像选择弹窗显隐（暂未实现选择器，预留）
const showAvatarPicker = ref(false)
// 昵称输入框临时值
const tempNickname = ref('')
// 简介输入框临时值
const tempBio = ref('')

// 性别展示文案：兼容 unknown / male / female
const genderLabel = computed(() => {
  const g = userStore.userInfo?.gender
  if (g === 'male') return '男'
  if (g === 'female') return '女'
  return 'unknown'
})

// 用户可编辑的表单数据
const form = reactive({
  id: '',
  username: '',
  nickname: '',
  email: '',
  phone: '',
  avatar: '',
  bio: ''
})

// 修改密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

/** 进入页面：主动调 /user/info 拉取最新用户信息，失败时回退到 store 缓存 */
onMounted(async () => {
  try {
    // 拉取最新数据；401 已在 axios 响应拦截器中处理（清 token + 跳登录）
    await userStore.fetchUserInfo()
  } catch (e) {
    // 拉取失败：用 store 缓存兜底渲染
  } finally {
    if (userStore.userInfo) {
      Object.assign(form, userStore.userInfo)
      tempBio.value = form.bio || ''
      tempNickname.value = form.nickname || '测试用户'
    }
  }
})

/** 打开昵称弹窗时，把当前昵称同步到临时变量 */
const openNicknameEdit = () => {
  tempNickname.value = form.nickname || '测试用户'
  showNicknameEdit.value = true
}

/** 保存昵称：调接口更新，成功后关闭弹窗 */
const saveNickname = async () => {
  const next = tempNickname.value.trim()
  if (!next) {
    ElMessage.warning('昵称不能为空')
    return
  }
  form.nickname = next
  try {
    saving.value = true
    await userStore.updateUserInfo({ nickname: form.nickname })
    ElMessage.success('修改成功')
  } catch (e) {
    ElMessage.error('修改失败')
  } finally {
    saving.value = false
    showNicknameEdit.value = false
  }
}

/** 保存个人简介：调接口更新，成功后关闭弹窗 */
const saveBio = async () => {
  form.bio = tempBio.value
  try {
    saving.value = true
    await userStore.updateUserInfo({ bio: form.bio })
    ElMessage.success('修改成功')
  } catch (e) {
    ElMessage.error('修改失败')
  } finally {
    saving.value = false
    showBioEdit.value = false
  }
}

/** 提交修改密码：必填校验 → 两次新密码一致性 → 新旧密码差异校验 → 调接口 → 清空表单并关闭弹窗 */
const handleChangePassword = async () => {
  const { oldPassword, newPassword, confirmPassword } = passwordForm
  if (!oldPassword || !newPassword || !confirmPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (newPassword !== confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  if (newPassword === oldPassword) {
    ElMessage.warning('新密码不能与旧密码相同')
    return
  }
  try {
    passwordSaving.value = true
    await userStore.changePassword({ oldPassword, newPassword })
    ElMessage.success('密码修改成功')
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    showPasswordDialog.value = false
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
    background: linear-gradient(135deg, #e63946 0%, #c62b36 100%);

    .el-icon {
      font-size: 20px;
      color: #fff;
      cursor: pointer;
    }

    span {
      flex: 1;
      text-align: center;
      font-size: 1rem;
      font-weight: 600;
      color: #fff;
    }
  }

  .list-section {
    background: #fff;
    margin-top: 10px;

    .list-item {
      display: flex;
      align-items: center;
      padding: 14px 15px;
      border-bottom: 1px solid #f0f0f0;
      cursor: pointer;

      &:last-child {
        border-bottom: none;
      }

      .label {
        font-size: 0.9375rem;
        color: #333;
        min-width: 80px;
      }

      .value {
        flex: 1;
        text-align: right;
        font-size: 0.875rem;
        color: #999;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 6px;

        &.editable {
          color: #999;
        }

        &.id-value {
          color: #bbb;
        }

        .avatar-img {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          object-fit: cover;
        }

        .el-icon {
          color: #ccc;
          font-size: 14px;
        }
      }
    }
  }
}
</style>