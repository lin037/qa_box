<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-8 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    
    <div class="w-full max-w-7xl flex flex-col md:flex-row gap-12 md:h-[85vh]">
        
        <!-- Left Column: Mailbox & Input Area -->
        <div class="relative flex-1 flex flex-col items-center justify-center perspective-1000 order-1 md:order-none min-h-[80vh] md:min-h-0 md:pt-24">
             <!-- Header (Mobile Only) -->
             <div 
                class="text-center mb-8 md:hidden w-full transition-opacity duration-300"
                :class="{ 'opacity-0 pointer-events-none': isSent }"
             >
                 <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">匿名提问箱</h1>
                 <p class="text-sm text-gray-600">向我投递你的秘密或困惑</p>
             </div>
             
             <!-- Header (Desktop - above mailbox) -->
             <div class="text-center mb-8 hidden md:block z-10 w-full absolute top-0 left-0 right-0">
                 <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">匿名提问箱</h1>
                 <p class="text-sm text-gray-600">向我投递你的秘密或困惑</p>
             </div>
             <!-- Mailbox Container (Background) -->
             <div 
                class="absolute inset-0 flex items-center justify-center transition-all duration-700 ease-in-out"
                :class="{ 
                    'blur-sm scale-90 opacity-80': !isAnimating && !isSent, 
                    'blur-0 scale-110 opacity-100': isAnimating || isSent
                }"
             >
                <!-- Redesigned Mailbox: Modern Rounded Box Style -->
                <div class="relative w-72 h-80 bg-gradient-to-b from-gray-800 to-black rounded-[3rem] shadow-2xl flex flex-col items-center border-t border-white/10">
                     <!-- Lid / Top Section -->
                     <div class="w-full h-32 bg-black/30 rounded-t-[3rem] border-b border-gray-900/50 flex items-center justify-center relative">
                         <!-- Slot -->
                         <div class="w-48 h-4 bg-black/60 rounded-full shadow-[inset_0_2px_4px_rgba(0,0,0,0.8)] border-b border-white/10"></div>
                     </div>
                     
                     <!-- Body Section -->
                     <div class="flex-1 w-full flex flex-col items-center justify-center relative">
                         <!-- Label -->
                         <div class="font-black text-gray-200/80 tracking-[0.5em] text-2xl">MAIL</div>
                         <div class="text-gray-400/50 text-[10px] tracking-widest mt-1">QA BOX</div>
                         
                         <!-- Decorative Lines -->
                         <div class="absolute bottom-8 w-12 h-1 bg-gray-700/40 rounded-full"></div>
                         <div class="absolute bottom-6 w-8 h-1 bg-gray-700/40 rounded-full"></div>
                     </div>

                     <!-- Success State (INSIDE Mailbox) -->
                     <div v-if="isSent && !isAnimating" class="absolute inset-0 z-30 flex flex-col items-center justify-center p-6 text-center animate-fade-in-up bg-white/95 backdrop-blur-sm rounded-[3rem] overflow-hidden">
                         <div class="flex items-center justify-center h-10 w-10 rounded-full bg-green-100 mb-3 shadow-inner shrink-0">
                            <svg class="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                         </div>
                         <h3 class="text-lg font-bold text-gray-900 mb-1">投递成功!</h3>
                         <p class="text-xs text-gray-500 mb-4">信件已安全落入信箱。</p>
                         
                         <div class="space-y-2 w-full px-2">
                             <button @click="resetForm" class="w-full py-2 px-4 bg-gray-900 hover:bg-black text-white rounded-lg shadow transition-colors font-medium text-xs">
                                再写一封
                             </button>
                             <button v-if="canRevoke" @click="revokeQuestion" class="w-full py-2 px-4 bg-gray-50 hover:bg-gray-100 text-gray-700 border border-gray-200 rounded-lg transition-colors text-xs">
                                撤回
                             </button>
                         </div>
                     </div>
                </div>
             </div>

             <!-- Envelope / Input Form -->
             <div 
                class="w-full max-w-md bg-white rounded-xl shadow-2xl p-8 relative z-20 transition-all duration-700 ease-in-out transform"
                :class="{ 
                    'translate-y-[200px] -translate-z-[200px] scale-50 opacity-0': isAnimating,
                    'opacity-100': !isSent && !isAnimating,
                    'hidden': isSent && !isAnimating
                }"
             >
                <div class="absolute -top-3 -right-3 w-12 h-12 bg-red-500 rounded-full flex items-center justify-center shadow-lg transform rotate-12">
                    <span class="text-white font-bold text-xs">NEW</span>
                </div>

                <div class="mb-6 border-b-2 border-dashed border-gray-200 pb-4">
                    <h2 class="text-2xl font-serif text-gray-800 font-bold md:block hidden">写信给林叁柒</h2>
                    <div class="flex justify-between items-center text-sm text-gray-500 mt-1">
                        <span>From: 匿名朋友</span>
                        <span class="font-mono">{{ new Date().toLocaleDateString() }}</span>
                    </div>
                </div>
                
                <textarea 
                    v-model="questionContent"
                    class="w-full h-40 resize-none outline-none text-gray-700 bg-gray-50/50 p-4 rounded-lg placeholder-gray-400 focus:bg-gray-100 focus:ring-2 focus:ring-gray-300 transition-all"
                    placeholder="在此写下你想问的问题..."
                ></textarea>
                
                <div class="mt-4 grid grid-cols-4 gap-2">
                    <div v-for="(img, idx) in images" :key="idx" class="relative aspect-square rounded-lg overflow-hidden group shadow-sm">
                        <img :src="img.preview" class="w-full h-full object-cover" />
                        <button @click="removeImage(idx)" class="absolute inset-0 bg-black/40 text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <span class="text-xl font-bold">×</span>
                        </button>
                    </div>
                    <label v-if="images.length < 9" class="aspect-square border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center text-gray-400 hover:border-gray-600 hover:text-gray-700 hover:bg-gray-50 cursor-pointer transition-all">
                        <span class="text-2xl mb-1">+</span>
                        <span class="text-[10px] uppercase font-bold">Photo</span>
                        <input type="file" accept="image/*" multiple class="hidden" @change="handleImageUpload" />
                    </label>
                </div>
                
                <button 
                    @click="triggerSendAnimation"
                    :disabled="!canSend"
                    class="mt-8 w-full bg-gray-900 hover:bg-black text-white font-bold py-4 px-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                    <span class="tracking-widest uppercase text-sm">投递信件</span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                </button>
             </div>
        </div>

        <!-- Right Column: Q&A List -->
        <div class="flex-1 flex flex-col h-full bg-white/80 backdrop-blur-md rounded-2xl shadow-xl border border-white/50 overflow-hidden order-2 md:order-none min-h-[50vh]">
            
            <!-- Mobile Scroll Hint (Bottom) -->
            <div class="md:hidden text-center py-2 text-xs text-gray-400">
                向下滚动查看更多问答
            </div>
            
            <div class="p-6 border-b border-gray-100 bg-white/50 sticky top-0 z-10">
                <div class="flex space-x-1 bg-gray-100 p-1 rounded-lg">
                    <button 
                        v-for="tab in ['public', 'mine']" 
                        :key="tab"
                        @click="changeTab(tab)"
                        class="flex-1 py-2 text-sm font-medium rounded-md transition-all duration-200"
                        :class="currentTab === tab ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                    >
                        {{ tab === 'public' ? '大家的提问' : '我的记录' }}
                    </button>
                </div>
            </div>

            <div class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
                <!-- Public List -->
                <template v-if="currentTab === 'public'">
                     <div v-if="publicQuestions.length === 0" class="h-full flex flex-col items-center justify-center text-gray-400">
                        <svg class="w-16 h-16 mb-4 opacity-20" fill="currentColor" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
                        <p>暂时还没有公开的回答</p>
                     </div>
                     <div 
                        v-for="q in publicQuestions" 
                        :key="q.id" 
                        @click="openQuestionDetail(q)"
                        class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer hover:border-gray-300 max-w-2xl mx-auto"
                     >
                        <!-- Card Header -->
                        <div class="flex items-start gap-3 mb-3">
                            <div class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-700 shrink-0">
                                <span class="font-bold text-xs">Q</span>
                            </div>
                            <div class="flex-1">
                                <div class="font-medium text-gray-900 text-base line-clamp-2 leading-relaxed">
                                    {{ q.content }}
                                </div>
                                <div class="text-xs text-gray-400 mt-1">{{ new Date(q.created_at).toLocaleDateString() }}</div>
                            </div>
                        </div>
                        
                        <!-- Images Thumbnail -->
                        <div v-if="q.images && q.images.length" class="mb-4 pl-11">
                            <div class="flex gap-2">
                                <img v-for="(img, i) in q.images.slice(0,3)" :key="i" :src="img" class="w-16 h-16 object-cover rounded-lg border border-gray-100" />
                                <div v-if="q.images.length > 3" class="w-16 h-16 bg-gray-50 rounded-lg flex items-center justify-center text-xs text-gray-400 border border-gray-100">
                                    +{{ q.images.length - 3 }}
                                </div>
                            </div>
                        </div>

                        <!-- Answer Section -->
                        <div class="relative pl-4 ml-3 border-l-2 border-gray-200">
                             <div class="flex items-start gap-2">
                                <div class="w-5 h-5 rounded-full bg-gray-800 flex items-center justify-center text-white shrink-0 mt-0.5">
                                    <span class="font-bold text-[10px]">A</span>
                                </div>
                                <div>
                                    <div class="text-gray-600 whitespace-pre-wrap text-sm leading-relaxed line-clamp-3">
                                        {{ q.answer_content }}
                                    </div>
                                     <div v-if="q.answer_images && q.answer_images.length" class="flex gap-1 mt-2">
                                         <div class="text-xs text-gray-400 flex items-center gap-1">
                                             <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                                             <span>查看图片</span>
                                         </div>
                                     </div>
                                </div>
                             </div>
                        </div>
                     </div>
                     
                     <!-- Pagination Load More -->
                     <div v-if="publicQuestions.length > 0" class="text-center pt-4 pb-2">
                         <button 
                            v-if="hasMorePublic" 
                            @click="loadMorePublicQuestions" 
                            class="px-6 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 shadow-sm transition-colors disabled:opacity-50"
                            :disabled="isLoadingMore"
                         >
                            {{ isLoadingMore ? '加载中...' : '加载更多' }}
                         </button>
                         <span v-else class="text-xs text-gray-400">没有更多了</span>
                     </div>
                </template>

                <!-- My History (With Pagination) -->
                <template v-if="currentTab === 'mine'">
                     <div v-if="myQuestions.length === 0" class="h-full flex flex-col items-center justify-center text-gray-400">
                        <p>这里空空如也</p>
                        <p class="text-xs mt-2 opacity-60">在这个设备上还没有投递记录</p>
                     </div>
                     <div 
                        v-for="q in myQuestions" 
                        :key="q.id" 
                        @click="openQuestionDetail(q)"
                        class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer hover:border-gray-300 max-w-2xl mx-auto"
                     >
                         <!-- My Question Header -->
                        <div class="flex items-start gap-3 mb-3">
                            <div class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-700 shrink-0">
                                <span class="font-bold text-xs">ME</span>
                            </div>
                            <div class="flex-1">
                                <div class="flex justify-between items-start">
                                    <div class="font-medium text-gray-900 text-base line-clamp-2 leading-relaxed">
                                        {{ q.content }}
                                    </div>
                                    <span 
                                      class="ml-2 px-2 py-0.5 text-[10px] font-bold rounded-full whitespace-nowrap"
                                      :class="q.is_answered ? 'bg-green-100 text-green-600' : 'bg-amber-100 text-amber-600'"
                                    >
                                      {{ q.is_answered ? '已回答' : '待回答' }}
                                    </span>
                                </div>
                                <div class="text-xs text-gray-400 mt-1">{{ new Date(q.created_at).toLocaleDateString() }}</div>
                            </div>
                        </div>
                        
                        <!-- Images -->
                        <div v-if="q.images && q.images.length" class="mb-4 pl-11">
                            <div class="flex gap-2">
                                <img v-for="(img, i) in q.images.slice(0,3)" :key="i" :src="img" class="w-16 h-16 object-cover rounded-lg border border-gray-100" />
                            </div>
                        </div>

                         <!-- Answer Preview (If answered) -->
                         <div v-if="q.is_answered" class="relative pl-4 ml-3 border-l-2 border-gray-200 bg-gray-50/30 p-3 rounded-r-lg">
                             <div class="flex items-start gap-2">
                                <div class="w-5 h-5 rounded-full bg-gray-800 flex items-center justify-center text-white shrink-0 mt-0.5">
                                    <span class="font-bold text-[10px]">A</span>
                                </div>
                                <div class="flex-1">
                                    <div class="text-gray-600 whitespace-pre-wrap text-sm leading-relaxed line-clamp-2">
                                        {{ q.answer_content }}
                                    </div>
                                     <div v-if="q.answer_images && q.answer_images.length" class="flex gap-1 mt-2">
                                         <div class="text-xs text-gray-400 flex items-center gap-1">
                                             <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                                             <span>查看图片</span>
                                         </div>
                                     </div>
                                </div>
                             </div>
                         </div>
                     </div>

                     <!-- Pagination Load More -->
                     <div v-if="myQuestions.length > 0" class="text-center pt-4 pb-2">
                         <button 
                            v-if="hasMoreMy" 
                            @click="loadMoreMyQuestions" 
                            class="px-6 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 shadow-sm transition-colors disabled:opacity-50"
                            :disabled="isLoadingMore"
                         >
                            {{ isLoadingMore ? '加载中...' : '加载更多' }}
                         </button>
                         <span v-else class="text-xs text-gray-400">没有更多了</span>
                     </div>
                </template>
            </div>
        </div>
    </div>

    <!-- Question Detail Modal -->
    <div v-if="selectedQuestion" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm transition-opacity" @click.self="closeQuestionDetail">
        <div class="bg-white w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-fade-in-up">
            <div class="p-6 overflow-y-auto custom-scrollbar">
                <!-- Question Part -->
                <div class="mb-8">
                    <div class="flex items-center space-x-2 mb-4">
                        <span class="px-2 py-1 bg-gray-100 rounded text-xs font-bold text-gray-500 uppercase tracking-wider">Question</span>
                        <span class="text-xs text-gray-400">{{ new Date(selectedQuestion.created_at).toLocaleString() }}</span>
                    </div>
                    <h3 class="text-xl md:text-2xl font-bold text-gray-900 leading-relaxed whitespace-pre-wrap">{{ selectedQuestion.content }}</h3>
                    
                    <!-- Images if any -->
                    <div v-if="selectedQuestion.images && selectedQuestion.images.length" class="mt-4 grid grid-cols-3 gap-2">
                        <img 
                            v-for="(img, i) in selectedQuestion.images" 
                            :key="i" 
                            :src="img" 
                            class="rounded-lg object-cover w-full aspect-square cursor-zoom-in hover:opacity-90 transition-opacity"
                            @click="previewImage(img)"
                        />
                    </div>
                </div>

                <!-- Answer Part -->
                <div v-if="selectedQuestion.is_answered" class="relative pl-6 border-l-4 border-gray-800 bg-gray-50/50 rounded-r-xl p-6">
                    <div class="flex items-center space-x-2 mb-3">
                        <span class="px-2 py-1 bg-gray-800 rounded text-xs font-bold text-white uppercase tracking-wider">Answer</span>
                        <span class="text-xs text-gray-400">{{ new Date(selectedQuestion.answered_at).toLocaleString() }}</span>
                    </div>
                    <div class="text-gray-800 leading-relaxed whitespace-pre-wrap text-lg">{{ selectedQuestion.answer_content }}</div>
                    
                    <!-- Answer Images if any -->
                    <div v-if="selectedQuestion.answer_images && selectedQuestion.answer_images.length" class="mt-4 grid grid-cols-3 gap-2">
                        <img 
                            v-for="(img, i) in selectedQuestion.answer_images" 
                            :key="i" 
                            :src="img" 
                            class="rounded-lg object-cover w-full aspect-square cursor-zoom-in hover:opacity-90 transition-opacity"
                            @click="previewImage(img)"
                        />
                    </div>
                </div>
                
                <div v-if="currentTab === 'mine' && !selectedQuestion.is_answered" class="p-6 bg-gray-50 rounded-xl text-center text-gray-400 italic border border-dashed border-gray-200">
                    等待回答中...
                </div>
            </div>
            <div class="p-4 border-t border-gray-100 bg-gray-50 flex justify-between items-center">
                 <button v-if="currentTab === 'mine'" @click="deleteQuestion(selectedQuestion.id)" class="text-red-500 hover:text-red-700 text-sm font-medium px-4">
                    删除记录
                 </button>
                 <div v-else></div> <!-- Spacer -->
                 
                <button @click="closeQuestionDetail" class="px-6 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors font-medium">
                    关闭
                </button>
            </div>
        </div>
    </div>

    <!-- Image Preview Modal (Zoom) -->
    <div v-if="previewImageUrl" class="fixed inset-0 z-[60] bg-black/90 flex items-center justify-center p-4 cursor-zoom-out" @click="previewImageUrl = null">
        <img :src="previewImageUrl" class="max-w-full max-h-full object-contain rounded-lg shadow-2xl" />
        <button class="absolute top-4 right-4 text-white/50 hover:text-white p-2">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { questionApi } from '@/api'

