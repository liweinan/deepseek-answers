# Vue Mixin Example

Below I will demonstrate a complete Vue mixin example, including its definition, usage, and practical application scenarios.

## 1. Define Mixin

First, we create a `loggerMixin.js` file:

```javascript
// src/mixins/loggerMixin.js
export default {
  data() {
    return {
      mixinMessage: 'Message from mixin'
    }
  },
  
  created() {
    this.log('Component created');
  },
  
  methods: {
    log(message) {
      console.log(`[Log] ${new Date().toLocaleTimeString()}: ${message}`);
      console.log(`Additional data: ${this.mixinMessage}`);
    },
    
    // A common formatting method
    formatDate(date) {
      return new Date(date).toLocaleDateString();
    }
  },
  
  computed: {
    // A common computed property
    currentYear() {
      return new Date().getFullYear();
    }
  }
}
```

## 2. Use Mixin in Component

```javascript
<!-- src/components/UserProfile.vue -->
<template>
  <div>
    <h2>User Profile</h2>
    <p>Registration Date: {{ formatDate(user.joinDate) }}</p>
    <p>© {{ currentYear }} All Rights Reserved</p>
    <button @click="logUser">Log User</button>
  </div>
</template>

<script>
import loggerMixin from '@/mixins/loggerMixin';

export default {
  name: 'UserProfile',
  // Import mixin
  mixins: [loggerMixin],
  
  data() {
    return {
      user: {
        name: 'John Doe',
        joinDate: '2020-06-15'
      }
    }
  },
  
  methods: {
    logUser() {
      this.log(`User: ${this.user.name}`);
    }
  },
  
  mounted() {
    this.log('User profile component mounted');
  }
}
</script>
```

## 3. Practical Application Scenarios

### Scenario 1: Multiple Components Share Logging Functionality
- Multiple components can use the same `log` method
- Unified log format

### Scenario 2: Date Formatting Utility
- Multiple components can use the `formatDate` method
- Ensure consistent date format across the application

### Scenario 3: Common Computed Properties
- Such as `currentYear` can be used in multiple components

## 4. Mixin Merge Rules

1. **data**: Component data takes priority, mixin data serves as supplement
2. **Methods**: Component methods override mixin methods when names conflict
3. **Lifecycle Hooks**: All execute, mixin hooks execute first
4. **Computed Properties/Watchers**: Component properties override mixin properties when names conflict

## 5. Alternative Solution (Vue 3)

In Vue 3, Composition API provides a better way for code reuse:

```javascript
// src/composables/useLogger.js
import { ref, onMounted } from 'vue';

export default function useLogger() {
  const message = ref('Message from composable');
  
  const log = (msg) => {
    console.log(`[Log] ${new Date().toLocaleTimeString()}: ${msg}`);
  };
  
  onMounted(() => {
    log('Component mounted');
  });
  
  return { message, log };
}
```

Mixins still have their use cases, but in Vue 3, Composition API is usually the more recommended choice as it provides clearer code organization and better type inference.
