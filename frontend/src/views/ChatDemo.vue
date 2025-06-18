<template>
  <div class="chat-demo">
    <ChatSidebar
      :sessions="sessions"
      :current-session-id="currentSession?.id"
      :is-loading="isLoading"
      @select-session="handleSelectSession"
      @new-session="handleNewSession"
    />

    <div class="chat-main">
      <div class="chat-header">
        <div class="flex items-center space-x-3">
          <h2 class="text-xl font-semibold text-gray-900">
            {{ currentSession?.title || '新对话' }}
          </h2>
          <div class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">在线</div>
          <!-- 文件上传状态指示器 -->
          <div
            v-if="hasActiveUploads"
            class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full flex items-center gap-1"
          >
            <Icon name="cloud_upload" size="xs" class="animate-pulse" />
            上传中
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <!-- 文档模板状态 -->
          <div class="flex items-center space-x-2 text-sm text-gray-500">
            <Icon name="description" size="sm" />
            <span>支持 {{ documentTemplates.length }} 种文档类型</span>
          </div>
          <div class="flex items-center space-x-2 text-sm text-gray-500">
            <Icon name="schedule" size="sm" />
            <span>响应时间通常在 2-3 秒</span>
          </div>
        </div>
      </div>

      <div class="messages-container" ref="messagesContainer">
        <!-- 欢迎页面 -->
        <div v-if="currentMessages.length === 0" class="welcome-section">
          <div class="welcome-content">
            <div class="welcome-icon">
              <Icon name="school" size="xl" color="red-600" />
            </div>
            <h3 class="welcome-title">欢迎使用人大智慧行政助手</h3>
            <p class="welcome-description">
              我是基于 RAG 技术驱动的智慧行政大模型，可以帮助您解答各类行政事务相关问题。
              您可以直接提问，或者上传相关文档来扩展知识库。
            </p>

            <!-- 文件上传区域 -->
            <div class="upload-section">
              <FileUploadArea
                :disabled="isLoading"
                :is-uploading="hasActiveUploads"
                :upload-progress="averageUploadProgress"
                @files-selected="handleFilesSelected"
                @upload-error="handleUploadError"
              />
            </div>

            <!-- 常见问题 -->
            <div class="common-questions">
              <h4 class="questions-title">常见问题</h4>
              <div class="questions-grid">
                <button
                  v-for="question in commonQuestions"
                  :key="question.title"
                  @click="handleQuestionClick(question.content)"
                  class="question-card"
                >
                  <Icon :name="question.icon" size="md" :color="question.color" />
                  <div class="question-text">
                    <h5 class="question-card-title">{{ question.title }}</h5>
                    <p class="question-card-desc">{{ question.description }}</p>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-else class="messages-list">
          <ChatMessage
            v-for="message in currentMessages"
            :key="message.id"
            :message="message"
            :upload-progress="getMessageUploadProgress(message.id)"
            @edit-metadata="handleEditMetadata"
            @confirm-upload="handleConfirmUpload"
            @cancel-upload="handleCancelUpload"
            @retry-upload="handleRetryUpload"
          />
        </div>

        <!-- 滚动到底部按钮 -->
        <Transition name="fade">
          <button v-if="showScrollButton" @click="scrollToBottom" class="scroll-button">
            <Icon name="keyboard_arrow_down" size="sm" />
          </button>
        </Transition>
      </div>

      <!-- 输入区域 -->
      <div class="input-container">
        <ChatInput
          :disabled="isLoading"
          :is-loading="isLoading"
          :show-suggestions="currentMessages.length === 0"
          @send="handleSendMessage"
          @upload-files="handleFilesSelected"
        />
      </div>
    </div>

    <!-- 元数据编辑弹窗 -->
    <MetadataEditorModal
      :is-open="showMetadataEditor"
      :file-info="editingFileInfo"
      :document-templates="documentTemplates"
      :is-submitting="isConfirming"
      @close="handleCloseMetadataEditor"
      @confirm="handleMetadataConfirm"
    />

    <!-- 错误提示 -->
    <Transition name="slide-up">
      <div v-if="errorMessage" class="error-toast">
        <Icon name="error" size="sm" color="red-600" />
        <span>{{ errorMessage }}</span>
        <button @click="clearError" class="ml-2">
          <Icon name="close" size="xs" />
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatSidebar from '@/components/chat/ChatSidebar.vue'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import FileUploadArea from '@/components/common/FileUploadArea.vue'
import MetadataEditorModal from '@/components/common/MetadataEditorModal.vue'
import Icon from '@/components/common/Icon.vue'
import type { FileInfo } from '@/services/api'

