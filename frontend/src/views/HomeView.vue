<script setup lang="ts">
import { useRouter } from 'vue-router'
import Icon from '@/components/common/Icon.vue'
import DesignSystemDemo from '@/components/common/DesignSystemDemo.vue'

const router = useRouter()

const goToChat = () => {
  router.push('/chat')
}
</script>

<template>
  <main class="min-h-screen bg-gray-50">
    <!-- Hero Section -->
    <div class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div class="text-center">
          <div
            class="w-16 h-16 bg-red-600 rounded-lg flex items-center justify-center mx-auto mb-6"
          >
            <Icon name="school" color="white" size="xl" />
          </div>
          <h1 class="text-4xl font-bold text-gray-900 mb-4">人大智慧行政大模型系统</h1>
          <p class="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            基于 RAG 技术驱动的智慧行政助手，为师生提供高效、准确的行政事务咨询服务
          </p>
          <button
            @click="goToChat"
            class="inline-flex items-center space-x-2 bg-red-600 hover:bg-red-700 text-white font-medium px-8 py-4 rounded-lg transition-colors text-lg"
          >
            <Icon name="chat" size="md" />
            <span>体验智慧助手</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        <div class="text-center">
          <div
            class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4"
          >
            <Icon name="psychology" color="blue-600" size="lg" />
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">智能问答</h3>
          <p class="text-gray-600">基于 RAG 技术，提供准确的行政政策解读和办事指南</p>
        </div>
        <div class="text-center">
          <div
            class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4"
          >
            <Icon name="schedule" color="green-600" size="lg" />
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">即时响应</h3>
          <p class="text-gray-600">7x24小时在线服务，快速响应各类咨询需求</p>
        </div>
        <div class="text-center">
          <div
            class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4"
          >
            <Icon name="verified" color="purple-600" size="lg" />
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">权威可靠</h3>
          <p class="text-gray-600">基于官方政策文件训练，确保信息的准确性和时效性</p>
        </div>
      </div>

      <!-- Demo Link -->
      <div class="text-center">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">立即体验</h2>
          <p class="text-gray-600 mb-6">现在就可以体验我们的智慧行政助手，获取专业的行政事务指导</p>
          <button
            @click="goToChat"
            class="inline-flex items-center space-x-3 bg-red-600 hover:bg-red-700 text-white font-medium px-6 py-3 rounded-lg transition-all duration-200 hover:scale-105"
          >
            <Icon name="smart_toy" size="md" />
            <span>开始对话</span>
            <Icon name="arrow_forward" size="sm" />
          </button>
        </div>
      </div>
    </div>

    <!-- Design System Demo (for development) -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <DesignSystemDemo />
    </div>
  </main>
</template>
