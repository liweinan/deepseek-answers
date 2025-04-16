# HackerRank - Blog Post

- https://www.hackerrank.com/challenges/blog-post

I'll help you complete the React application for the Blog Post according to the requirements. Here's the solution with all three files updated to work together:

1. First, let's modify `Home.js` to manage the state and handle post creation/deletion:

```jsx
import React, { useState } from "react";
import Input from "./Input";
import PostDisplay from "./PostDisplay";

function Home() {
  const [posts, setPosts] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const handleCreatePost = () => {
    if (title.trim() && description.trim()) {
      const newPost = {
        id: Date.now(),
        title,
        description
      };
      setPosts([...posts, newPost]);
      setTitle("");
      setDescription("");
    }
  };

  const handleDeletePost = (id) => {
    setPosts(posts.filter(post => post.id !== id));
  };

  return (
    <div className="text-center ma-20">
      <div className="mb-20">
        <Input 
          title={title} 
          setTitle={setTitle} 
          description={description} 
          setDescription={setDescription} 
        />
        <button 
          data-testid="create-button" 
          className="mt-10"
          onClick={handleCreatePost}
        >
          Create Post
        </button>
      </div>
      <div className="posts-section">
        <PostDisplay posts={posts} onDelete={handleDeletePost} />
      </div>
    </div>
  );
}

export default Home;
```

2. Now, let's update `Input.js` to handle user input:

```jsx
import React from "react";

function Input({ title, setTitle, description, setDescription }) {
  return (
    <div className="layout-column justify-content-center align-items-center">
      <input 
        className="w-100" 
        type="text" 
        placeholder="Enter Title" 
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        data-testid="title-input" 
      />
      <textarea 
        className="mt-10 w-100" 
        placeholder="Enter Description" 
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        data-testid="description-input" 
      />
    </div>
  );
}

export default Input;
```

3. Finally, let's update `PostDisplay.js` to show all posts with delete functionality:

```jsx
import React from "react";

function PostDisplay({ posts, onDelete }) {
  return (
    <div data-testid="posts-container" className="flex wrap gap-10">
      {posts.map(post => (
        <div key={post.id} className="post-box">
          <h3>{post.title}</h3>
          <p>{post.description}</p>
          <button onClick={() => onDelete(post.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
}

export default PostDisplay;
```

This solution meets all the requirements:
1. It has input fields for title and description
2. The Create button adds new posts only when both fields have values
3. Input fields are cleared after successful post creation
4. Posts are displayed in a grid layout (using flex with gap)
5. Each post has a title, description, and delete button
6. Delete button removes the specific post

The styling classes (like `flex wrap gap-10`) suggest you might be using a CSS framework or have predefined styles. Make sure those are properly set up in your project.

The component structure is:
- Home manages the state and passes down props
- Input is a controlled component that receives and updates the form state
- PostDisplay renders the list of posts and handles deletions through callbacks

All the test IDs are preserved as in the original code, so it should pass the unit tests.


---

The error occurs specifically when testing the delete functionality after adding multiple posts. Let's fix this by ensuring the delete operation works correctly and all elements are properly rendered. Here's the complete solution:

1. **Home.js** (updated with proper delete handling):
```jsx
import React, { useState } from "react";
import Input from "./Input";
import PostDisplay from "./PostDisplay";

function Home() {
  const [posts, setPosts] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const handleCreatePost = () => {
    if (title.trim() && description.trim()) {
      const newPost = {
        id: Date.now(),
        title,
        description
      };
      setPosts([...posts, newPost]);
      setTitle("");
      setDescription("");
    }
  };

  const handleDeletePost = (id) => {
    setPosts(prevPosts => prevPosts.filter(post => post.id !== id));
  };

  return (
    <div className="text-center ma-20">
      <div className="mb-20">
        <Input 
          title={title} 
          setTitle={setTitle} 
          description={description} 
          setDescription={setDescription} 
        />
        <button 
          data-testid="create-button" 
          className="mt-10"
          onClick={handleCreatePost}
        >
          Create Post
        </button>
      </div>
      <div className="posts-section">
        <PostDisplay posts={posts} onDelete={handleDeletePost} />
      </div>
    </div>
  );
}

export default Home;
```

2. **Input.js** (unchanged from previous working version):
```jsx
import React from "react";

function Input({ title, setTitle, description, setDescription }) {
  return (
    <div className="layout-column justify-content-center align-items-center">
      <input 
        className="w-100" 
        type="text" 
        placeholder="Enter Title" 
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        data-testid="title-input" 
      />
      <textarea 
        className="mt-10 w-100" 
        placeholder="Enter Description" 
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        data-testid="description-input" 
      />
    </div>
  );
}

export default Input;
```

3. **PostDisplay.js** (updated with proper delete button handling):
```jsx
import React from "react";

function PostDisplay({ posts = [], onDelete = () => {} }) {
  return (
    <div data-testid="posts-container" className="flex wrap gap-10">
      {posts.map(post => (
        <div key={post.id} className="post-box" data-testid={`post-${post.id}`}>
          <h3 data-testid={`post-title-${post.id}`}>{post.title}</h3>
          <p data-testid={`post-description-${post.id}`}>{post.description}</p>
          <button 
            onClick={() => onDelete(post.id)}
            data-testid={`delete-button-${post.id}`}
          >
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}

export default PostDisplay;
```

Key fixes made:
1. Changed the delete handler in Home.js to use the functional update form (`setPosts(prevPosts => ...)`) to ensure we're working with the latest state
2. Added specific data-testids for each post element in PostDisplay.js to help with testing
3. Ensured all components properly handle empty props with default values
4. Maintained proper prop passing between components

The error you're seeing typically occurs when:
- The test tries to access DOM elements that don't exist
- The component structure doesn't match what the test expects
- The delete functionality isn't properly updating the state

This solution should now:
1. Properly add multiple posts
2. Correctly delete specific posts when their delete button is clicked
3. Maintain all other required functionality
4. Pass all test cases including the delete-after-multiple-posts scenario

If you're still seeing issues, it might be helpful to see the specific test case that's failing to provide a more targeted solution. The current implementation matches all the requirements and should handle the delete operation correctly.