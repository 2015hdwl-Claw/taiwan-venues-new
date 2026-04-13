<template>
  <div class="analytics-page">
    <div class="page-header">
      <h1>數據分析</h1>
      <el-select
        v-model="days"
        style="width: 150px"
        @change="fetchData"
      >
        <el-option :value="7" label="過去 7 天" />
        <el-option :value="30" label="過去 30 天" />
        <el-option :value="90" label="過去 90 天" />
      </el-select>
    </div>

    <div v-loading="loading" class="analytics-content">
      <!-- 統計概覽 -->
      <div class="dashboard-grid">
        <el-card class="stat-card">
          <div class="stat-label">總對話數</div>
          <div class="stat-value">{{ analytics.total_conversations }}</div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-label">平均評分</div>
          <div class="stat-value">
            {{ analytics.avg_feedback ? analytics.avg_feedback.toFixed(1) : '-' }}
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-label">每日平均對話</div>
          <div class="stat-value">
            {{ dailyAverage }}
          </div>
        </el-card>
      </div>

      <!-- 每日統計圖表 -->
      <el-card class="chart-card">
        <template #header>
          <span>每日對話趨勢</span>
        </template>
        <v-chart
          :option="dailyChartOption"
          style="height: 300px"
        />
      </el-card>

      <!-- 熱門查詢 -->
      <el-card class="top-list">
        <template #header>
          <span>熱門 API 端點</span>
        </template>
        <el-table :data="analytics.top_queries" stripe>
          <el-table-column prop="endpoint" label="端點" />
          <el-table-column prop="count" label="調用次數" width="120" align="center" />
        </el-table>
      </el-card>

      <!-- 每日統計詳情 -->
      <el-card class="daily-stats">
        <template #header>
          <span>每日統計詳情</span>
        </template>
        <el-table :data="analytics.daily_stats" stripe>
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="conversations" label="對話數" width="100" align="center" />
          <el-table-column label="趨勢" width="100">
            <template #default="{ row, $index }">
              <el-icon v-if="$index < analytics.daily_stats.length - 1" class="trend-icon">
                <component :is="getTrendIcon(row, analytics.daily_stats[$index + 1])" />
              </el-icon>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, GridComponent, LegendComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { ArrowUp, ArrowDown, Minus } from '@element-plus/icons-vue'
import api from '@/utils/api'

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
])

const loading = ref(false)
const days = ref(30)
const analytics = ref({
  total_conversations: 0,
  avg_feedback: null,
  top_queries: [],
  daily_stats: []
})

const dailyAverage = computed(() => {
  if (!analytics.value.daily_stats.length) return 0
  const total = analytics.value.daily_stats.reduce((sum, day) => sum + day.conversations, 0)
  return Math.round(total / analytics.value.daily_stats.length)
})

const dailyChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: analytics.value.daily_stats.map(d => d.date),
    axisLabel: {
      formatter: (value) => {
        const date = new Date(value)
        return `${date.getMonth() + 1}/${date.getDate()}`
      }
    }
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '對話數',
      type: 'line',
      data: analytics.value.daily_stats.map(d => d.conversations),
      smooth: true,
      itemStyle: {
        color: '#409eff'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0)' }
          ]
        }
      }
    }
  ]
}))

async function fetchData() {
  loading.value = true
  try {
    const response = await api.get('/api/v1/admin/analytics', {
      params: { days: days.value }
    })
    analytics.value = response.data
  } catch (error) {
    console.error('Failed to fetch analytics:', error)
  } finally {
    loading.value = false
  }
}

function getTrendIcon(current, previous) {
  if (!previous) return Minus
  const diff = current.conversations - previous.conversations
  if (diff > 0) return ArrowUp
  if (diff < 0) return ArrowDown
  return Minus
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.analytics-page {
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

  .stat-card {
    .stat-value {
      font-size: 32px;
      font-weight: 600;
      margin: 10px 0;
      color: #303133;
    }

    .stat-label {
      color: #909399;
      font-size: 14px;
    }
  }

  .chart-card {
    margin: 20px 0;
  }

  .top-list,
  .daily-stats {
    margin: 20px 0;

    .trend-icon {
      &.up { color: #67c23a; }
      &.down { color: #f56c6c; }
    }
  }
}
</style>
