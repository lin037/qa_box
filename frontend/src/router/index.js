import { createRouter, createWebHistory } from 'vue-router'
import AskPage from '../views/AskPage.vue'
import AdminPage from '../views/AdminPage.vue'
import AdminLogin from '../views/AdminLogin.vue'

// 管理后台路由前缀 - 从环境变量读取，需要与后端 ADMIN_ROUTE_PREFIX 保持一致
const ADMIN_ROUTE = import.meta.env.VITE_ADMIN_ROUTE_PREFIX || '/console-x7k9m'

const routes = [
  { path: '/', component: AskPage },
  { 
    path: `${ADMIN_ROUTE}/login`, 
    name: 'AdminLogin',
    component: AdminLogin 
  },
  { 
    path: ADMIN_ROUTE, 
    name: 'Admin',
    component: AdminPage,
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫 - 检查管理后台登录状态
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('admin_token')
    if (!token) {
      next({ name: 'AdminLogin' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router

// 导出管理路由前缀供其他模块使用
export { ADMIN_ROUTE }
