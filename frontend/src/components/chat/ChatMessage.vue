<template>
  <div class="chat-message" :class="[message.role, { 'animate-in': animateIn }]">
    <!-- 用户消息 -->
    <div v-if="message.role === 'user'" class="flex justify-end mb-1">
      <div class="flex items-end space-x-2 max-w-3xl">
        <div class="bg-red-600 text-white px-4 py-3 rounded-2xl rounded-br-lg shadow-sm">
          <!-- 文件消息渲染 -->
          <FileMessageRenderer
            v-if="message.is_file_message"
            :message="message"
            :upload-progress="uploadProgress"
            @edit-metadata="$emit('edit-metadata', message.id)"
            @confirm-upload="$emit('confirm-upload', message.id)"
            @cancel-upload="$emit('cancel-upload', message.id)"
            @retry-upload="$emit('retry-upload', message.id)"
          />
          <!-- 普通文本消息 -->
          <p v-else class="text-sm leading-relaxed whitespace-pre-wrap">{{ message.content }}</p>
        </div>
        <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
          <Icon name="person" size="sm" color="red-600" />
        </div>
      </div>
    </div>

    <!-- 助手消息 -->
    <div v-else class="flex justify-start mb-1">
      <div class="flex items-start space-x-2 max-w-3xl">
        <div
          class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1"
        >
          <Icon name="smart_toy" size="sm" color="blue-600" />
        </div>
        <div class="flex flex-col w-full">
          <div
            class="bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-bl-lg shadow-sm"
          >
            <!-- 思考过程模块 -->
            <div v-if="message.steps && message.steps.length > 0" class="mb-4">
              <h4
                class="text-xs font-semibold text-gray-500 uppercase mb-3 flex items-center gap-2"
              >
                <Icon name="psychology" size="sm" class="text-blue-600" />
                思考过程
              </h4>
              <TransitionGroup name="step-fade" tag="div" class="space-y-3">
                <div
                  v-for="step in message.steps"
                  :key="step.id"
                  class="bg-gray-50 p-3 rounded-lg border border-gray-200 text-sm"
                >
                  <!-- 工具调用渲染 -->
                  <div v-if="step.type === 'tool_call'">
                    <div class="flex items-center space-x-2 font-medium text-gray-700">
                      <Icon
                        v-if="step.status === 'running'"
                        name="progress_activity"
                        size="sm"
                        class="text-blue-600 animate-spin"
                      />
                      <Icon
                        v-else-if="step.status === 'finished'"
                        name="check_circle"
                        size="sm"
                        class="text-green-600"
                        :fill="1"
                      />
                      <Icon v-else name="error" size="sm" class="text-red-500" />
                      <span
                        >调用工具:
                        <strong class="text-blue-700">{{ step.data.tool_name }}</strong></span
                      >
                    </div>
                    <details class="mt-2 pl-7 text-xs text-gray-500">
                      <summary class="cursor-pointer hover:text-gray-800 focus:outline-none">
                        查看参数
                      </summary>
                      <code class="block whitespace-pre-wrap bg-gray-100 p-2 rounded-md mt-1">{{
                        JSON.stringify(step.data.arguments, null, 2)
                      }}</code>
                    </details>
                    <details
                      v-if="step.status === 'finished' && step.data.result"
                      class="mt-1 pl-7 text-xs text-gray-500"
                      open
                    >
                      <summary class="cursor-pointer hover:text-gray-800 focus:outline-none">
                        查看结果
                      </summary>
                      <code class="block whitespace-pre-wrap bg-gray-100 p-2 rounded-md mt-1">{{
                        isJSON(step.data.result)
                          ? JSON.stringify(JSON.parse(step.data.result), null, 2)
                          : step.data.result
                      }}</code>
                    </details>
                  </div>

                  <!-- 思考过程渲染 -->
                  <div v-else-if="step.type === 'thought'">
                    <div class="flex items-start space-x-2 text-gray-700">
                      <Icon
                        name="psychology_alt"
                        size="sm"
                        class="text-purple-600 flex-shrink-0 mt-0.5"
                      />
                      <div class="flex-grow">
                        <p class="font-medium text-purple-800">思考中...</p>
                        <p class="mt-1 text-gray-600 whitespace-pre-wrap">
                          {{ step.data.content }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </TransitionGroup>
            </div>

            <!-- 文档搜索结果卡片 -->
            <div
              v-if="message.document_results && message.document_results.length > 0"
              class="mb-4"
            >
              <h4
                class="text-xs font-semibold text-gray-500 uppercase mb-3 flex items-center gap-2"
              >
                <Icon name="manage_search" size="sm" color="blue-600" />
                检索到相关文档
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div
                  v-for="(doc, index) in message.document_results"
                  :key="index"
                  class="bg-white border border-gray-200 rounded-lg shadow-sm p-3 space-y-2 flex flex-col justify-between hover:shadow-md hover:border-red-200 transition-all duration-200 cursor-pointer"
                >
                  <div>
                    <div class="flex items-start space-x-2">
                      <Icon name="article" size="sm" class="text-red-700 mt-0.5 flex-shrink-0" />
                      <p
                        class="font-medium text-sm text-gray-900 leading-tight"
                        :title="doc.file_name"
                      >
                        {{ doc.file_name }}
                      </p>
                    </div>
                    <p class="text-sm text-gray-600 line-clamp-2 mt-2 pl-6">
                      {{ doc.content }}
                    </p>
                  </div>
                  <div class="flex justify-end pt-1">
                    <span
                      class="text-xs font-semibold bg-red-50 text-red-700 px-2 py-1 rounded-full"
                    >
                      Score: {{ doc.score }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分隔线，区分思考过程和最终答案 -->
            <hr
              v-if="
                (message.steps.length > 0 || (message.document_results?.length || 0) > 0) &&
                message.content
              "
              class="my-4 border-gray-200"
            />

            <!-- 助手回复内容 -->
            <div
              v-if="message.content"
              class="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap min-h-[20px]"
            >
              {{ message.content }}
            </div>

            <!-- 引用来源 -->
            <div
              v-if="message.sources && message.sources.length > 0"
              class="mt-4 pt-3 border-t border-gray-200"
            >
              <h4
                class="text-xs font-semibold text-gray-500 uppercase mb-3 flex items-center gap-2"
              >
                <Icon name="library_books" size="sm" class="text-blue-600" />
                引用来源
              </h4>
              <div class="flex flex-wrap gap-2">
                <div
                  v-for="(source, index) in message.sources"
                  :key="index"
                  class="flex items-center space-x-1.5 bg-gray-100 border border-gray-200 rounded-full px-2.5 py-1 hover:bg-red-50 hover:border-red-300 transition-colors duration-200 cursor-pointer"
                  :title="`文件名: ${source.file_name}`"
                >
                  <Icon name="article" size="xs" class="text-red-700" />
                  <span class="text-xs font-medium text-gray-700 truncate max-w-[200px]">{{
                    source.file_name
                  }}</span>
                  <span class="text-xs text-gray-400">|</span>
                  <span class="text-xs text-gray-500 font-semibold">{{ source.score }}</span>
                </div>
              </div>
            </div>

            <!-- 加载状态 -->
            <div
              v-if="message.status && !message.content"
              class="flex items-center space-x-2 text-sm text-gray-500"
            >
              <Icon name="progress_activity" size="sm" class="text-blue-600 animate-spin" />
              <span>{{ message.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 时间戳 -->
    <div
      class="flex text-xs text-gray-400 mt-1"
      :class="message.role === 'user' ? 'justify-end mr-12' : 'justify-start ml-12'"
    >
      {{ formatTime(message.timestamp) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Icon from '@/components/common/Icon.vue'
import FileMessageRenderer from '@/components/chat/FileMessageRenderer.vue'
import type { ChatMessage } from '@/services/api'

interface Props {
  message: ChatMessage
  animateIn?: boolean
  uploadProgress?: number // 用于文件上传进度
}

interface Emits {
  (event: 'edit-metadata', messageId: string): void
  (event: 'confirm-upload', messageId: string): void
  (event: 'cancel-upload', messageId: string): void
  (event: 'retry-upload', messageId: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formatTime = (date: Date) => {
  return new Date(date).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 检查字符串是否是有效的JSON
const isJSON = (str: string | undefined): boolean => {
  if (typeof str !== 'string') return false
  try {
    JSON.parse(str)
    return true
  } catch (e) {
    return false
  }
}

// 如果消息是文件消息，使用传入的上传进度，否则为0
const uploadProgress = computed(() => {
  if (props.message.is_file_message && props.uploadProgress !== undefined) {
    return props.uploadProgress
  }
  return 0
})
</script>

<style scoped>
.chat-message {
  animation: slideIn 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-message:hover .bg-white {
  box-shadow:
    0 4px 6px -1px rgb(0 0 0 / 0.1),
    0 2px 4px -2px rgb(0 0 0 / 0.1);
}

.chat-message:hover .bg-red-600 {
  background-color: rgb(185 28 28);
}

/* 工具调用步骤的淡入动画 */
.step-fade-enter-active,
.step-fade-leave-active {
  transition: all 0.5s ease;
}
.step-fade-enter-from,
.step-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
.step-fade-move {
  transition: transform 0.5s ease;
}

/* 文本截断样式 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
