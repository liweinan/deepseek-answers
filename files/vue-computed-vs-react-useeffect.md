# Comparison: `computed` in Vue vs `useEffect` in React

Both `computed` in Vue and `useEffect` in React are used to handle side effects and reactive data, but they have different design philosophies and use cases.

## `computed` in Vue

**Purpose**:
- Used to declaratively define derived state that automatically updates when its dependencies change
- Primarily for calculating values based on other reactive properties

**Characteristics**:
- Declarative: You define what the value should be based on
- Automatic dependency tracking: Vue automatically detects what reactive properties are used inside the computed function
- Cached: Only re-evaluates when dependencies change
- Synchronous: Computed properties must be synchronous

**Example**:
```javascript
// Vue 3 Composition API
import { ref, computed } from 'vue'

const count = ref(0)
const doubleCount = computed(() => count.value * 2)
```

## `useEffect` in React

**Purpose**:
- Used to perform side effects in function components
- Handles operations that should happen after render, like data fetching, subscriptions, or manual DOM manipulations

**Characteristics**:
- Imperative: You specify when and how effects should run
- Explicit dependencies: You must specify the dependency array
- Not cached: Runs after every render where dependencies change
- Can be asynchronous
- More general-purpose than Vue's computed

**Example**:
```javascript
import { useState, useEffect } from 'react';

function Example() {
  const [count, setCount] = useState(0);
  const [doubleCount, setDoubleCount] = useState(0);

  useEffect(() => {
    setDoubleCount(count * 2);
  }, [count]);

  return /* ... */
}
```

## Key Differences

| Aspect          | Vue `computed` | React `useEffect` |
|-----------------|---------------|------------------|
| Primary Purpose | Derived state | Side effects |
| Dependency Tracking | Automatic | Manual (dependency array) |
| Execution Timing | Synchronous during reactivity updates | After render |
| Caching | Yes (memoized) | No (runs on every dependency change) |
| Async Support | No | Yes |
| Return Value | Returns the derived value | Returns cleanup function or nothing |
| Mental Model | "What is this value?" | "What should happen when these values change?" |

## When to Use Each

- Use Vue `computed` when you need to derive a value from other reactive properties
- Use React `useEffect` when you need to perform side effects in response to state/prop changes