const questionContent = ref('')
const images = ref([])
const isAnimating = ref(false)
const isSent = ref(false)
const canRevoke = ref(false)
const lastToken = ref('')
const currentTab = ref('public')

// Public questions state
const publicQuestions = ref([])
const pagePublic = ref(0)
const hasMorePublic = ref(true)

// My questions state
const myQuestions = ref([])
const pageMy = ref(0)
const hasMoreMy = ref(true)
const myQuestionIds = ref([]) // All IDs from local storage

const selectedQuestion = ref(null)
const limit = 20
const isLoadingMore = ref(false)
const previewImageUrl = ref(null)

const loadLocalIds = () => {
    const stored = localStorage.getItem('my_questions')
    if (stored) {
        try {
            const parsed = JSON.parse(stored)
            // Extract IDs whether it's [{id, token}] or just IDs
            myQuestionIds.value = parsed.map(item => item.id || item).reverse() // Newest first
        } catch (e) {
            myQuestionIds.value = []
        }
    }
}

const canSend = computed(() => {
    return questionContent.value.trim().length > 0 || images.value.length > 0
})

const changeTab = (tab) => {
    currentTab.value = tab
    if (tab === 'mine' && myQuestions.value.length === 0) {
        loadMyQuestions(true)
    }
}

const loadPublicQuestions = async (reset = false) => {
    if (reset) {
        pagePublic.value = 0
        publicQuestions.value = []
        hasMorePublic.value = true
    }
    
    if (!hasMorePublic.value) return

    isLoadingMore.value = true
    try {
        const res = await questionApi.getPublicQuestions(pagePublic.value * limit, limit)
        const newQuestions = res.data
        
        if (newQuestions.length < limit) {
            hasMorePublic.value = false
        }
        
        publicQuestions.value = [...publicQuestions.value, ...newQuestions]
        pagePublic.value++
    } catch (err) {
        console.error("Failed to load public questions", err)
    } finally {
        isLoadingMore.value = false
    }
}

