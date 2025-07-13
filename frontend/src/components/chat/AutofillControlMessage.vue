<template>
    <div class="control-message-card">
      <div class="message-content" v-html="message.content"></div>
  
      <div class="button-group">
        <button @click="showInput = !showInput; showKbInput = false">
          <Icon name="edit" size="xs" />
          <span>对话式输入</span>
        </button>
        <button @click="triggerFileUpload">
          <Icon name="upload_file" size="xs" />
          <span>上传内容文件</span>
        </button>
        <button @click="showKbInput = !showKbInput; showInput = false">
          <Icon name="search" size="xs" />
          <span>从知识库检索</span>
        </button>
      </div>
  
      <div v-if="showInput" class="input-area">
        <textarea v-model="textInput" placeholder="在此输入用于填充表格的详细信息..."></textarea>
        <button @click="submitText" class="submit-button">确定</button>
      </div>
  
      <div v-if="showKbInput" class="input-area">
        <input v-model="kbQuery" type="text" placeholder="输入检索知识库的关键词，例如“张三的所有信息”" />
        <button @click="submitKbQuery" class="submit-button">检索并填充</button>
      </div>
  
      <input
        type="file"
        ref="fileInput"
        @change="handleFileSelect"
        style="display: none"
        accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
      />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  import type { ChatMessage } from '@/services/api';
  import Icon from '@/components/common/Icon.vue';
  
  interface Props {
    message: ChatMessage;
  }
  defineProps<Props>();
  
  const emit = defineEmits<{
    'content-provided': [{ mode: 'conversational' | 'from_file' | 'from_kb'; data?: File | string }];
  }>();
  
  const showInput = ref(false);
  const showKbInput = ref(false);
  const textInput = ref('');
  const kbQuery = ref('');
  const fileInput = ref<HTMLInputElement | null>(null);
  
  const triggerFileUpload = () => {
    fileInput.value?.click();
  };
  
  const submitText = () => {
    if (!textInput.value.trim()) return;
    emit('content-provided', { mode: 'conversational', data: textInput.value });
    showInput.value = false;
  };
  
  const handleFileSelect = (e: Event) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) {
      emit('content-provided', { mode: 'from_file', data: file });
    }
  };
  
  const submitKbQuery = () => {
    if (!kbQuery.value.trim()) return;
    emit('content-provided', { mode: 'from_kb', data: kbQuery.value });
    showKbInput.value = false;
  };
  </script>
  
  <style scoped>
  .control-message-card {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 12px;
    padding: 1.5rem;
    max-width: 700px;
    margin: 0 auto;
  }
  .message-content {
    margin-bottom: 1.5rem;
    color: #212529;
  }
  .button-group {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }
  .button-group button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background-color: white;
    border: 1px solid #ced4da;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.875rem;
  }
  .button-group button:hover {
    background-color: #e9ecef;
    border-color: #adb5bd;
  }
  .input-area {
    margin-top: 1rem;
    border-top: 1px solid #e9ecef;
    padding-top: 1rem;
  }
  .input-area textarea, .input-area input {
    width: 100%;
    padding: 0.75rem;
    border-radius: 8px;
    border: 1px solid #ced4da;
    margin-bottom: 0.5rem;
    font-family: inherit;
    font-size: 0.9rem;
  }
  .input-area textarea {
    min-height: 80px;
    resize: vertical;
  }
  .submit-button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 0.5rem 1.25rem;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  .submit-button:hover {
    background-color: #0056b3;
  }
  </style>