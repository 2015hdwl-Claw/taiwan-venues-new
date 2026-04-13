<template>
  <div class="problems-page">
    <div class="page-header">
      <h1>問題追蹤</h1>
      <el-button :icon="Refresh" @click="fetchData">重新整理</el-button>
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
            <el-option label="待處理" value="open" />
            <el-option label="診斷中" value="diagnosing" />
            <el-option label="修復中" value="fixing" />
            <el-option label="已修復" value="fixed" />
            <el-option label="不可修復" value="wontfix" />
            <el-option label="確認無資料" value="confirmed_absent" />
          </el-select>
          <el-select
            v-model="filters.severity"
            placeholder="嚴重程度"
            clearable
            style="width: 120px"
            @change="fetchData"
          >
            <el-option label="嚴重" value="critical" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
          <el-select
            v-model="filters.problemType"
            placeholder="問題類型"
            clearable
            style="width: 150px"
            @change="fetchData"
          >
            <el-option label="缺少會議室" value="missing_rooms" />
            <el-option label="缺少定價" value="missing_pricing" />
            <el-option label="缺少容量" value="missing_capacity" />
            <el-option label="缺少圖片" value="missing_images" />
            <el-option label="Schema 錯誤" value="invalid_schema" />
          </el-select>
        </div>
      </div>
    </el-card>

    <!-- 問題列表 -->
    <div class="table-container">
      <el-table
        v-loading="problemStore.loading"
        :data="problems"
        stripe
      >
        <el-table-column label="嚴重" width="60">
          <template #default="{ row }">
            <span class="severity-badge" :class="row.severity" />
          </template>
        </el-table-column>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="場地" width="100">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/venues/${row.venueId}`)">
              {{ row.venueId }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="problemType" label="問題類型" width="140">
          <template #default="{ row }">
            <el-tag size="small">{{ getProblemTypeLabel(row.problemType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="field" label="欄位" min-width="180" show-overflow-tooltip />
        <el-table-column label="狀態" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="診斷結果" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.diagnosis">{{ row.diagnosis }}</span>
            <el-text v-else type="info">未診斷</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="occurrences" label="次數" width="70" align="center" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.diagnosis"
              type="primary"
              size="small"
              text
              :icon="MagicStick"
              :loading="diagnosing === row.id"
              @click="handleDiagnose(row)"
            >
              診斷
            </el-button>
            <el-dropdown @command="(cmd) => handleStatusChange(row, cmd)">
              <el-button size="small" text>
                狀態<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="fixing">修復中</el-dropdown-item>
                  <el-dropdown-item command="fixed">已修復</el-dropdown-item>
                  <el-dropdown-item command="wontfix">不可修復</el-dropdown-item>
                  <el-dropdown-item command="confirmed_absent">確認無資料</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button
              type="info"
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
          :total="problemStore.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </div>

    <!-- 詳情對話框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="問題詳情"
      width="700px"
    >
      <div v-if="currentProblem" class="detail-dialog">
        <div class="detail-item">
          <span class="detail-label">場地 ID</span>
          <span class="detail-value">{{ currentProblem.venueId }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">問題類型</span>
          <span class="detail-value">{{ getProblemTypeLabel(currentProblem.problemType) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">欄位</span>
          <span class="detail-value">{{ currentProblem.field }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">嚴重程度</span>
          <span class="detail-value">
            <span class="severity-badge" :class="currentProblem.severity" />
            {{ currentProblem.severity }}
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">狀態</span>
          <span class="detail-value">
            <el-tag :type="getStatusType(currentProblem.status)" size="small">
              {{ getStatusLabel(currentProblem.status) }}
            </el-tag>
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">發生次數</span>
          <span class="detail-value">{{ currentProblem.occurrences }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">首次發現</span>
          <span class="detail-value">{{ formatDate(currentProblem.firstSeen) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">最後發現</span>
          <span class="detail-value">{{ formatDate(currentProblem.lastSeen) }}</span>
        </div>
        <div v-if="currentProblem.diagnosis" class="detail-item">
          <span class="detail-label">診斷結果</span>
          <span class="detail-value">{{ currentProblem.diagnosis }}</span>
        </div>
        <div v-if="currentProblem.fixAction" class="detail-item">
          <span class="detail-label">修復建議</span>
          <span class="detail-value">{{ currentProblem.fixAction }}</span>
        </div>
        <div v-if="currentProblem.notes" class="detail-item">
          <span class="detail-label">備註</span>
          <span class="detail-value pre">{{ currentProblem.notes }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">關閉</el-button>
        <el-button type="primary" @click="showDetailDialog = false; $router.push(`/venues/${currentProblem.venueId}`)">
          查看場地
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import {
  Refresh, MagicStick, View, ArrowDown
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProblemStore } from '@/stores/problem'
import dayjs from 'dayjs'

const problemStore = useProblemStore()

const filters = reactive({
  venueId: '',
  status: '',
  severity: '',
  problemType: ''
})

const pagination = reactive({
  page: 1,
  size: 20
})

const showDetailDialog = ref(false)
const currentProblem = ref(null)
const diagnosing = ref(null)

const problems = computed(() => problemStore.problems)

async function fetchData() {
  try {
    await problemStore.fetchProblems({
      venue_id: filters.venueId || undefined,
      status: filters.status || undefined,
      severity: filters.severity || undefined,
      problem_type: filters.problemType || undefined,
      offset: (pagination.page - 1) * pagination.size,
      limit: pagination.size
    })
  } catch (error) {
    ElMessage.error('載入問題資料失敗')
  }
}

async function handleDiagnose(problem) {
  diagnosing.value = problem.id
  try {
    await problemStore.diagnoseProblem(problem.id)
    ElMessage.success('診斷完成')
    fetchData()
  } catch (error) {
    ElMessage.error('診斷失敗')
  } finally {
    diagnosing.value = null
  }
}

async function handleStatusChange(problem, status) {
  try {
    await ElMessageBox.prompt('請輸入備註（可選）', '更新狀態', {
      confirmButtonText: '確定',
      cancelButtonText: '取消',
      inputPattern: /.*/,
      inputErrorMessage: '請輸入有效的備註'
    }).then(({ value }) => {
      return problemStore.updateProblemStatus(problem.id, status, value || '')
    }).then(() => {
      ElMessage.success('狀態已更新')
      fetchData()
    })
  } catch {
    // 用戶取消
  }
}

function showDetail(problem) {
  currentProblem.value = problem
  showDetailDialog.value = true
}

function getProblemTypeLabel(type) {
  const labels = {
    missing_rooms: '缺少會議室',
    missing_pricing: '缺少定價',
    missing_capacity: '缺少容量',
    missing_images: '缺少圖片',
    invalid_schema: 'Schema 錯誤',
    low_quality_source: '資料來源品質低'
  }
  return labels[type] || type
}

function getStatusLabel(status) {
  const labels = {
    open: '待處理',
    diagnosing: '診斷中',
    fixing: '修復中',
    fixed: '已修復',
    wontfix: '不可修復',
    confirmed_absent: '確認無資料'
  }
  return labels[status] || status
}

function getStatusType(status) {
  const types = {
    open: 'danger',
    diagnosing: 'warning',
    fixing: 'primary',
    fixed: 'success',
    wontfix: 'info',
    confirmed_absent: 'info'
  }
  return types[status] || 'info'
}

function formatDate(date) {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.problems-page {
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

.severity-badge {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;

  &.critical { background-color: #f56c6c; }
  &.high { background-color: #e6a23c; }
  &.medium { background-color: #409eff; }
  &.low { background-color: #67c23a; }
}
</style>
