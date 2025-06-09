<template>
  <div class="chat-demo">
    <!-- Sidebar -->
    <ChatSidebar
      :sessions="sessions"
      :current-session-id="currentSession?.id"
      :is-loading="isLoading"
      @select-session="handleSelectSession"
      @new-session="handleNewSession"
    />

    <!-- Main Chat Area -->
    <div class="chat-main">
      <!-- Header -->
      <div class="chat-header">
        <div class="flex items-center space-x-3">
          <h2 class="text-xl font-semibold text-gray-900">
            {{ currentSession?.title || '新对话' }}
          </h2>
          <div class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">在线</div>
        </div>
        <div class="flex items-center space-x-2 text-sm text-gray-500">
          <Icon name="schedule" size="sm" />
          <span>响应时间通常在 2-3 秒</span>
        </div>
      </div>

      <!-- Messages Container -->
      <div class="messages-container" ref="messagesContainer">
        <!-- Welcome Message for Empty Chat -->
        <div v-if="currentMessages.length === 0" class="welcome-section">
          <div class="welcome-content">
            <div class="welcome-icon">
              <Icon name="school" size="xl" color="red-600" />
            </div>
            <h3 class="welcome-title">欢迎使用人大智慧行政助手</h3>
            <p class="welcome-description">
              我是基于 RAG 技术驱动的智慧行政大模型，可以帮助您解答各类行政事务相关问题。
              请选择下方的常见问题或直接输入您的问题。
            </p>

            <!-- Common Questions -->
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

        <!-- Chat Messages -->
        <div v-else class="messages-list">
          <ChatMessage
            v-for="message in currentMessages"
            :key="message.id"
            :message="message"
            :animate-in="message.id === lastMessageId"
          />

          <!-- Typing Indicator -->
          <ChatMessage v-if="isTyping" :message="typingMessage" :is-typing="true" />
        </div>

        <!-- Scroll to bottom button -->
        <Transition name="fade">
          <button v-if="showScrollButton" @click="scrollToBottom" class="scroll-button">
            <Icon name="keyboard_arrow_down" size="sm" />
          </button>
        </Transition>
      </div>

      <!-- Input Area -->
      <div class="input-container">
        <ChatInput
          :disabled="isLoading"
          :is-loading="isLoading"
          :show-suggestions="currentMessages.length === 0"
          @send="handleSendMessage"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatSidebar from '@/components/chat/ChatSidebar.vue'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import Icon from '@/components/common/Icon.vue'
import type { ChatMessage as ChatMessageType } from '@/services/api'

const chatStore = useChatStore()
const messagesContainer = ref<HTMLElement>()
const lastMessageId = ref<string>()
const showScrollButton = ref(false)

// Computed properties
const currentSession = computed(() => chatStore.currentSession)
const currentMessages = computed(() => chatStore.currentMessages)
const sessions = computed(() => chatStore.sessions)
const isLoading = computed(() => chatStore.isLoading)
const isTyping = computed(() => chatStore.isTyping)

// Common questions for welcome screen
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

// Typing indicator message
const typingMessage = computed(
  (): ChatMessageType => ({
    id: 'typing',
    role: 'assistant',
    content: '',
    timestamp: new Date(),
  }),
)

// Event handlers
const handleSelectSession = (sessionId: string) => {
  chatStore.switchToSession(sessionId)
}

const handleNewSession = async () => {
  await chatStore.createNewSession()
  scrollToBottom()
}

const handleSendMessage = async (content: string) => {
  const previousMessageCount = currentMessages.value.length
  await chatStore.sendMessage(content)

  // Track the last message for animation
  const newMessages = currentMessages.value
  if (newMessages.length > previousMessageCount) {
    lastMessageId.value = newMessages[newMessages.length - 1].id
  }

  await nextTick()
  scrollToBottom()
}

const handleQuestionClick = (question: string) => {
  handleSendMessage(question)
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

// Watch for new messages to auto-scroll
watch(
  () => currentMessages.value.length,
  async () => {
    await nextTick()
    if (!showScrollButton.value) {
      scrollToBottom()
    }
  },
)

// Watch for typing state changes
watch(
  () => isTyping.value,
  async (newValue) => {
    if (newValue) {
      await nextTick()
      scrollToBottom()
    }
  },
)
</script>

<style scoped>
.chat-demo {
  display: flex;
  height: 100vh;
  background-color: rgb(243 244 246); /* bg-gray-100 */
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: white;
}

.chat-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgb(229 231 235);
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
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
  height: 100%;
  padding: 2rem;
}

.welcome-content {
  max-width: 64rem;
  margin: 0 auto;
  text-align: center;
}

.welcome-icon {
  width: 4rem;
  height: 4rem;
  background-color: rgb(254 226 226); /* bg-red-100 */
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
  background-color: rgb(249 250 251); /* bg-gray-50 */
  border-radius: 0.75rem;
  transition: all 0.2s;
  text-align: left;
  cursor: pointer;
  border: none;
}

.question-card:hover {
  background-color: rgb(243 244 246); /* hover:bg-gray-100 */
  box-shadow:
    0 4px 6px -1px rgb(0 0 0 / 0.1),
    0 2px 4px -2px rgb(0 0 0 / 0.1); /* hover:shadow-md */
  transform: scale(1.05); /* hover:scale-105 */
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
  color: rgb(220 38 38); /* group-hover:text-red-600 */
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
}

.scroll-button:hover {
  background-color: rgb(249 250 251);
  transform: scale(1.1);
}

/* Transition animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Custom scrollbar */
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
</style>
