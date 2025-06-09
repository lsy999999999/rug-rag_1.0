<template>
  <div class="chat-sidebar">
    <!-- Header -->
    <div class="sidebar-header">
      <div class="flex items-center space-x-3 mb-6">
        <div class="w-10 h-10 bg-red-600 rounded-lg flex items-center justify-center">
          <Icon name="school" color="white" size="md" />
        </div>
        <div>
          <h1 class="text-lg font-bold text-gray-900">人大智慧助手</h1>
          <p class="text-sm text-gray-500">RAG 行政大模型</p>
        </div>
      </div>

      <!-- New Chat Button -->
      <button @click="createNewChat" class="new-chat-button" :disabled="isLoading">
        <Icon name="add" size="sm" />
        <span>新建对话</span>
      </button>
    </div>

    <!-- Sessions List -->
    <div class="sessions-container">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-medium text-gray-700">最近对话</h3>
        <span class="text-xs text-gray-400">{{ sessions.length }}</span>
      </div>

      <div class="sessions-list">
        <div
          v-for="session in sessions"
          :key="session.id"
          @click="selectSession(session.id)"
          class="session-item"
          :class="{ active: session.id === currentSessionId }"
        >
          <div class="flex items-start space-x-3">
            <div class="session-icon">
              <Icon name="chat" size="sm" color="gray-600" />
            </div>
            <div class="flex-1 min-w-0">
              <h4 class="session-title">{{ session.title }}</h4>
              <p class="session-preview">
                {{ getLastMessage(session) }}
              </p>
              <p class="session-time">{{ formatSessionTime(session.updatedAt) }}</p>
            </div>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="sessions.length === 0" class="empty-state">
          <Icon name="chat_bubble_outline" size="lg" color="gray-400" />
          <p class="text-sm text-gray-500 mt-2">暂无对话记录</p>
          <p class="text-xs text-gray-400">开始新对话来体验智慧助手</p>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="sidebar-footer">
      <div class="flex items-center space-x-2 text-xs text-gray-400">
        <Icon name="info" size="sm" />
        <span>基于 RAG 技术驱动</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Icon from '@/components/common/Icon.vue'
import type { ChatSession } from '@/services/api'

interface Props {
  sessions: ChatSession[]
  currentSessionId?: string
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
})

const emit = defineEmits<{
  'select-session': [sessionId: string]
  'new-session': []
}>()

const selectSession = (sessionId: string) => {
  emit('select-session', sessionId)
}

const createNewChat = () => {
  emit('new-session')
}

const getLastMessage = (session: ChatSession): string => {
  if (session.messages.length === 0) {
    return '新对话'
  }

  const lastMessage = session.messages[session.messages.length - 1]
  const content = lastMessage.content

  if (content.length > 30) {
    return content.slice(0, 30) + '...'
  }

  return content
}

const formatSessionTime = (date: Date): string => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // Less than 1 minute
  if (diff < 60000) {
    return '刚刚'
  }

  // Less than 1 hour
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return `${minutes}分钟前`
  }

  // Less than 1 day
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  }

  // Less than 1 week
  if (diff < 604800000) {
    const days = Math.floor(diff / 86400000)
    return `${days}天前`
  }

  // Format as date
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
  })
}
</script>

<style scoped>
.chat-sidebar {
  width: 20rem; /* w-80 equivalent */
  background-color: rgb(249 250 251); /* bg-gray-50 */
  border-right: 1px solid rgb(229 231 235); /* border-r border-gray-200 */
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-header {
  padding: 1.5rem; /* p-6 */
  border-bottom: 1px solid rgb(229 231 235); /* border-b border-gray-200 */
}

.new-chat-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: rgb(220 38 38); /* bg-red-600 */
  color: white;
  font-weight: 500;
  border-radius: 0.5rem;
  transition: background-color 0.2s;
  border: none;
}

.new-chat-button:hover {
  background-color: rgb(185 28 28); /* hover:bg-red-700 */
}

.new-chat-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sessions-container {
  flex: 1;
  padding: 1.5rem;
  overflow: hidden;
}

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  overflow-y: auto;
  max-height: 100%;
}

.session-item {
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.session-item:hover {
  background-color: white;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}

.session-item.active {
  background-color: white;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  border-color: rgb(252 165 165); /* border-red-200 */
  ring: 1px solid rgb(252 165 165);
}

.session-item:hover:not(.active) {
  border-color: rgb(229 231 235); /* border-gray-200 */
}

.session-icon {
  width: 2rem;
  height: 2rem;
  background-color: rgb(243 244 246); /* bg-gray-100 */
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.session-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgb(17 24 39); /* text-gray-900 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-preview {
  font-size: 0.75rem;
  color: rgb(107 114 128); /* text-gray-500 */
  margin-top: 0.25rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.session-time {
  font-size: 0.75rem;
  color: rgb(156 163 175); /* text-gray-400 */
  margin-top: 0.25rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  text-align: center;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid rgb(229 231 235); /* border-t border-gray-200 */
}

/* Custom scrollbar for sessions list */
.sessions-list::-webkit-scrollbar {
  width: 4px;
}

.sessions-list::-webkit-scrollbar-track {
  background: transparent;
}

.sessions-list::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 2px;
}

.sessions-list::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