const loadMorePublicQuestions = () => {
    loadPublicQuestions()
}

const loadMyQuestions = async (reset = false) => {
    if (reset) {
        pageMy.value = 0
        myQuestions.value = []
        hasMoreMy.value = true
        loadLocalIds() // Refresh IDs
    }
    
    if (!hasMoreMy.value || myQuestionIds.value.length === 0) {
        hasMoreMy.value = false
        return
    }

    isLoadingMore.value = true
    try {
        // Client-side pagination: slice the IDs array
        const start = pageMy.value * limit
        const end = start + limit
        const idsToFetch = myQuestionIds.value.slice(start, end)
        
        if (idsToFetch.length === 0) {
            hasMoreMy.value = false
            isLoadingMore.value = false
            return
        }

        const res = await questionApi.getMyQuestions(idsToFetch)
        const fetchedQuestions = res.data
        
        // 过滤掉可能已被删除的问题（返回空或错误）
        const validQuestions = fetchedQuestions.filter(q => q && q.id)
        
        // 如果获取的问题数量少于请求的ID数量，说明有些问题已被删除
        // 从本地存储中移除这些无效的ID
        if (validQuestions.length < idsToFetch.length) {
            const validIds = validQuestions.map(q => q.id)
            const deletedIds = idsToFetch.filter(id => !validIds.includes(id))
            
            // 更新本地存储，移除已删除的问题ID
            myQuestionIds.value = myQuestionIds.value.filter(id => !deletedIds.includes(id))
            localStorage.setItem('my_question_ids', JSON.stringify(myQuestionIds.value))
        }
        
        if (idsToFetch.length < limit) {
            hasMoreMy.value = false
        }
        
        myQuestions.value = [...myQuestions.value, ...validQuestions]
        pageMy.value++
    } catch (err) {
        console.error("Failed to load my questions", err)
        // 如果是404错误，说明某些问题可能已被删除
        if (err.response && err.response.status === 404) {
            // 可以在这里显示友好提示
            console.warn("Some questions may have been deleted")
        }
    } finally {
        isLoadingMore.value = false
    }
}

