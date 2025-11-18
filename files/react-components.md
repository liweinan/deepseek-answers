# React Component Patterns Reference

This note collects the React component techniques that appeared in the original document and rewrites them in English while preserving all of the technical detail.

---

## 1. When You Must Implement `render()`

`render()` is mandatory for class components and must remain a pure function.

1. **Defining UI for class components**
   ```jsx
   class MyComponent extends React.Component {
     render() {
       return <div>Hello, {this.props.name}</div>;
     }
   }
   ```
   React relies on `render()`; omitting it throws an error.

2. **Overriding the default render flow**  
   When the UI depends on `props`/`state`, override `render()` to return dynamic JSX.
   ```jsx
   class ConditionalComponent extends React.Component {
     render() {
       return this.props.isLoggedIn ? <div>Welcome!</div> : <div>Please log in.</div>;
     }
   }
   ```

3. **Working with `React.PureComponent` or custom `shouldComponentUpdate`**  
   React decides whether to update the DOM based on the value returned from `render()`. If you rely on shallow comparison, the method must be explicit.

4. **Manual invocation (rare)**  
   In tests you may instantiate a component and call `component.render()` to inspect the element tree. This is uncommon in production code.

### When `render()` is not needed

- **Function components** already act as implicit `render()` functions.
- **Hook-based components** return JSX directly, so no explicit `render()` is required.

### Best‑practice reminders

- Keep `render()` pure—no side effects, no direct DOM mutations, no `setState`.
- For performance, pair class components with `PureComponent`, `shouldComponentUpdate`, or switch to function components plus `React.memo`.

---

## 2. `React.Component` vs `React.PureComponent`

### When to choose `React.Component`

- You need the full lifecycle API (`componentDidMount`, `componentDidUpdate`, `componentWillUnmount`, etc.).
- The component manages complex state and you prefer manual control over updates.
- You plan to implement a custom `shouldComponentUpdate`.

Example:
```jsx
class FormComponent extends React.Component {
  state = { name: '', email: '' };

  handleChange = (e) => this.setState({ [e.target.name]: e.target.value });

  render() {
    return (
      <form>
        <input name="name" value={this.state.name} onChange={this.handleChange} />
        <input name="email" value={this.state.email} onChange={this.handleChange} />
      </form>
    );
  }
}
```

### When to choose `React.PureComponent`

- Props/state rarely change or are composed of primitive values.
- You want automatic shallow comparison to short-circuit re-renders.

Example:
```jsx
class ListItem extends React.PureComponent {
  render() {
    return <li>{this.props.text}</li>;
  }
}
```

Limitations: shallow comparison fails if you mutate nested objects; use immutable patterns or implement a custom comparison.

### Summary table

| Aspect | `React.Component` | `React.PureComponent` |
| --- | --- | --- |
| Render optimization | None by default | Shallow comparison of props/state |
| `shouldComponentUpdate` | Must be written manually | Auto‐implemented |
| Best use cases | Complex logic, manual control | Pure display components |
| Data structures | Flexible | Works best with immutable primitives |

### Alternatives

- Prefer function components + Hooks.
- Use `React.memo` for function components that need shallow comparison.

---

## 3. Key APIs Recap

1. **`React.PureComponent`**  
   Adds automatic shallow comparison. Great for lists or presentation components.

2. **`render()`**  
   Must return JSX/React elements, strings, numbers, fragments, arrays, or `null`.

3. **`React.forwardRef`**  
   Forwards a `ref` from a parent component down to a DOM node or child component:
   ```jsx
   const MyInput = React.forwardRef((props, ref) => <input ref={ref} {...props} />);
   ```

4. **`componentDidMount()`**  
   Runs once after mount; good for initial data fetches or DOM operations (e.g., focusing an input).

5. **`componentDidUpdate(prevProps, prevState, snapshot)`**  
   Runs after updates; compare previous values before calling `setState` to avoid loops.

---

## 4. Converting a Class Component to Hooks

Original class version:
```jsx
class Parent extends React.Component {
  inputRef = React.createRef();

  componentDidMount() {
    this.inputRef.current.focus();
  }

  render() {
    return <MyInput ref={this.inputRef} />;
  }
}
```

Hook-based rewrite:
```jsx
import { useRef, useEffect } from 'react';

const MyInput = React.forwardRef((props, ref) => <input ref={ref} {...props} />);

function Parent() {
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return <MyInput ref={inputRef} />;
}
```

### Simplifying `forwardRef`

- If `MyInput` only forwards props to a plain `<input>`, consider using the DOM element directly in the parent.
- When all you need is auto focus, `<input autoFocus />` removes the need for refs entirely.

---

## 5. React Context Essentials

```jsx
import React, { createContext, useContext } from 'react';

const ThemeContext = createContext('light');

export function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Toolbar />
    </ThemeContext.Provider>
  );
}

function Toolbar() {
  const theme = useContext(ThemeContext);
  return <div>Current theme: {theme}</div>;
}
```

### Key facts

- `defaultValue` is used only when there is no matching provider.
- Every `value` change re-renders subscribed consumers; wrap values in `useMemo` to keep references stable.
- Perfect for themes, locale, authentication, or any data that would otherwise require prop drilling.

---

## 6. Context vs Props

