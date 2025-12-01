import axios from 'axios'

const service = axios.create({
    baseURL: '',
    timeout: 10000
})

// Request interceptor - 添加 Admin Token
service.interceptors.request.use(
    config => {
        // 如果是 admin 接口，添加 Authorization header
        if (config.url && config.url.includes('/console-x7k9m')) {
            const token = localStorage.getItem('admin_token')
            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`
            }
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// Response interceptor - 处理 Token 续期和认证错误
service.interceptors.response.use(
    response => {
        // 检查是否有新 Token (续期)
        const newToken = response.headers['x-new-token']
        if (newToken) {
            localStorage.setItem('admin_token', newToken)
            console.log('[Auth] Token refreshed')
        }
        return response
    },
    error => {
        // 处理 401 错误 - 跳转到登录页
        if (error.response && error.response.status === 401) {
            // 如果是 admin 接口的 401，清除 token 并跳转登录
            if (error.config.url && error.config.url.includes('/console-x7k9m')) {
                localStorage.removeItem('admin_token')
                // 避免在登录页循环跳转
                if (!window.location.pathname.includes('/login')) {
                    window.location.href = '/console-x7k9m/login'
                }
            }
        }
        return Promise.reject(error)
    }
)

export default service