const loadMoreMyQuestions = () => {
    loadMyQuestions()
}

const openQuestionDetail = (q) => {
    selectedQuestion.value = q
}

const closeQuestionDetail = () => {
    selectedQuestion.value = null
}

const previewImage = (url) => {
    previewImageUrl.value = url
}

const deleteQuestion = (id) => {
    if (!confirm('确定要删除这条本地记录吗？')) return
    
    // Remove from local view
    myQuestions.value = myQuestions.value.filter(q => q.id !== id)
    
    // Remove from local storage
    const stored = JSON.parse(localStorage.getItem('my_questions') || '[]')
    const updated = stored.filter(item => (item.id || item) !== id)
    localStorage.setItem('my_questions', JSON.stringify(updated))
    
    // Update IDs list
    myQuestionIds.value = myQuestionIds.value.filter(uid => uid !== id)
    
    closeQuestionDetail()
}

const handleImageUpload = async (e) => {
    const files = Array.from(e.target.files)
    if (images.value.length + files.length > 9) {
        alert("最多只能上传9张图片")
        return
    }
    
    // Validate file sizes
    const MAX_SIZE_PER_FILE = 10 * 1024 * 1024 // 10MB per file
    const MAX_TOTAL_SIZE = 50 * 1024 * 1024 // 50MB total
    
    // Check individual file size
    for (const file of files) {
        if (file.size > MAX_SIZE_PER_FILE) {
            alert(`图片 "${file.name}" 超过10MB限制，请压缩后上传`)
            e.target.value = '' // Reset input
            return
        }
    }
    
    // Check total size (existing + new)
    const existingSize = images.value.reduce((sum, img) => sum + (img.file?.size || 0), 0)
    const newSize = files.reduce((sum, file) => sum + file.size, 0)
    const totalSize = existingSize + newSize
    
    if (totalSize > MAX_TOTAL_SIZE) {
        const totalMB = (totalSize / 1024 / 1024).toFixed(1)
        alert(`总图片大小为 ${totalMB}MB，超过50MB限制，请删除部分图片或压缩后上传`)
        e.target.value = '' // Reset input
        return
    }
    
    for (const file of files) {
        const formData = new FormData()
        formData.append('file', file)
        try {
            const res = await questionApi.uploadImage(formData)
            images.value.push({
                file,
                preview: URL.createObjectURL(file),
                serverUrl: res.data.url
            })
        } catch (err) {
            console.error("Upload failed", err)
            alert(`图片 "${file.name}" 上传失败`)
        }
    }
    
    e.target.value = '' // Reset input
}

