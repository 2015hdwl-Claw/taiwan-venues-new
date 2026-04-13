<template>
  <div class="admin-layout">
    <!-- 側邊欄 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="logo">
        <h2 v-if="!isCollapsed">EventMaster</h2>
        <h2 v-else>EM</h2>
      </div>

      <el-menu
        :default-active="currentRoute"
        :collapse="isCollapsed"
        background-color="#001529"
        text-color="#ffffff"
        active-text-color="#409eff"
        router
      >
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <template #title>儀表板</template>
        </el-menu-item>

        <el-menu-item index="/venues">
          <el-icon><OfficeBuilding /></el-icon>
          <template #title>場地管理</template>
        </el-menu-item>

        <el-menu-item index="/problems">
          <el-icon><Warning /></el-icon>
          <template #title>問題追蹤</template>
        </el-menu-item>

        <el-menu-item index="/scrape-tasks">
          <el-icon><Download /></el-icon>
          <template #title>爬蟲任務</template>
        </el-menu-item>

        <el-menu-item index="/conversations">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>對話記錄</template>
        </el-menu-item>

        <el-menu-item index="/analytics">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>數據分析</template>
        </el-menu-item>
      </el-menu>
    </aside>

    <!-- 主內容區 -->
    <div class="main-content">
      <!-- 頂部導航 -->
      <header class="header">
        <div class="header-left">
          <el-button
            :icon="isCollapsed ? DArrowRight : DArrowLeft"
            text
            @click="toggleCollapse"
          />
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首頁</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentPage">{{ currentPage }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-dropdown">
              <el-avatar :size="32" :icon="User" />
              <span class="username">管理員</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>個人資料
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>系統設置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>登出
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 內容區 -->
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DArrowLeft, DArrowRight, User, Setting, SwitchButton,
  Odometer, OfficeBuilding, Warning, Download, ChatDotRound, DataAnalysis
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapsed = ref(false)

const currentRoute = computed(() => route.path)
const currentPage = computed(() => route.meta?.title || '')

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}

async function handleCommand(command) {
  switch (command) {
    case 'profile':
      ElMessage.info('個人資料功能開發中')
      break
    case 'settings':
      ElMessage.info('系統設置功能開發中')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('確定要登出嗎？', '提示', {
          confirmButtonText: '確定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        authStore.clearAuth()
        ElMessage.success('已登出')
        router.push('/login')
      } catch {
        // 用戶取消
      }
      break
  }
}
</script>

<style lang="scss" scoped>
.admin-layout {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 220px;
  background: #001529;
  flex-shrink: 0;
  transition: width 0.3s;
  overflow: hidden;

  &.collapsed {
    width: 64px;

    .logo h2 {
      font-size: 20px;
    }
  }

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    h2 {
      margin: 0;
      font-size: 24px;
      transition: font-size 0.3s;
    }
  }

  .el-menu {
    border-right: none;
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 60px;
  background: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 15px;
  }

  .header-right {
    .user-dropdown {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;

      .username {
        color: #303133;
      }
    }
  }
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f5f5;
}
</style>
