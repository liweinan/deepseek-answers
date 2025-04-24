# React中的`preventDefault`和`stopPropagation`

在 React 中，`preventDefault` 是一个事件对象的方法，通常用于阻止浏览器默认行为。例如，点击 `<a>` 标签会跳转页面，提交
`<form>` 表单会刷新页面，通过调用 `event.preventDefault()` 可以阻止这些默认行为。

### 具体含义

- `preventDefault` 是 JavaScript 原生事件对象的方法，React 的事件系统基于此封装。
- 在 React 的事件处理函数中，通过调用 `event.preventDefault()`，可以阻止事件的默认行为，而不影响事件冒泡（若需阻止冒泡，使用
  `stopPropagation`）。
- 常用于表单提交、链接点击、键盘事件等场景。

### 示例代码

#### 阻止表单提交刷新页面

```jsx
function MyForm() {
    const handleSubmit = (event) => {
        event.preventDefault(); // 阻止表单默认提交行为
        console.log("表单提交被拦截");
    };

    return (
        <form onSubmit={handleSubmit}>
            <input type="text"/>
            <button type="submit">提交</button>
        </form>
    );
}
```

#### 阻止链接默认跳转

```jsx
function MyLink() {
    const handleClick = (event) => {
        event.preventDefault(); // 阻止链接默认跳转
        console.log("链接点击被拦截");
    };

    return <a href="https://example.com" onClick={handleClick}>点击我</a>;
}
```

### 注意事项

1. **事件对象**：React 的事件处理函数会接收一个合成事件对象（SyntheticEvent），它的 `preventDefault` 方法与原生 JavaScript
   一致。
2. **异步使用**：React 的合成事件对象在事件处理后会被重用，可能导致异步访问失效。如果需要在异步场景使用 `event`，需先调用
   `event.persist()` 保存事件对象。
   ```jsx
   const handleClick = (event) => {
     event.persist();
     setTimeout(() => {
       console.log(event.type); // 异步访问事件对象
     }, 1000);
   };
   ```
3. **适用场景**：仅对具有默认行为的元素（如 `<form>`、`<a>`、`<input>` 等）有效，无默认行为的事件（如 `onClick` 在 `<div>` 上）调用
   `preventDefault` 无效果。

### 总结

`event.preventDefault()` 在 React 中用于阻止浏览器对事件的默认处理，广泛应用于表单、链接等场景，确保开发者能自定义事件行为。

---

如果在 React 中不调用 `event.preventDefault()`，浏览器会执行事件的**默认行为**
，这可能导致不符合预期或干扰应用逻辑的结果。具体后果取决于事件类型和触发事件的元素。以下是常见场景及不调用 `preventDefault`
的影响：

### 1. **表单提交（`<form>` 的 `onSubmit` 事件）**

- **默认行为**：浏览器会提交表单，通常触发页面刷新或跳转到表单的 `action` 属性指定的 URL。
- **后果**：
    - 页面刷新会导致 React 组件状态丢失，单页应用（SPA）的体验被破坏。
    - 如果未指定 `action`，可能跳转到当前页面 URL，依然引发刷新。
- **示例**：
  ```jsx
  function MyForm() {
    const handleSubmit = (event) => {
      // 不调用 event.preventDefault()
      console.log("表单提交");
    };
  
    return (
      <form onSubmit={handleSubmit}>
        <input type="text" />
        <button type="submit">提交</button>
      </form>
    );
  }
  ```
  点击提交按钮后，页面会刷新，`console.log` 可能因刷新而看不到。

### 2. **链接点击（`<a>` 的 `onClick` 事件）**

- **默认行为**：浏览器会导航到 `<a>` 标签的 `href` 属性指定的 URL。
- **后果**：
    - 用户被带离当前页面，React 应用的路由机制（如 `react-router`）无法接管导航。
    - 单页应用的客户端路由失效，页面可能完全重新加载。
- **示例**：
  ```jsx
  function MyLink() {
    const handleClick = (event) => {
      // 不调用 event.preventDefault()
      console.log("链接被点击");
    };
  
    return <a href="https://example.com" onClick={handleClick}>点击我</a>;
  }
  ```
  点击链接后，浏览器会跳转到 `https://example.com`，React 应用的状态丢失。

### 3. **键盘事件（如 `<input>` 的 `onKeyDown`）**

- **默认行为**：某些按键可能触发浏览器默认行为，例如按下 `Enter` 提交表单，或按下 `Space` 滚动页面。
- **后果**：
    - 未阻止默认行为可能导致意外的用户体验，如输入框中按 `Enter` 意外提交表单。
- **示例**：
  ```jsx
  function MyInput() {
    const handleKeyDown = (event) => {
      // 不调用 event.preventDefault()
      console.log("按键:", event.key);
    };
  
    return <input onKeyDown={handleKeyDown} />;
  }
  ```
  如果 `<input>` 在 `<form>` 内，按 `Enter` 可能触发表单提交，导致页面刷新。

