<template>
  <div class="settings-page">
    <div class="page-header">
      <h1 class="page-title">Settings</h1>
    </div>
    <div class="page-content">
      <SettingsPanel />
    </div>
  </div>
</template>

<script setup>
import { SettingsPanel } from '../features/settings/index.js'
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.page-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>
