# HackerRank - Contact Form

- https://www.hackerrank.com/challenges/react-contact-form

I'll help you fix the code by implementing the missing form validation and submission logic. Here's the completed solution:

```jsx
import { useState } from "react";
import "./App.css";

import "h8k-components";

function App() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [submittedData, setSubmittedData] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Reset previous error and submission
    setError("");
    setSubmittedData(null);
    
    // Validate inputs
    if (!name || !email || !message) {
      setError("All fields are required.");
      return;
    }
    
    // If validation passes, set submitted data and clear form
    setSubmittedData({ name, email, message });
    setName("");
    setEmail("");
    setMessage("");
  };

  return (
    <>
      <h8k-navbar header="Contact Form"></h8k-navbar>
      <div className="App">
        <h1>Contact Form</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
            data-testid="name-input"
          />
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            data-testid="email-input"
          />
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Message"
            data-testid="message-input"
          />
          <button type="submit" data-testid="submit-button">
            Submit
          </button>
        </form>
        {error && (
          <p data-testid="error-message" className="error">
            {error}
          </p>
        )}
        {submittedData && (
          <div data-testid="submitted-data" className="submitted-data">
            <h2>Submitted Information</h2>
            <p>
              <strong>Name:</strong> {submittedData.name}
            </p>
            <p>
              <strong>Email:</strong> {submittedData.email}
            </p>
            <p>
              <strong>Message:</strong> {submittedData.message}
            </p>
          </div>
        )}
      </div>
    </>
  );
}

export default App;
```

Key changes made:

1. Implemented the `handleSubmit` function to:
    - Prevent default form submission behavior
    - Clear any previous error messages and submission data
    - Validate that all fields (name, email, message) are filled
    - Set an error message if any field is empty
    - If validation passes, store the submitted data and clear the form fields

2. The form now:
    - Shows error messages when validation fails
    - Displays submitted data when validation passes
    - Clears the form after successful submission

3. The validation checks for empty fields using the logical NOT operator (`!`) which will be true for empty strings.

This implementation meets all the requirements specified in the problem statement, including form validation, error handling, submission display, and form clearing after successful submission.