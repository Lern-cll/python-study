<template>
  <div class="category-nav">
    <div class="nav-scroll">
      <div
        v-for="category in categories"
        :key="category.id"
        :class="['nav-item', { active: currentId === category.id }]"
        @click="handleSelect(category)"
      >
        {{ category.name }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  // 分类列表数据
  categories: {
    type: Array,
    default: () => []
  },
  // v-model 绑定的当前选中分类 ID（number | string | null）
  modelValue: {
    type: [Number, String],
    default: null
  }
})

// 自定义事件：
// - update:modelValue：用于 v-model 双向同步当前选中 ID
// - change：选中分类变化时附带整个分类对象抛出
const emit = defineEmits(['update:modelValue', 'change'])

// 组件内部维护的当前选中 ID（避免直接修改 prop）
const currentId = ref(props.modelValue)

// 监听外部值变化：父组件直接修改 modelValue 时同步到组件内部
watch(() => props.modelValue, (val) => {
  currentId.value = val
})

/**
 * 选中某个分类：更新内部状态并抛出 update:modelValue 与 change 事件
 * @param category - 被点击的分类对象
 */
const handleSelect = (category) => {
  currentId.value = category.id
  emit('update:modelValue', category.id)
  emit('change', category)
}
</script>

<style lang="scss" scoped>
.category-nav {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;

  .nav-scroll {
    display: flex;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
    padding: 0 15px;

    &::-webkit-scrollbar {
      display: none;
    }

    .nav-item {
      flex-shrink: 0;
      padding: 12px 15px;
      font-size: 0.9375rem;
      color: #666;
      position: relative;
      white-space: nowrap;

      &.active {
        color: #e63946;
        font-weight: 600;

        &::after {
          content: '';
          position: absolute;
          bottom: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 20px;
          height: 3px;
          background: #e63946;
          border-radius: 2px;
        }
      }
    }
  }
}
</style>