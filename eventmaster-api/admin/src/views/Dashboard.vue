<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>儀表板</h1>
      <p>系統概況與統計</p>
    </div>

    <div v-loading="loading" class="dashboard-content">
      <!-- 統計卡片 -->
      <div class="dashboard-grid">
        <el-card class="stat-card">
          <div class="stat-label">場地總數</div>
          <div class="stat-value">{{ stats.total_venues }}</div>
          <div class="stat-trend up">
            <el-icon><TrendCharts /></el-icon>
            <span>系統中的所有場地</span>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-label">有問題場地</div>
          <div class="stat-value warning">{{ stats.venues_with_problems }}</div>
          <div class="stat-trend" :class="stats.venues_with_problems > 0 ? 'down' : 'up'">
            <el-icon><Warning /></el-icon>
            <span>需要關注的場地</span>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-label">未解決問題</div>
          <div class="stat-value danger">{{ stats.open_problems }}</div>
          <div class="stat-trend" :class="stats.open_problems > 0 ? 'down' : 'up'">
            <el-icon><WarningFilled /></el-icon>
            <span>待處理的問題</span>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-label">爬蟲成功率</div>
          <div class="stat-value" :class="stats.scrape_success_rate >= 80 ? 'success' : 'warning'">
            {{ stats.scrape_success_rate }}%
          </div>
          <div class="stat-trend" :class="stats.scrape_success_rate >= 80 ? 'up' : 'down'">
            <el-icon><TrendCharts /></el-icon>
            <span>最近 100 個任務</span>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-label">最近對話</div>
          <div class="stat-value">{{ stats.recent_conversations }}</div>
          <div class="stat-trend up">
            <el-icon><ChatDotRound /></el-icon>
            <span>過去 24 小時</span>
          </div>
        </el-card>
      </div>

      <!-- 快速操作 -->
      <el-card class="quick-actions">
        <template #header>
          <span>快速操作</span>
        </template>
        <div class="action-buttons">
          <el-button type="primary" :icon="Plus" @click="$router.push('/venues')">
            新增場地
          </el-button>
          <el-button type="warning" :icon="Warning" @click="$router.push('/problems')">
            查看問題
          </el-button>
          <el-button type="success" :icon="Download" @click="$router.push('/scrape-tasks')">
            執行爬蟲
          </el-button>
          <el-button :icon="DataAnalysis" @click="$router.push('/analytics')">
            數據分析
          </el-button>
        </div>
      </el-card>

      <!-- 最近問題 -->
      <el-card class="recent-problems">
        <template #header>
          <div class="card-header">
            <span>最近問題</span>
            <el-link type="primary" @click="$router.push('/problems')">查看全部</el-link>
          </div>
        </template>
        <el-empty v-if="!recentProblems.length" description="暫無問題" />
        <div v-else class="problem-list">
          <div
            v-for="problem in recentProblems"
            :key="problem.id"
            class="problem-item"
            @click="$router.push(`/problems`)"
          >
            <div class="problem-info">
              <div class="problem-title">
                <span class="severity-badge" :class="problem.severity" />
                {{ problem.venueId }} - {{ problem.problemType }}
              </div>
              <div class="problem-detail">{{ problem.field }}</div>
            </div>
            <el-tag :type="getStatusType(problem.status)" size="small">
              {{ problem.status }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  Plus, Warning, Download, DataAnalysis, TrendCharts,
  ChatDotRound, WarningFilled
} from '@element-plus/icons-vue'
import api from '@/utils/api'

const loading = ref(false)
const stats = ref({
  total_venues: 0,
  venues_with_problems: 0,
  open_problems: 0,
  recent_conversations: 0,
  scrape_success_rate: 0
})
const recentProblems = ref([])

async function fetchDashboard() {
  loading.value = true
  try {
    const [statsRes, problemsRes] = await Promise.all([
      api.get('/api/v1/admin/dashboard'),
      api.get('/api/v1/admin/problems', { params: { limit: 5 } })
    ])

    stats.value = statsRes.data
    recentProblems.value = problemsRes.data.items || []
  } catch (error) {
    console.error('Failed to fetch dashboard:', error)
  } finally {
    loading.value = false
  }
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

onMounted(() => {
  fetchDashboard()
})
</script>

<style lang="scss" scoped>
.dashboard {
  .page-header {
    margin-bottom: 20px;

    h1 {
      font-size: 24px;
      color: #303133;
      margin: 0 0 5px 0;
    }

    p {
      color: #909399;
      margin: 0;
    }
  }

  .stat-card {
    .stat-value {
      font-size: 32px;
      font-weight: 600;
      margin: 10px 0;
      color: #303133;

      &.warning { color: #e6a23c; }
      &.danger { color: #f56c6c; }
      &.success { color: #67c23a; }
    }

    .stat-label {
      color: #909399;
      font-size: 14px;
    }

    .stat-trend {
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: 12px;
      color: #909399;

      &.up { color: #67c23a; }
      &.down { color: #f56c6c; }
    }
  }

  .quick-actions {
    margin: 20px 0;

    .action-buttons {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
  }

  .recent-problems {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .problem-list {
      .problem-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;
        cursor: pointer;
        transition: background 0.2s;

        &:hover {
          background: #f5f7fa;
          margin: 0 -20px;
          padding: 12px 20px;
        }

        &:last-child {
          border-bottom: none;
        }

        .problem-info {
          .problem-title {
            font-weight: 500;
            color: #303133;
            margin-bottom: 4px;
          }

          .problem-detail {
            font-size: 12px;
            color: #909399;
          }
        }
      }
    }
  }
}
</style>