| Aspect | Context | Props |
| --- | --- | --- |
| Scope | Global / cross-tree | Parent → child |
| Setup cost | Higher (provider/consumer) | Very low |
| Debugging | Harder (implicit source) | Explicit data source |
| Performance | Provider updates re-render all consumers | Only receivers update |

Guideline: use props for local data and context for cross-cutting concerns. Combine both—context for shared values, props for local configuration.

---

## 7. `onClick` Handler Patterns

1. **Pass a reference**
   ```jsx
   <button onClick={handleClick}>Click</button>
   ```

2. **Arrow function for parameters**
   ```jsx
   <button onClick={() => handleClick('Hello')}>Click</button>
   ```

3. **Inline logic (acceptable for trivial cases)**
   ```jsx
   <button onClick={() => console.log('Clicked!')}>Click</button>
   ```

4. **`bind` (legacy style)**
   ```jsx
   <button onClick={this.handleClick.bind(this, 'Hello')}>Click</button>
   ```

5. **Class fields**
   ```jsx
   handleClick = () => { ... }
   ```

6. **Event object access**
   ```jsx
   function handleClick(event) {
     console.log(event.target);
   }
   ```

Performance tip: avoid recreating functions inside render loops unless you rely on memoization.

---

## 8. Curly Braces in JSX

- Embed expressions: `<h1>Hello, {name}!</h1>`
- Pass props: `<User age={30} />`
- Inline styles: `<div style={{ color: 'red' }} />`
- Render lists: `{items.map(item => <li key={item.id}>{item.label}</li>)}`
- Conditional rendering: `{isLoggedIn ? <Logout /> : <Login />}`
- Default props (class syntax):
  ```jsx
  class Greeting extends React.Component {
    static defaultProps = { name: 'Guest' };
    render() {
      return <h1>Hello, {this.props.name}</h1>;
    }
  }
  ```
- Destructure incoming props: `function Welcome({ name, age }) { ... }`

Remember: everything inside `{}` must be an expression. For object literals, use double braces when writing inline styles.

---

## 9. Passing Props Without Braces

- **String literals**: `<Button title="Click me" />`
- **Number literals**: `<Counter initialValue={5} />` or `<Counter initialValue=5 />`
- **Boolean shorthand**: `<Input disabled />` equals `<Input disabled={true} />`

Braces are still required for variables, expressions, objects, arrays, functions, and JSX values.

---

## 10. Spread Syntax in JSX

JSX spreads follow JavaScript spread semantics but also honor special React props:
```jsx
const props = { className: 'primary', disabled: false };
<Button {...props} />
```

Notes:

- Later spreads override earlier props.
- `key` and `ref` are intercepted by React and not passed as regular props.
- Use spreads judiciously—blindly spreading `this.props` may leak unintended data.

---

## 11. Passing Data Between Components

1. **Plain props**
   ```jsx
   <Child name="Alice" age={25} />
   ```

2. **Destructuring**
   ```jsx
   function Child({ name, age }) { ... }
   ```

3. **Functions as props**
   ```jsx
   function Parent() {
     const handleMessage = (msg) => console.log(msg);
     return <Child onSend={handleMessage} />;
   }
   ```

4. **Objects/arrays**
   ```jsx
   <Child user={{ name: 'Alice', age: 25 }} hobbies={['reading', 'gaming']} />
   ```

5. **Default props**
   ```jsx
   function Child({ name = 'Guest', age = 18 }) { ... }
   ```

6. **Context**
   Use `createContext`/`useContext` to avoid prop drilling for shared data.

7. **`children`**
   ```jsx
   <Card>
     <h1>Title</h1>
     <p>Body</p>
   </Card>
   ```

8. **Hooks/state lifting**
   ```jsx
   function Parent() {
     const [count, setCount] = useState(0);
     return <Child count={count} setCount={setCount} />;
   }
   ```

---

## 12. Renaming `props` and Event Delivery

- `props` is just a parameter name; rename it if needed:
  ```jsx
  function Child(componentProps) {
    return <div>{componentProps.name}</div>;
  }
  ```

- For events, parents pass handlers, and children call them with values:
  ```jsx
  function Child({ onButtonClick }) {
    return <button onClick={() => onButtonClick('Hello!')}>Send</button>;
  }
  ```

- You can forward the native SyntheticEvent along with custom data:
  ```jsx
  <button onClick={(event) => onClick(event, 'extra')}>Click</button>
  ```

- Use `event.persist()` if you need to access the event asynchronously because SyntheticEvents are pooled.

---

## 13. Implicit vs Explicit Event Passing

- **Implicit**: When you pass the handler directly (`onClick={handleClick}`), React automatically supplies the `event` object as the first argument.
- **Explicit**: When you need extra parameters, wrap the handler and call it with `(event, data)` yourself.
- Prefer implicit passing unless additional arguments or custom behavior (preventDefault, stopPropagation) are required.

---

## 14. Additional Notes on `forwardRef`

- If a wrapper component only renders an `<input>` with forwarded props, consider omitting the wrapper and referencing the DOM node directly in the parent.
- When only auto focus is needed, `autoFocus` on the DOM node is the smallest solution.

---

This completes the English rewrite of the original React component notes while preserving every technical recommendation from the source material.

