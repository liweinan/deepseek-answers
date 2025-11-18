# React's `preventDefault` and `stopPropagation`

In React, `preventDefault` is a method of the event object, typically used to prevent browser default behaviors. For example, clicking an `<a>` tag navigates to a page, submitting a `<form>` refreshes the page - calling `event.preventDefault()` can prevent these default behaviors.

### Specific Meaning

- `preventDefault` is a native JavaScript event object method, React's event system is built on top of this with encapsulation.
- In React's event handlers, calling `event.preventDefault()` prevents the default behavior of the event without affecting event bubbling (use `stopPropagation` to prevent bubbling).
- Commonly used in scenarios like form submission, link clicks, keyboard events, etc.

### Example Code

#### Prevent form submission from refreshing the page

```jsx
function MyForm() {
    const handleSubmit = (event) => {
        event.preventDefault(); // Prevent form's default submission behavior
        console.log("Form submission intercepted");
    };

    return (
        <form onSubmit={handleSubmit}>
            <input type="text"/>
            <button type="submit">Submit</button>
        </form>
    );
}
```

#### Prevent link default navigation

```jsx
function MyLink() {
    const handleClick = (event) => {
        event.preventDefault(); // Prevent link's default navigation
        console.log("Link click intercepted");
    };

    return <a href="https://example.com" onClick={handleClick}>Click me</a>;
}
```

### Considerations

1. **Event object**: React's event handlers receive a synthetic event object (SyntheticEvent), whose `preventDefault` method is consistent with native JavaScript.
2. **Asynchronous usage**: React's synthetic event objects are reused after event handling, which may cause asynchronous access to fail. If you need to use `event` in asynchronous scenarios, call `event.persist()` first to save the event object.
   ```jsx
   const handleClick = (event) => {
     event.persist();
     setTimeout(() => {
       console.log(event.type); // Asynchronously access event object
     }, 1000);
   };
   ```
3. **Applicable scenarios**: Only effective for elements with default behaviors (like `<form>`, `<a>`, `<input>`, etc.). Calling `preventDefault` on events without default behaviors (like `onClick` on `<div>`) has no effect.

### Summary

`event.preventDefault()` in React is used to prevent the browser's default handling of events, widely used in scenarios like forms and links, ensuring developers can customize event behaviors.

---

If you don't call `event.preventDefault()` in React, the browser will execute the event's **default behavior**, which may lead to unexpected results or interfere with application logic. Here are the impacts of not calling `preventDefault` in common scenarios:

### 1. **Form submission (`<form>`'s `onSubmit` event)**

- **Default behavior**: The browser submits the form, typically triggering page refresh or navigation to the URL specified in the form's `action` attribute.
- **Consequences**:
    - Page refresh causes React component state loss, breaking single-page application (SPA) experience.
    - If no `action` is specified, it may navigate to the current page URL, still causing a refresh.
- **Example**:
  ```jsx
  function MyForm() {
    const handleSubmit = (event) => {
      // Don't call event.preventDefault()
      console.log("Form submitted");
    };
  
    return (
      <form onSubmit={handleSubmit}>
        <input type="text" />
        <button type="submit">Submit</button>
      </form>
    );
  }
  ```
  After clicking submit, the page refreshes, and you might not see the `console.log` due to the refresh.

### 2. **Link click (`<a>`'s `onClick` event)**

- **Default behavior**: The browser navigates to the URL specified in the `<a>` tag's `href` attribute.
- **Consequences**:
    - Users are taken away from the current page, React application's routing mechanism (like `react-router`) cannot take over navigation.
    - Single-page application's client-side routing fails, page may completely reload.
- **Example**:
  ```jsx
  function MyLink() {
    const handleClick = (event) => {
      // Don't call event.preventDefault()
      console.log("Link clicked");
    };
  
    return <a href="https://example.com" onClick={handleClick}>Click me</a>;
  }
  ```
  After clicking the link, the browser navigates to `https://example.com`, React application state is lost.

### 3. **Keyboard events (like `<input>`'s `onKeyDown`)**

- **Default behavior**: Some keys may trigger browser default behaviors, like pressing `Enter` submits the form, or pressing `Space` scrolls the page.
- **Consequences**:
    - Not preventing default behavior may cause unexpected user experience, like pressing `Enter` in an input field unexpectedly submits the form.
