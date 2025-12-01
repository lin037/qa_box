<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
      <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">提问箱管理后台</h1>
            <p class="text-sm text-gray-500 mt-1">问题列表与回答管理</p>
          </div>
          <div class="flex gap-3">
            <button @click="loadQuestions" class="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>刷新</span>
            </button>
            <button @click="handleLogout" class="flex items-center space-x-2 px-4 py-2 bg-red-50 border border-red-200 text-red-600 rounded-lg hover:bg-red-100 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>退出</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- Toolbar -->
      <div class="bg-white rounded-lg shadow-sm p-4 mb-4 border border-gray-200">
        <div class="flex flex-col md:flex-row gap-4 items-center">
          <!-- Search -->
          <div class="flex-1 relative">
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="搜索问题或回答内容..." 
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
            <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          
          <!-- Status Filter -->
          <div class="flex gap-2">
            <button 
              v-for="filter in filters" 
              :key="filter.value"
              @click="currentFilter = filter.value"
              class="px-4 py-2 rounded-lg font-medium transition-all text-sm whitespace-nowrap"
              :class="currentFilter === filter.value 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            >
              {{ filter.label }}
            </button>
          </div>

          <!-- Stats -->
          <div class="flex gap-4 text-sm">
            <div class="px-3 py-1 bg-gray-100 rounded-lg">
              <span class="text-gray-500">总计:</span>
              <span class="font-semibold text-gray-900 ml-1">{{ totalFiltered }}</span>
            </div>
            <div class="px-3 py-1 bg-orange-100 rounded-lg">
              <span class="text-orange-600">待答:</span>
              <span class="font-semibold text-orange-700 ml-1">{{ unansweredCount }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-12">
                  #
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  问题内容
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
                  图片
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-40">
                  提交时间
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
                  状态
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-72">
                  操作
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-if="paginatedQuestions.length === 0">
                <td colspan="6" class="px-4 py-12 text-center text-gray-400">
                  <svg class="w-12 h-12 mx-auto mb-2 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                  </svg>
                  暂无数据
                </td>
              </tr>
              <tr v-for="(q, idx) in paginatedQuestions" :key="q.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-4 text-sm text-gray-500">
                  {{ (currentPage - 1) * pageSize + idx + 1 }}
                </td>
                <td class="px-4 py-4">
                  <div class="text-sm text-gray-900 line-clamp-2 max-w-md cursor-pointer hover:text-blue-600" @click="viewDetail(q)">
                    {{ q.content }}
                  </div>
                  <div v-if="q.is_answered" class="text-xs text-gray-500 mt-1 line-clamp-1">
                    回答: {{ q.answer_content }}
                  </div>
                </td>
                <td class="px-4 py-4">
                  <div v-if="q.images && q.images.length" class="flex gap-1">
                    <img 
                      v-for="(img, i) in q.images.slice(0, 2)" 
                      :key="i"
                      :src="img" 
                      class="w-10 h-10 object-cover rounded cursor-pointer hover:opacity-80"
                      @click="previewImage(img)"
                    />
                    <div v-if="q.images.length > 2" class="w-10 h-10 bg-gray-100 rounded flex items-center justify-center text-xs text-gray-500">
                      +{{ q.images.length - 2 }}
                    </div>
                  </div>
                  <span v-else class="text-xs text-gray-400">无</span>
                </td>
                <td class="px-4 py-4 text-sm text-gray-500 whitespace-nowrap">
                  {{ formatDate(q.created_at) }}
                </td>
                <td class="px-4 py-4">
                  <span 
                    class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="q.is_answered 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-orange-100 text-orange-800'"
                  >
                    {{ q.is_answered ? '已回答' : '待回答' }}
                  </span>
                  <span 
                    v-if="q.is_answered"
                    class="inline-flex ml-1 px-2 py-1 text-xs font-semibold rounded-full"
                    :class="q.is_public 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-gray-100 text-gray-600'"
                  >
                    {{ q.is_public ? '公开' : '私密' }}
                  </span>
                </td>
                <td class="px-4 py-4 text-sm">
                  <div class="flex gap-2">
                    <button 
                      @click="openAnswerModal(q)" 
                      class="px-3 py-1.5 rounded transition-colors"
                      :class="q.is_answered 
                        ? 'bg-gray-100 text-gray-700 hover:bg-gray-200' 
                        : 'bg-blue-600 text-white hover:bg-blue-700'"
                    >
                      {{ q.is_answered ? '修改' : '回答' }}
                    </button>
                    <button 
                      @click="viewDetail(q)" 
                      class="px-3 py-1.5 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      查看
                    </button>
                    <button 
                      v-if="q.is_answered"
                      @click="generateCard(q)" 
                      class="px-3 py-1.5 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-colors"
                    >
                      卡片
                    </button>
                    <button 
                      @click="confirmDelete(q)" 
                      class="px-3 py-1.5 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                    >
                      删除
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="bg-gray-50 px-4 py-3 border-t border-gray-200 flex items-center justify-between">
          <div class="text-sm text-gray-500">
            显示 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalFiltered) }} 条，共 {{ totalFiltered }} 条
          </div>
          <div class="flex gap-2">
            <button 
              @click="currentPage--"
              :disabled="currentPage === 1"
              class="px-3 py-1 border border-gray-300 rounded hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              上一页
            </button>
            <div class="flex gap-1">
              <button 
                v-for="page in visiblePages" 
                :key="page"
                @click="currentPage = page"
                class="px-3 py-1 border rounded transition-colors"
                :class="currentPage === page 
                  ? 'bg-blue-600 text-white border-blue-600' 
                  : 'border-gray-300 hover:bg-white'"
              >
                {{ page }}
              </button>
            </div>
            <button 
              @click="currentPage++"
              :disabled="currentPage === totalPages"
              class="px-3 py-1 border border-gray-300 rounded hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Answer Modal -->
    <div v-if="showAnswerModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" @click.self="closeAnswerModal">
      <div class="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
        <div class="p-6 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-bold text-gray-900">
              {{ currentQuestion.is_answered ? '修改回答' : '回答问题' }}
            </h3>
            <button @click="closeAnswerModal" class="text-gray-400 hover:text-gray-600 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          <!-- Question Display -->
          <div class="mb-6 p-4 bg-gray-50 rounded-lg">
            <div class="text-sm text-gray-500 mb-2">问题内容</div>
            <div class="text-gray-900 whitespace-pre-wrap">{{ currentQuestion.content }}</div>
            <div v-if="currentQuestion.images && currentQuestion.images.length" class="flex gap-2 mt-3">
              <img 
                v-for="(img, i) in currentQuestion.images" 
                :key="i"
                :src="img" 
                class="w-20 h-20 object-cover rounded cursor-pointer hover:opacity-80"
                @click="previewImage(img)"
              />
            </div>
          </div>

          <!-- Answer Input -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              {{ currentQuestion.is_answered ? '修改回答' : '撰写回答' }}
            </label>
            <textarea 
              v-model="currentAnswer" 
              class="w-full border border-gray-300 rounded-lg p-4 h-48 mb-3 outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none" 
              placeholder="写下你的回答..."
              autofocus
            ></textarea>
            
             <!-- Image Upload for Answer -->
            <div class="mb-3">
                <div class="flex flex-wrap gap-2 mb-2">
                  <div v-for="(img, index) in currentAnswerImages" :key="index" class="relative group">
                    <img :src="img" class="w-20 h-20 object-cover rounded border border-gray-200" />
                    <button @click="removeAnswerImage(index)" class="absolute -top-1 -right-1 bg-red-500 text-white rounded-full p-0.5 hover:bg-red-600 opacity-0 group-hover:opacity-100 transition-opacity">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                  </div>
                  <label class="w-20 h-20 border-2 border-dashed border-gray-300 rounded flex flex-col items-center justify-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors">
                    <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
                    <span class="text-xs text-gray-500 mt-1">添加图片</span>
                    <input type="file" class="hidden" accept="image/*" @change="handleAnswerImageUpload" multiple />
                  </label>
                </div>
            </div>

            <div class="flex items-center justify-between">
                <div class="text-xs text-gray-400">{{ currentAnswer?.length || 0 }} 字</div>
                
                <!-- Is Public Toggle -->
                <div class="flex items-center gap-2">
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" v-model="currentIsPublic" class="sr-only peer">
                      <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                      <span class="ml-2 text-sm font-medium text-gray-700">公开回答</span>
                    </label>
                </div>
            </div>
          </div>
        </div>

        <div class="p-6 border-t border-gray-200 flex justify-end gap-3">
          <button 
            @click="closeAnswerModal" 
            class="px-6 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
          >
            取消
          </button>
          <button 
            @click="submitAnswerFromModal" 
            :disabled="!currentAnswer?.trim()"
            class="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {{ currentQuestion.is_answered ? '更新回答' : '提交回答' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="showDetailModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" @click.self="closeDetailModal">
      <div class="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
        <div class="p-6 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-bold text-gray-900">问题详情</h3>
            <button @click="closeDetailModal" class="text-gray-400 hover:text-gray-600 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          <!-- Question -->
          <div class="mb-6">
            <div class="flex items-center space-x-2 mb-3">
              <span class="px-2 py-1 bg-gray-100 rounded text-xs font-bold text-gray-500">问题</span>
              <span class="text-xs text-gray-400">{{ formatDate(currentQuestion.created_at) }}</span>
            </div>
            <div class="text-gray-900 whitespace-pre-wrap text-lg">{{ currentQuestion.content }}</div>
            
            <div v-if="currentQuestion.images && currentQuestion.images.length" class="grid grid-cols-3 gap-2 mt-4">
              <img 
                v-for="(img, i) in currentQuestion.images" 
                :key="i"
                :src="img" 
                class="rounded-lg object-cover w-full aspect-square cursor-pointer hover:opacity-80"
                @click="previewImage(img)"
              />
            </div>
          </div>

          <!-- Answer -->
          <div v-if="currentQuestion.is_answered" class="p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100">
            <div class="flex items-center space-x-2 mb-3">
              <span class="px-2 py-1 bg-blue-100 rounded text-xs font-bold text-blue-600">回答</span>
              <span class="text-xs text-gray-500">{{ formatDate(currentQuestion.answered_at) }}</span>
            </div>
            <div class="text-gray-800 whitespace-pre-wrap text-lg leading-relaxed">{{ currentQuestion.answer_content }}</div>
            
            <!-- Answer Images -->
            <div v-if="currentQuestion.answer_images && currentQuestion.answer_images.length" class="grid grid-cols-3 gap-2 mt-4">
              <img 
                v-for="(img, i) in currentQuestion.answer_images" 
                :key="i"
                :src="img" 
                class="rounded-lg object-cover w-full aspect-square cursor-pointer hover:opacity-80"
                @click="previewImage(img)"
              />
            </div>
          </div>
        </div>

        <div class="p-6 border-t border-gray-200 flex justify-end gap-3">
          <button 
            v-if="currentQuestion.is_answered"
            @click="generateCard(currentQuestion)" 
            class="px-6 py-2.5 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors font-medium"
          >
            生成卡片
          </button>
          <button 
            @click="closeDetailModal" 
            class="px-6 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
    
    <!-- Card Generation Modal -->
    <div v-if="showCardModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-start justify-center z-50 p-4 overflow-y-auto" @click.self="showCardModal = false">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full my-8">
        <div class="p-6 border-b border-gray-100">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-bold text-gray-900">分享卡片</h3>
            <button @click="showCardModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Card Display Options -->
        <div class="p-6 bg-gray-50 border-b border-gray-100">
          <div class="text-sm font-medium text-gray-700 mb-3">显示选项</div>
          <div class="space-y-2">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="cardOptions.showQuestionImages" class="rounded border-gray-300 text-black focus:ring-black">
              <span class="text-sm text-gray-600">显示问题图片</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="cardOptions.showAnswerImages" class="rounded border-gray-300 text-black focus:ring-black">
              <span class="text-sm text-gray-600">显示回答图片</span>
            </label>
            <div class="flex items-center gap-4 mt-3">
              <span class="text-sm text-gray-600">图片布局：</span>
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" v-model="cardOptions.imageColumns" value="1" name="imageColumns" class="border-gray-300 text-black focus:ring-black">
                <span class="text-sm text-gray-600">单列</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" v-model="cardOptions.imageColumns" value="2" name="imageColumns" class="border-gray-300 text-black focus:ring-black">
                <span class="text-sm text-gray-600">双列</span>
              </label>
            </div>
          </div>
        </div>
        
        <div class="p-6 flex justify-center bg-gray-50">
          <div ref="cardRef" class="relative w-[320px] bg-white p-6 shadow-2xl overflow-hidden" style="min-height: 480px;">
             <!-- Style 1: Minimalist Modern -->
             <div class="absolute top-0 left-0 w-full h-2 bg-black"></div>
             
             <div class="flex flex-col h-full">
                 <div class="flex justify-between items-end mb-6 border-b border-gray-100 pb-4">
                     <div class="text-2xl font-black text-black">QA BOX</div>
                     <div class="text-xs font-mono text-gray-400">ANONYMOUS</div>
                 </div>
                 
                 <div class="flex-1 space-y-6">
                     <!-- Question -->
                     <div class="group">
                         <div class="text-[10px] font-bold text-gray-300 mb-1.5 tracking-widest">QUESTION</div>
                         <div class="text-sm font-bold text-gray-900 leading-snug whitespace-pre-wrap">
                            {{ currentCardQuestion.content }}
                         </div>
                         <!-- Question Images (if any) -->
                         <div 
                            v-if="cardOptions.showQuestionImages && currentCardQuestion.images && currentCardQuestion.images.length" 
                            class="mt-3"
                            :class="cardOptions.imageColumns === '1' ? 'grid grid-cols-1 gap-2' : 'grid grid-cols-2 gap-1.5'"
                         >
                             <img 
                                v-for="(img, i) in currentCardQuestion.images.slice(0, cardOptions.imageColumns === '1' ? 4 : 4)" 
                                :key="i"
                                :src="img" 
                                class="w-full rounded border border-gray-200"
                                :class="cardOptions.imageColumns === '1' ? 'h-auto object-contain' : 'aspect-square object-cover'"
                             />
                         </div>
                     </div>
                     
                     <!-- Divider -->
                     <div class="w-full h-0.5 bg-gray-200"></div>
                     
                     <!-- Answer -->
                     <div class="py-2">
                         <div class="text-[10px] font-bold text-gray-300 mb-1.5 tracking-widest">ANSWER</div>
                         <div class="text-sm text-gray-600 leading-relaxed font-serif whitespace-pre-wrap">
                            {{ currentCardQuestion.answer_content }}
                         </div>
                         <!-- Answer Images (if any) -->
                         <div 
                            v-if="cardOptions.showAnswerImages && currentCardQuestion.answer_images && currentCardQuestion.answer_images.length" 
                            class="mt-3"
                            :class="cardOptions.imageColumns === '1' ? 'grid grid-cols-1 gap-2' : 'grid grid-cols-2 gap-1.5'"
                         >
                             <img 
                                v-for="(img, i) in currentCardQuestion.answer_images.slice(0, cardOptions.imageColumns === '1' ? 4 : 4)" 
                                :key="i"
                                :src="img" 
                                class="w-full rounded border border-gray-200"
                                :class="cardOptions.imageColumns === '1' ? 'h-auto object-contain' : 'aspect-square object-cover'"
                             />
                         </div>
                     </div>
                 </div>
                 
                 <!-- Footer -->
                 <div class="mt-auto pt-8 border-t border-gray-100 flex justify-between items-end">
                     <div class="flex flex-col footer-date">
                         <span class="text-[8px] text-gray-400 font-mono">DATE</span>
                         <span class="text-[10px] font-bold text-gray-900 font-sans">{{ new Date(currentCardQuestion.answered_at).toLocaleDateString() }}</span>
                     </div>
                     
                     <!-- Signature Block: Brutalist Style with Physical Shadow -->
                     <div class="relative z-10">
                         <!-- Shadow Layer -->
                         <div class="absolute top-[4px] left-[4px] w-full h-full bg-[#e5e7eb] -z-10"></div>
                         
                         <!-- Content Layer -->
                         <div class="bg-black text-white px-3 py-[7px]">
                             <span class="text-[10px] font-bold tracking-widest font-mono block text-center signature-text" style="line-height: 1;">FROM 037</span>
                         </div>
                     </div>
                 </div>
             </div>
          </div>
        </div>

        <div class="p-6 bg-white border-t border-gray-100">
          <div class="space-y-3">
            <!-- Progress Bar -->
            <div v-if="exportProgress > 0 && exportProgress < 100" class="mb-2">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs text-gray-600">{{ exportStatus }}</span>
                <span class="text-xs text-gray-600">{{ exportProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div 
                  class="bg-black h-2 rounded-full transition-all duration-300"
                  :style="{ width: exportProgress + '%' }"
                ></div>
              </div>
            </div>
            
            <button 
              @click="downloadCardAsImage" 
              :disabled="exportProgress > 0 && exportProgress < 100"
              class="w-full py-3 bg-black hover:bg-gray-800 text-white rounded-lg transition-colors font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              {{ exportProgress > 0 && exportProgress < 100 ? '导出中...' : '保存为图片' }}
            </button>
            <p class="text-sm text-gray-500 text-center">或长按/截图保存卡片</p>
          </div>
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
import { useRouter } from 'vue-router'
import { questionApi } from '@/api'

const router = useRouter()

const questions = ref([])
const showCardModal = ref(false)
const showAnswerModal = ref(false)
const showDetailModal = ref(false)
const currentCardQuestion = ref({})
const currentQuestion = ref({})
const currentAnswer = ref('')
const currentAnswerImages = ref([])
const currentIsPublic = ref(true)
const cardRef = ref(null)
const searchQuery = ref('')
const currentFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const previewImageUrl = ref(null)
const exportProgress = ref(0)
const exportStatus = ref('')
const cardOptions = ref({
  showQuestionImages: true,
  showAnswerImages: true,
  imageColumns: '2'
})

const filters = [
  { label: '全部', value: 'all' },
  { label: '待回答', value: 'unanswered' },
  { label: '已回答', value: 'answered' },
  { label: '公开', value: 'public' },
  { label: '私密', value: 'private' }
]

const unansweredCount = computed(() => {
  return questions.value.filter(q => !q.is_answered).length
})

// Removed unused variable
// const answeredCount = computed(() => {
//   return questions.value.filter(q => q.is_answered).length
// })

const filteredQuestions = computed(() => {
  let filtered = questions.value

  // Apply status filter
  if (currentFilter.value === 'unanswered') {
    filtered = filtered.filter(q => !q.is_answered)
  } else if (currentFilter.value === 'answered') {
    filtered = filtered.filter(q => q.is_answered)
  } else if (currentFilter.value === 'public') {
    filtered = filtered.filter(q => q.is_public)
  } else if (currentFilter.value === 'private') {
    filtered = filtered.filter(q => !q.is_public)
  }

  // Apply search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(q => 
      q.content.toLowerCase().includes(query) ||
      q.answer_content?.toLowerCase().includes(query)
    )
  }

  // Sort: unanswered first, then by date descending
  return filtered.sort((a, b) => {
    if (a.is_answered === b.is_answered) {
      return new Date(b.created_at) - new Date(a.created_at)
    }
    return a.is_answered ? 1 : -1
  })
})

