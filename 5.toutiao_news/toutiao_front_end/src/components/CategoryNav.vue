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
  categories: {
    type: Array,
    default: () => []
  },
  modelValue: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const currentId = ref(props.modelValue)

// 监听外部值变化
watch(() => props.modelValue, (val) => {
  currentId.value = val
})

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