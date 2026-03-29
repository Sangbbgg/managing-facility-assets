import { defineStore } from 'pinia'
import { ref } from 'vue'

import { personsApi, departmentsApi } from '@/api/personsApi'

export const usePersonStore = defineStore('person', () => {
  const personList = ref([])
  const deptList = ref([])
  const loading = ref(false)

  async function fetchPersons() {
    loading.value = true
    try {
      personList.value = await personsApi.list()
    } finally {
      loading.value = false
    }
  }

  async function fetchDepts() {
    deptList.value = await departmentsApi.list()
  }

  async function createPerson(body) {
    const item = await personsApi.create(body)
    personList.value.push(item)
  }

  async function updatePerson(id, body) {
    const item = await personsApi.update(id, body)
    const index = personList.value.findIndex((person) => person.id === id)
    if (index !== -1) personList.value[index] = item
  }

  async function removePerson(id) {
    await personsApi.remove(id)
    personList.value = personList.value.filter((person) => person.id !== id)
  }

  async function createDept(body) {
    const item = await departmentsApi.create(body)
    deptList.value.push(item)
  }

  async function updateDept(id, body) {
    const item = await departmentsApi.update(id, body)
    const index = deptList.value.findIndex((dept) => dept.id === id)
    if (index !== -1) deptList.value[index] = item
  }

  async function removeDept(id) {
    await departmentsApi.remove(id)
    deptList.value = deptList.value.filter((dept) => dept.id !== id)
  }

  const list = personList
  const fetchList = fetchPersons

  return {
    personList,
    deptList,
    loading,
    list,
    fetchList,
    fetchPersons,
    fetchDepts,
    createPerson,
    updatePerson,
    removePerson,
    createDept,
    updateDept,
    removeDept,
  }
})
