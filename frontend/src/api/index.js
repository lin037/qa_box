import request from '@/utils/request'

// 管理后台 API 前缀 - 从环境变量读取，需要与后端 ADMIN_ROUTE_PREFIX 保持一致
const ADMIN_ROUTE = import.meta.env.VITE_ADMIN_ROUTE_PREFIX || '/console-x7k9m'
const ADMIN_API_PREFIX = `/api${ADMIN_ROUTE}`

export const questionApi = {
    // ============================================
    // 公共接口
    // ============================================
    uploadImage(formData) {
        // Try to get admin token for size limit exemption
        const token = localStorage.getItem('admin_token')
        const headers = {}
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`
        }
        
        return request.post('/api/upload', formData, { headers })
    },
    
    submitQuestion(data) {
        return request.post('/api/questions', data)
    },
    
    revokeQuestion(token) {
        return request.post('/api/questions/revoke', { token })
    },
    
    getPublicQuestions(skip = 0, limit = 20) {
        return request.get('/api/public/questions', { params: { skip, limit } })
    },
    
    getQuestion(id) {
        return request.get(`/api/questions/${id}`)
    },

    getMyQuestions(questionIds) {
        return request.post('/api/questions/batch', questionIds)
    },

    // ============================================
    // Admin 接口
    // ============================================
    adminLogin(username, password) {
        return request.post(`${ADMIN_API_PREFIX}/login`, { username, password })
    },

    adminVerifyToken() {
        return request.post(`${ADMIN_API_PREFIX}/verify`)
    },

    getQuestions() {
        return request.get(`${ADMIN_API_PREFIX}/questions`)
    },
    
    updateQuestion(id, data) {
        return request.put(`${ADMIN_API_PREFIX}/questions/${id}`, data)
    },

    answerQuestion(id, data) {
        return request.post(`${ADMIN_API_PREFIX}/questions/${id}/answer`, data)
    },

    deleteQuestion(id) {
        return request.delete(`${ADMIN_API_PREFIX}/questions/${id}`)
    }
}
