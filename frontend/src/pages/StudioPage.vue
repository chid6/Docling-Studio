<template>
  <div class="studio-page">
    <div class="studio-header">
      <h1 class="studio-title">Document Analysis</h1>
    </div>
    <div class="studio-content">
      <div class="input-panel">
        <AnalysisPanel />
      </div>
      <div class="output-panel">
        <ResultTabs />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useDocumentStore } from '../features/document/store.js'
import { useAnalysisStore } from '../features/analysis/store.js'
import { AnalysisPanel, ResultTabs } from '../features/analysis/index.js'

const documentStore = useDocumentStore()
const analysisStore = useAnalysisStore()

onMounted(() => {
  documentStore.load()
  analysisStore.load()
})
</script>

<style scoped>
.studio-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.studio-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.studio-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
}

.studio-content {
  flex: 1;
  display: grid;
  grid-template-columns: 360px 1fr;
  overflow: hidden;
}

.input-panel {
  border-right: 1px solid var(--border);
  overflow: hidden;
}

.output-panel {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>