- **Example**:
  ```jsx
  function MyInput() {
    const handleKeyDown = (event) => {
      // Don't call event.preventDefault()
      console.log("Key pressed:", event.key);
    };
  
    return <input onKeyDown={handleKeyDown} />;
  }
  ```
  If the `<input>` is inside a `<form>`, pressing `Enter` may trigger form submission, causing page refresh.

### 4. **Other events**

- **Drag and drop events**: Not preventing default behavior may cause the browser to perform operations like file opening.
- **Right-click menu**: Not preventing `onContextMenu`'s default behavior shows the browser's default context menu.
- **Mouse wheel**: Not preventing `onWheel`'s default behavior may cause page scrolling.

### Why need `preventDefault`?

React applications are typically single-page applications (SPAs) that rely on client-side logic to handle routing, form submission, etc. The browser's default behaviors (like page refresh, navigation) interrupt React's virtual DOM and state management, breaking user experience. Calling `preventDefault` allows developers to take over these behaviors and customize logic (like submitting forms via AJAX, using `react-router` for navigation, etc.).

### Exceptions

- If the event has no default behavior (like `onClick` on `<div>`), not calling `preventDefault` has no effect.
- If developers want to preserve default behavior (like allowing form submission to backend or link navigation), they can intentionally not call `preventDefault`.

### Summary

Not calling `event.preventDefault()` causes the browser to execute the event's default behavior, which may trigger page refresh, navigation, or other unexpected effects, breaking React application's logic and user experience. To avoid these issues, typically call `preventDefault` in scenarios requiring custom behavior (like form submission, link clicks) to prevent default behaviors.

---

# In JavaScript and React, `event.stopPropagation()` is a method of the event object used to **prevent the event from continuing to bubble up** (or capture down), thereby preventing the event from triggering the same type of event listeners on parent elements or other ancestor elements. Below is a detailed introduction to `event.stopPropagation()`, including its usage, scenarios, and considerations.

---

### 1. **Event Bubbling and Capturing**

In the DOM event model, event propagation is divided into three phases:

- **Capture Phase**: Events start from `window` and propagate down to the parent element of the target element level by level.
- **Target Phase**: Events reach the target element, triggering event listeners on the target element.
- **Bubble Phase**: Events propagate up from the target element to `window` level by level, triggering event listeners on ancestor elements along the way.

By default, most events (like `click`, `submit`, etc.) will **bubble**, meaning after triggering the target element, the event continues to propagate to parent elements, triggering the same type of event listeners on parent elements. `event.stopPropagation()` can prevent this propagation.

---

### 2. **The role of event.stopPropagation()**

- **Prevent event bubbling**: After calling `event.stopPropagation()`, the event won't continue to propagate up to parent elements, and the same type of event listeners on parent elements won't be triggered.
- **Doesn't affect current listener**: `stopPropagation` only prevents event propagation to other elements, it doesn't affect the current element's event handling logic.
- **Doesn't prevent default behavior**: Unlike `event.preventDefault()`, `stopPropagation` doesn't prevent browser default behaviors (like form submission, link navigation). If you need to prevent default behavior, you must call `preventDefault()` separately.

---

### 3. **Usage**

In event handlers, call `event.stopPropagation()` to prevent event bubbling. Here are the basic usages:

#### JavaScript Example

