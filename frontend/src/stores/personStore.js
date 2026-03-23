import { defineStore } from 'pinia'
import { ref } from 'vue'
import { personsApi, departmentsApi } from '@/api/personsApi'

export const usePersonStore = defineStore('person', () => {
  const personList = ref([])
  const deptList   = ref([])
  const loading    = ref(false)

  async function fetchPersons() {
    loading.value = true
    try { personList.value = await personsApi.list() }
    finally { loading.value = false }
  }

  async function fetchDepts() {
    deptList.value = await departmentsApi.list()
  }

  async function createPerson(body)       { const item = await personsApi.create(body); personList.value.push(item) }
  async function updatePerson(id, body)   { const item = await personsApi.update(id, body); const idx = personList.value.findIndex(p => p.id === id); if (idx !== -1) personList.value[idx] = item }
  async function removePerson(id)         { await personsApi.remove(id); personList.value = personList.value.filter(p => p.id !== id) }

  async function createDept(body)         { const item = await departmentsApi.create(body); deptList.value.push(item) }
  async function updateDept(id, body)     { const item = await departmentsApi.update(id, body); const idx = deptList.value.findIndex(d => d.id === id); if (idx !== -1) deptList.value[idx] = item }
  async function removeDept(id)           { await departmentsApi.remove(id); deptList.value = deptList.value.filter(d => d.id !== id) }

  return { personList, deptList, loading, fetchPersons, fetchDepts, createPerson, updatePerson, removePerson, createDept, updateDept, removeDept }
})
