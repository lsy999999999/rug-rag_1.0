<template>
  <div class="p-8 space-y-8">
    <h1 class="text-3xl font-bold mb-8">Material Symbols Icon Component</h1>

    <!-- Basic Usage -->
    <section>
      <h2 class="text-xl font-semibold mb-4">Basic Usage</h2>
      <div class="flex items-center gap-4">
        <Icon name="home" />
        <Icon name="search" />
        <Icon name="settings" />
        <Icon name="favorite" />
      </div>
    </section>

    <!-- Sizes -->
    <section>
      <h2 class="text-xl font-semibold mb-4">Sizes</h2>
      <div class="flex items-center gap-4">
        <Icon name="star" size="xs" />
        <Icon name="star" size="sm" />
        <Icon name="star" size="md" />
        <Icon name="star" size="lg" />
        <Icon name="star" size="xl" />
        <Icon name="star" :size="64" />
      </div>
    </section>

    <!-- Variants -->
    <section>
      <h2 class="text-xl font-semibold mb-4">Variants</h2>
      <div class="flex items-center gap-4">
        <Icon name="favorite" variant="outlined" />
        <Icon name="favorite" variant="rounded" />
        <Icon name="favorite" variant="sharp" />
      </div>
    </section>

    <!-- Colors -->
    <section>
      <h2 class="text-xl font-semibold mb-4">Colors</h2>
      <div class="flex items-center gap-4">
        <Icon name="circle" color="primary" />
        <Icon name="circle" color="secondary" />
        <Icon name="circle" color="success" />
        <Icon name="circle" color="warning" />
        <Icon name="circle" color="error" />
        <Icon name="circle" color="#ff6b35" />
      </div>
    </section>

    <!-- Fill Variations -->
    <section>
      <h2 class="text-xl font-semibold mb-4">Fill Variations</h2>
      <div class="flex items-center gap-4">
        <Icon name="favorite" :fill="0" />
        <Icon name="favorite" :fill="0.5" />
        <Icon name="favorite" :fill="1" />
      </div>
    </section>

    <!-- Weight Variations -->
    <section>
      <h2 class="text-xl font-semibold mb-4">Weight Variations</h2>
      <div class="flex items-center gap-4">
        <Icon name="home" :weight="100" />
        <Icon name="home" :weight="300" />
        <Icon name="home" :weight="400" />
        <Icon name="home" :weight="500" />
        <Icon name="home" :weight="700" />
      </div>
    </section>

    <!-- Common Icons Showcase -->
    <section>
      <h2 class="text-xl font-semibold mb-4">Common Icons</h2>
      <div class="grid grid-cols-8 gap-4">
        <div
          v-for="(iconName, key) in CommonIcons"
          :key="key"
          class="flex flex-col items-center gap-2"
        >
          <Icon :name="iconName" size="lg" />
          <span class="text-xs text-gray-600">{{ key }}</span>
        </div>
      </div>
    </section>

    <!-- Interactive Example -->
    <section>
      <h2 class="text-xl font-semibold mb-4">Interactive Example</h2>
      <div class="bg-gray-50 p-6 rounded-lg">
        <div class="flex items-center gap-4 mb-4">
          <button
            @click="toggleFavorite"
            class="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors"
            :class="isFavorite ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'"
          >
            <Icon name="favorite" :fill="isFavorite ? 1 : 0" color="inherit" />
            {{ isFavorite ? 'Remove from favorites' : 'Add to favorites' }}
          </button>

          <button
            @click="showNotification"
            class="flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-600 rounded-lg"
          >
            <Icon name="notifications" />
            Show notification
          </button>
        </div>

        <div
          v-if="notification"
          class="flex items-center gap-2 p-3 bg-green-100 text-green-800 rounded-lg"
        >
          <Icon name="check_circle" />
          {{ notification }}
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Icon from './Icon.vue'
import { CommonIcons } from './types'

const isFavorite = ref(false)
const notification = ref('')

const toggleFavorite = () => {
  isFavorite.value = !isFavorite.value
}

const showNotification = () => {
  notification.value = 'Notification sent!'
  setTimeout(() => {
    notification.value = ''
  }, 3000)
}
</script>
