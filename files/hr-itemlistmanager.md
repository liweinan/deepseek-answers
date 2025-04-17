# HackerRank - Item List Manager

- https://www.hackerrank.com/challenges/item-list-manager

I'll help you complete the `handleAddItem` function to meet the requirements. Here's the fixed code:

```jsx
import { useState } from "react";
import "h8k-components";

import "./App.css";

function App() {
  const [items, setItems] = useState([]);
  const [input, setInput] = useState("");

  const handleAddItem = () => {
    if (input.trim() !== "") {
      setItems([...items, input]);
      setInput("");
    }
  };

  return (
    <>
      <h8k-navbar header="Item List Manager"></h8k-navbar>
      <div className="App">
        <h3>Item List</h3>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter item"
          data-testid="input-field"
        />
        <button onClick={handleAddItem} data-testid="add-button">
          Add Item
        </button>
        <ul data-testid="item-list">
          {items.map((item, index) => (
            <li key={index} data-testid="list-item">
              {item}
            </li>
          ))}
        </ul>
      </div>
    </>
  );
}

export default App;
```

Key changes made:

1. Implemented the `handleAddItem` function to:
    - Check if the input is not empty (using `trim()` to ignore whitespace)
    - Add the input to the items list using the spread operator
    - Clear the input field by setting it to an empty string

2. The function follows all requirements:
    - Initial state shows empty list
    - Input field accepts text
    - Items are added when button is clicked
    - Input field is cleared after adding
    - Empty inputs don't add anything to the list

The rest of the code was already correctly set up with:
- Proper state management for items and input
- Correct rendering of the list using `map`
- Appropriate input field binding
- Proper test IDs for testing purposes