const totalFiltered = computed(() => filteredQuestions.value.length)

const totalPages = computed(() => {
  return Math.ceil(totalFiltered.value / pageSize.value) || 1
})

const paginatedQuestions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredQuestions.value.slice(start, end)
})

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const delta = 2
  const range = []
  
  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i)
  }
  
  if (current - delta > 2) {
    range.unshift('...')
  }
  if (current + delta < total - 1) {
    range.push('...')
  }
  
  range.unshift(1)
  if (total > 1) {
    range.push(total)
  }
  
  return range.filter((v, i, a) => a.indexOf(v) === i)
})

const formatDate = (dateStr) => {
  // 后端返回UTC时间，需要转换为本地时间
  const date = new Date(dateStr + 'Z') // 添加 Z 指示 UTC 时区
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  }
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadQuestions = async () => {
  try {
    const res = await questionApi.getQuestions()
    questions.value = res.data
  } catch (err) {
    console.error(err)
  }
}

const openAnswerModal = (question) => {
  currentQuestion.value = question
  // 如果已回答，预填充原答案
  currentAnswer.value = question.is_answered ? question.answer_content : ''
  currentAnswerImages.value = question.answer_images || []
  currentIsPublic.value = question.is_answered ? question.is_public : true
  showAnswerModal.value = true
}

