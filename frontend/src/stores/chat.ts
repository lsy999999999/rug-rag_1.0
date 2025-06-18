import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import {
  chatAPI,
  type ChatMessage,
  type ChatSession,
  type ChatStep,
  type DocumentUploadResponse,
  type DocumentConfirmRequest,
  type DocumentTemplate,
  FileUploadHelper,
} from '@/services/api'

export const useChatStore = defineStore('chat', () => {
  // State
  const currentSession = ref<ChatSession | null>(null)
  const sessions = ref<ChatSession[]>([])
  const isLoading = ref(false)
  const documentTemplates = ref<DocumentTemplate[]>([])
  const uploadProgress = ref<Record<string, number>>({}) // messageId -> progress

  // Computed
  const currentMessages = computed(() => currentSession.value?.messages || [])
  const hasActiveSession = computed(() => currentSession.value !== null)

  // 流式消息发送
  async function streamMessage(content: string) {
    if (!content.trim() || isLoading.value || !currentSession.value) return

    isLoading.value = true

    // 添加用户消息
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
      steps: [],
    }
    currentSession.value.messages.push(userMessage)

    // 添加助手占位消息
    const assistantMessageId = `assistant-${Date.now()}`
    const placeholderMessage: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      status: '正在思考...',
      steps: [],
      sources: [],
      document_results: [],
    }
    currentSession.value.messages.push(placeholderMessage)

    // 准备发送到API的聊天历史
    const historyToSend = currentSession.value.messages.slice(0, -1)

    // 调用流式API
    await chatAPI.streamChat(content.trim(), historyToSend, {
      onData: (data: any) => {
        const targetMessage = currentSession.value?.messages.find(
          (m) => m.id === assistantMessageId,
        )
        if (!targetMessage) return

        if (targetMessage.status) targetMessage.status = undefined

        switch (data.type) {
          case 'tool_call_start':
            targetMessage.steps.push({
              id: data.data.tool_name + Date.now(),
              type: 'tool_call',
              status: 'running',
              data: {
                tool_name: data.data.tool_name,
                arguments: data.data.arguments,
              },
            })
            break

          case 'tool_call_end':
            const runningStep = [...targetMessage.steps]
              .reverse()
              .find((s) => s.status === 'running')
            if (runningStep) {
              runningStep.status = 'finished'
              runningStep.data.result = data.data.result
            }
            break

          case 'thought':
            targetMessage.steps.push({
              id: 'thought-' + Date.now(),
              type: 'thought',
              status: 'complete',
              data: {
                content: data.data,
              },
            })
            break

          case 'retrieved_documents':
            targetMessage.document_results = data.data
            break

          case 'sources':
            targetMessage.sources = data.data
            break

          case 'token':
            targetMessage.content += data.data
            break

          case 'error':
            targetMessage.status = `错误: ${data.data}`
            targetMessage.content = ''
            isLoading.value = false
            break
        }
      },
      onError: (error: any) => {
        console.error('Stream error:', error)
        const targetMessage = currentSession.value?.messages.find(
          (m) => m.id === assistantMessageId,
        )
        if (targetMessage) {
          targetMessage.status = `连接失败: ${error.message}`
        }
        isLoading.value = false
      },
      onClose: () => {
        console.log('Stream closed')
        isLoading.value = false
      },
    })
  }

  // 文件上传处理
  async function uploadFiles(files: File[]) {
    if (!currentSession.value) return

    for (const file of files) {
      await uploadSingleFile(file)
    }
  }

  async function uploadSingleFile(file: File) {
    if (!currentSession.value) return

    // 创建文件上传消息
    const uploadMessage = FileUploadHelper.createFileUploadMessage(file)
    currentSession.value.messages.push(uploadMessage)

    // 初始化上传进度
    uploadProgress.value[uploadMessage.id] = 0

    try {
      // 调用上传API
      await chatAPI.uploadDocument(file, {
        onProgress: (progress: number) => {
          uploadProgress.value[uploadMessage.id] = progress
        },
        onSuccess: (response: DocumentUploadResponse) => {
          console.log('Upload success:', response)
          // 更新消息状态
          const messageIndex = currentSession.value!.messages.findIndex(
            (m) => m.id === uploadMessage.id,
          )
          if (messageIndex !== -1) {
            currentSession.value!.messages[messageIndex] = FileUploadHelper.updateFileUploadMessage(
              uploadMessage,
              'uploaded',
              response,
            )
          }

          // 清除进度
          delete uploadProgress.value[uploadMessage.id]
        },
        onError: (error: Error) => {
          // 更新消息为错误状态
          const messageIndex = currentSession.value!.messages.findIndex(
            (m) => m.id === uploadMessage.id,
          )
          if (messageIndex !== -1) {
            currentSession.value!.messages[messageIndex] = FileUploadHelper.updateFileUploadMessage(
              uploadMessage,
              'error',
              undefined,
              error.message,
            )
          }

          // 清除进度
          delete uploadProgress.value[uploadMessage.id]
        },
      })
    } catch (error) {
      console.error('Upload failed:', error)

      // 更新消息为错误状态
      const messageIndex = currentSession.value!.messages.findIndex(
        (m) => m.id === uploadMessage.id,
      )
      if (messageIndex !== -1) {
        currentSession.value!.messages[messageIndex] = FileUploadHelper.updateFileUploadMessage(
          uploadMessage,
          'error',
          undefined,
          error instanceof Error ? error.message : '上传失败',
        )
      }

      // 清除进度
      delete uploadProgress.value[uploadMessage.id]
    }
  }

  // 确认文档元数据
  async function confirmDocument(messageId: string, metadata: Record<string, any>) {
    if (!currentSession.value) return

    const messageIndex = currentSession.value.messages.findIndex((m) => m.id === messageId)
    if (messageIndex === -1) return

    const message = currentSession.value.messages[messageIndex]
    if (!message.file_info?.file_id) return

    // 更新消息状态为处理中
    currentSession.value.messages[messageIndex] = FileUploadHelper.updateFileUploadMessage(
      message,
      'confirming',
    )

    try {
      const confirmRequest: DocumentConfirmRequest = {
        file_id: message.file_info.file_id,
        metadata: JSON.stringify(metadata),
        filename: message.file_info.filename,
      }

      const response = await chatAPI.confirmDocument(confirmRequest)

      if (response.status === 'success') {
        // 更新消息状态为已确认
        currentSession.value.messages[messageIndex] = FileUploadHelper.updateFileUploadMessage(
          message,
          'confirmed',
        )

        // 添加一条系统消息表示文档已添加成功
        const successMessage: ChatMessage = {
          id: `system-${Date.now()}`,
          role: 'assistant',
          content: `文档 "${message.file_info.filename}" 已成功添加到知识库，现在您可以询问有关此文档的问题了。`,
          timestamp: new Date(),
          steps: [],
        }
        currentSession.value.messages.push(successMessage)
      } else {
        throw new Error(response.message || '确认文档失败')
      }
    } catch (error) {
      console.error('Document confirmation failed:', error)

      // 更新消息为错误状态
      currentSession.value.messages[messageIndex] = FileUploadHelper.updateFileUploadMessage(
        message,
        'error',
        undefined,
        error instanceof Error ? error.message : '确认失败',
      )
    }
  }

  // 取消文件上传/删除文件消息
  function cancelFileUpload(messageId: string) {
    if (!currentSession.value) return

    const messageIndex = currentSession.value.messages.findIndex((m) => m.id === messageId)
    if (messageIndex !== -1) {
      // 删除消息
      currentSession.value.messages.splice(messageIndex, 1)

      // 清除进度
      delete uploadProgress.value[messageId]
    }
  }

  // 重试文件上传
  async function retryFileUpload(messageId: string) {
    if (!currentSession.value) return

    const message = currentSession.value.messages.find((m) => m.id === messageId)
    if (!message?.file_info) return

    // 重置消息状态
    const messageIndex = currentSession.value.messages.findIndex((m) => m.id === messageId)
    if (messageIndex !== -1) {
      currentSession.value.messages[messageIndex] = {
        ...message,
        upload_status: 'uploading',
        content: `正在重新上传文件: ${message.file_info.filename}`,
      }
    }

    // 这里需要重新获取File对象，实际实现中可能需要用户重新选择文件
    // 或者在消息中保存File对象的引用
    // 简化处理：直接提示用户重新上传
    setTimeout(() => {
      if (currentSession.value) {
        const msg = currentSession.value.messages.find((m) => m.id === messageId)
        if (msg) {
          const idx = currentSession.value.messages.findIndex((m) => m.id === messageId)
          if (idx !== -1) {
            currentSession.value.messages[idx] = {
              ...msg,
              upload_status: 'error',
              content: '请重新选择文件上传',
            }
          }
        }
      }
    }, 1000)
  }

  // 加载文档模板
  async function loadDocumentTemplates() {
    try {
      const response = await chatAPI.getDocumentTemplates()
      documentTemplates.value = Object.values(response.templates)
    } catch (error) {
      console.error('Failed to load document templates:', error)
    }
  }

  // 获取文件上传进度
  function getUploadProgress(messageId: string): number {
    return uploadProgress.value[messageId] || 0
  }

  async function createNewSession() {
    try {
      const session = await chatAPI.createSession()
      currentSession.value = session
      await loadSessions()
      return session
    } catch (error) {
      console.error('Failed to create session:', error)
      throw error
    }
  }

  async function switchToSession(sessionId: string) {
    try {
      currentSession.value = await chatAPI.getSession(sessionId)
    } catch (error) {
      console.error('Failed to switch session:', error)
      throw error
    }
  }

  async function loadSessions() {
    try {
      sessions.value = await chatAPI.getSessions()
    } catch (error) {
      console.error('Failed to load sessions:', error)
    }
  }

  function clearCurrentSession() {
    currentSession.value = null
  }

  async function initialize() {
    await Promise.all([loadSessions(), loadDocumentTemplates()])

    if (sessions.value.length === 0) {
      await createNewSession()
    } else {
      currentSession.value = sessions.value[0]
    }
  }

  return {
    // State
    currentSession,
    sessions,
    isLoading,
    documentTemplates,

    // Computed
    currentMessages,
    hasActiveSession,

    // Methods
    streamMessage,
    uploadFiles,
    uploadSingleFile,
    confirmDocument,
    cancelFileUpload,
    retryFileUpload,
    getUploadProgress,
    loadDocumentTemplates,
    createNewSession,
    switchToSession,
    loadSessions,
    clearCurrentSession,
    initialize,
  }
})