For React developers wanting computed-like behavior, consider:
- `useMemo` for memoized derived values (closer to Vue's computed)
- `useCallback` for memoized functions

Vue's approach is more declarative for derived state, while React's approach gives more control over side effects but requires more manual dependency management.

---

# Comparison: `useEffect` vs `useMemo` in React

Both hooks help manage side effects and optimize performance, but they serve different purposes in React applications.

## `useEffect`

**Primary Purpose**: Handle side effects in functional components (data fetching, subscriptions, DOM manipulations).

**Key Characteristics**:
- Runs **after** render completes
- Used for operations that need to happen when certain dependencies change
- Can contain imperative code with side effects
- Returns a cleanup function (optional)
- Doesn't return a value to the component

**Syntax**:
```javascript
useEffect(() => {
  // Side effect code
  return () => { /* Cleanup */ }; // Optional
}, [dependencies]);
```

## `useMemo`

**Primary Purpose**: Memoize expensive calculations to avoid re-computation on every render.

**Key Characteristics**:
- Runs **during** render
- Used for performance optimization by memoizing values
- Must be pure (no side effects)
- Returns a value that can be used in rendering
- Skips recomputation when dependencies haven't changed

**Syntax**:
```javascript
const memoizedValue = useMemo(() => {
  // Expensive calculation
  return computedValue;
}, [dependencies]);
```

## Key Differences

| Aspect          | `useEffect` | `useMemo` |
|-----------------|------------|-----------|
| **Timing** | Runs after render | Runs during render |
| **Return Value** | No return (or cleanup function) | Returns memoized value |
| **Side Effects** | Allowed | Not allowed (should be pure) |
| **Primary Use Case** | Responding to changes (fetching data, subscriptions) | Optimizing expensive calculations |
| **Dependencies** | Runs when dependencies change | Recomputes when dependencies change |
| **Performance Impact** | Can cause additional renders | Prevents unnecessary recalculations |

## When to Use Each

**Use `useEffect` when**:
- You need to fetch data when props/state change
- You need to set up and clean up event listeners
- You need to interact with the DOM after render
- You need to perform any operation with side effects

**Use `useMemo` when**:
- You have expensive calculations that don't need to run every render
- You want to prevent child components from re-rendering unnecessarily
- You need to maintain referential equality for values between renders
- You're deriving complex values from props/state

## Example Comparison

```javascript
// Using useEffect - runs after render, no return value
function ComponentA({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);
  
  return /* ... */;
}

// Using useMemo - runs during render, returns memoized value
function ComponentB({ items, filter }) {
  const filteredItems = useMemo(() => {
    return items.filter(item => item.includes(filter));
  }, [items, filter]);
  
  return <List items={filteredItems} />;
}
```

## Common Pitfalls

For `useEffect`:
- Forgetting dependency array causing infinite loops
- Not cleaning up subscriptions leading to memory leaks
- Overusing for state derivation when `useMemo` would be better

For `useMemo`:
- Using for simple calculations (can be slower than recomputing)
- Including non-primitive dependencies that change too often
- Using for side effects (should use `useEffect` instead)

---

# Understanding Dependencies in `useEffect`

In React's `useEffect` hook, dependencies are values that determine when the effect should re-run. They're the second argument passed to `useEffect` in an array format.

## What Are Dependencies?

Dependencies are variables, props, or state values that:
1. Are used inside your effect function
2. Might change between renders
3. Could affect the behavior of your effect

## How They Work

```javascript
useEffect(() => {
  // Effect logic here
}, [dependency1, dependency2]); // Dependency array
```

- When **any value in the dependency array changes** between renders, the effect will re-run
- With an **empty array `[]`**, the effect runs only once (on mount)
- With **no array**, the effect runs after every render (usually undesirable)

## Example

```javascript
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(setUser);
  }, [userId]); // userId is the dependency
  // Effect will re-run whenever userId changes
}
```

## Why Dependencies Matter

1. **Avoid Infinite Loops**: Without proper dependencies, effects might run excessively
2. **Data Consistency**: Ensures your effect works with current values, not stale ones
3. **Performance Optimization**: Prevents unnecessary effect executions

## Common Dependency Scenarios

1. **Props as Dependencies**:
```javascript
useEffect(() => {
  // Runs whenever `props.someValue` changes
}, [props.someValue]);
```

2. **State as Dependencies**:
```javascript
const [count, setCount] = useState(0);
useEffect(() => {
  // Runs whenever `count` changes
}, [count]);
```

3. **Multiple Dependencies**:
```javascript
useEffect(() => {
  // Runs when either userId or filters change
}, [userId, filters]);
```

## The ESLint Warning

React's ESLint plugin will warn you about missing dependencies because:
- It analyzes which variables are used in your effect
- Helps prevent bugs from stale closures
- Can be disabled with `// eslint-disable-next-line` if truly intentional

## Special Cases

1. **Functions as Dependencies**:
    - If you use a function inside your effect, either:
        - Declare it inside the effect, or
        - Wrap it in `useCallback` and include in dependencies

2. **Objects/Arrays as Dependencies**:
    - These are compared by reference, so they might cause unnecessary re-runs
    - Consider using primitive values instead when possible

## Best Practices

1. Include all values used inside the effect that could change
2. Keep dependency arrays as small as possible
3. Consider splitting effects if dependency arrays get too large
4. Use the ESLint plugin to help identify missing dependencies

Remember: Proper dependency management is crucial for avoiding bugs and ensuring your React components behave as expected.

---

# The Risks of Writing Side Effects in `useMemo`

Writing side effect code in `useMemo` is considered an **anti-pattern** in React and can lead to several problems. Here's what you need to know:

## What Happens If You Put Side Effects in `useMemo`?

1. **Unpredictable Behavior**:
    - `useMemo` is designed to run **during rendering**, not after like `useEffect`
    - React may call your memoized function multiple times or not at all (it can discard results)
    - Side effects might execute at unexpected times

2. **Violation of React's Rules**:
    - `useMemo` should be a **pure function** (no side effects)
    - React's concurrent rendering features may break your side effects

3. **Strict Mode Double-Calling**:
    - In development with Strict Mode, React intentionally calls your `useMemo` function twice
    - This would cause your side effects to run twice!

## Example of Bad Practice

```javascript
// ❌ Dangerous anti-pattern
const value = useMemo(() => {
  console.log("Side effect!"); // Bad
  localStorage.setItem('key', data); // Very bad
  return computeExpensiveValue(a, b);
}, [a, b]);
```

## Proper Alternatives

1. **For derived values (what `useMemo` is for)**:
```javascript
// ✅ Good - pure computation only
const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);
```

2. **For side effects**:
```javascript
// ✅ Correct - use useEffect for side effects
useEffect(() => {
  console.log("Side effect!");
  localStorage.setItem('key', data);
}, [data]);
```

## When You Might Be Tempted (But Shouldn't)

1. **"I want to memoize and trigger a side effect"**:
    - Split into `useMemo` + `useEffect`:
   ```javascript
   const memoizedValue = useMemo(() => compute(a, b), [a, b]);
   useEffect(() => {
     // Side effect using memoizedValue
   }, [memoizedValue]);
   ```

2. **"I want to skip the effect on first render"**:
    - Use a ref to track first render instead:
   ```javascript
   const isFirstRender = useRef(true);
   useEffect(() => {
     if (isFirstRender.current) {
       isFirstRender.current = false;
       return;
     }
     // Your effect
   }, [deps]);
   ```

## Why React Allows This (But You Shouldn't)

While React doesn't technically prevent side effects in `useMemo`, it violates the hook's intended purpose and can cause:
- Broken behavior in concurrent rendering
- Difficult-to-debug issues
- Performance problems (since `useMemo` might run more often than expected)

Always use the right tool for the job: `useMemo` for calculations, `useEffect` for side effects.

---

# Why Side Effects Execute Unexpectedly in `useMemo`

The unpredictable nature of side effects in `useMemo` stems from how React's rendering model works. Here's a detailed explanation:

## 1. React's Rendering Phases

React separates work into:
- **Render phase** (where `useMemo` runs): Determines what needs to be updated
- **Commit phase** (where `useEffect` runs): Actually applies changes to DOM

Side effects in `useMemo` execute during the render phase, which is:
- Potentially **multiple times** before commits
- Possibly **thrown away** if React aborts the render

## 2. Fiber Architecture Behavior

React's reconciliation process may:
- **Discard renders** if higher priority updates come in
- **Replay renders** when handling suspense or errors
- **Partially render** components without committing

Your `useMemo` side effects would run during these unstable intermediate states.

## 3. Specific Unexpected Scenarios

### A. Double Invocation in Strict Mode
```javascript
// In development with StrictMode:
function Component() {
  useMemo(() => {
    console.log('Side effect!'); // Logs TWICE!
  }, []);
  // ...
}
```

### B. Concurrent Rendering Interruptions
```javascript
// React might:
// 1. Start rendering
// 2. Run useMemo (side effect executes)
// 3. Pause for higher priority update
// 4. Discard this render entirely
// → Side effect ran but result was never used
```

### C. Unexpected Dependency Changes
```javascript
const [state, setState] = useState(0);

const value = useMemo(() => {
  console.log('Running effect'); // Might log more than expected
  return state * 2;
}, [state]); // React may re-render with same state value
```

## 4. Why This Doesn't Happen with `useEffect`

`useEffect` specifically:
1. Only runs **after commit**
2. Runs exactly **once per completed render**
3. Has **cleanup mechanism** for consistency
4. Respects React's **lifecycle guarantees**

## Practical Example of the Danger

```javascript
function ShoppingCart() {
  const [items, setItems] = useState([]);
  
  // ❌ Dangerous side effect
  const cartTotal = useMemo(() => {
    // This might execute multiple times
    analytics.track('Cart recalculated'); 
    return items.reduce((sum, item) => sum + item.price, 0);
  }, [items]);

  // ✅ Correct approach would be:
  // const cartTotal = useMemo(() => (...), [items]);
  // useEffect(() => { analytics.track(...) }, [cartTotal]);
}
```

## Key Takeaways

1. **Render-phase purity**: React assumes render-phase code (including `useMemo`) is pure
2. **No timing guarantees**: `useMemo` may run at any point during rendering
3. **No completion guarantees**: The render where your side effect ran might be discarded
4. **Performance impact**: Unexpected side effects can trigger additional renders

Always use `useEffect` for side effects to maintain predictable behavior aligned with React's rendering model.


---

# Why `useEffect` Can't Replace `useMemo` (And Vice Versa)

While it's true that `useMemo` might execute multiple times, it serves fundamentally different purposes than `useEffect` that make them non-interchangeable. Here's why you can't simply replace `useMemo` with `useEffect`:

## Core Differences in Purpose

### `useMemo` is for **synchronous value calculation**
- Returns a value immediately during render
- Must complete before the component finishes rendering
- Used for performance optimization

### `useEffect` is for **asynchronous side effects**
- Runs after render is complete
- Doesn't return values to the render flow
- Used for operations that don't block rendering

## Key Problems with Using `useEffect` Instead

### 1. Timing Issues (Race Conditions)
```javascript
// ❌ Can't use useEffect for derived values
function Component({ a, b }) {
  const [sum, setSum] = useState(0);
  
  useEffect(() => {
    setSum(a + b); // Too late! Render already happened
  }, [a, b]);
  
  return <div>{sum}</div>; // Uses stale value on first render
}
```

### 2. Extra Re-renders
```javascript
// ❌ Causes double render
function Component({ items }) {
  const [filtered, setFiltered] = useState([]);
  
  useEffect(() => {
    setFiltered(items.filter(/*...*/)); // Triggers another render
  }, [items]);
  
  // Better with useMemo:
  // const filtered = useMemo(() => items.filter(/*...*/), [items]);
}
```

### 3. Impossible Return Values
```javascript
// ❌ useEffect can't return a value to use in JSX
function Component({ user }) {
  const [fullName, setFullName] = useState('');
  
  useEffect(() => {
    setFullName(`${user.first} ${user.last}`);
  }, [user]);
  
  return <div>{fullName}</div>; // useMemo could do this directly
}
```

## When Each Should Be Used

| Situation | Correct Hook |
|-----------|-------------|
| Calculate derived value | `useMemo` |
| Format complex data | `useMemo` |
| Memoize components/props | `useMemo` |
| API calls | `useEffect` |
| DOM manipulation | `useEffect` |
| Subscriptions | `useEffect` |
| Analytics logging | `useEffect` |

## The Correct Pattern: Combining Both

For cases needing both calculation and side effects:
```javascript
function Component({ data }) {
  // Calculate synchronously
  const processedData = useMemo(() => {
    return expensiveProcessing(data);
  }, [data]);

  // Handle side effects
  useEffect(() => {
    if (processedData) {
      analytics.track('Data processed', processedData);
    }
  }, [processedData]);

  return <Display data={processedData} />;
}
```

## Performance Implications

`useMemo` is critical for:
- Preventing child component re-renders (when passing memoized values)
- Avoiding expensive recalculations
- Maintaining reference equality for dependency arrays

`useEffect` would force these to happen every render, then trigger additional renders when setting state.

## Conclusion

While `useMemo` might run multiple times, it's still essential for:
1. Synchronous value derivation during render
2. Performance optimization
3. Preventing unnecessary child re-renders

React's architecture intentionally separates these concerns - `useMemo` for render-phase calculations, `useEffect` for commit-phase side effects. They're complementary tools, not interchangeable solutions.

---

Here's what happens when React calls your `useMemo` function multiple times, and why it's designed this way:

### The Multi-Call Behavior of `useMemo`

1. **Development Mode (StrictMode)**
    - React intentionally calls your function twice to help detect impurities
    - This only happens in development, not production
    - Example:
      ```javascript
      const value = useMemo(() => {
        console.log('Calculating...'); // Logs twice in dev
        return expensiveCalculation(a, b);
      }, [a, b]);
      ```

2. **Concurrent Rendering Scenarios**
    - React may compute the value but then discard it if:
        - A higher priority update interrupts the render
        - Props/state change during rendering
        - Suspense boundaries trigger fallbacks

3. **Reference Stability Guarantee**
    - Even if called multiple times, React will:
        - Return the same memoized value if dependencies don't change
        - Only expose one consistent value to your component
        - Never show intermediate calculations

### What This Means For Your Code

1. **Pure Functions Required**
    - Your function must be pure (no side effects) because:
      ```javascript
      // ❌ Dangerous - could execute multiple times
      useMemo(() => {
        localStorage.setItem('key', data); // Side effect!
        return data;
      }, [data]);
      ```

2. **Performance Characteristics**
    - The computation cost is paid on each call
    - But the returned value is cached when dependencies are equal
    - Example safe usage:
      ```javascript
      // ✅ Safe pure function
      const sortedList = useMemo(() => {
        return [...largeList].sort((a, b) => a.value - b.value);
      }, [largeList]);
      ```

3. **React's Optimization Logic**
   | Scenario | Calls | Result |
   |----------|-------|--------|
   | First render | 1+ | Caches result |
   | Same deps | 0 | Uses cached value |
   | Changed deps | 1+ | Recomputes |
   | Aborted render | 1+ | Discards result |

### Best Practices

1. **Treat it as a Performance Optimization**
    - Only use for expensive calculations
    - Don't rely on execution count for logic

2. **Assume Multi-Call Possibility**
    - Write idempotent functions
    - Never put side effects inside

3. **Combine with `useEffect` When Needed**
   ```javascript
   const computedValue = useMemo(() => compute(a, b), [a, b]);
   
   useEffect(() => {
     // Side effects based on computedValue here
   }, [computedValue]);
   ```

React's multi-call behavior is intentional - it ensures your components work correctly in concurrent rendering while maintaining reference equality between renders. The key is writing pure functions that can safely run multiple times without side effects.

---

# What Happens When `useMemo` Doesn't Execute Its Function

When React skips calling your `useMemo` function, here's exactly what occurs and why it matters:

## The Skipped Execution Scenario

React will **not** call your `useMemo` function when:
1. Dependencies haven't changed since last render
2. React reuses a previous render result (bailing out of rendering)

## What Actually Happens

1. **Memory Optimization**
    - React returns the **cached value** from previous computation
    - No new calculation occurs
    - Example:
      ```javascript
      const a = 5, b = 10;
      
      // First render - function executes
      const sum1 = useMemo(() => a + b, [a, b]); // 15
      
      // Second render with same a,b - function SKIPPED
      const sum2 = useMemo(() => a + b, [a, b]); // Returns cached 15
      ```

2. **Reference Stability Maintained**
    - The returned object/array maintains identical reference
    - This prevents unnecessary child component re-renders:
      ```javascript
      const config = useMemo(() => ({ color: 'red' }), []);
      // Returns same object reference on subsequent renders
      ```

3. **Performance Benefit Realized**
    - Expensive calculations are avoided
    - No JavaScript execution occurs for the memoized function
    - No new memory allocation (for the return value)

## When This Behavior Matters Most

1. **With Expensive Calculations**
   ```javascript
   // Saves 100ms of computation when dependencies don't change
   const analyticsData = useMemo(() => {
     return processMillionsOfRecords(rawData);
   }, [rawData]);
   ```

2. **When Passing Props to Pure Components**
   ```javascript
   const memoizedProps = useMemo(() => ({ user }), [user]);
   <PureChildComponent config={memoizedProps} /> 
   // Child won't re-render if user reference is stable
   ```

3. **In Context Providers**
   ```javascript
   const contextValue = useMemo(() => ({ theme, user }), [theme, user]);
   // Prevents unnecessary context updates
   ```

## Key Characteristics

| Situation | `useMemo` Behavior |
|-----------|---------------------|
| Dependencies unchanged | Returns cached value |
| First render | Executes function |
| Dependency array empty (`[]`) | Executes once then caches forever |
| New dependencies | Executes and caches new value |

## Why This Is Valuable

1. **Prevents Wasteful Recalculations**
    - Saves CPU cycles on unchanged data
    - Critical for performance-sensitive applications

2. **Maintains Reference Equality**
    - Objects/arrays keep same memory reference
    - Enables cheap equality checks (`===`)

3. **Works With React's Rendering Model**
    - Complements React's reconciliation process
    - Supports concurrent rendering features

Remember: This skipping behavior is the entire purpose of `useMemo` - to avoid unnecessary work when inputs haven't changed. It's what makes it a performance optimization tool rather than just a code organization feature.

