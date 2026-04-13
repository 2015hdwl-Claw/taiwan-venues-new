<template>
  <div class="venues-page">
    <div class="page-header">
      <h1>場地管理</h1>
      <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
        新增場地
      </el-button>
    </div>

    <!-- 篩選工具欄 -->
    <el-card class="toolbar-card">
      <div class="toolbar">
        <div class="filters">
          <el-input
            v-model="filters.search"
            placeholder="搜尋場地名稱"
            :prefix-icon="Search"
            clearable
            style="width: 200px"
            @input="handleFilterChange"
          />
          <el-select
            v-model="filters.city"
            placeholder="城市"
            clearable
            style="width: 120px"
            @change="handleFilterChange"
          >
            <el-option label="台北市" value="台北市" />
            <el-option label="新北市" value="新北市" />
            <el-option label="台中市" value="台中市" />
            <el-option label="高雄市" value="高雄市" />
            <el-option label="台南市" value="台南市" />
            <el-option label="桃園市" value="桃園市" />
            <el-option label="屏東縣" value="屏東縣" />
            <el-option label="南投縣" value="南投縣" />
            <el-option label="宜蘭縣" value="宜蘭縣" />
            <el-option label="新竹市" value="新竹市" />
            <el-option label="彰化縣" value="彰化縣" />
            <el-option label="花蓮縣" value="花蓮縣" />
            <el-option label="台東縣" value="台東縣" />
          </el-select>
          <el-select
            v-model="filters.type"
            placeholder="類型"
            clearable
            style="width: 130px"
            @change="handleFilterChange"
          >
            <el-option label="飯店場地" value="飯店" />
            <el-option label="會議中心" value="會議中心" />
            <el-option label="展演場地" value="展演場地" />
            <el-option label="機關場地" value="機關場地" />
            <el-option label="運動場地" value="運動場地" />
            <el-option label="婚宴場地" value="婚宴場地" />
            <el-option label="咖啡廳" value="咖啡廳" />
            <el-option label="宴會廳" value="宴會廳" />
            <el-option label="其他" value="其他" />
          </el-select>
        </div>
        <div class="actions">
          <el-button :icon="Refresh" @click="fetchData">重新整理</el-button>
        </div>
      </div>
    </el-card>

    <!-- 場地表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="venues"
        stripe
        @row-click="handleRowClick"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="場地名稱" min-width="150" />
        <el-table-column prop="nameEn" label="英文名稱" min-width="150" />
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column prop="venueType" label="類型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ row.venueType || getTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              text
              :icon="View"
              @click.stop="$router.push(`/venues/${row.id}`)"
            >
              查看
            </el-button>
            <el-button
              type="danger"
              size="small"
              text
              :icon="Delete"
              @click.stop="handleDelete(row)"
            >
              刪除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="totalFiltered"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 新增場地對話框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新增場地"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="場地名稱" prop="name">
          <el-input v-model="form.name" placeholder="請輸入場地名稱" />
        </el-form-item>
        <el-form-item label="英文名稱" prop="nameEn">
          <el-input v-model="form.nameEn" placeholder="請輸入英文名稱" />
        </el-form-item>
        <el-form-item label="類型" prop="venueType">
          <el-select v-model="form.venueType" placeholder="請選擇類型" style="width: 100%">
            <el-option label="飯店場地" value="飯店" />
            <el-option label="會議中心" value="會議中心" />
            <el-option label="展演場地" value="展演場地" />
            <el-option label="機關場地" value="機關場地" />
            <el-option label="運動場地" value="運動場地" />
            <el-option label="婚宴場地" value="婚宴場地" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="城市" prop="city">
          <el-input v-model="form.city" placeholder="請輸入城市" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" placeholder="請輸入地址" />
        </el-form-item>
        <el-form-item label="聯絡電話" prop="contactPhone">
          <el-input v-model="form.contactPhone" placeholder="請輸入聯絡電話" />
        </el-form-item>
        <el-form-item label="網址" prop="url">
          <el-input v-model="form.url" placeholder="請輸入網址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          確定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Plus, Search, Refresh, View, Delete
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const router = useRouter()

const filters = reactive({
  search: '',
  city: '',
  type: ''
})

const pagination = reactive({
  page: 1,
  size: 20
})

const showCreateDialog = ref(false)
const submitting = ref(false)
const formRef = ref()
const loading = ref(false)
const allVenues = ref([])

const form = reactive({
  name: '',
  nameEn: '',
  venueType: '',
  city: '',
  address: '',
  contactPhone: '',
  url: ''
})

const formRules = {
  name: [{ required: true, message: '請輸入場地名稱', trigger: 'blur' }],
  venueType: [{ required: true, message: '請選擇類型', trigger: 'change' }],
  city: [{ required: true, message: '請輸入城市', trigger: 'blur' }]
}

// 客戶端過濾
const filteredVenues = computed(() => {
  let result = allVenues.value

  if (filters.search) {
    const q = filters.search.toLowerCase()
    result = result.filter(v =>
      (v.name && v.name.toLowerCase().includes(q)) ||
      (v.nameEn && v.nameEn.toLowerCase().includes(q))
    )
  }

  if (filters.city) {
    result = result.filter(v => v.city === filters.city)
  }

  if (filters.type) {
    result = result.filter(v =>
      (v.venueType && v.venueType === filters.type) ||
      (v.type && v.type === filters.type)
    )
  }

  return result
})

const totalFiltered = computed(() => filteredVenues.value.length)

const venues = computed(() => {
  const start = (pagination.page - 1) * pagination.size
  return filteredVenues.value.slice(start, start + pagination.size)
})

async function fetchData() {
  loading.value = true
  try {
    const response = await api.get('/api/v1/admin/venues-json')
    allVenues.value = response.data || []
  } catch (error) {
    console.error('Error fetching venues:', error)
    ElMessage.error('載入場地資料失敗')
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  pagination.page = 1
}

function handleSearch() {
  pagination.page = 1
}

function handlePageSizeChange() {
  pagination.page = 1
}

function handlePageChange() {
  // pagination.page is already updated by v-model
}

function handleRowClick(row) {
  router.push(`/venues/${row.id}`)
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    submitting.value = true

    // 直接新增到 venues.json
    const newId = Math.max(...allVenues.value.map(v => v.id), 0) + 1
    const newVenue = { id: newId, ...JSON.parse(JSON.stringify(form)) }
    newVenue.isActive = true

    await api.put(`/api/v1/admin/venues/${newId}`, newVenue)

    ElMessage.success('場地新增成功')
    showCreateDialog.value = false

    Object.keys(form).forEach(key => {
      form[key] = ''
    })

    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('新增場地失敗')
    }
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `確定要刪除場地「${row.name}」嗎？此操作無法恢復。`,
      '確認刪除',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    ElMessage.info('刪除功能需透過 API 實作')
  } catch {
    // 用戶取消
  }
}

function getTypeLabel(type) {
  const labels = {
    conference: '會議中心',
    hotel: '飯店',
    exhibition: '展覽中心',
    other: '其他'
  }
  return labels[type] || type
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.venues-page {
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

    :deep(.el-table) {
      cursor: pointer;

      tbody tr:hover {
        background-color: #f5f7fa;
      }
    }

    .pagination {
      padding: 15px 20px;
      display: flex;
      justify-content: flex-end;
      border-top: 1px solid #f0f0f0;
    }
  }
}
</style>
