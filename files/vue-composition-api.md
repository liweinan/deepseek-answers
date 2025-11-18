# Vue Composition API Detailed Explanation and Examples

Composition API is a new API style introduced in Vue 3, providing better code organization and reusability, especially for managing complex component logic.

## Composition API Core Concepts

1. **Reactive State**: Created using `ref` and `reactive`
2. **Composables**: Organize related functionality together
3. **Lifecycle Hooks**: Used in function form
4. **Code Reusability**: Achieved through custom composable functions

## Basic Example: Counter Component

```javascript
<template>
  <div>
    <p>Count: {{ count }}</p>
    <button @click="increment">Increment</button>
    <button @click="decrement">Decrement</button>
    <p>Double Count: {{ doubleCount }}</p>
  </div>
</template>

<script>
import { ref, computed } from 'vue';

export default {
  setup() {
    // Reactive state
    const count = ref(0);

    // Computed property
    const doubleCount = computed(() => count.value * 2);

    // Methods
    const increment = () => {
      count.value++;
    };

    const decrement = () => {
      count.value--;
    };

    // Return what's available in template
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

## Advanced Example: Composable Function for Logic Reuse

### 1. Create Reusable Composable Function

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

### 2. Use Composable Function in Component

```javascript
<template>
  <div>
    <p>Main Count: {{ count }}</p>
    <p>Double Count: {{ doubleCount }}</p>
    <button @click="increment">Increment</button>
    <button @click="decrement">Decrement</button>
    
    <p>Secondary Count: {{ secondary.count }}</p>
    <button @click="secondary.increment">Increment Secondary</button>
  </div>
</template>

<script>
import useCounter from '@/composables/useCounter';

export default {
  setup() {
    // Use composable function
    const { count, doubleCount, increment, decrement } = useCounter(5);
    
    // Can use the same composable function multiple times
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

## Practical Application Example: Get Mouse Position

### 1. Create Mouse Tracking Composable Function

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

### 2. Use in Component

```vue
<template>
  <div>
    <p>Mouse Position: ({{ x }}, {{ y }})</p>
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

## Advantages of Composition API

1. **Better Logic Reuse**: Clearer than mixins, no naming conflicts
2. **More Flexible Code Organization**: Can organize code by functionality rather than option types
3. **Better Type Inference**: Better TypeScript support
4. **Smaller Bundle Size**: Can import on demand
5. **Clearer Dependencies**: All reactive dependencies are explicitly declared

## Comparison with Options API

| Feature | Composition API | Options API |
|------|----------------|-------------|
| Code Organization | Organized by functional logic | Organized by option types (data, methods, etc.) |
| Reusability | High (composable functions) | Medium (mixins) |
| TypeScript Support | Excellent | Average |
| Learning Curve | Steeper | Gentler |
| Use Cases | Complex components | Simple components |

- [ ] Composition API is not meant to completely replace Options API, but provides another option, especially more powerful when handling complex logic.
