# React题 - Logout Wrapper

- https://www.testdome.com/library?page=1&skillArea=48&questionId=132235

Let’s analyze the provided React code and evaluate the statements based on the scenario where `ControlsComponent` is rendered with the `username` prop equal to `"James"`. The goal is to select all correct statements.

### Code Analysis
```jsx
const SecurityContext = React.createContext({ username: "", permissions: [] });

const ControlsComponent = (props) => {
  return (
    <SecurityContext.Provider value={{ username: props.username }}>
      <LogoutWrapper></LogoutWrapper>
    </SecurityContext.Provider>
  );
};

const LogoutWrapper = (props) => {
  var context = React.useContext(SecurityContext);
  return (
    <div>
      <p>{context.username}</p>
      <button>Click here to logout</button>
    </div>
  );
};
```

- **SecurityContext**: A React context created with a default value of `{ username: "", permissions: [] }`.
- **ControlsComponent**: Receives a `username` prop and provides a `SecurityContext` with a value of `{ username: props.username }`. It renders `LogoutWrapper` inside the `SecurityContext.Provider`.
- **LogoutWrapper**: Consumes the `SecurityContext` using `React.useContext(SecurityContext)` and displays the `context.username` in a `<p>` tag.
- **Rendering**: `ControlsComponent` is rendered with `username="James"`.

### Evaluating Each Statement

1. **context.username in the LogoutWrapper will have "James" as its value.**
    - **Analysis**: The `ControlsComponent` wraps `LogoutWrapper` in a `SecurityContext.Provider` with the value `{ username: props.username }`. Since `props.username` is `"James"`, the context value provided is `{ username: "James" }`. In `LogoutWrapper`, `React.useContext(SecurityContext)` retrieves this context, so `context.username` is `"James"`.
    - **Conclusion**: This statement is **correct**.

2. **context.permissions in the LogoutWrapper will have [] as its value.**
    - **Analysis**: The `SecurityContext.Provider` in `ControlsComponent` only specifies `{ username: props.username }`, omitting the `permissions` property. When a partial object is provided to a context, properties not included in the `value` object are not automatically inherited from the default context value (`{ username: "", permissions: [] }`). Thus, `context.permissions` is `undefined` in `LogoutWrapper`, not `[]`.
    - **Conclusion**: This statement is **incorrect**.

3. **When LogoutWrapper has more than one SecurityContext.Provider as an ancestor, the LogoutWrapper will use the context provided by the Provider component which is closer to the root of the element tree.**
    - **Analysis**: In React, when multiple `Provider` components for the same context are nested, the `useContext` hook in a descendant component retrieves the value from the **closest** `Provider` in the component tree (i.e., the one nearest to the component in the hierarchy, not the root). This statement incorrectly suggests that the provider closer to the root is used, which is the opposite of React’s behavior.
    - **Conclusion**: This statement is **incorrect**.

4. **ControlsComponent can declare multiple instances of SecurityContext.Provider.**
    - **Analysis**: There is no restriction in React preventing a component like `ControlsComponent` from rendering multiple `SecurityContext.Provider` components, either nested or sequentially. For example, `ControlsComponent` could be modified to include:
      ```jsx
      <SecurityContext.Provider value={{ username: "James" }}>
        <SecurityContext.Provider value={{ username: "Alice" }}>
          <LogoutWrapper />
        </SecurityContext.Provider>
      </SecurityContext.Provider>
      ```
      This is syntactically valid, and `LogoutWrapper` would use the closest provider’s value (e.g., `{ username: "Alice" }`). The statement is about the ability to declare multiple providers, which is possible.
    - **Conclusion**: This statement is **correct**.

### Final Answer
The correct statements are:
- **context.username in the LogoutWrapper will have "James" as its value.**
- **ControlsComponent can declare multiple instances of SecurityContext.Provider.**

**Answer**: [1, 4]
