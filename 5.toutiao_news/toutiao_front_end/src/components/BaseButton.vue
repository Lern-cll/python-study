<template>
  <el-button
    :type="type"
    :size="size"
    :disabled="disabled"
    :loading="loading"
    :plain="plain"
    :round="round"
    :circle="circle"
    :class="['base-button', { 'full-width': block }]"
    @click="handleClick"
  >
    <slot />
  </el-button>
</template>

<script setup>
// 基础按钮组件：基于 Element Plus <el-button> 二次封装，
// 用于统一禁用/loading 状态下的点击行为，并对外暴露 click 事件。
const props = defineProps({
  // 按钮类型（primary / success / warning / danger / info / text ...）
  type: {
    type: String,
    default: 'primary'
  },
  // 按钮尺寸（Element Plus 仅支持 ''/default/small/large；此处对齐默认 '')
  size: {
    type: String,
    default: ''
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 是否显示 loading
  loading: {
    type: Boolean,
    default: false
  },
  // 是否为朴素按钮
  plain: {
    type: Boolean,
    default: false
  },
  // 是否为圆角按钮
  round: {
    type: Boolean,
    default: false
  },
  // 是否为圆形按钮
  circle: {
    type: Boolean,
    default: false
  },
  // 是否撑满父容器宽度
  block: {
    type: Boolean,
    default: false
  }
})

// 自定义事件：click（仅在非禁用/非 loading 状态下触发）
const emit = defineEmits(['click'])

/**
 * 点击事件处理：禁用或 loading 时不向上抛出 click
 * @param e - 原生鼠标事件
 */
const handleClick = (e) => {
  if (!props.disabled && !props.loading) {
    emit('click', e)
  }
}
</script>

<style lang="scss" scoped>
.base-button {
  &.full-width {
    width: 100%;
  }
}
</style>