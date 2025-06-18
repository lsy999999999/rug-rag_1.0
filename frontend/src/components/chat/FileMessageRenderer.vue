<!-- FileMessageRenderer.vue -->
<template>
  <div class="file-message-card bg-white border border-gray-200 rounded-lg p-4">
    <!-- 文件信息头部 -->
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
            <Icon
              :name="getFileIcon(message.file_info?.filename || '')"
              size="md"
              color="gray-600"
            />
          </div>
        </div>
        <div class="flex-1 min-w-0">
          <h4 class="text-sm font-medium text-gray-900 truncate">
            {{ message.file_info?.filename || '未知文件' }}
          </h4>
          <p class="text-xs text-gray-500">
            {{ formatFileSize(message.file_info?.file_size || 0) }}
          </p>
        </div>
      </div>

      <!-- 状态图标 -->
      <div class="flex-shrink-0">
        <Icon
          v-if="message.upload_status === 'uploading'"
          name="sync"
          size="sm"
          color="blue-500"
          class="animate-spin"
        />
        <Icon
          v-else-if="message.upload_status === 'uploaded'"
          name="check_circle"
          size="sm"
          color="green-500"
        />
        <Icon
          v-else-if="message.upload_status === 'error'"
          name="error"
          size="sm"
          color="red-500"
        />
        <Icon
          v-else-if="message.upload_status === 'confirming'"
          name="hourglass_empty"
          size="sm"
          color="yellow-500"
        />
        <Icon
          v-else-if="message.upload_status === 'confirmed'"
          name="task_alt"
          size="sm"
          color="green-600"
        />
      </div>
    </div>

    <!-- 进度条 -->
    <div v-if="message.upload_status === 'uploading'" class="mb-3">
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div
          class="bg-blue-500 h-2 rounded-full transition-all duration-300"
          :style="{ width: `${uploadProgress}%` }"
        ></div>
      </div>
      <p class="text-xs text-gray-500 mt-1">上传中... {{ Math.round(uploadProgress) }}%</p>
    </div>

    <!-- 状态消息 -->
    <div class="mb-3">
      <p class="text-sm text-gray-700">{{ message.content }}</p>
    </div>

    <!-- 元数据预览 (上传成功后显示) -->
    <div
      v-if="message.upload_status === 'uploaded' && message.file_info?.extracted_metadata"
      class="bg-gray-50 rounded-lg p-3 mb-3"
    >
      <h5 class="text-sm font-medium text-gray-900 mb-2">提取的文档信息</h5>
      <div class="space-y-2">
        <div v-if="message.file_info.extracted_metadata.document_type" class="text-xs">
          <span class="text-gray-500">文档类型:</span>
          <span class="text-gray-900 ml-2">{{
            getDocumentTypeName(message.file_info.extracted_metadata.document_type)
          }}</span>
        </div>
        <div v-if="message.file_info.extracted_metadata.extracted_fields" class="text-xs">
          <span class="text-gray-500">字段数量:</span>
          <span class="text-gray-900 ml-2"
            >{{
              Object.keys(message.file_info.extracted_metadata.extracted_fields).length
            }}
            个</span
          >
        </div>
        <div v-if="message.file_info.extracted_metadata.content_preview" class="text-xs">
          <span class="text-gray-500">内容预览:</span>
          <p class="text-gray-700 mt-1 truncate">
            {{ message.file_info.extracted_metadata.content_preview }}
          </p>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="flex items-center space-x-2">
      <!-- 上传中状态 -->
      <template v-if="message.upload_status === 'uploading'">
        <button @click="handleCancelUpload" class="btn-secondary text-xs px-2 py-1">
          <Icon name="close" size="xs" />
          取消
        </button>
      </template>

      <!-- 上传成功状态 -->
      <template v-else-if="message.upload_status === 'uploaded'">
        <button @click="handleEditMetadata" class="btn-primary text-xs px-2 py-1">
          <Icon name="edit" size="xs" />
          编辑元数据
        </button>
        <button @click="handleConfirmUpload" class="btn-primary text-xs px-2 py-1">
          <Icon name="check" size="xs" />
          添加到知识库
        </button>
        <button @click="handleCancelUpload" class="btn-secondary text-xs px-2 py-1">
          <Icon name="delete" size="xs" />
          删除
        </button>
      </template>

      <!-- 错误状态 -->
      <template v-else-if="message.upload_status === 'error'">
        <button @click="handleRetryUpload" class="btn-primary text-xs px-2 py-1">
          <Icon name="refresh" size="xs" />
          重试
        </button>
        <button @click="handleCancelUpload" class="btn-secondary text-xs px-2 py-1">
          <Icon name="delete" size="xs" />
          删除
        </button>
      </template>

      <!-- 确认中状态 -->
      <template v-else-if="message.upload_status === 'confirming'">
        <div class="text-xs text-gray-500 flex items-center">
          <Icon name="hourglass_empty" size="xs" color="yellow-500" class="mr-1" />
          正在添加到知识库...
        </div>
      </template>

      <!-- 已确认状态 -->
      <template v-else-if="message.upload_status === 'confirmed'">
        <div class="text-xs text-green-600 flex items-center">
          <Icon name="check_circle" size="xs" color="green-600" class="mr-1" />
          已添加到知识库
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import Icon from '@/components/common/Icon.vue'
import type { ChatMessage } from '@/services/api'

interface Props {
  message: ChatMessage
  uploadProgress: number
}

interface Emits {
  (event: 'editMetadata', messageId: string): void
  (event: 'confirmUpload', messageId: string): void
  (event: 'cancelUpload', messageId: string): void
  (event: 'retryUpload', messageId: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const handleEditMetadata = () => {
  emit('editMetadata', props.message.id)
}

const handleConfirmUpload = () => {
  emit('confirmUpload', props.message.id)
}

const handleCancelUpload = () => {
  emit('cancelUpload', props.message.id)
}

const handleRetryUpload = () => {
  emit('retryUpload', props.message.id)
}

const getFileIcon = (filename: string): string => {
  const extension = filename.split('.').pop()?.toLowerCase()
  switch (extension) {
    case 'pdf':
      return 'picture_as_pdf'
    case 'doc':
    case 'docx':
      return 'description'
    case 'ppt':
    case 'pptx':
      return 'slideshow'
    case 'xls':
    case 'xlsx':
      return 'table_chart'
    case 'txt':
      return 'text_snippet'
    default:
      return 'attach_file'
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getDocumentTypeName = (docType: string): string => {
  const typeMap: Record<string, string> = {
    academic_paper: '学术论文',
    administrative_document: '行政文件',
    meeting_minutes: '会议纪要',
    general_document: '通用文档',
  }
  return typeMap[docType] || docType
}
</script>

<style scoped>
.file-message-card {
  max-width: 400px;
}
</style>