const closeAnswerModal = () => {
  showAnswerModal.value = false
  currentQuestion.value = {}
  currentAnswer.value = ''
  currentAnswerImages.value = []
  currentIsPublic.value = true
}

const handleAnswerImageUpload = async (e) => {
  const files = Array.from(e.target.files)
  if (!files.length) return
  
  for (const file of files) {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await questionApi.uploadImage(formData)
      currentAnswerImages.value.push(res.data.url)
    } catch (err) {
      console.error('Upload failed', err)
      alert('图片上传失败')
    }
  }
  e.target.value = '' // Reset input
}

const removeAnswerImage = (index) => {
  currentAnswerImages.value.splice(index, 1)
}

const submitAnswerFromModal = async () => {
  if (!currentAnswer.value.trim()) return
  
  try {
    await questionApi.answerQuestion(currentQuestion.value.id, {
        answer_content: currentAnswer.value,
        answer_images: currentAnswerImages.value,
        is_public: currentIsPublic.value
    })
    closeAnswerModal()
    await loadQuestions()
  } catch (err) {
    alert("回答失败")
  }
}

// Removed unused function
// const submitAnswer = async (id) => {
//   if (!answers.value[id]?.trim()) return
//   
//   try {
//     await questionApi.answerQuestion(id, {
//         answer_content: answers.value[id],
//         is_public: true // Default public for quick answer? Or simple text answer.
//     })
//     answers.value[id] = ''
//     await loadQuestions()
//   } catch (err) {
//     alert("回答失败")
//   }
// }

