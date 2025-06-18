// utils/fileUtils.ts

/**
 * 文件类型映射
 */
export const FILE_TYPE_ICONS: Record<string, string> = {
  // PDF
  'application/pdf': 'picture_as_pdf',

  // Microsoft Word
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'description',
  'application/msword': 'description',

  // Microsoft PowerPoint
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'slideshow',
  'application/vnd.ms-powerpoint': 'slideshow',

  // Microsoft Excel
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'table_chart',
  'application/vnd.ms-excel': 'table_chart',

  // Text files
  'text/plain': 'article',
  'text/csv': 'table_chart',

  // Default
  default: 'description',
}

/**
 * 文件类型显示名称映射
 */
export const FILE_TYPE_NAMES: Record<string, string> = {
  'application/pdf': 'PDF',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
  'application/msword': 'Word',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
  'application/vnd.ms-powerpoint': 'PowerPoint',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
  'application/vnd.ms-excel': 'Excel',
  'text/plain': 'Text',
  'text/csv': 'CSV',
}

/**
 * 支持的文件类型列表
 */
export const SUPPORTED_FILE_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/msword',
  'application/vnd.ms-powerpoint',
  'application/vnd.ms-excel',
  'text/plain',
]

/**
 * 最大文件大小 (50MB)
 */
export const MAX_FILE_SIZE = 50 * 1024 * 1024

/**
 * 获取文件类型对应的图标名称
 */
export function getFileIcon(fileType?: string): string {
  if (!fileType) return FILE_TYPE_ICONS.default
  return FILE_TYPE_ICONS[fileType] || FILE_TYPE_ICONS.default
}

/**
 * 获取文件类型的显示名称
 */
export function getFileTypeName(fileType: string): string {
  return FILE_TYPE_NAMES[fileType] || fileType.split('/').pop()?.toUpperCase() || '未知'
}

/**
 * 检查文件类型是否支持
 */
