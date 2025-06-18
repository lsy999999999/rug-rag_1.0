<template>
  <div
    class="file-upload-area"
    :class="{
      'drag-over': isDragOver,
      uploading: isUploading,
      disabled: disabled,
    }"
    @drop="handleDrop"
    @dragover="handleDragOver"
    @dragenter="handleDragEnter"
    @dragleave="handleDragLeave"
    @click="triggerFileInput"
  >
    <input
      ref="fileInput"
      type="file"
      multiple
      accept=".pdf,.docx,.pptx,.xlsx,.doc,.ppt,.xls,.txt"
      @change="handleFileSelect"
      class="hidden"
    />

    <div class="upload-content">
      <div class="upload-icon">
        <Icon
          :name="isUploading ? 'cloud_upload' : 'cloud_upload'"
          size="xl"
          :class="isUploading ? 'animate-pulse text-blue-600' : 'text-gray-400'"
        />
      </div>

      <div class="upload-text">
        <h3 class="upload-title">
          {{ isUploading ? '正在上传文件...' : '拖拽文件到此处或点击上传' }}
        </h3>
        <p class="upload-description" v-if="!isUploading">
          支持 PDF、Word、PowerPoint、Excel 等文档格式
        </p>
        <p class="upload-description" v-else>
          {{ uploadProgress > 0 ? `上传进度: ${Math.round(uploadProgress)}%` : '准备上传...' }}
        </p>
      </div>

      <div class="supported-formats" v-if="!isUploading">
        <div class="format-tag">PDF</div>
        <div class="format-tag">DOCX</div>
        <div class="format-tag">PPTX</div>
        <div class="format-tag">XLSX</div>
      </div>
    </div>

    <!-- 上传进度条 -->
    <div v-if="isUploading && uploadProgress > 0" class="progress-bar">
      <div class="progress-fill" :style="{ width: `${uploadProgress}%` }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Icon from '@/components/common/Icon.vue'
import { FileUploadHelper } from '@/services/api'

interface Props {
  disabled?: boolean
  isUploading?: boolean
  uploadProgress?: number
}

interface Emits {
  (event: 'files-selected', files: File[]): void
  (event: 'upload-error', error: string): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  isUploading: false,
  uploadProgress: 0,
})

const emit = defineEmits<Emits>()

const fileInput = ref<HTMLInputElement>()
const isDragOver = ref(false)

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  isDragOver.value = false

  if (props.disabled || props.isUploading) return

  const files = Array.from(e.dataTransfer?.files || [])
  handleFiles(files)
}

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
}

const handleDragEnter = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  if (!props.disabled && !props.isUploading) {
    isDragOver.value = true
  }
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  // 只有当离开整个拖拽区域时才设置为false
  const currentTarget = e.currentTarget as HTMLElement | null
  if (currentTarget && !currentTarget.contains(e.relatedTarget as Node)) {
    isDragOver.value = false
  }
}

const triggerFileInput = () => {
  if (props.disabled || props.isUploading) return
  fileInput.value?.click()
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = Array.from(target.files || [])
  handleFiles(files)

  // 清空input值，允许选择相同文件
  target.value = ''
}

const handleFiles = (files: File[]) => {
  if (files.length === 0) return

  // 检查文件类型
  const invalidFiles = files.filter((file) => !FileUploadHelper.isSupportedFileType(file))

  if (invalidFiles.length > 0) {
    emit('upload-error', `不支持的文件类型: ${invalidFiles.map((f) => f.name).join(', ')}`)
    return
  }

  // 检查文件大小 (限制50MB)
  const oversizedFiles = files.filter((file) => file.size > 50 * 1024 * 1024)

  if (oversizedFiles.length > 0) {
    emit('upload-error', `文件过大 (超过50MB): ${oversizedFiles.map((f) => f.name).join(', ')}`)
    return
  }

  emit('files-selected', files)
}
</script>

<style scoped>
.file-upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  background-color: #fafafa;
  position: relative;
  overflow: hidden;
}

.file-upload-area:hover:not(.disabled):not(.uploading) {
  border-color: #dc2626;
  background-color: #fef2f2;
}

.file-upload-area.drag-over {
  border-color: #dc2626;
  background-color: #fef2f2;
  transform: scale(1.02);
}

.file-upload-area.uploading {
  border-color: #2563eb;
  background-color: #eff6ff;
  cursor: not-allowed;
}

.file-upload-area.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #f3f4f6;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  background-color: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.file-upload-area:hover:not(.disabled) .upload-icon {
  background-color: #fee2e2;
}

.file-upload-area.drag-over .upload-icon {
  background-color: #fee2e2;
  transform: scale(1.1);
}

.upload-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.upload-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.supported-formats {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 0.5rem;
}

.format-tag {
  background-color: #e5e7eb;
  color: #374151;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background-color: #e5e7eb;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #2563eb;
  transition: width 0.3s ease;
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%,
    transparent
  );
  background-size: 1rem 1rem;
  animation: progress-stripes 1s linear infinite;
}

@keyframes progress-stripes {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 1rem 0;
  }
}

.hidden {
  display: none;
}
</style>