const viewDetail = (question) => {
  currentQuestion.value = question
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  currentQuestion.value = {}
}

const generateCard = (q) => {
  currentCardQuestion.value = q
  showCardModal.value = true
  closeDetailModal()
}

// Removed unused function
// const openImage = (url) => {
//   window.open(url, '_blank')
// }

const previewImage = (url) => {
  previewImageUrl.value = url
}

const handleLogout = () => {
  localStorage.removeItem('admin_token')
  router.push(`${ADMIN_ROUTE}/login`)
}

const confirmDelete = (question) => {
  if (confirm(`确定要删除这个问题吗？\n\n问题内容：${question.content.substring(0, 50)}...\n\n此操作将同时删除相关图片，且无法恢复！`)) {
    deleteQuestion(question.id)
  }
}

const deleteQuestion = async (id) => {
  try {
    await questionApi.deleteQuestion(id)
    await loadQuestions()
  } catch (err) {
    console.error('Delete failed:', err)
    alert('删除失败，请重试')
  }
}

const downloadCardAsImage = async () => {
  if (!cardRef.value) return
  
  try {
    exportProgress.value = 0
    exportStatus.value = '准备导出...'
    
    // Step 1: Load html2canvas
    exportProgress.value = 10
    exportStatus.value = '加载渲染引擎...'
    const html2canvas = (await import('html2canvas')).default
    
    // Step 2: Render to canvas
    exportProgress.value = 30
    exportStatus.value = '渲染卡片...'
    
    const canvas = await html2canvas(cardRef.value, {
      backgroundColor: '#ffffff',
      scale: 3, // Increase scale for sharper text
      logging: false,
      useCORS: true,
      allowTaint: true,
      scrollY: -window.scrollY,
      onclone: (clonedDoc) => {
        // Fix html2canvas text baseline issue for signature text
        const signatureText = clonedDoc.querySelector('.signature-text')
        if (signatureText) {
          signatureText.style.position = 'relative'
          signatureText.style.top = '-5px'
        }
        // Fix html2canvas text baseline issue for date
        const dateElement = clonedDoc.querySelector('.footer-date')
        if (dateElement) {
          dateElement.style.position = 'relative'
          dateElement.style.top = '-3px'
        }
      }
    })
    
    // Step 3: Compress and convert to blob
    exportProgress.value = 70
    exportStatus.value = '压缩图片...'
    
    // Compress image with quality settings
    await new Promise(resolve => {
      canvas.toBlob((blob) => {
        exportProgress.value = 90
        exportStatus.value = '保存文件...'
        
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `qa-card-037-${Date.now()}.png`
        link.click()
        URL.revokeObjectURL(url)
        
        exportProgress.value = 100
        exportStatus.value = '导出完成！'
        
        // Reset after 1 second
        setTimeout(() => {
          exportProgress.value = 0
          exportStatus.value = ''
        }, 1000)
        
        resolve()
      }, 'image/png', 0.92) // PNG with quality 0.92 for compression
    })
    
  } catch (err) {
    console.error('Failed to generate card image:', err)
    alert('生成图片失败，请截图保存')
    exportProgress.value = 0
    exportStatus.value = ''
  }
}

onMounted(() => {
  loadQuestions()
})
</script>

<style scoped>
/* Line clamp utility */
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Smooth scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
