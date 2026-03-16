import axios from 'axios'

const api = axios.create({
    baseURL: '/api',
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' }
})

// Request interceptor
api.interceptors.request.use(config => {
    return config
}, error => Promise.reject(error))

// Response interceptor – normalize errors
api.interceptors.response.use(
    res => res.data,
    err => {
        const message =
            err.response?.data?.detail ||
            err.response?.data?.message ||
            err.message ||
            'Lỗi không xác định'
        return Promise.reject(new Error(message))
    }
)

export const healthCheck = () => api.get('/health')
export const getMotorcycles = (params = {}) => api.get('/motorcycles', { params })
export const getStats = () => api.get('/motorcycles/stats')
export const recommend = (payload) => api.post('/recommend', payload)
export const calculateAHP = (matrix, names) => api.post('/ahp/calculate', { matrix, names })
export const getDemo = () => api.get('/demo')
export const retrainModel = (n_samples) => api.post('/retrain', { n_samples })
export const sensitivityRank = (weights, motorcycles) =>
    api.post('/sensitivity/rank', { weights, motorcycles })

export default api
