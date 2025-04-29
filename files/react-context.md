# React.createContext

`React.createContext` 是 React 提供的一个 API，用于创建上下文（Context），以便在组件树中共享数据，而无需通过 props 逐层传递。它是 React 上下文 API 的核心部分，适用于管理全局状态、主题、用户设置等需要在多个组件间共享的数据。

### 基本用法
1. **创建上下文**：
   ```javascript
   const MyContext = React.createContext(defaultValue);
   ```
    - `defaultValue`：上下文的默认值，仅在组件未匹配到任何 `Provider` 时使用。
    - 返回一个对象，包含 `Provider` 和 `Consumer` 两个组件，以及上下文的其他方法（在新版本中，`Consumer` 较少使用，推荐使用 `useContext` 钩子）。

2. **提供上下文（Provider）**：
   使用 `MyContext.Provider` 组件将数据传递给组件树中的子组件。
   ```javascript
   <MyContext.Provider value={/* 共享的数据 */}>
     <ChildComponent />
   </MyContext.Provider>
   ```
    - `value`：要共享的数据，可以是任何类型（对象、数组、函数等）。
    - 每当 `value` 改变时，所有消费该上下文的组件都会重新渲染（除非优化）。

3. **消费上下文**：
   有以下几种方式访问上下文的值：
    - **使用 `useContext` 钩子**（推荐，React 16.8+）：
      ```javascript
      import { useContext } from 'react';
 
      function MyComponent() {
        const value = useContext(MyContext);
        return <div>{value}</div>;
      }
      ```
    - **使用 `Consumer` 组件**（较老的方式）：
      ```javascript
      <MyContext.Consumer>
        {value => <div>{value}</div>}
      </MyContext.Consumer>
      ```
    - **类组件中的 `contextType`**（较少使用）：
      ```javascript
      class MyComponent extends React.Component {
        static contextType = MyContext;
        render() {
          const value = this.context;
          return <div>{value}</div>;
        }
      }
      ```

### 示例
以下是一个简单的主题上下文示例：
```javascript
import React, { createContext, useContext } from 'react';

// 创建上下文
const ThemeContext = createContext('light');

// 提供上下文
function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Toolbar />
    </ThemeContext.Provider>
  );
}

// 消费上下文
function Toolbar() {
  const theme = useContext(ThemeContext);
  return <div>当前主题: {theme}</div>;
}

export default App;
```

### 关键点
- **默认值**：`defaultValue` 只有在组件没有匹配到任何 `Provider` 时生效。
- **性能注意**：每次 `Provider` 的 `value` 变化都会导致消费者组件重新渲染。建议使用 `useMemo` 或其他优化手段来避免不必要的渲染。
- **动态上下文**：可以通过在 `value` 中传递函数或对象来实现动态数据共享。
- **多上下文**：可以嵌套多个上下文，但注意不要过度使用，以免代码复杂化。

### 使用场景
- 全局状态管理（如主题、语言、认证状态）。
- 替代 props 钻透（prop drilling）问题。
- 与状态管理库（如 Redux）结合使用，或作为轻量级状态管理方案。

### 注意事项
- 上下文 API 适合中低复杂度的状态管理，复杂场景可能需要 Redux 或 MobX。
- 确保 `Provider` 的 `value` 引用稳定，避免不必要的重新渲染。
- React 18+ 的 `useContext` 是最推荐的消费方式，简洁且现代化。

更多详细信息可参考 [React 官方文档](https://react.dev/reference/react/createContext)。