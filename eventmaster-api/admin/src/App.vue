<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // 檢查本地存儲的 API Key
  authStore.loadFromStorage()
})
</script>

<style lang="scss">
#app {
  height: 100vh;
  overflow: hidden;
}

// 全局樣式覆蓋
.el-table {
  --el-table-border-color: #f0f0f0;
  --el-table-bg-color: #ffffff;
}

.el-card {
  --el-card-border-color: #f0f0f0;
}

// 狀態標籤顏色
.status-tag {
  &.open { background-color: #fef0f0; color: #f56c6c; }
  &.diagnosing { background-color: #fdf6ec; color: #e6a23c; }
  &.fixing { background-color: #ecf5ff; color: #409eff; }
  &.fixed { background-color: #f0f9ff; color: #67c23a; }
  &.wontfix { background-color: #f4f4f5; color: #909399; }
  &.confirmed_absent { background-color: #f4f4f5; color: #909399; }
}
</style>