export function isSupportedFileType(fileType: string): boolean {
  return SUPPORTED_FILE_TYPES.includes(fileType)
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 验证文件是否有效
 */
export function validateFile(file: File): { valid: boolean; error?: string } {
  // 检查文件类型
  if (!isSupportedFileType(file.type)) {
    return {
      valid: false,
      error: `不支持的文件类型: ${getFileTypeName(file.type)}`,
    }
  }

  // 检查文件大小
  if (file.size > MAX_FILE_SIZE) {
    return {
      valid: false,
      error: `文件过大，最大支持 ${formatFileSize(MAX_FILE_SIZE)}`,
    }
  }

  // 检查文件名
  if (!file.name || file.name.trim() === '') {
    return {
      valid: false,
      error: '文件名不能为空',
    }
  }

  return { valid: true }
}

/**
 * 批量验证文件
 */
export function validateFiles(files: File[]): {
  validFiles: File[]
  invalidFiles: Array<{ file: File; error: string }>
} {
  const validFiles: File[] = []
  const invalidFiles: Array<{ file: File; error: string }> = []

  files.forEach((file) => {
    const validation = validateFile(file)
    if (validation.valid) {
      validFiles.push(file)
    } else {
      invalidFiles.push({ file, error: validation.error || '未知错误' })
    }
  })

  return { validFiles, invalidFiles }
}

/**
 * 获取文件扩展名
 */
export function getFileExtension(filename: string): string {
  const lastDotIndex = filename.lastIndexOf('.')
  if (lastDotIndex === -1 || lastDotIndex === filename.length - 1) {
    return ''
  }
  return filename.substring(lastDotIndex + 1).toLowerCase()
}

/**
 * 根据文件扩展名获取 MIME 类型
 */
export function getMimeTypeFromExtension(extension: string): string {
  const mimeTypes: Record<string, string> = {
    pdf: 'application/pdf',
    docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    doc: 'application/msword',
    pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    ppt: 'application/vnd.ms-powerpoint',
    xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    xls: 'application/vnd.ms-excel',
    txt: 'text/plain',
    csv: 'text/csv',
  }

  return mimeTypes[extension.toLowerCase()] || 'application/octet-stream'
}

/**
 * 生成唯一的文件ID
 */
export function generateFileId(): string {
  return `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 检查是否为图片文件（虽然当前不支持，但为了扩展性）
 */
export function isImageFile(fileType: string): boolean {
  return fileType.startsWith('image/')
}

/**
 * 检查是否为文档文件
 */
export function isDocumentFile(fileType: string): boolean {
  const documentTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'text/plain',
  ]

  return documentTypes.includes(fileType)
}

/**
 * 文件上传状态类型
 */
export type FileUploadStatus =
  | 'idle'
  | 'uploading'
  | 'uploaded'
  | 'confirming'
  | 'confirmed'
  | 'error'

/**
 * 获取上传状态的显示文本
 */
export function getUploadStatusText(status: FileUploadStatus): string {
  const statusTexts: Record<FileUploadStatus, string> = {
    idle: '等待上传',
    uploading: '上传中...',
    uploaded: '等待确认',
    confirming: '处理中...',
    confirmed: '已添加到知识库',
    error: '上传失败',
  }

  return statusTexts[status] || '未知状态'
}

/**
 * 获取上传状态的颜色
 */
export function getUploadStatusColor(status: FileUploadStatus): string {
  const statusColors: Record<FileUploadStatus, string> = {
    idle: 'gray-500',
    uploading: 'blue-600',
    uploaded: 'yellow-600',
    confirming: 'purple-600',
    confirmed: 'green-600',
    error: 'red-600',
  }

  return statusColors[status] || 'gray-500'
}

/**
 * 创建文件预览信息
 */
export function createFilePreview(file: File): {
  id: string
  name: string
  size: number
  type: string
  icon: string
  typeName: string
  formattedSize: string
} {
  return {
    id: generateFileId(),
    name: file.name,
    size: file.size,
    type: file.type,
    icon: getFileIcon(file.type),
    typeName: getFileTypeName(file.type),
    formattedSize: formatFileSize(file.size),
  }
}

/**
 * 文件拖拽处理工具
 */
export class FileDragHandler {
  private dragCounter = 0
  private element: HTMLElement
  private onDragEnter?: () => void
  private onDragLeave?: () => void
  private onDrop?: (files: File[]) => void

  constructor(
    element: HTMLElement,
    callbacks: {
      onDragEnter?: () => void
      onDragLeave?: () => void
      onDrop?: (files: File[]) => void
    },
  ) {
    this.element = element
    this.onDragEnter = callbacks.onDragEnter
    this.onDragLeave = callbacks.onDragLeave
    this.onDrop = callbacks.onDrop

    this.bindEvents()
  }

  private bindEvents() {
    this.element.addEventListener('dragenter', this.handleDragEnter.bind(this))
    this.element.addEventListener('dragleave', this.handleDragLeave.bind(this))
    this.element.addEventListener('dragover', this.handleDragOver.bind(this))
    this.element.addEventListener('drop', this.handleDrop.bind(this))
  }

  private handleDragEnter(e: DragEvent) {
    e.preventDefault()
    e.stopPropagation()
    this.dragCounter++

    if (this.dragCounter === 1) {
      this.onDragEnter?.()
    }
  }

  private handleDragLeave(e: DragEvent) {
    e.preventDefault()
    e.stopPropagation()
    this.dragCounter--

    if (this.dragCounter === 0) {
      this.onDragLeave?.()
    }
  }

  private handleDragOver(e: DragEvent) {
    e.preventDefault()
    e.stopPropagation()
  }

  private handleDrop(e: DragEvent) {
    e.preventDefault()
    e.stopPropagation()
    this.dragCounter = 0

    const files = Array.from(e.dataTransfer?.files || [])
    this.onDrop?.(files)
    this.onDragLeave?.()
  }

  destroy() {
    this.element.removeEventListener('dragenter', this.handleDragEnter)
    this.element.removeEventListener('dragleave', this.handleDragLeave)
    this.element.removeEventListener('dragover', this.handleDragOver)
    this.element.removeEventListener('drop', this.handleDrop)
  }
}
