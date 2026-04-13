<template>
  <div class="venue-detail-page">
    <div v-loading="loading" class="venue-detail">
      <!-- 頂部操作欄 -->
      <div class="page-header">
        <el-button :icon="ArrowLeft" @click="$router.back()">返回</el-button>
        <div class="actions">
          <el-button :icon="Refresh" @click="fetchData">重新整理</el-button>
          <el-button
            v-if="venue"
            :type="isActive ? 'warning' : 'success'"
            @click="toggleActiveStatus"
          >
            {{ isActive ? '下架場地' : '上架場地' }}
          </el-button>
          <el-button type="primary" :icon="Edit" @click="openEditDialog">編輯</el-button>
        </div>
      </div>

      <template v-if="venue">
        <!-- 基本資訊 -->
        <el-card class="info-card">
          <template #header>
            <span>基本資訊</span>
          </template>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">場地 ID</span>
              <span class="value">{{ venue.id }}</span>
            </div>
            <div class="info-item">
              <span class="label">名稱</span>
              <span class="value">{{ venue.name }}</span>
            </div>
            <div class="info-item">
              <span class="label">英文名稱</span>
              <span class="value">{{ venue.nameEn }}</span>
            </div>
            <div class="info-item">
              <span class="label">類型</span>
              <span class="value">
                <el-tag size="small">{{ getTypeLabel(venue.type) }}</el-tag>
              </span>
            </div>
            <div class="info-item">
              <span class="label">城市</span>
              <span class="value">{{ venue.city }}</span>
            </div>
            <div class="info-item">
              <span class="label">地址</span>
              <span class="value">{{ venue.address }}</span>
            </div>
            <div class="info-item">
              <span class="label">上架狀態</span>
              <span class="value">
                <el-tag :type="isActive ? 'success' : 'danger'" size="small">
                  {{ isActive ? '上架中' : '已下架' }}
                </el-tag>
              </span>
            </div>
            <div class="info-item full" v-if="!isActive && (venue.statusNotes || venue.statusNote)">
              <span class="label">下架原因</span>
              <span class="value">{{ (venue.statusNotes || venue.statusNote) }}</span>
            </div>
            <div class="info-item full">
              <span class="label">描述</span>
              <span class="value">{{ venue.description || '-' }}</span>
            </div>
            <div class="info-item full">
              <span class="label">設備</span>
              <span class="value">
                <el-tag
                  v-for="(item, index) in parseAmenities(venue.amenities)"
                  :key="index"
                  size="small"
                  style="margin-right: 5px; margin-bottom: 5px"
                >
                  {{ item }}
                </el-tag>
                <span v-if="!venue.amenities">-</span>
              </span>
            </div>
          </div>
        </el-card>

        <!-- 聯絡資訊 -->
        <el-card class="info-card">
          <template #header>
            <span>聯絡資訊</span>
          </template>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">聯絡人</span>
              <span class="value">{{ venue.contactPhone || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Email</span>
              <span class="value">{{ venue.contactEmail || '-' }}</span>
            </div>
            <div class="info-item full">
              <span class="label">網址</span>
              <span class="value">
                <el-link
                  v-if="venue.url"
                  :href="venue.url"
                  target="_blank"
                  type="primary"
                >
                  {{ venue.url }}
                </el-link>
                <span v-else>-</span>
              </span>
            </div>
          </div>
        </el-card>

        <!-- 資料來源 -->
        <el-card v-if="venue.dataSources" class="info-card">
          <template #header>
            <span>資料來源</span>
          </template>
          <div class="info-grid">
            <div class="info-item full" v-if="venue.dataSources.official">
              <span class="label">官網</span>
              <span class="value">
                <el-link :href="venue.dataSources.official" target="_blank" type="primary">
                  {{ venue.dataSources.official }}
                </el-link>
              </span>
            </div>
            <div class="info-item full" v-if="venue.dataSources.pdf">
              <span class="label">PDF 資料</span>
              <span class="value">
                <el-link :href="venue.dataSources.pdf" target="_blank" type="primary">
                  {{ venue.dataSources.pdfName || venue.dataSources.pdf }}
                </el-link>
              </span>
            </div>
            <div class="info-item full" v-if="venue.dataSources.scrapedAt">
              <span class="label">爬蟲擷取時間</span>
              <span class="value">{{ venue.dataSources.scrapedAt }}</span>
            </div>
          </div>
        </el-card>

        <!-- 會議室 -->
        <el-card class="rooms-card">
          <template #header>
            <div class="card-header">
              <span>會議室 ({{ rooms.length }})</span>
              <el-button type="primary" size="small" :icon="Plus">
                新增會議室
              </el-button>
            </div>
          </template>
          <el-empty v-if="!rooms.length" description="暫無會議室資料" />
          <el-table v-else :data="rooms" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column label="狀態" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="row.isActive !== false ? 'success' : 'danger'" size="small">
                  {{ row.isActive !== false ? '上架' : '下架' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="名稱" min-width="150" />
            <el-table-column label="容量" width="100" align="center">
              <template #default="{ row }">
                {{ row.capacity?.theater || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="定價" min-width="150">
              <template #default="{ row }">
                <span v-if="row.pricing">{{ formatPricing(row.pricing) }}</span>
                <el-text v-else type="warning">未設定</el-text>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="250" align="center">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  :icon="Edit"
                  @click="openRoomEditDialog(row)"
                >
                  編輯
                </el-button>
                <el-button
                  :type="row.isActive !== false ? 'warning' : 'success'"
                  size="small"
                  @click="toggleRoomActive(row)"
                >
                  {{ row.isActive !== false ? '下架' : '上架' }}
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  text
                  @click="viewRoomDetail(row)"
                >
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 相關問題 -->
        <el-card class="problems-card">
          <template #header>
            <div class="card-header">
              <span>相關問題</span>
              <el-link type="primary" @click="$router.push('/problems')">
                查看全部
              </el-link>
            </div>
          </template>
          <div v-loading="problemsLoading">
            <el-empty v-if="!problems.length" description="暫無問題記錄" />
            <div v-else class="problem-list">
              <div
                v-for="problem in problems"
                :key="problem.id"
                class="problem-item"
              >
                <div class="problem-info">
                  <div class="problem-header">
                    <span class="severity-badge" :class="problem.severity" />
                    <el-tag size="small">{{ getProblemTypeLabel(problem.problemType) }}</el-tag>
                    <el-tag :type="getStatusType(problem.status)" size="small">
                      {{ problem.status }}
                    </el-tag>
                  </div>
                  <div class="problem-field">{{ problem.field }}</div>
                  <div v-if="problem.diagnosis" class="problem-diagnosis">
                    診斷：{{ problem.diagnosis }}
                  </div>
                </div>
                <div class="problem-actions">
                  <el-button
                    v-if="!problem.diagnosis"
                    size="small"
                    :icon="MagicStick"
                    @click="handleDiagnose(problem)"
                  >
                    診斷
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 爬蟲任務 -->
        <el-card class="tasks-card">
          <template #header>
            <div class="card-header">
              <span>爬蟲任務</span>
              <el-link type="primary" @click="$router.push('/scrape-tasks')">
                查看全部
              </el-link>
            </div>
          </template>
          <div v-loading="tasksLoading">
            <el-empty v-if="!tasks.length" description="暫無爬蟲記錄" />
            <el-table v-else :data="tasks" stripe>
              <el-table-column prop="id" label="ID" width="60" />
              <el-table-column label="類型" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ getTaskTypeLabel(row.taskType) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="狀態" width="80">
                <template #default="{ row }">
                  <el-tag :type="getTaskStatusType(row.status)" size="small">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="完成時間" width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.completedAt) }}
                </template>
              </el-table-column>
              <el-table-column prop="roomsFound" label="會議室" width="80" align="center" />
              <el-table-column prop="problemsFound" label="問題" width="80" align="center" />
            </el-table>
          </div>
        </el-card>
      </template>
    </div>

    <!-- 編輯場地對話框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="`編輯場地 - ${editForm.name || ''}`"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" label-width="120px">
        <!-- 照片設定 -->
        <el-divider content-position="left">照片設定</el-divider>
        <el-form-item label="主照片 URL">
          <el-input v-model="editForm.images.main" placeholder="主照片 URL">
            <template #append>
              <el-button @click="previewImage(editForm.images.main)">預覽</el-button>
            </template>
          </el-input>
          <div v-if="editForm.images.main" class="image-preview-mini">
            <img :src="editForm.images.main" @error="handleImageError" />
          </div>
        </el-form-item>

        <el-form-item label="相簿照片">
          <div class="gallery-editor">
            <div
              v-for="(url, index) in editForm.images.gallery"
              :key="index"
              class="gallery-item-edit"
            >
              <el-input v-model="editForm.images.gallery[index]" placeholder="照片 URL">
                <template #prepend>{{ index + 1 }}</template>
                <template #append>
                  <el-button @click="previewImage(url)">預覽</el-button>
                  <el-button type="danger" @click="removeGalleryImage(index)">刪除</el-button>
                </template>
              </el-input>
            </div>
            <el-button @click="addGalleryImage" :icon="Plus">新增照片</el-button>
          </div>
        </el-form-item>

        <!-- 基本資訊 -->
        <el-divider content-position="left">基本資訊</el-divider>
        <el-form-item label="場地名稱">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="英文名稱">
          <el-input v-model="editForm.nameEn" />
        </el-form-item>
        <el-form-item label="類型">
          <el-select v-model="editForm.venueType">
            <el-option label="會議中心" value="會議中心" />
            <el-option label="飯店" value="飯店" />
            <el-option label="展覽中心" value="展覽中心" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="城市">
          <el-input v-model="editForm.city" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="editForm.address" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="設備">
          <el-input v-model="editForm.equipment" type="textarea" :rows="2" />
        </el-form-item>

        <!-- 聯絡資訊 -->
        <el-divider content-position="left">聯絡資訊</el-divider>
        <el-form-item label="聯絡電話">
          <el-input v-model="editForm.contactPhone" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="editForm.contactEmail" />
        </el-form-item>
        <el-form-item label="官網 URL">
          <el-input v-model="editForm.url" />
        </el-form-item>

        <!-- 容納人數 -->
        <el-divider content-position="left">容量與價格</el-divider>
        <el-form-item label="戲劇式容納人數">
          <el-input-number v-model="editForm.maxCapacityTheater" :min="0" />
        </el-form-item>
        <el-form-item label="教室式容納人數">
          <el-input-number v-model="editForm.maxCapacityClassroom" :min="0" />
        </el-form-item>
        <el-form-item label="半天價格">
          <el-input-number v-model="editForm.priceHalfDay" :min="0" />
        </el-form-item>
        <el-form-item label="全天價格">
          <el-input-number v-model="editForm.priceFullDay" :min="0" />
        </el-form-item>

        <!-- 時間與規定 -->
        <el-divider content-position="left">時間與規定</el-divider>
        <el-form-item label="平日可用時間">
          <el-input v-model="editForm.availableTimeWeekday" />
        </el-form-item>
        <el-form-item label="假日可用時間">
          <el-input v-model="editForm.availableTimeWeekend" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveVenue" :loading="saving">儲存變更</el-button>
      </template>
    </el-dialog>

    <!-- 編輯會議室對話框 -->
    <el-dialog
      v-model="roomEditDialogVisible"
      :title="'編輯會議室 - ' + (roomEditForm.name || '')"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="roomEditForm" label-width="120px">
        <!-- 基本資訊 -->
        <el-divider content-position="left">基本資訊</el-divider>
        <el-form-item label="名稱">
          <el-input v-model="roomEditForm.name" />
        </el-form-item>
        <el-form-item label="樓層">
          <el-input v-model="roomEditForm.floor" placeholder="例如：1F、B1" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="roomEditForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="面積">
          <el-input v-model="roomEditForm.area" placeholder="例如：100" style="width: 200px" />
          <el-select v-model="roomEditForm.areaUnit" style="width: 120px; margin-left: 10px" placeholder="單位">
            <el-option label="平方公尺 (坪)" value="坪" />
            <el-option label="平方公尺" value="平方公尺" />
            <el-option label="平方米" value="平方米" />
          </el-select>
        </el-form-item>
        <el-form-item label="天花板高度">
          <el-input v-model="roomEditForm.ceilingHeight" placeholder="例如：3.5m" />
        </el-form-item>

        <!-- 容量 -->
        <el-divider content-position="left">容量</el-divider>
        <el-form-item label="戲劇式">
          <el-input-number v-model="roomEditForm.capacity.theater" :min="0" />
        </el-form-item>
        <el-form-item label="教室式">
          <el-input-number v-model="roomEditForm.capacity.classroom" :min="0" />
        </el-form-item>
        <el-form-item label="U 型">
          <el-input-number v-model="roomEditForm.capacity.uShape" :min="0" />
        </el-form-item>
        <el-form-item label="空心方形">
          <el-input-number v-model="roomEditForm.capacity.hollowSquare" :min="0" />
        </el-form-item>

        <!-- 定價 -->
        <el-divider content-position="left">定價</el-divider>
        <el-form-item label="半天價格">
          <el-input v-model="roomEditForm.pricing.halfDay" placeholder="例如：NT$15,000" />
        </el-form-item>
        <el-form-item label="全天價格">
          <el-input v-model="roomEditForm.pricing.fullDay" placeholder="例如：NT$25,000" />
        </el-form-item>
        <el-form-item label="定價備註">
          <el-input v-model="roomEditForm.pricing.note" type="textarea" :rows="2" />
        </el-form-item>

        <!-- 設備 -->
        <el-divider content-position="left">設備</el-divider>
        <el-form-item label="設備">
          <el-input v-model="roomEditForm.equipmentText" type="textarea" :rows="2" placeholder="設備描述，或 JSON 陣列格式" />
        </el-form-item>

        <!-- 照片 -->
        <el-divider content-position="left">照片</el-divider>
        <el-form-item label="主照片 URL">
          <el-input v-model="roomEditForm.images.main" placeholder="主照片 URL">
            <template #append>
              <el-button @click="previewImage(roomEditForm.images.main)">預覽</el-button>
            </template>
          </el-input>
          <div v-if="roomEditForm.images.main" class="image-preview-mini">
            <img :src="roomEditForm.images.main" @error="handleImageError" />
          </div>
        </el-form-item>
        <el-form-item label="相簿照片">
          <div class="gallery-editor">
            <div
              v-for="(url, index) in roomEditForm.images.gallery"
              :key="index"
              class="gallery-item-edit"
            >
              <el-input v-model="roomEditForm.images.gallery[index]" placeholder="照片 URL">
                <template #prepend>{{ index + 1 }}</template>
                <template #append>
                  <el-button @click="previewImage(url)">預覽</el-button>
                  <el-button type="danger" @click="removeRoomGalleryImage(index)">刪除</el-button>
                </template>
              </el-input>
            </div>
            <el-button @click="addRoomGalleryImage" :icon="Plus">新增照片</el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="roomEditDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRoom" :loading="roomSaving">儲存變更</el-button>
      </template>
    </el-dialog>

    <!-- 照片預覽對話框 -->
    <el-dialog v-model="imagePreviewVisible" title="照片預覽" width="60%">
      <div class="image-preview-container">
        <img :src="previewImageUrl" alt="預覽" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowLeft, Edit, Refresh, Plus, MagicStick
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useVenueStore } from '@/stores/venue'
import { useProblemStore } from '@/stores/problem'
import { useScrapeStore } from '@/stores/scrape'
import api from '@/utils/api'
import dayjs from 'dayjs'

const route = useRoute()
const venueStore = useVenueStore()
const problemStore = useProblemStore()
const scrapeStore = useScrapeStore()

const loading = ref(false)
const problemsLoading = ref(false)
const tasksLoading = ref(false)

const venue = ref(null)
const rooms = ref([])
const problems = ref([])
const tasks = ref([])

// 編輯相關狀態
const editDialogVisible = ref(false)
const imagePreviewVisible = ref(false)
const previewImageUrl = ref('')
const saving = ref(false)
const editForm = ref({
  id: null,
  name: '',
  nameEn: '',
  venueType: '',
  city: '',
  address: '',
  description: '',
  equipment: '',
  contactPhone: '',
  contactEmail: '',
  url: '',
  maxCapacityTheater: 0,
  maxCapacityClassroom: 0,
  priceHalfDay: 0,
  priceFullDay: 0,
  availableTimeWeekday: '',
  availableTimeWeekend: '',
  images: {
    main: '',
    gallery: []
  },
  isActive: true
})

// 會議室編輯相關狀態
const roomEditDialogVisible = ref(false)
const roomSaving = ref(false)
const roomEditForm = ref({
  _roomId: '',
  name: '',
  floor: '',
  description: '',
  area: '',
  areaUnit: '',
  ceilingHeight: '',
  capacity: {
    theater: 0,
    classroom: 0,
    uShape: 0,
    hollowSquare: 0
  },
  pricing: {
    halfDay: '',
    fullDay: '',
    note: ''
  },
  equipmentText: '',
  images: {
    main: '',
    gallery: []
  }
})

// Normalized active status: handles both isActive and active fields
// Treats null/undefined as active (venue is active unless explicitly deactivated)
const isActive = computed(() => {
  if (!venue.value) return true
  if (venue.value.isActive !== undefined && venue.value.isActive !== null) return venue.value.isActive
  if (venue.value.active !== undefined && venue.value.active !== null) return venue.value.active
  return true
})

async function fetchData() {
  const venueId = parseInt(route.params.id)
  loading.value = true
  try {
    // 從 API 載入 venues.json（與前端靜態網站完全同步）
    const response = await api.get('/api/v1/admin/venues-json')
    const venuesData = response.data

    const venueData = venuesData.find(v => v.id === venueId)

    if (!venueData) {
      throw new Error('找不到場地')
    }

    venue.value = venueData
    rooms.value = venueData.rooms || []

    // 同時載入問題和爬蟲任務
    await Promise.all([
      fetchProblems(venueId),
      fetchTasks(venueId)
    ])
  } catch (error) {
    console.error('Failed to fetch venue:', error)
    ElMessage.error('載入場地資料失敗: ' + error.message)
  } finally {
    loading.value = false
  }
}

async function fetchProblems(venueId) {
  problemsLoading.value = true
  try {
    const response = await api.get('/api/v1/admin/problems', {
      params: { venue_id: venueId, limit: 10 }
    })
    problems.value = response.data.items || []
  } catch (error) {
    console.error('Failed to fetch problems:', error)
  } finally {
    problemsLoading.value = false
  }
}

async function fetchTasks(venueId) {
  tasksLoading.value = true
  try {
    const response = await api.get('/api/v1/admin/scrape-tasks', {
      params: { venue_id: venueId, limit: 10 }
    })
    tasks.value = response.data
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
  } finally {
    tasksLoading.value = false
  }
}

async function handleDiagnose(problem) {
  try {
    await problemStore.diagnoseProblem(problem.id)
    ElMessage.success('診斷完成')
    fetchProblems(venue.value.id)
  } catch (error) {
    ElMessage.error('診斷失敗')
  }
}

async function toggleActiveStatus() {
  try {
    if (!venue.value) {
      ElMessage.error('場地資料無效')
      return
    }

    const newStatus = !isActive.value
    const reason = newStatus ? '' : await prompt('請輸入下架原因（選填）:')

    if (newStatus && reason !== null && reason === '') {
      // 上架時不詢詢問原因
    } else if (reason === null) {
      // 用戶取消
      return
    }

    await api.put(`/api/v1/venues/${venue.value.id}`, {
      is_active: newStatus,
      status_notes: reason || null
    })

    venue.value.isActive = newStatus; venue.value.active = newStatus
    venue.value.statusNotes = reason || null; venue.value.statusNote = reason || null

    ElMessage.success(newStatus ? '場地已上架' : '場地已下架')
  } catch (error) {
    ElMessage.error('更新狀態失敗')
  }
}

async function toggleRoomActive(room) {
  try {
    if (!room) {
      ElMessage.error('會議室資料無效')
      return
    }

    const newStatus = room.isActive !== false ? false : true
    const roomId = room.id || room.name
    const roomName = room.name || roomId

    // 調用 API 持久化到 venues.json
    await api.put(`/api/v1/admin/venues/${venue.value.id}/rooms/${roomId}/status`, null, {
      params: { is_active: newStatus }
    })

    // 更新本地狀態
    const roomIndex = rooms.value.findIndex(r => r.id === roomId || r.name === roomName)
    if (roomIndex !== -1) {
      rooms.value[roomIndex].isActive = newStatus
    }

    ElMessage.success(`${roomName} 已${newStatus ? '上架' : '下架'}`)
  } catch (error) {
    console.error('Toggle room active error:', error)
    ElMessage.error('更新狀態失敗: ' + (error.response?.data?.detail || error.message))
  }
}

function viewRoomDetail(room) {
  // 跳轉到會議室詳情頁面（與前台同步）
  const roomId = room.id || room.name
  // 打開新標籤顠�指向前台會議室詳情
  window.open(`https://taiwan-venues-new-indol.vercel.app/room.html?venueId=${venue.value.id}&roomId=${roomId}`, '_blank')
}



// ===== 編輯相關函數 =====
function openEditDialog() {
  if (!venue.value) return

  // 深拷貝場地資料到編輯表單
  editForm.value = JSON.parse(JSON.stringify(venue.value))

  // 確保 images 結構完整
  if (!editForm.value.images) {
    editForm.value.images = { main: '', gallery: [] }
  }
  if (!editForm.value.images.gallery) {
    editForm.value.images.gallery = []
  }

  editDialogVisible.value = true
}

async function saveVenue() {
  try {
    saving.value = true

    // 調用 API 更新場地資料
    await api.put(`/api/v1/admin/venues/${editForm.value.id}`, editForm.value)

    // 更新本地狀態
    venue.value = JSON.parse(JSON.stringify(editForm.value))

    // 重新載入資料以確保同步
    await fetchData()

    ElMessage.success('場地資料已更新')
    editDialogVisible.value = false
  } catch (error) {
    console.error('Save venue error:', error)
    ElMessage.error('儲存失敗: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

function previewImage(url) {
  if (!url) {
    ElMessage.warning('請先輸入照片 URL')
    return
  }
  previewImageUrl.value = url
  imagePreviewVisible.value = true
}

function handleImageError(event) {
  event.target.src = 'https://via.placeholder.com/400x300?text=Invalid+Image'
}

function addGalleryImage() {
  editForm.value.images.gallery.push('')
}

function removeGalleryImage(index) {
  editForm.value.images.gallery.splice(index, 1)
}

// ===== 會議室編輯相關函數 =====
function openRoomEditDialog(room) {
  if (!room) return

  const roomId = room.id || room.name

  // 深拷貝會議室資料到編輯表單
  const roomCopy = JSON.parse(JSON.stringify(room))

  roomEditForm.value = {
    _roomId: roomId,
    name: roomCopy.name || '',
    floor: roomCopy.floor || '',
    description: roomCopy.description || '',
    area: roomCopy.area || '',
    areaUnit: roomCopy.areaUnit || '',
    ceilingHeight: roomCopy.ceilingHeight || '',
    capacity: {
      theater: roomCopy.capacity?.theater || 0,
      classroom: roomCopy.capacity?.classroom || 0,
      uShape: roomCopy.capacity?.uShape || 0,
      hollowSquare: roomCopy.capacity?.hollowSquare || 0
    },
    pricing: {
      halfDay: roomCopy.pricing?.halfDay || '',
      fullDay: roomCopy.pricing?.fullDay || '',
      note: roomCopy.pricing?.note || ''
    },
    equipmentText: '',
    images: {
      main: roomCopy.images?.main || '',
      gallery: Array.isArray(roomCopy.images?.gallery) ? [...roomCopy.images.gallery] : []
    }
  }

  // 處理 equipment 欄位（可能是字串或陣列）
  if (roomCopy.equipment) {
    if (Array.isArray(roomCopy.equipment)) {
      roomEditForm.value.equipmentText = JSON.stringify(roomCopy.equipment)
    } else {
      roomEditForm.value.equipmentText = roomCopy.equipment
    }
  }

  roomEditDialogVisible.value = true
}

async function saveRoom() {
  try {
    roomSaving.value = true

    const roomId = roomEditForm.value._roomId

    // 建構更新 payload（不包含 _roomId）
    const payload = {
      name: roomEditForm.value.name,
      floor: roomEditForm.value.floor,
      description: roomEditForm.value.description,
      area: roomEditForm.value.area,
      areaUnit: roomEditForm.value.areaUnit,
      ceilingHeight: roomEditForm.value.ceilingHeight,
      capacity: {
        theater: roomEditForm.value.capacity.theater,
        classroom: roomEditForm.value.capacity.classroom,
        uShape: roomEditForm.value.capacity.uShape,
        hollowSquare: roomEditForm.value.capacity.hollowSquare
      },
      pricing: {
        halfDay: roomEditForm.value.pricing.halfDay,
        fullDay: roomEditForm.value.pricing.fullDay,
        note: roomEditForm.value.pricing.note
      },
      equipment: roomEditForm.value.equipmentText || null,
      images: {
        main: roomEditForm.value.images.main,
        gallery: roomEditForm.value.images.gallery
      }
    }

    // 調用 API 更新會議室資料
    await api.put(`/api/v1/admin/venues/${venue.value.id}/rooms/${roomId}`, payload)

    // 重新載入資料以確保同步
    await fetchData()

    ElMessage.success('會議室資料已更新')
    roomEditDialogVisible.value = false
  } catch (error) {
    console.error('Save room error:', error)
    ElMessage.error('儲存失敗: ' + (error.response?.data?.detail || error.message))
  } finally {
    roomSaving.value = false
  }
}

function addRoomGalleryImage() {
  roomEditForm.value.images.gallery.push('')
}

function removeRoomGalleryImage(index) {
  roomEditForm.value.images.gallery.splice(index, 1)
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

function parseAmenities(amenities) {
  if (!amenities) return []
  if (Array.isArray(amenities)) return amenities
  if (typeof amenities === 'string') {
    try {
      return JSON.parse(amenities)
    } catch {
      return amenities.split(',').map(s => s.trim())
    }
  }
  return []
}

function formatPricing(pricing) {
  if (typeof pricing === 'string') {
    try {
      pricing = JSON.parse(pricing)
    } catch {
      return pricing
    }
  }

  if (pricing && typeof pricing === 'object') {
    if (pricing.hourly) return `時: ${pricing.hourly}`
    if (pricing.daily) return `日: ${pricing.daily}`
    if (pricing.fullDay) return `全日: ${pricing.fullDay}`
  }
  return JSON.stringify(pricing)
}

function getProblemTypeLabel(type) {
  const labels = {
    missing_rooms: '缺少會議室',
    missing_pricing: '缺少定價',
    missing_capacity: '缺少容量',
    missing_images: '缺少圖片',
    invalid_schema: 'Schema 錯誤'
  }
  return labels[type] || type
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

function getTaskTypeLabel(type) {
  const labels = {
    full: '完整爬取',
    incremental: '增量更新',
    verify: '驗證'
  }
  return labels[type] || type
}

function getTaskStatusType(status) {
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
.venue-detail-page {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .info-card,
  .rooms-card,
  .problems-card,
  .tasks-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;

    .info-item {
      display: flex;
      flex-direction: column;

      &.full {
        grid-column: 1 / -1;
      }

      .label {
        font-size: 12px;
        color: #909399;
        margin-bottom: 5px;
      }

      .value {
        color: #303133;
        word-break: break-word;
      }
    }
  }

  .problem-list {
    .problem-item {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 12px;
      border: 1px solid #f0f0f0;
      border-radius: 4px;
      margin-bottom: 10px;

      &:last-child {
        margin-bottom: 0;
      }

      .problem-info {
        flex: 1;

        .problem-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
        }

        .problem-field {
          color: #606266;
          margin-bottom: 5px;
        }

        .problem-diagnosis {
          font-size: 12px;
          color: #909399;
        }
      }

      .problem-actions {
        margin-left: 15px;
      }
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

.image-preview-mini {
  margin-top: 8px;
  max-width: 300px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e4e7ed;

  img {
    width: 100%;
    height: auto;
    display: block;
  }
}

.gallery-editor {
  width: 100%;

  .gallery-item-edit {
    margin-bottom: 8px;
  }
}

.image-preview-container {
  text-align: center;

  img {
    max-width: 100%;
    max-height: 70vh;
    border-radius: 8px;
  }
}
</style>