### 4. **其他事件**

- **拖放事件**：不阻止默认行为可能导致浏览器执行文件打开等操作。
- **右键菜单**：不阻止 `onContextMenu` 的默认行为会显示浏览器默认上下文菜单。
- **鼠标滚轮**：不阻止 `onWheel` 的默认行为可能导致页面滚动。

### 为什么需要 `preventDefault`？

React 应用通常是单页应用（SPA），依赖客户端逻辑处理路由、表单提交等操作。浏览器的默认行为（如页面刷新、跳转）会打断 React 的虚拟
DOM 和状态管理，破坏用户体验。调用 `preventDefault` 允许开发者接管这些行为，自定义逻辑（如通过 AJAX 提交表单、使用
`react-router` 导航等）。

### 例外情况

- 如果事件没有默认行为（如 `onClick` 在 `<div>` 上），不调用 `preventDefault` 不会有任何影响。
- 如果开发者希望保留默认行为（如允许表单提交到后端或链接跳转），可以故意不调用 `preventDefault`。

### 总结

不调用 `event.preventDefault()` 会导致浏览器执行事件的默认行为，可能引发页面刷新、跳转或其他意外效果，破坏 React
应用的逻辑和用户体验。为避免这些问题，通常在需要自定义行为的场景（如表单提交、链接点击）调用 `preventDefault` 来阻止默认行为。

---

# 在 JavaScript 和 React 中，`event.stopPropagation()` 是一个事件对象的方法，用于**阻止事件继续向上冒泡
**（或向下捕获），从而防止事件触发父元素或其他祖先元素上的同类型事件监听器。以下是对
`event.stopPropagation()` 的详细介绍，包括其用法、场景和注意事项。

---

### 1. **事件冒泡和捕获**

在 DOM 事件模型中，事件传播分为三个阶段：

- **捕获阶段**（Capture Phase）：事件从 `window` 开始，逐级向下传递到目标元素的父元素。
- **目标阶段**（Target Phase）：事件到达目标元素，触发目标元素上的事件监听器。
- **冒泡阶段**（Bubble Phase）：事件从目标元素逐级向上传播到 `window`，触发沿途祖先元素的事件监听器。

默认情况下，大多数事件（如 `click`、`submit` 等）会进行**冒泡**，即触发目标元素后，事件会继续传播到父元素，触发父元素的同类型事件监听器。
`event.stopPropagation()` 可以阻止这种传播。

---

### 2. **event.stopPropagation() 的作用**

- **阻止事件冒泡**：调用 `event.stopPropagation()` 后，事件不会继续向上传播到父元素，父元素上的同类型事件监听器不会被触发。
- **不影响当前监听器**：`stopPropagation` 只阻止事件传播到其他元素，不会影响当前元素的事件处理逻辑。
- **不阻止默认行为**：与 `event.preventDefault()` 不同，`stopPropagation` 不会阻止浏览器的默认行为（如表单提交、链接跳转）。如果需要阻止默认行为，必须单独调用
  `preventDefault()`。

---

### 3. **用法**

在事件处理函数中，调用 `event.stopPropagation()` 来阻止事件冒泡。以下是基本用法：

#### JavaScript 示例

```javascript
document.querySelector('.child').addEventListener('click', (event) => {
    console.log('Child clicked');
    event.stopPropagation(); // 阻止事件冒泡
});

document.querySelector('.parent').addEventListener('click', () => {
    console.log('Parent clicked');
});
```

```html

<div class="parent">
    <button class="child">Click me</button>
</div>
```

- **行为**：点击按钮时，只输出 `Child clicked`，因为 `event.stopPropagation()` 阻止了事件冒泡到 `.parent`，所以
  `Parent clicked` 不会输出。

#### React 示例

在 React 中，事件处理函数接收的是 `SyntheticEvent`（React 封装的事件对象），但 `stopPropagation` 的用法与原生 JavaScript 相同。

```jsx
function MyComponent() {
    const handleChildClick = (event) => {
        console.log('Child clicked');
        event.stopPropagation(); // 阻止事件冒泡
    };

    const handleParentClick = () => {
        console.log('Parent clicked');
    };

    return (
        <div onClick={handleParentClick}>
            <button onClick={handleChildClick}>Click me</button>
        </div>
    );
}
```

- **行为**：点击按钮时，只输出 `Child clicked`，父 `<div>` 的 `onClick` 不会触发。

---

### 4. **常见使用场景**

`event.stopPropagation()` 常用于以下场景：

#### a. **防止父元素事件触发**

当子元素和父元素都有事件监听器，但希望子元素的事件处理独立完成，不触发父元素的事件时，使用 `stopPropagation`。

- 示例：在一个 Todo 列表中，点击列表项标记为完成，但不触发列表容器的事件（如选择整个列表）。

