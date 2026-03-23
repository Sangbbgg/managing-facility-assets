import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 30000,
})

client.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || '서버 오류가 발생했습니다'
    console.error('[API Error]', err.config?.url, msg)
    return Promise.reject(new Error(msg))
  }
)

export default client
