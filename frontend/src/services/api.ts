import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface DocumentSource {
  file_name: string
  score: string
  content?: string // Preview content for document card
}

// Agent step structure for reasoning visualization
export interface ChatStep {
  id: string // 用 tool_name + 时间戳等方式唯一标识
  type: 'tool_call' | 'thought'
  status: 'running' | 'finished' | 'error' | 'complete'
  data: {
    tool_name?: string
    arguments?: any
    result?: any // 存放 tool_call_end 的结果
    content?: string // 用于存放 thought 的内容
  }
}

export interface ChatMessageToolResult {
  [key: string]: any
}

// 文件上传相关类型定义 - 更新以匹配后端实际响应
export interface DocumentUploadResponse {
  status: string // "success" 或 "error"
  file_id: string
  filename: string
  document_type: string
  metadata: {
    document_type: string
    template_name: string
    extracted_fields: Record<string, any>
    extraction_time: string
    model_used: string
    extraction_method: string
    extraction_error?: string
  }
  schema: {
    type: string
    name: string
    schema: Record<string, any>
    fields: Record<string, string>
  }
  content_preview: string
}

export interface DocumentConfirmRequest {
  file_id: string
  metadata: string // JSON字符串形式的元数据
  filename: string
}

export interface DocumentConfirmResponse {
  status: string // "success" 或 "error"
  message: string
  nodes_added: number
  validated_metadata: Record<string, any>
  document_type: string
}

export interface DocumentTemplate {
  type: string
  name: string
  schema: Record<string, any>
  fields: Record<string, string>
}

export interface DocumentTemplatesResponse {
  templates: Record<string, DocumentTemplate>
  available_types: string[]
}

export interface DocumentSchema {
  type: string
  name: string
  schema: Record<string, any>
  fields: Record<string, string>
}

// 文件上传状态枚举
export type UploadStatus = 'uploading' | 'uploaded' | 'confirming' | 'confirmed' | 'error'

// 文件信息接口
export interface FileInfo {
  file_id: string
  filename: string
  file_size?: number
  file_type?: string
  extracted_metadata: Record<string, any>
  doc_type?: string
  upload_timestamp?: Date
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  status?: string
  sources?: DocumentSource[]
  steps: ChatStep[]
  document_results?: DocumentSource[]
  tool_result?: ChatMessageToolResult

  // 文件上传相关字段
  upload_status?: UploadStatus
  file_info?: FileInfo
  is_file_message?: boolean

  // START: 为智能填表流程新增的属性
  is_autofill_control_message?: boolean // 标识这是一个模式选择消息
  autofill_preview?: any // 用于存放填表的预览结果
  // END: 新增属性
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}

export interface StreamCallbacks {
  onData: (data: { type: string; data: any }) => void
  onError: (error: Error) => void
  onClose: () => void
}

// 文件上传回调接口
export interface UploadCallbacks {
  onProgress?: (progress: number) => void
  onSuccess: (response: DocumentUploadResponse) => void
  onError: (error: Error) => void
}

export interface ChatAPI {
  // 现有聊天方法
  streamChat(query: string, history: ChatMessage[], callbacks: StreamCallbacks): Promise<void>
  getSession(sessionId: string): Promise<ChatSession>
  createSession(): Promise<ChatSession>
  getSessions(): Promise<ChatSession[]>

  // 文件上传相关方法
  uploadDocument(file: File, callbacks: UploadCallbacks): Promise<void>
  confirmDocument(request: DocumentConfirmRequest): Promise<DocumentConfirmResponse>
  getDocumentTemplates(): Promise<DocumentTemplatesResponse>
  getDocumentSchema(docType: string): Promise<DocumentSchema>

  // Autofill related methods
  startAutofill(templateFile: File, contentFiles: File[], conversationalQuery?: string): Promise<{ session_id: string; preview: any; }>;
  startAutofillFromFile(templateFile: File, contentFile: File): Promise<{ session_id: string; preview: any; }>;
  refineAutofill(sessionId: string, feedback: string): Promise<{ preview: any; }>;
  downloadAutofillResult(sessionId: string): Promise<void>;
}

