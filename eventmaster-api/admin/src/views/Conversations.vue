<template>
  <div class="conversations-page">
    <div class="page-header">
      <h1>對話記錄</h1>
      <el-button :icon="Refresh" @click="fetchData">重新整理</el-button>
    </div>

    <!-- 篩選工具欄 -->
    <el-card class="toolbar-card">
      <div class="toolbar">
        <div class="filters">
          <el-input
            v-model="filters.sessionId"
            placeholder="Session ID"
            clearable
            style="width: 200px"
            @change="fetchData"
          />
        </div>
      </div>
    </el-card>

    <!-- 對話列表 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="conversations"
        stripe
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="sessionId" label="Session ID" width="200" />
        <el-table-column prop="userQuery" label="使用者查詢" min-width="250" show-overflow-tooltip />
        <el-table-column prop="aiResponse" label="AI 回應" min-width="250" show-overflow-tooltip />
        <el-table-column label="推薦場地" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.venuesRecommended && row.venuesRecommended.length" size="small">
              {{ row.venuesRecommended.length }} 個
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="評分" width="80" align="center">
          <template #default="{ row }">
            <el-rate
              v-if="row.feedback"
              v-model="row.feedback"
              disabled
              show-score
              score-template="{value}"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="時間" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              text
              :icon="View"
              @click="showDetail(row)"
            >
              詳情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </div>

    <!-- 詳情對話框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="對話詳情"
      width="700px"
    >
      <div v-if="currentConversation" class="detail-dialog">
        <div class="detail-item">
          <span class="detail-label">Session ID</span>
          <span class="detail-value">{{ currentConversation.sessionId }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">時間</span>
          <span class="detail-value">{{ formatDateTime(currentConversation.createdAt) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">使用者查詢</span>
          <span class="detail-value pre">{{ currentConversation.userQuery }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">AI 回應</span>
          <span class="detail-value pre">{{ currentConversation.aiResponse }}</span>
        </div>
        <div v-if="currentConversation.venuesRecommended && currentConversation.venuesRecommended.length" class="detail-item">
          <span class="detail-label">推薦場地</span>
          <span class="detail-value">
            <el-tag
              v-for="venueId in currentConversation.venuesRecommended"
              :key="venueId"
              size="small"
              style="margin-right: 5px"
            >
              {{ venueId }}
            </el-tag>
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">使用者評分</span>
          <span class="detail-value">
            <el-rate
              v-if="currentConversation.feedback"
              v-model="currentConversation.feedback"
              disabled
              show-score
            />
            <span v-else>未評分</span>
          </span>
        </div>
        <div v-if="currentConversation.userFingerprint" class="detail-item">
          <span class="detail-label">用戶指紋</span>
          <span class="detail-value">{{ currentConversation.userFingerprint }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">關閉</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Refresh, View } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import dayjs from 'dayjs'

const loading = ref(false)
const conversations = ref([])
const total = ref(0)
const showDetailDialog = ref(false)
const currentConversation = ref(null)

const filters = reactive({
  sessionId: ''
})

const pagination = reactive({
  page: 1,
  size: 20
})

async function fetchData() {
  loading.value = true
  try {
    const params = {
      limit: pagination.size,
      offset: (pagination.page - 1) * pagination.size
    }

    if (filters.sessionId) {
      params.session_id = filters.sessionId
    }

    const response = await api.get('/api/v1/admin/conversations', { params })
    conversations.value = response.data
    total.value = response.data.length
  } catch (error) {
    ElMessage.error('載入對話記錄失敗')
  } finally {
    loading.value = false
  }
}

function showDetail(conversation) {
  currentConversation.value = conversation
  showDetailDialog.value = true
}

function formatDateTime(date) {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.conversations-page {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h1 {
      font-size: 24px;
      color: #303133;
      margin: 0;
    }
  }

  .toolbar-card {
    margin-bottom: 20px;

    .toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 15px;

      .filters {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
      }
    }
  }

  .table-container {
    background: #ffffff;
    border-radius: 4px;

    .pagination {
      padding: 15px 20px;
      display: flex;
      justify-content: flex-end;
      border-top: 1px solid #f0f0f0;
    }
  }
}
</style>
