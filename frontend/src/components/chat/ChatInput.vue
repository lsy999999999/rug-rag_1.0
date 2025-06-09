<template>
  <div class="chat-input-container">
    <!-- Quick suggestions -->
    <div v-if="showSuggestions && suggestions.length > 0" class="suggestions-container">
      <div class="flex flex-wrap gap-2 mb-4">
        <button
          v-for="suggestion in suggestions"
          :key="suggestion"
          @click="applySuggestion(suggestion)"
          class="suggestion-chip"
        >
          {{ suggestion }}
        </button>
      </div>
    </div>

    <!-- Modern Input area -->
    <div class="input-area">
      <div class="input-wrapper">
        <!-- Input icon -->
        <div class="input-icon">
          <Icon name="smart_toy" size="sm" color="gray-400" />
        </div>

        <!-- Text input -->
        <div class="textarea-container">
          <textarea
            ref="textareaRef"
            v-model="message"
            :placeholder="placeholder"
            :disabled="disabled"
            class="input-textarea"
            rows="1"
            @keydown="handleKeydown"
            @input="adjustHeight"
          />
        </div>

        <!-- Action buttons -->
        <div class="button-container">
          <!-- Attachment button (for future) -->
          <button class="attachment-button" type="button">
            <Icon name="attach_file" size="sm" color="gray-400" />
          </button>

          <!-- Send button -->
          <button
            @click="handleSend"
            :disabled="!canSend"
            class="send-button"
            :class="{ active: canSend }"
            type="button"
          >
            <Icon
              :name="isLoading ? 'hourglass_empty' : 'send'"
              size="sm"
              :class="isLoading ? 'animate-spin' : ''"
            />
          </button>
        </div>
      </div>

      <!-- Status bar -->
      <div class="status-bar">
        <div class="status-left">
          <span class="hint-text">
            <Icon name="keyboard" size="xs" />
            按 <kbd class="kbd">Enter</kbd> 发送，<kbd class="kbd">Shift + Enter</kbd> 换行
          </span>
        </div>
        <div class="status-right">
          <span
            class="character-count"
            :class="{ warning: message.length > 800, error: message.length > 950 }"
          >
            {{ message.length }}/1000
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import Icon from '@/components/common/Icon.vue'

interface Props {
  disabled?: boolean
  isLoading?: boolean
  placeholder?: string
  showSuggestions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  isLoading: false,
  placeholder: '请输入您的问题...',
  showSuggestions: true,
})

const emit = defineEmits<{
  send: [message: string]
}>()

const message = ref('')
const textareaRef = ref<HTMLTextAreaElement>()

// Quick suggestions for first-time users
const suggestions = ref([
  '如何查询成绩？',
  '学籍注册流程是什么？',
  '奖学金申请条件',
  '图书馆开放时间',
  '宿舍管理规定',
  '选课系统使用指南',
])

const canSend = computed(() => {
  return (
    message.value.trim().length > 0 &&
    message.value.length <= 1000 &&
    !props.disabled &&
    !props.isLoading
  )
})

const handleSend = () => {
  if (!canSend.value) return

  const content = message.value.trim()
  message.value = ''
  adjustHeight()

  emit('send', content)
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}

const applySuggestion = (suggestion: string) => {
  message.value = suggestion
  nextTick(() => {
    textareaRef.value?.focus()
    adjustHeight()
  })
}

const adjustHeight = () => {
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
      textareaRef.value.style.height = `${Math.min(textareaRef.value.scrollHeight, 128)}px`
    }
  })
}

onMounted(() => {
  adjustHeight()
})
</script>

<style scoped>
.chat-input-container {
  position: relative;
}

.suggestions-container {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.suggestion-chip {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, rgb(249 250 251), rgb(243 244 246));
  color: rgb(55 65 81);
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 20px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  border: 1px solid rgb(229 231 235);
  box-shadow: 0 1px 2px rgb(0 0 0 / 0.05);
}

.suggestion-chip:hover {
  background: linear-gradient(135deg, rgb(243 244 246), rgb(229 231 235));
  border-color: rgb(209 213 219);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgb(0 0 0 / 0.1);
}