const removeImage = (idx) => {
    images.value.splice(idx, 1)
}

const triggerSendAnimation = async () => {
    if (!canSend.value) return
    
    isAnimating.value = true
    
    setTimeout(async () => {
        await submitQuestion()
        isAnimating.value = false
    }, 800)
}

const submitQuestion = async () => {
    try {
        const payload = {
            content: questionContent.value,
            images: images.value.map(img => img.serverUrl)
        }
        const res = await questionApi.submitQuestion(payload)
        
        lastToken.value = res.data.access_token
        localStorage.setItem('qa_last_token', res.data.access_token)
        
        // Save to My Records
        const myQuestionsStore = JSON.parse(localStorage.getItem('my_questions') || '[]')
        myQuestionsStore.push({
            id: res.data.question_id,
            token: res.data.access_token
        })
        localStorage.setItem('my_questions', JSON.stringify(myQuestionsStore))
        
        // Prepend to myQuestions list if currently viewing mine
        if (currentTab.value === 'mine') {
             // Fetch the full object to display properly or mock it
             const newQ = {
                 id: res.data.question_id,
                 content: payload.content,
                 images: payload.images,
                 created_at: new Date().toISOString(),
                 is_answered: false
             }
             myQuestions.value.unshift(newQ)
             myQuestionIds.value.unshift(res.data.question_id)
        }

        canRevoke.value = true
        isSent.value = true
        
    } catch (err) {
        console.error(err)
        alert("发送失败，请重试")
        isAnimating.value = false 
    }
}

const resetForm = () => {
    isSent.value = false
    questionContent.value = ''
    images.value = []
    canRevoke.value = false 
}

const revokeQuestion = async () => {
    if (!lastToken.value) return
    if (!confirm("确定要撤回刚刚这封信吗？")) return
    
    try {
        await questionApi.revokeQuestion(lastToken.value)
        alert("撤回成功")
        localStorage.removeItem('qa_last_token')
        
        // Remove from my records
        // Need ID... wait, we didn't save ID in accessible var easily, 
        // but it's the last one added. 
        // Simplification: Reload my questions list
        loadMyQuestions(true)
        
        resetForm()
    } catch (err) {
        alert("撤回失败或已被回答")
    }
}

onMounted(() => {
    loadPublicQuestions(true)
    loadLocalIds()
})
</script>

<style scoped>
.perspective-1000 {
    perspective: 1000px;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translate3d(0, 20px, 0);
    }
    to {
        opacity: 1;
        transform: translate3d(0, 0, 0);
    }
}

.animate-fade-in-up {
    animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Custom scrollbar for list area */
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: rgba(156, 163, 175, 0.3);
    border-radius: 20px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background-color: rgba(156, 163, 175, 0.5);
}
</style>
