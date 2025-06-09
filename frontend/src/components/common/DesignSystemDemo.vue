<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">RUC RAG Frontend 设计系统</h1>
        <p class="text-lg text-gray-600 max-w-3xl mx-auto">
          基于人大品牌色彩的专业行政管理界面设计系统，强调简约、规整与细节之美
        </p>
      </div>

      <!-- Color Palette Section -->
      <section class="mb-16">
        <h2 class="text-2xl font-semibold text-gray-900 mb-8">色彩系统</h2>

        <!-- Primary Red Colors -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-800 mb-4">主品牌色 - 深沉红色系</h3>
          <div class="grid grid-cols-6 md:grid-cols-11 gap-2">
            <div v-for="(shade, index) in redShades" :key="shade" class="group relative">
              <div
                :class="`bg-red-${shade} h-20 rounded-lg border border-gray-200 shadow-sm cursor-pointer transition-transform hover:scale-105`"
                @click="copyColor(`red-${shade}`)"
              ></div>
              <div class="mt-2 text-center">
                <p class="text-xs font-medium text-gray-700">{{ shade }}</p>
                <p class="text-xs text-gray-500">red-{{ shade }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Primary Alias Colors -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-800 mb-4">主色别名</h3>
          <div class="grid grid-cols-6 md:grid-cols-11 gap-2">
            <div v-for="(shade, index) in primaryShades" :key="shade" class="group relative">
              <div
                :class="`bg-primary-${shade} h-20 rounded-lg border border-gray-200 shadow-sm cursor-pointer transition-transform hover:scale-105`"
                @click="copyColor(`primary-${shade}`)"
              ></div>
              <div class="mt-2 text-center">
                <p class="text-xs font-medium text-gray-700">{{ shade }}</p>
                <p class="text-xs text-gray-500">primary-{{ shade }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Neutral Colors -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-800 mb-4">中性色系</h3>
          <div class="grid grid-cols-6 md:grid-cols-11 gap-2">
            <div v-for="(shade, index) in grayShades" :key="shade" class="group relative">
              <div
                :class="`bg-gray-${shade} h-20 rounded-lg border border-gray-200 shadow-sm cursor-pointer transition-transform hover:scale-105`"
                @click="copyColor(`gray-${shade}`)"
              ></div>
              <div class="mt-2 text-center">
                <p class="text-xs font-medium text-gray-700">{{ shade }}</p>
                <p class="text-xs text-gray-500">gray-{{ shade }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Semantic Colors -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-800 mb-4">语义色彩</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center">
              <div class="bg-green-600 h-16 rounded-lg mb-2 shadow-sm"></div>
              <p class="text-sm font-medium text-gray-700">Success</p>
              <p class="text-xs text-gray-500">green-600</p>
            </div>
            <div class="text-center">
              <div class="bg-yellow-600 h-16 rounded-lg mb-2 shadow-sm"></div>
              <p class="text-sm font-medium text-gray-700">Warning</p>
              <p class="text-xs text-gray-500">yellow-600</p>
            </div>
            <div class="text-center">
              <div class="bg-red-600 h-16 rounded-lg mb-2 shadow-sm"></div>
              <p class="text-sm font-medium text-gray-700">Error</p>
              <p class="text-xs text-gray-500">red-600</p>
            </div>
            <div class="text-center">
              <div class="bg-blue-600 h-16 rounded-lg mb-2 shadow-sm"></div>
              <p class="text-sm font-medium text-gray-700">Info</p>
              <p class="text-xs text-gray-500">blue-600</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Typography Section -->
      <section class="mb-16">
        <h2 class="text-2xl font-semibold text-gray-900 mb-8">字体系统</h2>
        <div class="bg-white rounded-lg p-8 shadow-sm border border-gray-200">
          <div class="space-y-6">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">页面标题 - text-3xl font-bold</h1>
            </div>
            <div>
              <h2 class="text-2xl font-semibold text-gray-900">
                章节标题 - text-2xl font-semibold
              </h2>
            </div>
            <div>
              <h3 class="text-xl font-medium text-gray-900">小节标题 - text-xl font-medium</h3>
            </div>
            <div>
              <h4 class="text-lg font-medium text-gray-800">子标题 - text-lg font-medium</h4>
            </div>
            <div>
              <p class="text-base text-gray-700">
                正文内容 - text-base，这是标准的正文字体大小，适合大段文字阅读。
              </p>
            </div>
            <div>
              <p class="text-sm text-gray-600">辅助文字 - text-sm，用于说明、提示等次要信息。</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">标注文字 - text-xs，用于版权、时间戳等微小信息。</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Component Examples -->
      <section class="mb-16">
        <h2 class="text-2xl font-semibold text-gray-900 mb-8">组件示例</h2>

        <!-- Buttons -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-800 mb-4">按钮组件</h3>
          <div class="bg-white rounded-lg p-8 shadow-sm border border-gray-200">
            <div class="space-y-4">
              <div class="flex flex-wrap gap-4">
                <button
                  class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
                >
                  <Icon name="add" size="sm" color="inherit" class="mr-2" />
                  主要操作
                </button>
                <button
                  class="px-4 py-2 border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium rounded-lg transition-colors"
                >
                  <Icon name="edit" size="sm" color="inherit" class="mr-2" />
                  次要操作
                </button>
                <button
                  class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
                >
                  <Icon name="check" size="sm" color="inherit" class="mr-2" />
                  确认操作
                </button>
                <button
                  class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors"
                >
                  <Icon name="delete" size="sm" color="inherit" class="mr-2" />
                  删除操作
                </button>
              </div>
              <div class="flex flex-wrap gap-4">
                <button
                  class="px-3 py-1.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-md transition-colors"
                >
                  小按钮
                </button>
                <button
                  class="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white text-lg font-medium rounded-xl transition-colors"
                >
                  大按钮
                </button>
                <button
                  class="p-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                >
                  <Icon name="settings" size="md" color="inherit" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Cards -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-800 mb-4">卡片组件</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
              <div class="flex items-center mb-4">
                <Icon name="description" size="lg" color="primary" class="mr-3" />
                <h4 class="text-lg font-semibold text-gray-900">文档管理</h4>
              </div>
              <p class="text-gray-600 mb-4">管理和组织您的文档资料，支持多种格式上传和预览。</p>
              <button
                class="w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
              >
                查看详情
              </button>
            </div>

            <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
              <div class="flex items-center mb-4">
                <Icon name="analytics" size="lg" color="blue" class="mr-3" />
                <h4 class="text-lg font-semibold text-gray-900">数据分析</h4>
              </div>
              <p class="text-gray-600 mb-4">深入分析您的数据，生成专业的报告和可视化图表。</p>
              <button
                class="w-full px-4 py-2 border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium rounded-lg transition-colors"
              >
                查看详情
              </button>
            </div>

            <div class="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
              <div class="flex items-center mb-4">
                <Icon name="security" size="lg" color="green" class="mr-3" />
                <h4 class="text-lg font-semibold text-gray-900">安全管理</h4>
              </div>
              <p class="text-gray-600 mb-4">确保系统安全性，管理用户权限和访问控制。</p>
              <button
                class="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
              >
                查看详情
              </button>
            </div>
          </div>
        </div>

        <!-- Form Elements -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-800 mb-4">表单组件</h3>
          <div class="bg-white rounded-lg p-8 shadow-sm border border-gray-200">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1"> 姓名 </label>
                  <input
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                    type="text"
                    placeholder="请输入姓名"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1"> 部门 </label>
                  <select
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                  >
                    <option>请选择部门</option>
                    <option>行政办公室</option>
                    <option>人事处</option>
                    <option>财务处</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1"> 备注 </label>
                  <textarea
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                    rows="3"
                    placeholder="请输入备注信息"
                  ></textarea>
                </div>
              </div>
              <div class="space-y-4">
                <div class="flex items-center">
                  <input
                    type="checkbox"
                    id="checkbox1"
                    class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label for="checkbox1" class="ml-2 text-sm text-gray-700"> 同意服务条款 </label>
                </div>
                <div class="space-y-2">
                  <div class="flex items-center">
                    <input
                      type="radio"
                      id="radio1"
                      name="priority"
                      class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                    />
                    <label for="radio1" class="ml-2 text-sm text-gray-700"> 高优先级 </label>
                  </div>
                  <div class="flex items-center">
                    <input
                      type="radio"
                      id="radio2"
                      name="priority"
                      class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                    />
                    <label for="radio2" class="ml-2 text-sm text-gray-700"> 普通优先级 </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-800 mb-4">导航组件</h3>
          <div class="bg-white rounded-lg p-8 shadow-sm border border-gray-200">
            <nav class="flex space-x-8 mb-6">
              <a class="text-primary-600 border-b-2 border-primary-600 font-medium pb-2">
                <Icon name="home" size="sm" color="inherit" class="mr-2" />
                主页
              </a>
              <a class="text-gray-500 hover:text-gray-700 font-medium pb-2 transition-colors">
                <Icon name="folder" size="sm" color="inherit" class="mr-2" />
                文件管理
              </a>
              <a class="text-gray-500 hover:text-gray-700 font-medium pb-2 transition-colors">
                <Icon name="people" size="sm" color="inherit" class="mr-2" />
                用户管理
              </a>
              <a class="text-gray-500 hover:text-gray-700 font-medium pb-2 transition-colors">
                <Icon name="settings" size="sm" color="inherit" class="mr-2" />
                系统设置
              </a>
            </nav>

            <div class="flex flex-wrap gap-2">
              <span
                class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
              >
                <Icon name="label" size="xs" color="inherit" class="mr-1" />
                重要
              </span>
              <span
                class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
              >
                <Icon name="check_circle" size="xs" color="inherit" class="mr-1" />
                已完成
              </span>
              <span
                class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800"
              >
                <Icon name="schedule" size="xs" color="inherit" class="mr-1" />
                待处理
              </span>
              <span
                class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800"
              >
                <Icon name="error" size="xs" color="inherit" class="mr-1" />
                错误
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Layout Examples -->
      <section class="mb-16">
        <h2 class="text-2xl font-semibold text-gray-900 mb-8">布局示例</h2>
        <div class="bg-white rounded-lg p-8 shadow-sm border border-gray-200">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div class="lg:col-span-2">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">主要内容区域</h3>
              <div class="space-y-4">
                <div class="p-4 bg-gray-50 rounded-lg">
                  <h4 class="font-medium text-gray-900 mb-2">内容块 1</h4>
                  <p class="text-gray-600 text-sm">
                    这里是主要内容的展示区域，使用了合适的间距和层次结构。
                  </p>
                </div>
                <div class="p-4 bg-gray-50 rounded-lg">
                  <h4 class="font-medium text-gray-900 mb-2">内容块 2</h4>
                  <p class="text-gray-600 text-sm">保持一致的设计风格和视觉层次，提升用户体验。</p>
                </div>
              </div>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-4">侧边栏</h3>
              <div class="space-y-3">
                <div class="p-3 bg-primary-50 border border-primary-200 rounded-lg">
                  <p class="text-sm font-medium text-primary-800">快速操作</p>
                </div>
                <div class="p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <p class="text-sm font-medium text-gray-700">相关信息</p>
                </div>
                <div class="p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <p class="text-sm font-medium text-gray-700">额外功能</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Icon Examples -->
      <section class="mb-16">
        <h2 class="text-2xl font-semibold text-gray-900 mb-8">图标系统</h2>
        <div class="bg-white rounded-lg p-8 shadow-sm border border-gray-200">
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8">
            <div v-for="iconName in commonIcons" :key="iconName" class="text-center">
              <Icon :name="iconName" size="lg" color="gray" class="mb-2" />
              <p class="text-xs text-gray-600">{{ iconName }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Icon from './Icon.vue'

const redShades = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900', '950']
const primaryShades = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900', '950']
const grayShades = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900', '950']

const commonIcons = [
  'home',
  'search',
  'settings',
  'person',
  'folder',
  'description',
  'edit',
  'delete',
  'add',
  'check',
  'close',
  'menu',
  'notifications',
  'security',
  'analytics',
  'schedule',
  'error',
  'info',
]

const copyColor = (colorClass: string) => {
  navigator.clipboard.writeText(colorClass)
  // 这里可以添加一个提示消息
}
</script>
