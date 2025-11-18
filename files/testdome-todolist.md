# React Question - Todo List

- https://www.testdome.com/library?page=1&skillArea=48&questionId=107226

Let’s fix the `TodoList` component to meet the requirements. The goal is to implement the `handleItemClick` function in
the `TodoList` component so that:

1. When an item is clicked, the `onItemClick` function is called **only if the item is not marked as done** (
   `item.done === false`).
2. The `onItemClick` function should receive the `item` object as the first parameter and the `event` as the second
   parameter.
3. If the item is marked as done (`item.done === true`), the `onItemClick` function should not be called, and the click
   event should not propagate further (i.e., stop the event from bubbling up to parent elements like the `<ul>`).
4. The `<ul>` has an `onListClick` handler that should still be triggered for non-done items unless explicitly stopped.

### Solution

The key is to use `event.preventDefault()` to control default behavior and `event.stopPropagation()` to prevent the
click event from bubbling up when the item is done. Here's the corrected code for the `handleItemClick` function:

```jsx
const handleItemClick = (item, event) => {
    if (item.done) {
        // If item is done, prevent event propagation
        event.stopPropagation();
    } else {
        // If item is not done, call onItemClick with item and event
        onItemClick(item, event);
    }
};
```

### Explanation of the Fix

- **Check `item.done`**: The function first checks if the item is marked as done (`item.done === true`).
- **If `item.done` is `true`**:
    - Call `event.stopPropagation()` to prevent the click event from bubbling up to parent elements (e.g., the `<ul>`
      with the `onListClick` handler).
    - Do not call `onItemClick`, as required.
- **If `item.done` is `false`**:
    - Call `onItemClick(item, event)` to pass the `item` object and the `event` to the provided `onItemClick` function.
    - Allow the event to propagate normally (e.g., to trigger `onListClick` on the `<ul>`).
- **`preventDefault` not needed**: The requirements don’t specify any default browser behavior to prevent (e.g., no form
  submission or link navigation), so `event.preventDefault()` is not used here.

### Full Corrected Code

Here’s the complete code with the fixed `handleItemClick` function:

```jsx
import React from 'react';
import {createRoot} from 'react-dom/client';

const TodoItem = (props) => <li onClick={props.onClick}>{props.item.text}</li>;

const TodoList = ({items, onListClick, onItemClick}) => {
    const handleItemClick = (item, event) => {
        if (item.done) {
            event.stopPropagation();
        } else {
            onItemClick(item, event);
        }
    };

    return (
        <ul onClick={onListClick}>
            {items.map((item, index) => (
                <TodoItem
                    item={item}
                    key={index}
                    onClick={(event) => handleItemClick(item, event)}
                />
            ))}
        </ul>
    );
};

const items = [
    {text: 'Buy grocery', done: true},
    {text: 'Play guitar', done: false},
    {text: 'Romantic dinner', done: false},
];

const App = (props) => (
    <TodoList
        items={props.items}
        onListClick={(event) => console.log('List clicked!')}
        onItemClick={(item, event) => {
            console.log(item, event);
        }}
    />
);

document.body.innerHTML = "<div id='root'></div>";
const root = createRoot(document.getElementById('root'));

root.render(<App items={items}/>);
```

### How It Works

- **For `done: true` items (e.g., "Buy grocery")**:
    - Clicking the item triggers `handleItemClick`.
    - Since `item.done` is `true`, `event.stopPropagation()` is called, preventing the event from reaching the `<ul>`’s
      `onListClick` handler.
    - `onItemClick` is not called, so nothing is logged for the item click.
    - Result: No console output for `onItemClick`, and "List clicked!" is not logged.

- **For `done: false` items (e.g., "Play guitar", "Romantic dinner")**:
    - Clicking the item triggers `handleItemClick`.
    - Since `item.done` is `false`, `onItemClick(item, event)` is called, logging the item object and event to the
      console.
    - The event propagates to the `<ul>`, triggering `onListClick` and logging "List clicked!".
    - Result: Console shows the item object, event details, and "List clicked!".

### Example Console Output

- Clicking "Buy grocery" (`done: true`):
    - No output (because `onItemClick` is not called and propagation is stopped).

- Clicking "Play guitar" (`done: false`):
  ```
  { text: 'Play guitar', done: false } SyntheticBaseEvent { ... }
  List clicked!
  ```

- Clicking "Romantic dinner" (`done: false`):
  ```
  { text: 'Romantic dinner', done: false } SyntheticBaseEvent { ... }
  List clicked!
  ```

### Notes

- **Key Prop**: Using `index` as the `key` in `items.map` is acceptable here since the list is static. For dynamic
  lists, a unique identifier (e.g., `item.id`) should be used to avoid React rendering issues.
- **Event Propagation**: Stopping propagation for `done` items ensures the `<ul>`’s `onListClick` isn’t triggered, which
  aligns with the requirement to prevent further event handling.
- **Synthetic Events**: The `event` passed to `handleItemClick` is a React `SyntheticEvent`, which is safe to use
  directly in this synchronous context.

This solution fully meets the requirements and handles the event logic correctly. Let me know if you need further
clarification or additional features!