class RealChatAPI implements ChatAPI {
  private readonly BASE_URL = 'http://127.0.0.1:8080'

  // ... (existing streamChat, uploadDocument, etc. methods) ...

  async streamChat(
    query: string,
    history: ChatMessage[],
    callbacks: StreamCallbacks,
  ): Promise<void> {
    const formData = new FormData()
    formData.append('query', query)

    // Prepare chat history for backend, removing UI-only fields
    const historyForApi = history.map((msg) => ({
      role: msg.role,
      content: msg.content,
    }))

    formData.append('chat_history', JSON.stringify(historyForApi))

    try {
      const response = await fetch(`${this.BASE_URL}/chat`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      if (!response.body) {
        throw new Error('Response body is null')
      }

      const reader = response.body.pipeThrough(new TextDecoderStream()).getReader()

      while (true) {
        const { value, done } = await reader.read()
        if (done) {
          callbacks.onClose()
          break
        }

        const lines = value.split('\n\n').filter((line) => line.trim())
        for (const line of lines) {
          if (line.startsWith('data:')) {
            const jsonData = line.substring(5).trim()
            try {
              const parsedData = JSON.parse(jsonData)
              callbacks.onData(parsedData)
            } catch (e) {
              console.error('Failed to parse stream JSON:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming failed:', error)
      callbacks.onError(error instanceof Error ? error : new Error(String(error)))
    }
  }

  // 文件上传方法
  async uploadDocument(file: File, callbacks: UploadCallbacks): Promise<void> {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const xhr = new XMLHttpRequest()

      // 设置上传进度监听
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && callbacks.onProgress) {
          const progress = (event.loaded / event.total) * 100
          callbacks.onProgress(progress)
        }
      })

      // 设置完成监听
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response: DocumentUploadResponse = JSON.parse(xhr.responseText)
            callbacks.onSuccess(response)
          } catch (e) {
            callbacks.onError(new Error('Failed to parse upload response'))
          }
        } else {
          callbacks.onError(new Error(`Upload failed with status: ${xhr.status}`))
        }
      })

      // 设置错误监听
      xhr.addEventListener('error', () => {
        callbacks.onError(new Error('Upload failed due to network error'))
      })

      // 发送请求
      xhr.open('POST', `${this.BASE_URL}/upload_document`)
      xhr.send(formData)
    } catch (error) {
      callbacks.onError(error instanceof Error ? error : new Error(String(error)))
    }
  }

  // 确认文档元数据
  async confirmDocument(request: DocumentConfirmRequest): Promise<DocumentConfirmResponse> {
    const formData = new FormData()
    formData.append('file_id', request.file_id)
    formData.append('metadata', request.metadata)
    formData.append('filename', request.filename)

    try {
      const response = await fetch(`${this.BASE_URL}/confirm_document`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Document confirmation failed:', error)
      throw error
    }
  }

  // 获取文档模板
  async getDocumentTemplates(): Promise<DocumentTemplatesResponse> {
    try {
      const response = await fetch(`${this.BASE_URL}/document_templates`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to fetch document templates:', error)
      throw error
    }
  }

  // 获取特定文档类型的schema
  async getDocumentSchema(docType: string): Promise<DocumentSchema> {
    try {
      const response = await fetch(
        `${this.BASE_URL}/document_schema/${encodeURIComponent(docType)}`,
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`Failed to fetch schema for document type ${docType}:`, error)
      throw error
    }
  }

  // --- Autofill Methods ---

  async startAutofill(templateFile: File, contentFiles: File[]): Promise<{ session_id: string; preview: any; }> {
    const formData = new FormData();
    formData.append('template_file', templateFile);
    contentFiles.forEach(file => {
      formData.append('content_files', file);
    });

    const response = await fetch(`${this.BASE_URL}/autofill/start`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(`Failed to start autofill session: ${errorData.detail}`);
    }
    return response.json();
  }

  async startAutofillFromFile(templateFile: File, contentFile: File): Promise<{ session_id: string; preview: any; }> {
    const formData = new FormData();
    formData.append('template_file', templateFile);
    formData.append('content_file', contentFile);

    const response = await fetch(`${this.BASE_URL}/autofill/start_from_file`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(`Failed to start autofill from file session: ${errorData.detail}`);
    }
    return response.json();
  }

  async refineAutofill(sessionId: string, feedback: string): Promise<{ preview: any; }> {
    const response = await fetch(`${this.BASE_URL}/autofill/refine`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ session_id: sessionId, feedback: feedback }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(`Failed to refine autofill session: ${errorData.detail}`);
    }
    return response.json();
  }

  async downloadAutofillResult(sessionId: string): Promise<void> {
    const response = await fetch(`${this.BASE_URL}/autofill/download/${sessionId}`);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(`Failed to download file: ${errorData.detail}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    
    // Extract filename from content-disposition header if available
    const disposition = response.headers.get('content-disposition');
    let filename = `filled_document_${sessionId.substring(0, 8)}.docx`;
    if (disposition && disposition.indexOf('attachment') !== -1) {
      const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
      const matches = filenameRegex.exec(disposition);
      if (matches != null && matches[1]) {
        filename = matches[1].replace(/['"]/g, '');
      }
    }
    
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  }

  private sessions: Map<string, ChatSession> = new Map()

  async getSession(sessionId: string): Promise<ChatSession> {
    const session = this.sessions.get(sessionId)
    if (!session) throw new Error('Session not found')
    return JSON.parse(JSON.stringify(session))
  }

  async createSession(): Promise<ChatSession> {
    const sessionId = `${Date.now()}`
    const session: ChatSession = {
      id: sessionId,
      title: '新对话',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    this.sessions.set(sessionId, session)
    return JSON.parse(JSON.stringify(session))
  }

  async getSessions(): Promise<ChatSession[]> {
    return Array.from(this.sessions.values()).sort(
      (a, b) => b.updatedAt.getTime() - a.updatedAt.getTime(),
    )
  }
}

// 文件上传工具函数
export class FileUploadHelper {
  /**
   * 更新文件上传消息状态
   */
  static updateFileUploadMessage(
    message: ChatMessage,
    status: UploadStatus,
    response?: DocumentUploadResponse,
    error?: string,
  ): ChatMessage {
    const updatedMessage = { ...message }
    updatedMessage.upload_status = status

    if (response && updatedMessage.file_info) {
      updatedMessage.file_info.file_id = response.file_id

      // 简单直接：把API响应的数据传递给组件
      const extractedMetadata = {
        document_type: response.document_type, // 关键：确保 document_type 在顶层
        extracted_fields: response.metadata.extracted_fields,
        content_preview: response.content_preview,
        template_name: response.metadata.template_name,
      }

      updatedMessage.file_info.extracted_metadata = extractedMetadata
      updatedMessage.file_info.doc_type = response.document_type
      updatedMessage.content = `文件上传成功: ${response.filename}`
    }

    if (error) {
      updatedMessage.content = `文件上传失败: ${error}`
    }

    if (status === 'confirmed') {
      updatedMessage.content = `文件已成功添加到知识库: ${updatedMessage.file_info?.filename}`
    }

    return updatedMessage
  }

  static createFileUploadMessage(file: File): ChatMessage {
    return {
      id: `upload_${Date.now()}_${Math.random()}`,
      role: 'user',
      content: `正在上传文件: ${file.name}`,
      timestamp: new Date(),
      steps: [],
      upload_status: 'uploading',
      is_file_message: true,
      file_info: {
        file_id: '',
        filename: file.name,
        file_size: file.size,
        file_type: file.type,
        extracted_metadata: {},
        upload_timestamp: new Date(),
      },
    }
  }

  static isSupportedFileType(file: File): boolean {
    const supportedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/msword',
      'application/vnd.ms-powerpoint',
      'application/vnd.ms-excel',
      'text/plain',
    ]
    return supportedTypes.includes(file.type)
  }

  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
}

// 导出单例
export const chatAPI: ChatAPI = new RealChatAPI()