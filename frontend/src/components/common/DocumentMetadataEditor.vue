<template>
  <div class="h-full flex flex-col max-h-full">
    <!-- 文件信息头部 -->
    <div class="flex-shrink-0 p-6 border-b border-gray-200 bg-gray-50">
      <div class="file-info">
        <Icon name="description" size="lg" color="red-600" />
        <div class="flex-1 min-w-0">
          <h3 class="file-name">{{ filename }}</h3>
          <p class="file-details">
            {{ FileUploadHelper.formatFileSize(fileSize) }} •
            {{ new Date().toLocaleDateString('zh-CN') }}
          </p>
        </div>
      </div>
      <div v-if="selectedTemplate" class="tag-blue">
        <Icon name="category" size="sm" />
        <span>{{ selectedTemplate.name }}</span>
      </div>
    </div>

    <!-- 主要内容区域 - 可滚动 -->
    <div class="flex-1 overflow-y-auto min-h-0">
      <div class="p-6 space-y-6">
        <!-- 文档类型选择 -->
        <div class="section">
          <h4 class="section-title">
            <Icon name="category" size="sm" color="blue-600" />
            文档类型
          </h4>
          <p class="section-description">请选择文档类型以应用相应的元数据模板</p>

          <div class="form-group">
            <select v-model="selectedDocType" class="form-select" @change="onDocTypeChange">
              <option value="">请选择文档类型</option>
              <option
                v-for="template in documentTemplates"
                :key="template.type"
                :value="template.type"
              >
                {{ template.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- 动态元数据表单 -->
        <div v-if="selectedTemplate" class="section">
          <h4 class="section-title">
            <Icon name="auto_fix_high" size="sm" color="blue-600" />
            文档元数据
          </h4>
          <p class="section-description">以下是AI自动提取的文档信息，请检查并根据需要进行修改</p>

          <div class="space-y-4">
            <div
              v-for="[fieldKey, fieldSchema] in templateFields"
              :key="fieldKey"
              class="form-group"
            >
              <label class="form-label">
                <Icon :name="getFieldIcon(fieldKey, fieldSchema)" size="sm" />
                {{ fieldSchema.title || fieldSchema.description || fieldKey }}
                <span v-if="isRequired(fieldKey)" class="text-red-500">*</span>
              </label>

              <!-- 数组输入（如作者、关键词等） -->
              <div v-if="isArrayField(fieldSchema)" class="array-input">
                <div v-if="getArrayValue(fieldKey).length > 0" class="array-items">
                  <span
                    v-for="(item, index) in getArrayValue(fieldKey)"
                    :key="index"
                    class="array-tag"
                  >
                    {{ item }}
                    <button @click="removeArrayItem(fieldKey, index)" class="array-tag-remove">
                      <Icon name="close" size="xs" />
                    </button>
                  </span>
                </div>
                <input
                  v-model="arrayInputs[fieldKey]"
                  @keydown.enter="addArrayItem(fieldKey)"
                  @keydown.comma.prevent="addArrayItem(fieldKey)"
                  type="text"
                  class="array-input-field"
                  :placeholder="`输入${fieldSchema.title || fieldKey}，按回车或逗号添加`"
                />
              </div>

              <!-- 日期输入 -->
              <input
                v-else-if="isDateField(fieldSchema)"
                v-model="formData[fieldKey]"
                type="date"
                class="form-input"
              />

              <!-- 多行文本输入（如摘要） -->
              <textarea
                v-else-if="
                  fieldKey === 'abstract' ||
                  fieldKey === 'summary' ||
                  (fieldSchema.description && fieldSchema.description.includes('摘要'))
                "
                v-model="formData[fieldKey]"
                rows="4"
                class="form-textarea"
                :placeholder="`请输入${fieldSchema.title || fieldKey}`"
              ></textarea>

              <!-- 字符串输入（默认） -->
              <input
                v-else
                v-model="formData[fieldKey]"
                type="text"
                class="form-input"
                :placeholder="`请输入${fieldSchema.title || fieldKey}`"
              />
            </div>
          </div>
        </div>

        <!-- 文档预览 -->
        <div v-if="extractedContent" class="section">
          <h4 class="section-title">
            <Icon name="preview" size="sm" color="green-600" />
            文档预览
          </h4>
          <div
            class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm text-gray-700 max-h-48 overflow-y-auto"
          >
            {{ extractedContent }}
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 - 固定在底部 -->
    <div class="flex-shrink-0 px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end gap-3">
      <button @click="handleCancel" class="btn-secondary" :disabled="isSubmitting">
        <Icon name="close" size="sm" />
        取消
      </button>
      <button
        @click="handleConfirm"
        class="btn-primary"
        :disabled="isSubmitting || !selectedDocType"
      >
        <Icon
          :name="isSubmitting ? 'progress_activity' : 'check'"
          size="sm"
          :class="{ 'animate-spin': isSubmitting }"
        />
        {{ isSubmitting ? '添加中...' : '确认并添加到知识库' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import Icon from '@/components/common/Icon.vue'
import { FileUploadHelper, type DocumentTemplate } from '@/services/api'

interface Props {
  filename: string
  fileSize: number
  fileId: string
  extractedMetadata: Record<string, any>
  documentTemplates: DocumentTemplate[]
  isSubmitting?: boolean
}

interface Emits {
  (
    event: 'confirm',
    data: { fileId: string; metadata: Record<string, any>; filename: string },
  ): void
  (event: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  isSubmitting: false,
})

const emit = defineEmits<Emits>()

// 响应式数据
const selectedDocType = ref('')
const formData = ref<Record<string, any>>({})
const arrayInputs = ref<Record<string, string>>({})
const extractedContent = ref('')

// 计算属性
const selectedTemplate = computed(() => {
  return props.documentTemplates.find((t) => t.type === selectedDocType.value)
})

const templateFields = computed(() => {
  if (!selectedTemplate.value?.schema?.properties) return []
  return Object.entries(selectedTemplate.value.schema.properties) as [string, any][]
})

const isRequired = (fieldKey: string) => {
  return selectedTemplate.value?.schema?.required?.includes(fieldKey) || false
}

// 工具函数
const isArrayField = (fieldSchema: any) => {
  return fieldSchema.type === 'array'
}

const isStringField = (fieldSchema: any) => {
  // 处理直接的string类型
  if (fieldSchema.type === 'string') return true

  // 处理anyOf结构（如 anyOf: [{type: "string"}, {type: "null"}]）
  if (fieldSchema.anyOf && Array.isArray(fieldSchema.anyOf)) {
    return fieldSchema.anyOf.some((option: any) => option.type === 'string')
  }

  return false
}

const isDateField = (fieldSchema: any) => {
  return (
    fieldSchema.format === 'date' ||
    (fieldSchema.anyOf && fieldSchema.anyOf.some((option: any) => option.format === 'date'))
  )
}

const getArrayValue = (fieldKey: string): string[] => {
  const value = formData.value[fieldKey]
  if (Array.isArray(value)) return value
  if (typeof value === 'string' && value.trim()) {
    return value
      .split(',')
      .map((item) => item.trim())
      .filter((item) => item)
  }
  return []
}

const getFieldIcon = (fieldKey: string, fieldSchema: any) => {
  const iconMap: Record<string, string> = {
    title: 'title',
    name: 'title',
    authors: 'person',
    author: 'person',
    participants: 'group',
    date: 'event',
    time: 'schedule',
    keywords: 'tag',
    tags: 'tag',
    abstract: 'description',
    summary: 'description',
    journal: 'book',
    department: 'business',
    subject: 'subject',
    agenda: 'list',
    decisions: 'check_circle',
    actions: 'task',
  }

  // 根据字段名匹配图标
  for (const [key, icon] of Object.entries(iconMap)) {
    if (fieldKey.toLowerCase().includes(key)) {
      return icon
    }
  }

  // 根据类型匹配图标
  if (fieldSchema.type === 'array') return 'list'
  if (fieldSchema.format === 'date') return 'event'

  return 'extension'
}

// 数组操作
const addArrayItem = (fieldKey: string) => {
  const input = arrayInputs.value[fieldKey]?.trim().replace(/,$/, '')
  if (!input) return

  const currentArray = getArrayValue(fieldKey)
  if (!currentArray.includes(input)) {
    formData.value[fieldKey] = [...currentArray, input]
    arrayInputs.value[fieldKey] = ''
  }
}

const removeArrayItem = (fieldKey: string, index: number) => {
  const currentArray = getArrayValue(fieldKey)
  currentArray.splice(index, 1)
  formData.value[fieldKey] = [...currentArray]
}

// 事件处理
const onDocTypeChange = () => {
  // 切换文档类型时，重新初始化表单数据
  initializeFormData()
}

const handleConfirm = () => {
  if (!selectedDocType.value) return

  // 准备字段数据
  const extractedFields: Record<string, any> = { ...formData.value }

  templateFields.value.forEach(([fieldKey, fieldSchema]) => {
    if (isArrayField(fieldSchema)) {
      extractedFields[fieldKey] = getArrayValue(fieldKey)
    }
  })

  // 🔥 修复：按照后端期待的结构组织数据
  const finalMetadata = {
    document_type: selectedDocType.value,
    extracted_fields: extractedFields,
  }

  console.log('Final metadata to send:', finalMetadata)

  emit('confirm', {
    fileId: props.fileId,
    metadata: finalMetadata,
    filename: props.filename,
  })
}

const handleCancel = () => {
  emit('cancel')
}

// 初始化表单数据
const initializeFormData = () => {
  if (!selectedTemplate.value) {
    formData.value = {}
    return
  }

  // 基于模板字段初始化表单数据
  const newFormData: Record<string, any> = {}

  // 直接从 extracted_fields 获取数据
  const sourceData = props.extractedMetadata?.extracted_fields || {}

  templateFields.value.forEach(([fieldKey, fieldSchema]) => {
    const extractedValue = sourceData[fieldKey]

    if (isArrayField(fieldSchema)) {
      // 处理数组字段
      if (Array.isArray(extractedValue)) {
        newFormData[fieldKey] = extractedValue
      } else {
        newFormData[fieldKey] = fieldSchema.default || []
      }
    } else {
      // 处理其他字段 - 包括anyOf类型的字段
      newFormData[fieldKey] = extractedValue ?? fieldSchema.default ?? ''
    }

    // 初始化数组输入框
    if (isArrayField(fieldSchema)) {
      arrayInputs.value[fieldKey] = ''
    }
  })

  console.log('Initialized form data:', newFormData)
  formData.value = newFormData
}

// 组件初始化
onMounted(() => {
  console.log('Props extractedMetadata:', props.extractedMetadata)
  console.log(
    'Available templates:',
    props.documentTemplates.map((t) => t.type),
  )

  // 直接读取 document_type
  const extractedDocType = props.extractedMetadata?.document_type
  console.log('Extracted doc type:', extractedDocType)

  if (extractedDocType && props.documentTemplates.some((t) => t.type === extractedDocType)) {
    selectedDocType.value = extractedDocType
    console.log('Auto-selected document type:', extractedDocType)
  }

  // 初始化表单数据
  initializeFormData()

  // 设置内容预览
  if (props.extractedMetadata?.content_preview) {
    extractedContent.value = props.extractedMetadata.content_preview.substring(0, 500) + '...'
  }

  // 调试：检查模板字段
  if (selectedTemplate.value) {
    console.log('Template fields debug:')
    templateFields.value.forEach(([fieldKey, fieldSchema]) => {
      console.log(`Field: ${fieldKey}`, {
        type: fieldSchema.type,
        anyOf: fieldSchema.anyOf,
        format: fieldSchema.format,
        title: fieldSchema.title,
        isArray: isArrayField(fieldSchema),
        isString: isStringField(fieldSchema),
        isDate: isDateField(fieldSchema),
      })
    })
  }
})

// 监听文档类型变化
watch(
  selectedDocType,
  () => {
    initializeFormData()
  },
  { immediate: false },
)
</script>
