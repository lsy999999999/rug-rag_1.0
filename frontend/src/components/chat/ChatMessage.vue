<template>
  <div
    class="chat-message"
    :class="[message.role === 'user' ? 'user-message' : 'assistant-message', { typing: isTyping }]"
  >
    <!-- User Message -->
    <div v-if="message.role === 'user'" class="flex justify-end mb-4">
      <div class="flex items-end space-x-2 max-w-3xl">
        <div class="bg-red-600 text-white px-4 py-3 rounded-2xl rounded-br-lg shadow-sm">
          <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ message.content }}</p>
        </div>
        <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
          <Icon name="person" size="sm" color="red-600" />
        </div>
      </div>
    </div>

    <!-- Assistant Message -->
    <div v-else class="flex justify-start mb-4">
      <div class="flex items-end space-x-2 max-w-3xl">
        <div
          class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0"
        >
          <Icon name="smart_toy" size="sm" color="blue-600" />
        </div>
        <div class="bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-bl-lg shadow-sm">
          <div v-if="isTyping" class="flex items-center space-x-1">
            <div class="flex space-x-1">
              <div
                class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                style="animation-delay: 0ms"
              ></div>
              <div
                class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                style="animation-delay: 150ms"
              ></div>
              <div
                class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                style="animation-delay: 300ms"
              ></div>
            </div>
            <span class="text-sm text-gray-500 ml-2">正在思考...</span>
          </div>
          <div v-else class="message-content">
            <p class="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
              {{ displayContent }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Timestamp -->
    <div class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
      <div class="text-xs text-gray-400 px-2" :class="message.role === 'user' ? 'mr-10' : 'ml-10'">
        {{ formatTime(message.timestamp) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import Icon from '@/components/common/Icon.vue'
import type { ChatMessage } from '@/services/api'

interface Props {
  message: ChatMessage
  isTyping?: boolean
  animateIn?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isTyping: false,
  animateIn: false,
})

const displayContent = ref('')
const isAnimating = ref(false)

// Typewriter effect for assistant messages
const animateText = async (text: string) => {
  if (props.message.role === 'user' || !props.animateIn) {
    displayContent.value = text
    return
  }

  isAnimating.value = true
  displayContent.value = ''

  for (let i = 0; i <= text.length; i++) {
    displayContent.value = text.slice(0, i)
    await new Promise((resolve) => setTimeout(resolve, 20))
  }

  isAnimating.value = false
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  if (props.message.content) {
    animateText(props.message.content)
  }
})
</script>

<style scoped>
.chat-message {
  transform: translateY(0);
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94); /* ease-out equivalent */
  animation: slideIn 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.user-message {
  animation: slideInRight 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.assistant-message {
  animation: slideInLeft 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.message-content {
  min-height: 20px;
}

/* Smooth hover effects */
.chat-message:hover .bg-white {
  box-shadow:
    0 4px 6px -1px rgb(0 0 0 / 0.1),
    0 2px 4px -2px rgb(0 0 0 / 0.1); /* shadow-md */
}

.chat-message:hover .bg-red-600 {
  background-color: rgb(185 28 28); /* bg-red-700 */
}
</style>
