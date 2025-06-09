# Material Symbols Icon Component

基于 Google Material Symbols 系统的通用图标组件，支持丰富的自定义选项和优化的性能。

## 特性

- 🎨 **三种样式变体**: outlined, rounded, sharp
- 📏 **灵活尺寸控制**: 预设尺寸 + 自定义数值
- 🎯 **颜色系统**: 预设主题色 + 自定义颜色
- ⚙️ **高级定制**: fill, weight, grade, optical size
- 🚀 **性能优化**: 基于 vite-plugin-material-symbols 的按需加载
- 💪 **TypeScript 支持**: 完整的类型定义

## 基础用法

```vue
<template>
  <!-- 基础图标 -->
  <Icon name="home" />

  <!-- 指定尺寸 -->
  <Icon name="star" size="lg" />

  <!-- 自定义颜色 -->
  <Icon name="favorite" color="error" />

  <!-- 组合属性 -->
  <Icon name="settings" variant="rounded" size="xl" color="primary" :fill="1" />
</template>

<script setup>
import { Icon } from '@/components/common'
</script>
```

## 属性说明

### name (必需)

- **类型**: `string`
- **说明**: Material Symbols 图标名称
- **示例**: `"home"`, `"search"`, `"favorite"`

### size

- **类型**: `'xs' | 'sm' | 'md' | 'lg' | 'xl' | number`
- **默认值**: `'md'`
- **说明**: 图标尺寸，可使用预设值或自定义像素值
- **预设尺寸**:
  - `xs`: 16px
  - `sm`: 20px
  - `md`: 24px
  - `lg`: 32px
  - `xl`: 48px

### variant

- **类型**: `'outlined' | 'rounded' | 'sharp'`
- **默认值**: `'outlined'`
- **说明**: 图标样式变体

### color

- **类型**: `'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'inherit' | string`
- **默认值**: `'inherit'`
- **说明**: 图标颜色，可使用预设主题色或自定义颜色值

### fill

- **类型**: `number`
- **默认值**: `0`
- **范围**: `0-1`
- **说明**: 图标填充程度

### weight

- **类型**: `number`
- **默认值**: `400`
- **范围**: `100-700`
- **说明**: 图标粗细

### grade

- **类型**: `number`
- **默认值**: `0`
- **范围**: `-25-200`
- **说明**: 图标对比度调整

### opticalSize

- **类型**: `number`
- **默认值**: `24`
- **范围**: `20-48`
- **说明**: 光学尺寸，影响图标在不同尺寸下的视觉效果

### title

- **类型**: `string`
- **说明**: 图标的 tooltip 提示文本

## 使用示例

### 基础图标

```vue
<Icon name="home" />
<Icon name="search" />
<Icon name="settings" />
```

### 不同尺寸

```vue
<Icon name="star" size="xs" />
<Icon name="star" size="sm" />
<Icon name="star" size="md" />
<Icon name="star" size="lg" />
<Icon name="star" size="xl" />
<Icon name="star" :size="64" />
```

### 样式变体

```vue
<Icon name="favorite" variant="outlined" />
<Icon name="favorite" variant="rounded" />
<Icon name="favorite" variant="sharp" />
```

### 颜色系统

```vue
<Icon name="circle" color="primary" />
<Icon name="circle" color="success" />
<Icon name="circle" color="error" />
<Icon name="circle" color="#ff6b35" />
```

### 高级定制

```vue
<!-- 实心图标 -->
<Icon name="favorite" :fill="1" />

<!-- 细线条图标 -->
<Icon name="home" :weight="200" />

<!-- 高对比度图标 -->
<Icon name="star" :grade="200" />
```

### 交互式用法

```vue
<template>
  <button @click="toggleFavorite" class="flex items-center gap-2">
    <Icon name="favorite" :fill="isFavorite ? 1 : 0" :color="isFavorite ? 'error' : 'inherit'" />
    {{ isFavorite ? '已收藏' : '收藏' }}
  </button>
</template>

<script setup>
import { ref } from 'vue'
import { Icon } from '@/components/common'

const isFavorite = ref(false)

const toggleFavorite = () => {
  isFavorite.value = !isFavorite.value
}
</script>
```

## 常用图标

组件提供了 `CommonIcons` 常量，包含常用图标名称：

```typescript
import { CommonIcons } from '@/components/common'

// 使用预定义图标
<Icon :name="CommonIcons.home" />
<Icon :name="CommonIcons.search" />
<Icon :name="CommonIcons.settings" />
```

## 性能优化

项目已配置 `vite-plugin-material-symbols` 插件，会自动：

- 扫描代码中使用的 `Icon` 组件
- 在构建时只加载实际使用的图标字体
- 在 `index.html` 中自动注入选择性的字体链接
- 显著减少字体文件大小和加载时间

### 工作原理

- **开发模式**: 加载完整的字体文件以便调试
- **生产模式**: 仅加载代码中实际使用的图标，生成类似：
  ```html
  <link
    href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&icon_names=home,search,favorite"
    rel="stylesheet"
  />
  ```

## 更多图标

查看完整的 Material Symbols 图标库：

- [Material Symbols 官方网站](https://fonts.google.com/icons)
- [GitHub - Material Design Icons](https://github.com/google/material-design-icons)

## 类型支持

```typescript
import type { IconProps, IconSize, IconVariant, IconColor } from '@/components/common'
```
