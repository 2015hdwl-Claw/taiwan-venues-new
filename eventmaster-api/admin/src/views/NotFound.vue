<template>
  <div class="not-found">
    <div class="content">
      <h1>404</h1>
      <p>頁面不存在</p>
      <el-button type="primary" @click="$router.push('/')">
        返回首頁
      </el-button>
    </div>
  </div>
</template>

<script setup>
// No script needed
</script>

<style lang="scss" scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: #f5f5f5;

  .content {
    text-align: center;

    h1 {
      font-size: 120px;
      color: #409eff;
      margin: 0 0 20px 0;
    }

    p {
      font-size: 18px;
      color: #606266;
      margin: 0 0 30px 0;
    }
  }
}
</style>
