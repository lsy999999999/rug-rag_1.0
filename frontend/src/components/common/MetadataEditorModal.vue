<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click="handleOverlayClick">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h2 class="modal-title">
              <Icon name="edit_document" size="md" color="red-600" />
              编辑文档元数据
            </h2>
            <button @click="handleClose" class="btn-secondary !p-2">
              <Icon name="close" size="sm" />
            </button>
          </div>

          <div class="modal-body">
            <DocumentMetadataEditor
              v-if="fileInfo"
              :filename="fileInfo.filename"
              :file-size="fileInfo.file_size || 0"
              :file-id="fileInfo.file_id"
              :extracted-metadata="fileInfo.extracted_metadata"
              :document-templates="documentTemplates"
              :is-submitting="isSubmitting"
              @confirm="handleConfirm"
              @cancel="handleClose"
            />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { watch, onUnmounted } from 'vue'
import Icon from '@/components/common/Icon.vue'
import DocumentMetadataEditor from '@/components/common/DocumentMetadataEditor.vue'
import type { FileInfo, DocumentTemplate } from '@/services/api'

interface Props {
  isOpen: boolean
  fileInfo: FileInfo | null
  documentTemplates: DocumentTemplate[]
  isSubmitting?: boolean
}

interface Emits {
  (event: 'close'): void
  (
    event: 'confirm',
    data: { fileId: string; metadata: Record<string, any>; filename: string },
  ): void
}

const props = withDefaults(defineProps<Props>(), {
  isSubmitting: false,
})

const emit = defineEmits<Emits>()

const handleClose = () => {
  if (props.isSubmitting) return
  emit('close')
}

const handleOverlayClick = () => {
  handleClose()
}

const handleConfirm = (data: {
  fileId: string
  metadata: Record<string, any>
  filename: string
}) => {
  emit('confirm', data)
}

// 键盘事件处理
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && props.isOpen && !props.isSubmitting) {
    handleClose()
  }
}

// 管理页面滚动和键盘事件
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      // 禁止页面滚动
      document.body.style.overflow = 'hidden'
      document.addEventListener('keydown', handleKeydown)
    } else {
      // 恢复页面滚动
      document.body.style.overflow = ''
      document.removeEventListener('keydown', handleKeydown)
    }
  },
)

// 组件卸载时恢复状态
onUnmounted(() => {
  document.body.style.overflow = ''
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* 模态框动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95) translateY(-20px);
}
</style>
