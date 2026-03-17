import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from './api.js'

export const useHistoryStore = defineStore('history', () => {
  const analyses = ref([])

  async function load() {
    try {
      analyses.value = await api.fetchAnalyses()
    } catch (e) {
      console.error('Failed to load history', e)
    }
  }

  async function remove(id) {
    try {
      await api.deleteAnalysis(id)
      analyses.value = analyses.value.filter(a => a.id !== id)
    } catch (e) {
      console.error('Failed to delete analysis', e)
    }
  }

  return { analyses, load, remove }
})
