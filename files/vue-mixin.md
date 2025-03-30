# Vue Mixin 示例

下面我将展示一个完整的 Vue mixin 示例，包括它的定义、使用以及实际应用场景。

## 1. 定义 Mixin

首先我们创建一个 `loggerMixin.js` 文件：

```javascript
// src/mixins/loggerMixin.js
export default {
  data() {
    return {
      mixinMessage: '来自mixin的消息'
    }
  },
  
  created() {
    this.log('组件已创建');
  },
  
  methods: {
    log(message) {
      console.log(`[日志] ${new Date().toLocaleTimeString()}: ${message}`);
      console.log(`附加数据: ${this.mixinMessage}`);
    },
    
    // 一个通用的格式化方法
    formatDate(date) {
      return new Date(date).toLocaleDateString();
    }
  },
  
  computed: {
    // 一个通用的计算属性
    currentYear() {
      return new Date().getFullYear();
    }
  }
}
```

## 2. 在组件中使用 Mixin

```javascript
<!-- src/components/UserProfile.vue -->
<template>
  <div>
    <h2>用户资料</h2>
    <p>注册日期: {{ formatDate(user.joinDate) }}</p>
    <p>© {{ currentYear }} 版权所有</p>
    <button @click="logUser">记录用户</button>
  </div>
</template>

<script>
import loggerMixin from '@/mixins/loggerMixin';

export default {
  name: 'UserProfile',
  // 引入mixin
  mixins: [loggerMixin],
  
  data() {
    return {
      user: {
        name: '张三',
        joinDate: '2020-06-15'
      }
    }
  },
  
  methods: {
    logUser() {
      this.log(`用户: ${this.user.name}`);
    }
  },
  
  mounted() {
    this.log('用户资料组件已挂载');
  }
}
</script>
```

## 3. 实际应用场景

### 场景1：多个组件共享日志功能
- 多个组件都可以使用相同的 `log` 方法
- 统一的日志格式

### 场景2：日期格式化工具
- 多个组件都可以使用 `formatDate` 方法
- 确保整个应用的日期格式一致

### 场景3：公共计算属性
- 如 `currentYear` 可以在多个组件中使用

## 4. Mixin 合并规则

1. **data**：组件数据优先，mixin 数据作为补充
2. **方法**：同名时组件方法覆盖 mixin 方法
3. **生命周期钩子**：都会执行，mixin 的先执行
4. **计算属性/侦听器**：同名时组件属性覆盖 mixin 属性

## 5. 替代方案（Vue 3）

在 Vue 3 中，Composition API 提供了更好的代码复用方式：

```javascript
// src/composables/useLogger.js
import { ref, onMounted } from 'vue';

export default function useLogger() {
  const message = ref('来自composable的消息');
  
  const log = (msg) => {
    console.log(`[日志] ${new Date().toLocaleTimeString()}: ${msg}`);
  };
  
  onMounted(() => {
    log('组件已挂载');
  });
  
  return { message, log };
}
```

Mixin 仍然有其适用场景，但在 Vue 3 中，Composition API 通常是更推荐的选择，因为它提供了更清晰的代码组织和更好的类型推断。