```javascript
document.querySelector('.child').addEventListener('click', (event) => {
    console.log('Child clicked');
    event.stopPropagation(); // Prevent event bubbling
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

- **Behavior**: When clicking the button, only output `Child clicked`, because `event.stopPropagation()` prevents event bubbling to `.parent`, so `Parent clicked` won't be output.

#### React Example

In React, event handlers receive `SyntheticEvent` (React's encapsulated event object), but the usage of `stopPropagation` is the same as native JavaScript.

```jsx
function MyComponent() {
    const handleChildClick = (event) => {
        console.log('Child clicked');
        event.stopPropagation(); // Prevent event bubbling
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

- **Behavior**: When clicking the button, only output `Child clicked`, the parent `<div>`'s `onClick` won't be triggered.

---

### 4. **Common Usage Scenarios**

`event.stopPropagation()` is commonly used in the following scenarios:

#### a. **Prevent parent element events from triggering**

When both child and parent elements have event listeners, but you want the child element's event handling to be independent and not trigger the parent element's events, use `stopPropagation`.

- Example: In a Todo list, clicking a list item marks it as complete, but doesn't trigger the list container's event (like selecting the entire list).

```jsx
const TodoList = ({items}) => {
    const handleItemClick = (item, event) => {
        event.stopPropagation(); // Prevent triggering parent element's click event
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

#### b. **Independent behavior of nested components**

In complex UI structures, child components may need to handle their own events without affecting parent component logic. For example, clicking a button in a modal closes the modal, but doesn't trigger click events on the page.

#### c. **Custom event logic**

When you want events to propagate only under specific conditions, or need complete control over the event flow, `stopPropagation` provides a mechanism to limit the scope of event propagation.

---

### 5. **Difference from preventDefault**

| Method                        | Role                                                                 | Example Scenario                                      |
|---------------------------|----------------------------------------------------------------------|---------------------------------------------------|
| `event.preventDefault()`  | Prevents browser default behaviors (like form submission, link navigation) | Preventing form from refreshing page                      |
| `event.stopPropagation()` | Prevents event bubbling or capturing to other elements                    | Preventing child element click from triggering parent click event |

**Combined usage**: In some scenarios, you may need to use both. For example, when clicking a button inside a form, you might want to both prevent form submission (`preventDefault`) and prevent event bubbling (`stopPropagation`).

```jsx
const handleClick = (event) => {
    event.preventDefault(); // Prevent default behavior
    event.stopPropagation(); // Prevent event bubbling
    console.log('Button clicked');
};
```

---

### 6. **Considerations**

1. **React's SyntheticEvent**:
    - In React, `event` is a `SyntheticEvent` object, and the behavior of `stopPropagation` is consistent with native events.
    - If you need to access `event` in asynchronous code (like `setTimeout`), you need to call `event.persist()` first, otherwise `SyntheticEvent` may be reused, making properties inaccessible.
   ```jsx
   const handleClick = (event) => {
     event.persist();
     setTimeout(() => {
       event.stopPropagation(); // Need persist in asynchronous scenarios
     }, 1000);
   };
   ```

2. **Capture phase**:
    - By default, event listeners trigger during the bubble phase. If the listener is in the capture phase (set through the third parameter of `addEventListener` as `true` or React's `onClickCapture`), `stopPropagation` can also prevent further propagation during the capture phase.
   ```jsx
   <div onClickCapture={(e) => e.stopPropagation()}>
     <button onClick={() => console.log('Button clicked')}>Click</button>
   </div>
   ```
    - The button's `onClick` won't trigger because the capture phase event has been prevented.

3. **Use with caution**:
    - Overusing `stopPropagation` may make event flows difficult to debug, especially in complex component trees.
    - Ensure you only prevent bubbling when necessary to avoid accidentally breaking parent element event handling logic.

4. **Doesn't affect other listeners**:
    - `stopPropagation` won't prevent other same-type event listeners on the same element from triggering. For example, if the same `<div>` has multiple `onClick` listeners, `stopPropagation` only affects parent element listeners.

5. **Difference from `stopImmediatePropagation`** (native JS):
    - `event.stopImmediatePropagation()` not only prevents bubbling but also prevents other same-type listeners on the same element from triggering.
    - React's `SyntheticEvent` also supports this method, but it's rarely used.

---

### 7. **Combining with your TodoList question**

In your TodoList component, `event.stopPropagation()` is used when `item.done` is `true` to prevent the click event from bubbling to the `<ul>`'s `onListClick` listener:

```jsx
const handleItemClick = (item, event) => {
    if (item.done) {
        event.stopPropagation(); // Prevent event bubbling to <ul>'s onListClick
    } else {
        onItemClick(item, event); // Call onItemClick
    }
};
```

- **Effect**:
    - When clicking an item with `done: true` (like "Buy grocery"), `onListClick` won't trigger, and `onItemClick` won't be called either.
    - When clicking an item with `done: false` (like "Play guitar"), `onItemClick` triggers, and the event bubbles to `<ul>`, triggering `onListClick`.

---

### 8. **Summary**

- **`event.stopPropagation()`** prevents event bubbling (or capturing), preventing parent element event listeners from being triggered.
- **Applicable scenarios**: Controlling event propagation, isolating child component events, preventing parent elements from being accidentally triggered.
- **React features**: Consistent with native JS, but note that `SyntheticEvent` requires `event.persist()` for asynchronous use.
- **Note**: Only prevents propagation, doesn't affect default behavior (use `preventDefault` for that), use with caution to avoid complex event flow issues.

If you have other questions about `stopPropagation` or React events, please let me know!