# Vue Composition API 详解与示例

Composition API 是 Vue 3 引入的一套新的 API 风格，它提供了更好的代码组织和复用方式，特别是对于复杂组件逻辑的管理。

## Composition API 核心概念

1. **响应式状态**：使用 `ref` 和 `reactive` 创建
2. **组合函数**：将相关功能组织在一起
3. **生命周期钩子**：以函数形式使用
4. **代码复用**：通过自定义组合函数实现

## 基础示例：计数器组件

```javascript
<template>
  <div>
    <p>计数: {{ count }}</p>
    <button @click="increment">增加</button>
    <button @click="decrement">减少</button>
    <p>两倍计数: {{ doubleCount }}</p>
  </div>
</template>

<script>
import { ref, computed } from 'vue';

export default {
  setup() {
    // 响应式状态
    const count = ref(0);

    // 计算属性
    const doubleCount = computed(() => count.value * 2);

    // 方法
    const increment = () => {
      count.value++;
    };

    const decrement = () => {
      count.value--;
    };

    // 返回模板中可用的内容
    return {
      count,
      doubleCount,
      increment,
      decrement
    };
  }
}
</script>
```

## 进阶示例：组合函数复用逻辑

### 1. 创建可复用的组合函数

```javascript
// src/composables/useCounter.js
import { ref, computed } from 'vue';

export default function useCounter(initialValue = 0) {
  const count = ref(initialValue);
  
  const doubleCount = computed(() => count.value * 2);
  
  const increment = () => {
    count.value++;
  };
  
  const decrement = () => {
    count.value--;
  };
  
  return {
    count,
    doubleCount,
    increment,
    decrement
  };
}
```

### 2. 在组件中使用组合函数

```javascript
<template>
  <div>
    <p>主计数: {{ count }}</p>
    <p>两倍计数: {{ doubleCount }}</p>
    <button @click="increment">增加</button>
    <button @click="decrement">减少</button>
    
    <p>副计数: {{ secondary.count }}</p>
    <button @click="secondary.increment">增加副计数</button>
  </div>
</template>

<script>
import useCounter from '@/composables/useCounter';

export default {
  setup() {
    // 使用组合函数
    const { count, doubleCount, increment, decrement } = useCounter(5);
    
    // 可以多次使用同一个组合函数
    const secondary = useCounter(10);
    
    return {
      count,
      doubleCount,
      increment,
      decrement,
      secondary
    };
  }
}
</script>
```

## 实际应用场景示例：获取鼠标位置

### 1. 创建鼠标跟踪组合函数

```javascript
// src/composables/useMousePosition.js
import { ref, onMounted, onUnmounted } from 'vue';

export default function useMousePosition() {
  const x = ref(0);
  const y = ref(0);
  
  const update = (event) => {
    x.value = event.pageX;
    y.value = event.pageY;
  };
  
  onMounted(() => {
    window.addEventListener('mousemove', update);
  });
  
  onUnmounted(() => {
    window.removeEventListener('mousemove', update);
  });
  
  return { x, y };
}
```

### 2. 在组件中使用

```vue
<template>
  <div>
    <p>鼠标位置: ({{ x }}, {{ y }})</p>
  </div>
</template>

<script>
import useMousePosition from '@/composables/useMousePosition';

export default {
  setup() {
    const { x, y } = useMousePosition();
    
    return { x, y };
  }
}
</script>
```

## Composition API 的优势

1. **更好的逻辑复用**：比 mixins 更清晰，没有命名冲突
2. **更灵活的代码组织**：可以按功能而非选项类型组织代码
3. **更好的类型推断**：对 TypeScript 支持更好
4. **更小的打包体积**：可以按需导入
5. **更清晰的依赖关系**：所有响应式依赖都显式声明

## 与 Options API 对比

| 特性 | Composition API | Options API |
|------|----------------|-------------|
| 代码组织 | 按功能逻辑组织 | 按选项类型(data, methods等)组织 |
| 复用性 | 高(组合函数) | 中(mixins) |
| TypeScript支持 | 优秀 | 一般 |
| 学习曲线 | 较陡峭 | 较平缓 |
| 适用场景 | 复杂组件 | 简单组件 |

- [ ] Composition API 不是要完全替代 Options API，而是提供了另一种选择，特别是在处理复杂逻辑时更为强大。