.input-area {
  position: relative;
}

.input-wrapper {
  background: linear-gradient(135deg, rgb(255 255 255), rgb(249 250 251));
  border: 2px solid rgb(229 231 235);
  border-radius: 20px;
  padding: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  box-shadow: 0 2px 8px rgb(0 0 0 / 0.04);
  min-height: 3.5rem;
}

.input-wrapper:focus-within {
  border-color: rgb(220 38 38);
  background: white;
  box-shadow:
    0 0 0 4px rgb(220 38 38 / 0.1),
    0 4px 16px rgb(0 0 0 / 0.08);
  transform: translateY(-1px);
}

.input-wrapper:hover:not(:focus-within) {
  border-color: rgb(209 213 219);
  box-shadow: 0 4px 12px rgb(0 0 0 / 0.06);
}

.input-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 8px;
  background-color: rgb(249 250 251);
}

.textarea-container {
  flex: 1;
  min-height: 1.5rem;
  max-height: 128px;
  display: flex;
  align-items: center;
}

.input-textarea {
  width: 100%;
  resize: none;
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.95rem;
  line-height: 1.5;
  color: rgb(17 24 39);
  font-weight: 400;
  min-height: 1.5rem;
}

.input-textarea::placeholder {
  color: rgb(156 163 175);
  font-weight: 400;
}

.button-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.attachment-button {
  width: 2rem;
  height: 2rem;
  border-radius: 10px;
  background-color: transparent;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  cursor: pointer;
}

.attachment-button:hover {
  background-color: rgb(243 244 246);
}

.send-button {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 12px;
  background: linear-gradient(135deg, rgb(243 244 246), rgb(229 231 235));
  color: rgb(156 163 175);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  box-shadow: 0 2px 4px rgb(0 0 0 / 0.1);
}

.send-button:not(.active):hover {
  background: linear-gradient(135deg, rgb(229 231 235), rgb(209 213 219));
  transform: scale(1.05);
}

.send-button.active {
  background: linear-gradient(135deg, rgb(220 38 38), rgb(185 28 28));
  color: white;
  transform: scale(1.05);
  box-shadow:
    0 4px 12px rgb(220 38 38 / 0.4),
    0 2px 4px rgb(0 0 0 / 0.1);
}

.send-button.active:hover {
  background: linear-gradient(135deg, rgb(185 28 28), rgb(153 27 27));
  transform: scale(1.1);
}

.send-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
  transform: none !important;
}

.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.75rem;
  padding: 0 0.5rem;
}

.status-left {
  display: flex;
  align-items: center;
}

.hint-text {
  font-size: 0.75rem;
  color: rgb(107 114 128);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.kbd {
  display: inline-block;
  padding: 0.125rem 0.25rem;
  background: linear-gradient(135deg, rgb(249 250 251), rgb(243 244 246));
  border: 1px solid rgb(209 213 219);
  border-radius: 4px;
  font-size: 0.675rem;
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-weight: 500;
  box-shadow: 0 1px 2px rgb(0 0 0 / 0.05);
}

.character-count {
  font-size: 0.75rem;
  color: rgb(156 163 175);
  font-weight: 500;
  transition: color 0.2s;
}

.character-count.warning {
  color: rgb(217 119 6); /* amber-600 */
}

.character-count.error {
  color: rgb(220 38 38); /* red-600 */
}

/* Smooth animations */
.input-wrapper::before {
  content: '';
  position: absolute;
  inset: -2px;
  background: linear-gradient(135deg, rgb(220 38 38), rgb(239 68 68));
  border-radius: 22px;
  opacity: 0;
  transition: opacity 0.3s;
  z-index: -1;
}

.input-wrapper:focus-within::before {
  opacity: 0.1;
}

/* Textarea scrollbar styling */
.input-textarea::-webkit-scrollbar {
  width: 4px;
}

.input-textarea::-webkit-scrollbar-track {
  background: transparent;
}

.input-textarea::-webkit-scrollbar-thumb {
  background: rgb(203 213 225);
  border-radius: 2px;
}

.input-textarea::-webkit-scrollbar-thumb:hover {
  background: rgb(148 163 184);
}
</style>
