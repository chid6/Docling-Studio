<template>
  <div class="settings-panel">
    <div class="setting-group">
      <label class="setting-label">API URL</label>
      <input class="setting-input" v-model="store.apiUrl" readonly />
    </div>
    <div class="setting-group">
      <label class="setting-label">Version</label>
      <span class="setting-value">0.1.0</span>
    </div>
  </div>
</template>

<script setup>
import { useSettingsStore } from '../store.js'
const store = useSettingsStore()
</script>

<style scoped>
.settings-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 500px;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.setting-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.setting-input {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  color: var(--text);
  font-size: 13px;
  font-family: 'IBM Plex Mono', monospace;
}

.setting-value {
  font-size: 14px;
  color: var(--text);
  font-family: 'IBM Plex Mono', monospace;
}
</style>