```jsx
const TodoList = ({items}) => {
    const handleItemClick = (item, event) => {
        event.stopPropagation(); // 防止触发父元素的点击事件
        console.log(`Item ${item.text} clicked`);
    };

    const handleListClick = () => {
        console.log('List clicked');
    };

    return (
        <ul onClick={handleListClick}>
            {items.map((item) => (
                <li key={item.id} onClick={(e) => handleItemClick(item, e)}>
                    {item.text}
                </li>
            ))}
        </ul>
    );
};
```

#### b. **嵌套组件的独立行为**

在复杂的 UI 结构中，子组件可能需要处理自己的事件，而不影响父组件的逻辑。例如，点击弹窗中的按钮关闭弹窗，但不触发页面上的点击事件。

#### c. **自定义事件逻辑**

当你希望事件仅在特定条件下传播，或者需要完全控制事件流时，`stopPropagation` 提供了一种机制来限制事件的传播范围。

---

### 5. **与 preventDefault 的区别**

| 方法                        | 作用                    | 示例场景              |
|---------------------------|-----------------------|-------------------|
| `event.preventDefault()`  | 阻止浏览器默认行为（如表单提交、链接跳转） | 阻止表单刷新页面          |
| `event.stopPropagation()` | 阻止事件冒泡或捕获到其他元素        | 阻止子元素点击触发父元素的点击事件 |

**组合使用**：在某些场景下，可能需要同时使用两者。例如，在一个表单内的按钮点击时，既阻止表单提交（`preventDefault`），又阻止事件冒泡（
`stopPropagation`）。

```jsx
const handleClick = (event) => {
    event.preventDefault(); // 阻止默认行为
    event.stopPropagation(); // 阻止事件冒泡
    console.log('Button clicked');
};
```

---

### 6. **注意事项**

1. **React 的 SyntheticEvent**：
    - 在 React 中，`event` 是 `SyntheticEvent` 对象，`stopPropagation` 的行为与原生事件一致。
    - 如果在异步代码中访问 `event`（如 `setTimeout`），需要先调用 `event.persist()`，否则 `SyntheticEvent` 可能被重用，导致属性不可访问。
   ```jsx
   const handleClick = (event) => {
     event.persist();
     setTimeout(() => {
       event.stopPropagation(); // 异步场景下需 persist
     }, 1000);
   };
   ```

2. **捕获阶段**：
    - 默认情况下，事件监听器在冒泡阶段触发。如果监听器在捕获阶段（通过 `addEventListener` 的第三个参数设置为 `true` 或
      React 的 `onClickCapture`），`stopPropagation` 也可以阻止捕获阶段的进一步传播。
   ```jsx
   <div onClickCapture={(e) => e.stopPropagation()}>
     <button onClick={() => console.log('Button clicked')}>Click</button>
   </div>
   ```
    - 按钮的 `onClick` 不会触发，因为捕获阶段的事件已被阻止。

3. **谨慎使用**：
    - 过度使用 `stopPropagation` 可能导致事件流变得难以调试，特别是在复杂组件树中。
    - 确保只在必要时阻止冒泡，以避免意外破坏父元素的事件处理逻辑。

4. **不影响其他监听器**：
    - `stopPropagation` 不会阻止同一元素上的其他同类型事件监听器触发。例如，同一个 `<div>` 上绑定了多个 `onClick` 监听器，
      `stopPropagation` 只影响父元素的监听器。

5. **与 `stopImmediatePropagation` 的区别**（原生 JS）：
    - `event.stopImmediatePropagation()` 不仅阻止冒泡，还阻止同一元素上的其他同类型监听器触发。
    - React 的 `SyntheticEvent` 也支持此方法，但使用较少。

---

### 7. **结合你的 TodoList 问题**

在你的 TodoList 组件中，`event.stopPropagation()` 用于当 `item.done` 为 `true` 时，阻止点击事件冒泡到 `<ul>` 的
`onListClick` 监听器：

```jsx
const handleItemClick = (item, event) => {
    if (item.done) {
        event.stopPropagation(); // 阻止事件冒泡到 <ul> 的 onListClick
    } else {
        onItemClick(item, event); // 调用 onItemClick
    }
};
```

- **效果**：
    - 当点击 `done: true` 的项（如 "Buy grocery"），`onListClick` 不会触发，`onItemClick` 也不会调用。
    - 当点击 `done: false` 的项（如 "Play guitar"），`onItemClick` 触发，且事件冒泡到 `<ul>`，触发 `onListClick`。

---

### 8. **总结**

- **`event.stopPropagation()`** 阻止事件冒泡（或捕获），防止触发父元素的事件监听器。
- **适用场景**：控制事件传播，隔离子组件事件，防止父元素意外触发。
- **React 特点**：与原生 JS 一致，但注意 `SyntheticEvent` 的异步使用需 `event.persist()`。
- **注意**：仅阻止传播，不影响默认行为（需用 `preventDefault`），谨慎使用以避免复杂的事件流问题。

如果有其他关于 `stopPropagation` 或 React 事件的疑问，请随时告诉我！