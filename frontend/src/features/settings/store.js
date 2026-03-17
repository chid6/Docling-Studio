import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const apiUrl = ref('http://localhost:8000')

  return { apiUrl }
})
