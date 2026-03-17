import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const parserUrl = ref('http://localhost:8000')
  const backendUrl = ref('http://localhost:8081')

  return { parserUrl, backendUrl }
})