const chatStore = useChatStore()
const messagesContainer = ref<HTMLElement>()
const showScrollButton = ref(false)
const showMetadataEditor = ref(false)
const editingFileInfo = ref<FileInfo | null>(null)
const isConfirming = ref(false)
const errorMessage = ref('')

// Computed properties
const currentSession = computed(() => chatStore.currentSession)
const currentMessages = computed(() => chatStore.currentMessages)
const sessions = computed(() => chatStore.sessions)
const isLoading = computed(() => chatStore.isLoading)
const documentTemplates = computed(() => chatStore.documentTemplates)

// 检查是否有活跃的上传
const hasActiveUploads = computed(() => {
  return currentMessages.value.some(
    (msg) => msg.is_file_message && ['uploading', 'confirming'].includes(msg.upload_status || ''),
  )
})

// 计算平均上传进度
const averageUploadProgress = computed(() => {
  const uploadingMessages = currentMessages.value.filter(
    (msg) => msg.is_file_message && msg.upload_status === 'uploading',
  )

  if (uploadingMessages.length === 0) return 0

  const totalProgress = uploadingMessages.reduce((sum, msg) => {
    return sum + chatStore.getUploadProgress(msg.id)
  }, 0)

  return totalProgress / uploadingMessages.length
})

const commonQuestions = ref([
  {
    title: '成绩查询',
    description: '如何查询学期成绩和学分',
    content: '如何查询成绩？',
    icon: 'assessment',
    color: 'blue-600',
  },
  {
    title: '学籍管理',
    description: '学籍注册和变更流程',
    content: '学籍注册流程是什么？',
    icon: 'school',
    color: 'green-600',
  },
  {
    title: '奖助学金',
    description: '奖学金申请条件和流程',
    content: '奖学金申请条件有哪些？',
    icon: 'military_tech',
    color: 'yellow-600',
  },
  {
    title: '选课系统',
    description: '选课时间和注意事项',
    content: '选课系统使用指南',
    icon: 'menu_book',
    color: 'purple-600',
  },
  {
    title: '宿舍管理',
    description: '住宿申请和管理规定',
    content: '宿舍管理规定有哪些？',
    icon: 'home',
    color: 'indigo-600',
  },
  {
    title: '图书服务',
    description: '图书馆借阅和预约',
    content: '图书馆开放时间和借阅规则',
    icon: 'local_library',
    color: 'red-600',
  },
])

// Methods
const handleSelectSession = (sessionId: string) => {
  chatStore.switchToSession(sessionId)
}

const handleNewSession = async () => {
  await chatStore.createNewSession()
}

const handleSendMessage = async (content: string) => {
  await chatStore.streamMessage(content)
}

const handleQuestionClick = (question: string) => {
  handleSendMessage(question)
}

const handleFilesSelected = async (files: File[]) => {
  await chatStore.uploadFiles(files)
}

const handleUploadError = (error: string) => {
  showError(error)
}

const handleEditMetadata = (messageId: string) => {
  const message = currentMessages.value.find((m) => m.id === messageId)
  if (message?.file_info) {
    editingFileInfo.value = message.file_info
    showMetadataEditor.value = true
  }
}

const handleConfirmUpload = async (messageId: string) => {
  const message = currentMessages.value.find((m) => m.id === messageId)
  if (message?.file_info) {
    // 直接确认，使用AI提取的元数据
    await chatStore.confirmDocument(messageId, message.file_info.extracted_metadata)
  }
}

const handleCancelUpload = (messageId: string) => {
  chatStore.cancelFileUpload(messageId)
}

const handleRetryUpload = async (messageId: string) => {
  await chatStore.retryFileUpload(messageId)
}

const handleCloseMetadataEditor = () => {
  showMetadataEditor.value = false
  editingFileInfo.value = null
}

const handleMetadataConfirm = async (data: {
  fileId: string
  metadata: Record<string, any>
  filename: string
}) => {
  isConfirming.value = true

  try {
    // 查找对应的消息
    const message = currentMessages.value.find((m) => m.file_info?.file_id === data.fileId)

    if (message) {
      await chatStore.confirmDocument(message.id, data.metadata)
      showMetadataEditor.value = false
      editingFileInfo.value = null
    }
  } catch (error) {
    showError(error instanceof Error ? error.message : '确认文档失败')
  } finally {
    isConfirming.value = false
  }
}

const getMessageUploadProgress = (messageId: string) => {
  return chatStore.getUploadProgress(messageId)
}

