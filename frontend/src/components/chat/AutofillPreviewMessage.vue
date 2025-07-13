<template>
    <div class="preview-card">
      <div class="message-content">
        <Icon name="check_circle" color="green-600" size="md" class="icon" />
        <p>{{ message.content }}</p>
      </div>
      <div class="action-group">
        <details class="preview-details">
          <summary>查看填充详情</summary>
          <pre>{{ JSON.stringify(message.autofill_preview?.filling_instructions || '无详情', null, 2) }}</pre>
        </details>
        <button class="download-button" @click="$emit('download')">
          <Icon name="download" size="sm" />
          <span>下载文档</span>
        </button>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import type { ChatMessage } from '@/services/api';
  import Icon from '@/components/common/Icon.vue';
  
  interface Props {
    message: ChatMessage;
  }
  defineProps<Props>();
  
  defineEmits<{
    download: [];
  }>();
  </script>
  
  <style scoped>
  .preview-card {
    background-color: #e6f7ff;
    border: 1px solid #91d5ff;
    border-radius: 12px;
    padding: 1.5rem;
    max-width: 700px;
    margin: 0 auto;
    color: #0050b3;
  }
  .message-content {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }
  .icon {
    flex-shrink: 0;
    margin-top: 2px;
  }
  .action-group {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 1rem;
    border-top: 1px solid #b7e0ff;
    padding-top: 1rem;
  }
  .preview-details {
    font-size: 0.875rem;
  }
  .preview-details summary {
    cursor: pointer;
    font-weight: 500;
    color: #0050b3;
  }
  pre {
    margin-top: 0.75rem;
    background-color: rgba(255, 255, 255, 0.5);
    padding: 1rem;
    border-radius: 8px;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-size: 0.8rem;
    color: #333;
  }
  .download-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background-color: #1890ff;
    color: white;
    border: none;
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.2s;
  }
  .download-button:hover {
    background-color: #096dd9;
  }
  </style>