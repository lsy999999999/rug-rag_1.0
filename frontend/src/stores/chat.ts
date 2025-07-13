import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import {
  chatAPI,
  type ChatMessage,
  type ChatSession,
  type DocumentUploadResponse,
  type DocumentConfirmRequest,
  type DocumentTemplate,
  FileUploadHelper,
} from '@/services/api'

export const useChatStore = defineStore('chat', () => {
  // --- STATE ---
  const currentSession = ref<ChatSession | null>(null)
  const sessions = ref<ChatSession[]>([])
  const isLoading = ref(false)
  const documentTemplates = ref<DocumentTemplate[]>([])
  const uploadProgress = ref<Record<string, number>>({}) // messageId -> progress

  // --- NEW STATE for Autofill Mode ---
  const isAutofillMode = ref(false)
  const isAwaitingAutofillContent = ref(false)
  const autofillSessionId = ref<string | null>(null)
  const autofillTemplateFile = ref<File | null>(null)

  // --- COMPUTED ---
  const currentMessages = computed(() => currentSession.value?.messages || [])
  const hasActiveSession = computed(() => currentSession.value !== null)

  // --- ACTIONS ---

  // #region Main Chat & Interaction Logic (Modified)
  // This is the primary function for user interaction. It now intelligently
  // routes the user's input to either the RAG agent or the autofill service.
  async function streamMessage(content: string) {
    if (!content.trim() || isLoading.value || !currentSession.value) return

    // **MODIFIED LOGIC**: If in autofill mode, treat the message as refinement feedback.
    if (isAutofillMode.value && autofillSessionId.value) {
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content,
        timestamp: new Date(),
        steps: [],
      }
      currentSession.value.messages.push(userMessage)
      await refineAutofill(content)
      return
    }

    // --- Original RAG Chat Logic ---
    isLoading.value = true
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
      steps: [],
    }
    currentSession.value.messages.push(userMessage)

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

    const historyToSend = currentSession.value.messages.slice(0, -1)

    await chatAPI.streamChat(content.trim(), historyToSend, {
      onData: (data: any) => {
        const targetMessage = currentSession.value?.messages.find((m) => m.id === assistantMessageId)
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
            const runningStep = [...targetMessage.steps].reverse().find((s) => s.status === 'running')
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
        const targetMessage = currentSession.value?.messages.find((m) => m.id === assistantMessageId)
        if (targetMessage) {
          targetMessage.status = `连接失败: ${error.message}`
        }
        isLoading.value = false
      },
      onClose: () => {
        isLoading.value = false
      },
    })
  }
  // #endregion

  // #region Autofill Workflow Actions (New)
  function startAutofillMode(templateFile: File) {
    if (!currentSession.value) return
    currentSession.value.title = `填表: ${templateFile.name}`
    isAutofillMode.value = true
    isAwaitingAutofillContent.value = true
    autofillTemplateFile.value = templateFile
    autofillSessionId.value = null

    const modeSelectorMessage: ChatMessage = {
      id: `autofill-selector-${Date.now()}`,
      role: 'assistant',
      content: `已选择模板: <strong>${templateFile.name}</strong>。<br/>请选择填充内容的方式：`,
      timestamp: new Date(),
      steps: [],
      is_autofill_control_message: true,
    }
    currentSession.value.messages.push(modeSelectorMessage)
  }

  async function provideAutofillContent(
    mode: 'conversational' | 'from_file' | 'from_kb',
    data?: File | string,
  ) {
    if (!autofillTemplateFile.value || !currentSession.value) return

    // Remove the control message from UI
    const controlMsgIndex = currentSession.value.messages.findIndex(
      (m) => m.is_autofill_control_message,
    )
    if (controlMsgIndex > -1) {
      currentSession.value.messages.splice(controlMsgIndex, 1)
    }

    isAwaitingAutofillContent.value = false
    isLoading.value = true

    try {
      let response
      if (mode === 'from_file' && data instanceof File) {
        response = await chatAPI.startAutofillFromFile(autofillTemplateFile.value, data)
      } else {
        // RAG and Conversational modes use the general start endpoint
        response = await chatAPI.startAutofill(autofillTemplateFile.value, [])
      }
      autofillSessionId.value = response.session_id

      if (mode === 'conversational' && typeof data === 'string') {
        await refineAutofill(`请根据以下信息填充表单：\n${data}`)
      } else if (mode === 'from_kb' && typeof data === 'string') {
        const ragSummary = await getRAGSummary(data) // Helper to get context from knowledge base
        const refineQuery = `请根据以下信息填充表单：\n${ragSummary}`
        await refineAutofill(refineQuery)
      } else {
        // For 'from_file' mode, the initial preview is what we need
        displayAutofillPreview(response.preview)
      }
    } catch (e) {
      console.error('Autofill start failed:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function refineAutofill(feedback: string) {
    if (!autofillSessionId.value) return
    isLoading.value = true
    try {
      const response = await chatAPI.refineAutofill(autofillSessionId.value, feedback)
      displayAutofillPreview(response.preview)
    } catch (e) {
      console.error('Autofill refine failed:', e)
    } finally {
      isLoading.value = false
    }
  }

  function displayAutofillPreview(previewData: any) {
    if (!currentSession.value) return
    const previewMessage: ChatMessage = {
      id: `autofill-preview-${Date.now()}`,
      role: 'assistant',
      content: '已根据您的信息生成填充预览。您可以继续通过对话修正，或直接下载。',
      timestamp: new Date(),
      steps: [],
      autofill_preview: previewData,
    }
    currentSession.value.messages.push(previewMessage)
  }

  

  async function getRAGSummary(query: string): Promise<string> {
    let summary = ''
    return new Promise((resolve, reject) => {
      chatAPI.streamChat(query, [], {
        onData: (data) => {
          if (data.type === 'token') summary += data.data
        },
        onClose: () => resolve(summary),
        onError: (err) => reject(err),
      })
    })
  }

  function endAutofillMode() {
    isAutofillMode.value = false
    isAwaitingAutofillContent.value = false
    autofillSessionId.value = null
    autofillTemplateFile.value = null
  }
  // #endregion




  
  // #region Document Upload Actions (Original + Modified)
  // This function is now aware of the autofill mode.
  async function uploadFiles(files: File[]) {
    if (!currentSession.value) return

    // **MODIFIED LOGIC**: If waiting for autofill content, treat a docx file as such.
    if (isAutofillMode.value && isAwaitingAutofillContent.value) {
      const docxFile = files.find(f => f.name.endsWith('.docx'));
      if (docxFile) {
        await provideAutofillContent('from_file', docxFile);
        // Optionally handle other files for knowledge base upload if needed
        return;
      }
    }

    // Original logic for knowledge base upload
    for (const file of files) {
      await uploadSingleFile(file)
    }
  }

  async function uploadSingleFile(file: File) {
    if (!currentSession.value) return

    const uploadMessage = FileUploadHelper.createFileUploadMessage(file)
    currentSession.value.messages.push(uploadMessage)
    uploadProgress.value[uploadMessage.id] = 0

    try {
      await chatAPI.uploadDocument(file, {
        onProgress: (progress: number) => {
          uploadProgress.value[uploadMessage.id] = progress
        },
        onSuccess: (response: DocumentUploadResponse) => {
          const messageIndex = currentSession.value!.messages.findIndex((m) => m.id === uploadMessage.id)
          if (messageIndex !== -1) {
            currentSession.value!.messages[messageIndex] = FileUploadHelper.updateFileUploadMessage(
              uploadMessage,
              'uploaded',
              response,
            )
          }
          delete uploadProgress.value[uploadMessage.id]
        },
        onError: (error: Error) => {
          const messageIndex = currentSession.value!.messages.findIndex((m) => m.id === uploadMessage.id)
          if (messageIndex !== -1) {
            currentSession.value!.messages[messageIndex] = FileUploadHelper.updateFileUploadMessage(
              uploadMessage,
              'error',
              undefined,
              error.message,
            )
          }
          delete uploadProgress.value[uploadMessage.id]
        },
      })
    } catch (error) {
      const messageIndex = currentSession.value.messages.findIndex((m) => m.id === uploadMessage.id)
      if (messageIndex !== -1) {
        currentSession.value!.messages[messageIndex] = FileUploadHelper.updateFileUploadMessage(
          uploadMessage, 'error', undefined, error instanceof Error ? error.message : '上传失败',
        )
      }
      delete uploadProgress.value[uploadMessage.id]
    }
  }

  async function confirmDocument(messageId: string, metadata: Record<string, any>) {
    if (!currentSession.value) return

    const messageIndex = currentSession.value.messages.findIndex((m) => m.id === messageId)
    if (messageIndex === -1) return

    const message = currentSession.value.messages[messageIndex]
    if (!message.file_info?.file_id) return

    currentSession.value.messages[messageIndex] = FileUploadHelper.updateFileUploadMessage(
      message, 'confirming',
    )

    try {
      const confirmRequest: DocumentConfirmRequest = {
        file_id: message.file_info.file_id,
        metadata: JSON.stringify(metadata),
        filename: message.file_info.filename,
      }
      const response = await chatAPI.confirmDocument(confirmRequest)
      if (response.status === 'success') {
        currentSession.value.messages[messageIndex] = FileUploadHelper.updateFileUploadMessage(
          message, 'confirmed',
        )
        const successMessage: ChatMessage = {
          id: `system-${Date.now()}`, role: 'assistant',
          content: `文档 "${message.file_info.filename}" 已成功添加到知识库，现在您可以询问有关此文档的问题了。`,
          timestamp: new Date(), steps: [],
        }
        currentSession.value.messages.push(successMessage)
      } else {
        throw new Error(response.message || '确认文档失败')
      }
    } catch (error) {
      currentSession.value.messages[messageIndex] = FileUploadHelper.updateFileUploadMessage(
        message, 'error', undefined, error instanceof Error ? error.message : '确认失败',
      )
    }
  }
  
  function cancelFileUpload(messageId: string) {
    if (!currentSession.value) return
    const messageIndex = currentSession.value.messages.findIndex((m) => m.id === messageId)
    if (messageIndex !== -1) {
      currentSession.value.messages.splice(messageIndex, 1)
      delete uploadProgress.value[messageId]
    }
  }

  async function retryFileUpload(messageId: string) {
    if (!currentSession.value) return
    const message = currentSession.value.messages.find((m) => m.id === messageId)
    if (!message?.file_info) return
    const idx = currentSession.value.messages.findIndex((m) => m.id === messageId)
    if (idx !== -1) {
      currentSession.value.messages[idx] = { ...message, upload_status: 'error', content: '重试功能暂未实现，请重新上传文件。' }
    }
  }

  async function loadDocumentTemplates() {
    try {
      const response = await chatAPI.getDocumentTemplates()
      documentTemplates.value = Object.values(response.templates)
    } catch (error) {
      console.error('Failed to load document templates:', error)
    }
  }

  function getUploadProgress(messageId: string): number {
    return uploadProgress.value[messageId] || 0
  }
  // #endregion

  // #region Session Management (Modified)
  async function createNewSession() {
    endAutofillMode() // **CRITICAL**: Reset mode when creating a new session
    try {
      const session = await chatAPI.createSession()
      sessions.value.unshift(session)
      currentSession.value = session
      return session
    }  catch (error) {
      console.error('Failed to create session:', error)
      throw error
    }
  }

  async function switchToSession(sessionId: string) {
    try {
      const session = await chatAPI.getSession(sessionId)
      currentSession.value = session
      
      const hasAutofillMessages = session.messages.some(
        m => m.is_autofill_control_message || m.autofill_preview
      );
      if (!hasAutofillMessages) {
        endAutofillMode(); // **CRITICAL**: Reset mode when switching to a normal chat
      } else {
        isAutofillMode.value = true; // Restore autofill mode state
      }
    }catch (error) {
      console.error('Failed to switch session:', error)
      // If session not found, create a new one
      await createNewSession()
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
  // #endregion

  return {
    // State
    currentSession, sessions, isLoading, documentTemplates,
    isAutofillMode, isAwaitingAutofillContent, autofillSessionId,
    // Computed
    currentMessages, hasActiveSession,
    // Methods
    streamMessage, uploadFiles, confirmDocument, cancelFileUpload, retryFileUpload,
    getUploadProgress, loadDocumentTemplates, createNewSession, switchToSession,
    clearCurrentSession, initialize,
    // Autofill Methods
    startAutofillMode, provideAutofillContent, endAutofillMode,
  }
})