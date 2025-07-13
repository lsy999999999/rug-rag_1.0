
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface FillingInstruction {
  table: number;
  row: number;
  col: number;
  value: string;
  reason: string;
}

export const useAutofillStore = defineStore('autofill', () => {
  const sessionId = ref<string | null>(null);
  const isSessionActive = computed(() => sessionId.value !== null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const preview = ref<{"filling_instructions": FillingInstruction[]} | null>(null);

  function startSession(newSessionId: string) {
    sessionId.value = newSessionId;
    error.value = null;
    preview.value = null;
  }

  function endSession() {
    sessionId.value = null;
    preview.value = null;
  }

  function setLoading(status: boolean) {
    isLoading.value = status;
  }

  function setError(errorMessage: string) {
    error.value = errorMessage;
  }

  function setPreview(previewData: {"filling_instructions": FillingInstruction[]}) {
    preview.value = previewData;
  }

  return {
    sessionId,
    isSessionActive,
    isLoading,
    error,
    preview,
    startSession,
    endSession,
    setLoading,
    setError,
    setPreview
  }
})
