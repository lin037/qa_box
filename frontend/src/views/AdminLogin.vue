<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <!-- Logo / Title -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-black rounded-2xl mb-4">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">QA Box 管理后台</h1>
        <p class="text-gray-500 mt-2">请登录以继续</p>
      </div>

      <!-- Login Form -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Username -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
              用户名
            </label>
            <input
              id="username"
              v-model="username"
              type="text"
              required
              autocomplete="username"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition-all"
              placeholder="请输入用户名"
            />
          </div>

          <!-- Password -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              密码
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              autocomplete="current-password"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition-all"
              placeholder="请输入密码"
            />
          </div>

          <!-- Error Message -->
          <div v-if="errorMsg" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-sm text-red-600">{{ errorMsg }}</p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-black text-white rounded-lg font-medium hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            <svg v-if="loading" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ loading ? '登录中...' : '登录' }}</span>
          </button>
        </form>
      </div>

      <!-- Footer -->
      <p class="text-center text-gray-400 text-sm mt-6">
        QA Box &copy; {{ new Date().getFullYear() }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { questionApi } from '@/api'
import { ADMIN_ROUTE } from '@/router'

const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

const handleLogin = async () => {
  if (!username.value.trim() || !password.value.trim()) {
    errorMsg.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const res = await questionApi.adminLogin(username.value, password.value)
    
    // 保存 Token
    localStorage.setItem('admin_token', res.data.access_token)
    
    // 跳转到管理页面
    router.push(ADMIN_ROUTE)
  } catch (err) {
    console.error('Login failed:', err)
    if (err.response && err.response.status === 401) {
      errorMsg.value = '用户名或密码错误'
    } else {
      errorMsg.value = '登录失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}
</script>