const showError = (message: string) => {
  errorMessage.value = message
  // 3秒后自动清除错误
  setTimeout(() => {
    errorMessage.value = ''
  }, 3000)
}

const clearError = () => {
  errorMessage.value = ''
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTo({
      top: messagesContainer.value.scrollHeight,
      behavior: 'smooth',
    })
  }
}

const handleScroll = () => {
  if (!messagesContainer.value) return

  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  const isNearBottom = scrollHeight - scrollTop - clientHeight < 100

  showScrollButton.value = !isNearBottom && currentMessages.value.length > 0
}

// Lifecycle
onMounted(async () => {
  await chatStore.initialize()

  if (messagesContainer.value) {
    messagesContainer.value.addEventListener('scroll', handleScroll)
  }

  await nextTick()
  scrollToBottom()
})

// Watchers
watch(
  () => currentMessages.value.length,
  async (newLength, oldLength) => {
    if (newLength > oldLength) {
      await nextTick()
      scrollToBottom()
    }
  },
  { deep: true },
)

watch(
  () => {
    const messages = currentMessages.value
    return messages.length > 0 ? messages[messages.length - 1].content : ''
  },
  async () => {
    await nextTick()
    if (messagesContainer.value) {
      const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
      if (scrollHeight - scrollTop - clientHeight < 200) {
        scrollToBottom()
      }
    }
  },
)
</script>

<style scoped>
.chat-demo {
  display: flex;
  height: 100vh;
  background-color: rgb(243 244 246);
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: white;
  position: relative;
}

.chat-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgb(229 231 235);
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  position: relative;
  scroll-behavior: smooth;
}

.welcome-section {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: 2rem;
}

.welcome-content {
  max-width: 64rem;
  margin: 0 auto;
  text-align: center;
  width: 100%;
}

.welcome-icon {
  width: 4rem;
  height: 4rem;
  background-color: rgb(254 226 226);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}

.welcome-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: rgb(17 24 39);
  margin-bottom: 1rem;
}

.welcome-description {
  font-size: 1.125rem;
  color: rgb(75 85 99);
  margin-bottom: 2rem;
  line-height: 1.75;
}

.upload-section {
  margin-bottom: 3rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.common-questions {
  margin-top: 2rem;
}

.questions-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: rgb(17 24 39);
  margin-bottom: 1.5rem;
}

.questions-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1rem;
}

@media (min-width: 768px) {
  .questions-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .questions-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.question-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background-color: rgb(249 250 251);
  border-radius: 0.75rem;
  transition: all 0.2s;
  text-align: left;
  cursor: pointer;
  border: none;
}

.question-card:hover {
  background-color: rgb(243 244 246);
  box-shadow:
    0 4px 6px -1px rgb(0 0 0 / 0.1),
    0 2px 4px -2px rgb(0 0 0 / 0.1);
  transform: scale(1.02);
}

.question-text {
  flex: 1;
}

.question-card-title {
  font-weight: 500;
  color: rgb(17 24 39);
  margin-bottom: 0.25rem;
  transition: color 0.2s;
}

.question-card:hover .question-card-title {
  color: rgb(220 38 38);
}

.question-card-desc {
  font-size: 0.875rem;
  color: rgb(107 114 128);
}

.messages-list {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.input-container {
  padding: 1.5rem;
  background-color: white;
  border-top: 1px solid rgb(229 231 235);
}

.scroll-button {
  position: fixed;
  bottom: 8rem;
  right: 2rem;
  width: 2.5rem;
  height: 2.5rem;
  background-color: white;
  border: 1px solid rgb(229 231 235);
  border-radius: 50%;
  box-shadow:
    0 10px 15px -3px rgb(0 0 0 / 0.1),
    0 4px 6px -4px rgb(0 0 0 / 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  cursor: pointer;
  z-index: 10;
}

.scroll-button:hover {
  background-color: rgb(249 250 251);
  transform: scale(1.1);
}

.error-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  max-width: 24rem;
  z-index: 50;
}

.error-toast button {
  background: none;
  border: none;
  color: #991b1b;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.error-toast button:hover {
  background-color: #fecaca;
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* 自定义滚动条 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-header {
    padding: 1rem;
    flex-direction: column;
    align-items: flex-start;
  }

  .welcome-section {
    padding: 1rem;
  }

  .messages-list {
    padding: 1rem;
  }

  .input-container {
    padding: 1rem;
  }

  .error-toast {
    right: 1rem;
    left: 1rem;
    max-width: none;
  }
}
</style>
