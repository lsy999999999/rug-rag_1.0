import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { chatAPI, type ChatMessage, type ChatSession } from '@/services/api'

export const useChatStore = defineStore('chat', () => {
  // State
  const currentSession = ref<ChatSession | null>(null)
  const sessions = ref<ChatSession[]>([])
  const isLoading = ref(false)
  const isTyping = ref(false)

  // Computed
  const currentMessages = computed(() => currentSession.value?.messages || [])
  const hasActiveSession = computed(() => currentSession.value !== null)

  // Actions
  async function sendMessage(content: string) {
    if (!content.trim() || isLoading.value) return

    isLoading.value = true
    isTyping.value = true

    try {
      const response = await chatAPI.sendMessage({
        message: content.trim(),
        sessionId: currentSession.value?.id,
      })

      // Update current session
      currentSession.value = await chatAPI.getSession(response.sessionId)

      // Update sessions list
      await loadSessions()
    } catch (error) {
      console.error('Failed to send message:', error)
      // Here you could show a toast notification or error message
    } finally {
      isLoading.value = false
      isTyping.value = false
    }
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

  // Initialize
  async function initialize() {
    await loadSessions()
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
    isTyping,

    // Computed
    currentMessages,
    hasActiveSession,

    // Actions
    sendMessage,
    createNewSession,
    switchToSession,
    loadSessions,
    clearCurrentSession,
    initialize,
  }
})
