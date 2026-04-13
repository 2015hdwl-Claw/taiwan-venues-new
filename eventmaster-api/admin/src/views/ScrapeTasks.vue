<template>
  <div class="scrape-tasks-page">
    <div class="page-header">
      <h1>爬蟲任務</h1>
      <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
        新增任務
      </el-button>
    </div>

    <!-- 篩選工具欄 -->
    <el-card class="toolbar-card">
      <div class="toolbar">
        <div class="filters">
          <el-input
            v-model="filters.venueId"
            placeholder="場地 ID"
            clearable
            style="width: 120px"
            @change="fetchData"
          />
          <el-select
            v-model="filters.status"
            placeholder="狀態"
            clearable
            style="width: 120px"
            @change="fetchData"
          >
            <el-option label="等待中" value="pending" />
            <el-option label="執行中" value="running" />
            <el-option label="成功" value="success" />
            <el-option label="失敗" value="failed" />
          </el-select>
          <el-select
            v-model="filters.taskType"
            placeholder="任務類型"
            clearable
            style="width: 120px"
            @change="fetchData"
          >
            <el-option label="完整爬取" value="full" />
            <el-option label="增量更新" value="incremental" />
            <el-option label="驗證" value="verify" />
          </el-select>
        </div>
      </div>
    </el-card>

    <!-- 任務列表 -->
    <div class="table-container">
      <el-table
        v-loading="scrapeStore.loading"
        :data="tasks"
        stripe
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="場地" width="100">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/venues/${row.venueId}`)">
              {{ row.venueId }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column label="任務類型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ getTaskTypeLabel(row.taskType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="狀態" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="開始時間" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.startedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="完成時間" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.completedAt) }}
          </template>
        </el-table-column>
        <el-table-column prop="roomsFound" label="發現會議室" width="100" align="center" />
        <el-table-column prop="problemsFound" label="發現問題" width="100" align="center" />
        <el-table-column label="錯誤訊息" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.errorMessage">{{ row.errorMessage }}</span>
            <el-text v-else type="success">無</el-text>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              type="info"
              size="small"
              text
              :icon="Document"
              @click="showTaskDetail(row)"
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
          layout="total, sizes, prev, pager, next"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </div>

    <!-- 新增任務對話框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新增爬蟲任務"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        label-width="100px"
      >
        <el-form-item label="場地 ID">
          <el-input
            v-model="form.venueIds"
            type="textarea"
            :rows="3"
            placeholder="輸入場地 ID，多個用逗號或換行分隔"
          />
          <div class="form-tip">例如：1501, 1502 或每行一個 ID</div>
        </el-form-item>
        <el-form-item label="任務類型">
          <el-radio-group v-model="form.taskType">
            <el-radio value="full">完整爬取</el-radio>
            <el-radio value="incremental">增量更新</el-radio>
            <el-radio value="verify">驗證</el-radio>
          </el-radio-group>
          <div class="form-tip">
            完整爬取：重新抓取所有資料
            <br>增量更新：只更新有變化的資料
            <br>驗證：檢查現有資料完整性
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">
          建立
        </el-button>
      </template>
    </el-dialog>

    <!-- 任務詳情對話框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="任務詳情"
      width="700px"
    >
      <div v-if="currentTask" class="detail-dialog">
        <div class="detail-item">
          <span class="detail-label">任務 ID</span>
          <span class="detail-value">{{ currentTask.id }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">場地 ID</span>
          <span class="detail-value">{{ currentTask.venueId }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">任務類型</span>
          <span class="detail-value">{{ getTaskTypeLabel(currentTask.taskType) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">狀態</span>
          <span class="detail-value">
            <el-tag :type="getStatusType(currentTask.status)" size="small">
              {{ getStatusLabel(currentTask.status) }}
            </el-tag>
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">開始時間</span>
          <span class="detail-value">{{ formatDateTime(currentTask.startedAt) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">完成時間</span>
          <span class="detail-value">{{ formatDateTime(currentTask.completedAt) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">發現會議室</span>
          <span class="detail-value">{{ currentTask.roomsFound }} 個</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">發現問題</span>
          <span class="detail-value">{{ currentTask.problemsFound }} 個</span>
        </div>
        <div v-if="currentTask.errorMessage" class="detail-item">
          <span class="detail-label">錯誤訊息</span>
          <span class="detail-value error">{{ currentTask.errorMessage }}</span>
        </div>
        <div v-if="currentTask.techReport" class="detail-item">
          <span class="detail-label">技術報告</span>
          <span class="detail-value pre">{{ JSON.stringify(currentTask.techReport, null, 2) }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">關閉</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Plus, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useScrapeStore } from '@/stores/scrape'
import dayjs from 'dayjs'

const scrapeStore = useScrapeStore()

const filters = reactive({
  venueId: '',
  status: '',
  taskType: ''
})

const pagination = reactive({
  page: 1,
  size: 20
})

const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const submitting = ref(false)
const formRef = ref()
const currentTask = ref(null)

const form = reactive({
  venueIds: '',
  taskType: 'full'
})

const tasks = computed(() => scrapeStore.tasks)
const total = ref(0)

async function fetchData() {
  try {
    const response = await scrapeStore.fetchTasks({
      venue_id: filters.venueId || undefined,
      status: filters.status || undefined,
      task_type: filters.taskType || undefined,
      limit: pagination.size,
      offset: (pagination.page - 1) * pagination.size
    })
    total.value = response.length
  } catch (error) {
    ElMessage.error('載入任務資料失敗')
  }
}

async function handleCreate() {
  if (!form.venueIds.trim()) {
    ElMessage.warning('請輸入場地 ID')
    return
  }

  submitting.value = true
  try {
    // 解析場地 ID
    const venueIds = form.venueIds
      .split(/[,\n]+/)
      .map(id => id.trim())
      .filter(id => id)
      .map(id => parseInt(id))

    if (venueIds.length === 0 || venueIds.some(id => isNaN(id))) {
      ElMessage.error('場地 ID 格式錯誤')
      return
    }

    await scrapeStore.createTask(venueIds, form.taskType)
    ElMessage.success('任務已建立')
    showCreateDialog.value = false
    form.venueIds = ''
    fetchData()
  } catch (error) {
    ElMessage.error('建立任務失敗')
  } finally {
    submitting.value = false
  }
}

function showTaskDetail(task) {
  currentTask.value = task
  showDetailDialog.value = true
}

function getTaskTypeLabel(type) {
  const labels = {
    full: '完整爬取',
    incremental: '增量更新',
    verify: '驗證'
  }
  return labels[type] || type
}

function getStatusLabel(status) {
  const labels = {
    pending: '等待中',
    running: '執行中',
    success: '成功',
    failed: '失敗'
  }
  return labels[status] || status
}

function getStatusType(status) {
  const types = {
    pending: 'info',
    running: 'warning',
    success: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

function formatDateTime(date) {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.scrape-tasks-page {
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

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
    line-height: 1.5;
  }
}
</style>
