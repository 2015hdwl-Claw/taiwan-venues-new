<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>EventMaster</h1>
        <p>活動大師管理後台</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="apiKey">
          <el-input
            v-model="form.apiKey"
            type="password"
            placeholder="請輸入 API Key"
            show-password
            :prefix-icon="Key"
            size="large"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            登入
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p>請使用管理員 API Key 登入</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Key } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  apiKey: ''
})

const rules = {
  apiKey: [
    { required: true, message: '請輸入 API Key', trigger: 'blur' },
    { min: 10, message: 'API Key 格式不正確', trigger: 'blur' }
  ]
}

async function handleLogin() {
  try {
    await formRef.value.validate()
    loading.value = true

    // 測試 API Key 是否有效
    api.defaults.headers['X-API-Key'] = form.apiKey
    await api.get('/api/v1/admin/dashboard')

    // 保存 API Key
    authStore.setApiKey(form.apiKey)

    ElMessage.success('登入成功')

    // 跳轉到原目標頁面或儀表板
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    if (error.response?.status === 401) {
      ElMessage.error('API Key 無效，請檢查後重試')
    } else {
      console.error('Login error:', error)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;

  h1 {
    font-size: 32px;
    color: #303133;
    margin: 0 0 10px 0;
  }

  p {
    color: #909399;
    margin: 0;
  }
}

.login-form {
  .login-button {
    width: 100%;
  }
}

.login-footer {
  text-align: center;
  margin-top: 20px;

  p {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }
}
</style>
