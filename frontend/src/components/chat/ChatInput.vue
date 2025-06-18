<template>
  <div class="chat-input-container">
    <!-- 文件上传区域 (拖拽时显示) -->
    <Transition name="slide-up">
      <div v-if="isDragOver" class="drag-overlay">
        <div class="drag-content">
          <Icon name="cloud_upload" size="xl" color="blue-600" class="animate-bounce" />
          <h3 class="drag-title">释放文件以上传</h3>
          <p class="drag-description">支持 PDF、Word、PowerPoint、Excel 等文档格式</p>
        </div>
      </div>
    </Transition>

    <!-- 主输入区域 -->
    <div
      class="input-wrapper"
      :class="{ 'drag-active': isDragOver }"
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragenter="handleDragEnter"
      @dragleave="handleDragLeave"
    >
      <!-- 文件上传显示区域 -->
      <div v-if="pendingFiles.length > 0" class="pending-files">
        <div class="pending-files-header">
          <h4 class="pending-title">
            <Icon name="attach_file" size="sm" />
            待上传文件 ({{ pendingFiles.length }})
          </h4>
          <button @click="clearPendingFiles" class="clear-btn">
            <Icon name="close" size="sm" />
          </button>
        </div>
        <div class="pending-files-list">
          <div v-for="(file, index) in pendingFiles" :key="index" class="pending-file">
            <Icon :name="getFileIcon(file.type)" size="sm" color="blue-600" />
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ FileUploadHelper.formatFileSize(file.size) }}</span>
            <button @click="removePendingFile(index)" class="remove-file-btn">
              <Icon name="close" size="xs" />
            </button>
          </div>
        </div>
      </div>

      <!-- 输入框区域 -->
      <div class="input-area">
        <div class="input-row">
          <!-- 文件上传按钮 -->
          <button
            @click="triggerFileInput"
            class="file-upload-btn"
            :disabled="disabled"
            title="上传文档"
          >
            <Icon name="attach_file" size="sm" />
          </button>

          <!-- 文本输入框 -->
          <textarea
            ref="textareaRef"
            v-model="inputValue"
            :placeholder="getPlaceholder()"
            :disabled="disabled"
            @keydown="handleKeydown"
            @input="handleInput"
            class="text-input"
            rows="1"
          ></textarea>

          <!-- 发送按钮 -->
          <button
            @click="handleSend"
            :disabled="!canSend"
            class="send-btn"
            :class="{ loading: isLoading }"
          >
            <Icon
              :name="isLoading ? 'progress_activity' : 'send'"
              size="sm"
              :class="{ 'animate-spin': isLoading }"
            />
          </button>
        </div>

        <!-- 建议词（仅在对话开始时显示） -->
        <div v-if="showSuggestions && suggestions.length > 0" class="suggestions">
          <button
            v-for="suggestion in suggestions"
            :key="suggestion"
            @click="handleSuggestionClick(suggestion)"
            class="suggestion-chip"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInputRef"
      type="file"
      multiple
      accept=".pdf,.docx,.pptx,.xlsx,.doc,.ppt,.xls,.txt"
      @change="handleFileSelect"
      class="hidden"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import Icon from '@/components/common/Icon.vue'
import { FileUploadHelper } from '@/services/api'

interface Props {
  disabled?: boolean
  isLoading?: boolean
  showSuggestions?: boolean
}

interface Emits {
  (event: 'send', content: string): void
  (event: 'upload-files', files: File[]): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  isLoading: false,
  showSuggestions: false,
})

const emit = defineEmits<Emits>()

const textareaRef = ref<HTMLTextAreaElement>()
const fileInputRef = ref<HTMLInputElement>()
const inputValue = ref('')
const pendingFiles = ref<File[]>([])
const isDragOver = ref(false)

const suggestions = ref([
  '查询课程安排',
  '学籍管理流程',
  '奖学金申请',
  '图书馆服务',
  '宿舍管理规定',
])

const canSend = computed(() => {
  return (
    !props.disabled &&
    !props.isLoading &&
    (inputValue.value.trim() || pendingFiles.value.length > 0)
  )
})

const getPlaceholder = () => {
  if (props.isLoading) return '正在处理中...'
  if (pendingFiles.value.length > 0) return '输入消息或直接上传文件...'
  return '输入您的问题，或拖拽文件到此处上传...'
}

const getFileIcon = (fileType: string) => {
  if (fileType.includes('pdf')) return 'picture_as_pdf'
  if (fileType.includes('word') || fileType.includes('document')) return 'description'
  if (fileType.includes('presentation') || fileType.includes('powerpoint')) return 'slideshow'
  if (fileType.includes('spreadsheet') || fileType.includes('excel')) return 'table_chart'
  if (fileType.includes('text')) return 'article'
  return 'description'
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

const handleInput = () => {
  adjustTextareaHeight()
}

const adjustTextareaHeight = async () => {
  await nextTick()
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    const newHeight = Math.min(textareaRef.value.scrollHeight, 150) // 最大高度150px
    textareaRef.value.style.height = newHeight + 'px'
  }
}

