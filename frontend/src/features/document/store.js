import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from './api.js'

export const useDocumentStore = defineStore('document', () => {
  const documents = ref([])
  const selectedId = ref(null)
  const uploading = ref(false)

  async function load() {
    try {
      documents.value = await api.fetchDocuments()
    } catch (e) {
      console.error('Failed to load documents', e)
    }
  }

  async function upload(file) {
    uploading.value = true
    try {
      const doc = await api.uploadDocument(file)
      documents.value.unshift(doc)
      selectedId.value = doc.id
      return doc
    } catch (e) {
      console.error('Failed to upload document', e)
      throw e
    } finally {
      uploading.value = false
    }
  }

  async function remove(id) {
    try {
      await api.deleteDocument(id)
      documents.value = documents.value.filter(d => d.id !== id)
      if (selectedId.value === id) selectedId.value = null
    } catch (e) {
      console.error('Failed to delete document', e)
    }
  }

  function select(id) {
    selectedId.value = id
  }

  return { documents, selectedId, uploading, load, upload, remove, select }
})
