<template>
  <span
    :class="[variantClass, `icon-${size}`, colorClass]"
    :style="customStyle"
    :title="title"
    v-bind="$attrs"
  >
    {{ name }}
  </span>
</template>

<script setup lang="ts">
import { computed, type CSSProperties } from 'vue'

export interface IconProps {
  // Icon name from Material Symbols
  name: string
  // Icon size preset or custom size
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | number
  // Icon variant style
  variant?: 'outlined' | 'rounded' | 'sharp'
  // Icon color preset or custom color
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'inherit' | string
  // Custom fill value (0-1)
  fill?: number
  // Custom weight value (100-700)
  weight?: number
  // Custom grade value (-25 to 200)
  grade?: number
  // Custom optical size (20-48)
  opticalSize?: number
  // Tooltip title
  title?: string
}

const props = withDefaults(defineProps<IconProps>(), {
  size: 'md',
  variant: 'outlined',
  color: 'inherit',
  fill: 0,
  weight: 400,
  grade: 0,
  opticalSize: 24,
})

defineOptions({
  inheritAttrs: false,
})

// Size mapping
const sizeMap = {
  xs: 16,
  sm: 20,
  md: 24,
  lg: 32,
  xl: 48,
} as const

// Color class mapping
const colorClassMap = {
  primary: 'text-blue-600',
  secondary: 'text-gray-600',
  success: 'text-green-600',
  warning: 'text-yellow-600',
  error: 'text-red-600',
  inherit: 'text-inherit',
} as const

// Variant class mapping
const variantClassMap = {
  outlined: 'material-symbols-outlined',
  rounded: 'material-symbols-rounded',
  sharp: 'material-symbols-sharp',
} as const

const variantClass = computed(() => variantClassMap[props.variant])

const colorClass = computed(() => {
  if (props.color in colorClassMap) {
    return colorClassMap[props.color as keyof typeof colorClassMap]
  }
  return ''
})

const iconSize = computed(() => {
  if (typeof props.size === 'number') {
    return props.size
  }
  return sizeMap[props.size]
})

const customStyle = computed((): CSSProperties => {
  const style: CSSProperties = {
    fontSize: `${iconSize.value}px`,
    fontVariationSettings: `'FILL' ${props.fill}, 'wght' ${props.weight}, 'GRAD' ${props.grade}, 'opsz' ${props.opticalSize}`,
  }

  // Apply custom color if not a preset
  if (!(props.color in colorClassMap)) {
    style.color = props.color
  }

  return style
})
</script>

<style scoped>
.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-weight: normal;
  font-style: normal;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
  vertical-align: middle;
}

.material-symbols-rounded {
  font-family: 'Material Symbols Rounded';
  font-weight: normal;
  font-style: normal;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
  vertical-align: middle;
}

.material-symbols-sharp {
  font-family: 'Material Symbols Sharp';
  font-weight: normal;
  font-style: normal;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
  vertical-align: middle;
}

.icon-xs {
  width: 16px;
  height: 16px;
}
.icon-sm {
  width: 20px;
  height: 20px;
}
.icon-md {
  width: 24px;
  height: 24px;
}
.icon-lg {
  width: 32px;
  height: 32px;
}
.icon-xl {
  width: 48px;
  height: 48px;
}
</style>