const handleSend = () => {
  if (!canSend.value) return

  // 如果有文件，先上传文件
  if (pendingFiles.value.length > 0) {
    emit('upload-files', [...pendingFiles.value])
    clearPendingFiles()
  }

  // 如果有文本内容，发送消息
  if (inputValue.value.trim()) {
    emit('send', inputValue.value.trim())
    inputValue.value = ''
    adjustTextareaHeight()
  }
}

const handleSuggestionClick = (suggestion: string) => {
  inputValue.value = suggestion
  handleSend()
}

const triggerFileInput = () => {
  if (props.disabled) return
  fileInputRef.value?.click()
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = Array.from(target.files || [])
  addFiles(files)
  target.value = '' // 清空input，允许选择相同文件
}

const addFiles = (files: File[]) => {
  const validFiles = files.filter((file) => {
    // 检查文件类型
    if (!FileUploadHelper.isSupportedFileType(file)) {
      return false
    }
    // 检查文件大小（50MB限制）
    if (file.size > 50 * 1024 * 1024) {
      return false
    }
    // 检查是否重复
    if (pendingFiles.value.some((f) => f.name === file.name && f.size === file.size)) {
      return false
    }
    return true
  })

  pendingFiles.value.push(...validFiles)
}

const removePendingFile = (index: number) => {
  pendingFiles.value.splice(index, 1)
}

const clearPendingFiles = () => {
  pendingFiles.value = []
}

// 拖拽处理
const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  isDragOver.value = false

  if (props.disabled) return

  const files = Array.from(e.dataTransfer?.files || [])
  addFiles(files)
}

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
}

const handleDragEnter = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  if (!props.disabled) {
    isDragOver.value = true
  }
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()

  // Only set isDragOver to false when leaving the entire input area
  const currentTarget = e.currentTarget as Node | null
  const relatedTarget = e.relatedTarget as Node | null
  if (currentTarget && (!relatedTarget || !currentTarget.contains(relatedTarget))) {
    isDragOver.value = false
  }
}

// 监听输入值变化，自动调整高度
watch(inputValue, () => {
  adjustTextareaHeight()
})
</script>

<style scoped>
.chat-input-container {
  position: relative;
}

.drag-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(59, 130, 246, 0.1);
  border: 2px dashed #3b82f6;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  backdrop-filter: blur(2px);
}

.drag-content {
  text-align: center;
  padding: 2rem;
}

.drag-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e40af;
  margin: 0.5rem 0;
}

.drag-description {
  font-size: 0.875rem;
  color: #3b82f6;
  margin: 0;
}

.input-wrapper {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.input-wrapper:focus-within {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgb(220 38 38 / 0.1);
}

.input-wrapper.drag-active {
  border-color: #3b82f6;
  background-color: rgba(59, 130, 246, 0.05);
}

.pending-files {
  border-bottom: 1px solid #e5e7eb;
  background-color: #f8fafc;
}

.pending-files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem 0.5rem;
}

.pending-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.clear-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.clear-btn:hover {
  background-color: #f3f4f6;
  color: #374151;
}

.pending-files-list {
  padding: 0 1rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.pending-file {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
}

.file-name {
  flex: 1;
  color: #374151;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: #6b7280;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.remove-file-btn {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.125rem;
  border-radius: 4px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.remove-file-btn:hover {
  background-color: #f3f4f6;
  color: #ef4444;
}

.input-area {
  padding: 1rem;
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
}

.file-upload-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-upload-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
  color: #dc2626;
}

.file-upload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.text-input {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-size: 0.875rem;
  line-height: 1.5;
  padding: 0.5rem 0;
  min-height: 1.5rem;
  max-height: 150px;
  font-family: inherit;
}

.text-input::placeholder {
  color: #9ca3af;
}

.text-input:disabled {
  color: #9ca3af;
  cursor: not-allowed;
}

.send-btn {
  background-color: #dc2626;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  min-height: 2.5rem;
}

.send-btn:hover:not(:disabled) {
  background-color: #b91c1c;
  transform: scale(1.05);
}

.send-btn:disabled {
  background-color: #d1d5db;
  cursor: not-allowed;
  transform: none;
}

.send-btn.loading {
  background-color: #3b82f6;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
}

.suggestion-chip {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-size: 0.75rem;
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.suggestion-chip:hover {
  background-color: #fee2e2;
  border-color: #fecaca;
  color: #dc2626;
}

.hidden {
  display: none;
}

/* 动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
