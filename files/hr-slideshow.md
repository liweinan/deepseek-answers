# HackerRank - SlideShow

- [https://www.hackerrank.com/challenges/react-slideshow-1](https://www.hackerrank.com/challenges/react-slideshow-1)

Here's the completed code that meets all the requirements:

```jsx
import React, { useState } from "react";

function Slides({ slides }) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const isFirstSlide = currentIndex === 0;
  const isLastSlide = currentIndex === slides.length - 1;

  const goToNext = () => {
    if (!isLastSlide) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const goToPrev = () => {
    if (!isFirstSlide) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const restart = () => {
    setCurrentIndex(0);
  };

  return (
    <div>
      <div id="navigation" className="text-center">
        <button
          data-testid="button-restart"
          className="small outlined"
          onClick={restart}
          disabled={isFirstSlide}
        >
          Restart
        </button>
        <button
          data-testid="button-prev"
          className="small"
          onClick={goToPrev}
          disabled={isFirstSlide}
        >
          Prev
        </button>
        <button
          data-testid="button-next"
          className="small"
          onClick={goToNext}
          disabled={isLastSlide}
        >
          Next
        </button>
      </div>
      <div id="slide" className="card text-center">
        <h1 data-testid="title">{slides[currentIndex].title}</h1>
        <p data-testid="text">{slides[currentIndex].text}</p>
      </div>
    </div>
  );
}

export default Slides;
```

### Explanation:

1. **State Management**:
    - We use `useState` to track the current slide index (starting at 0 for the first slide).

2. **Navigation Logic**:
    - `goToNext()`: Increments the index if not at the last slide
    - `goToPrev()`: Decrements the index if not at the first slide
    - `restart()`: Resets the index to 0

3. **Button Disabling**:
    - `isFirstSlide` and `isLastSlide` boolean variables help determine when to disable buttons
    - Prev and Restart buttons are disabled on the first slide
    - Next button is disabled on the last slide

4. **Slide Display**:
    - The current slide's title and text are displayed using `slides[currentIndex]`

5. **Data Attributes**:
    - Maintained all the required `data-testid` attributes for testing
    - Kept the original className values for styling

This implementation meets all the specified requirements:
- Shows first slide initially
- Proper button disabling behavior
- Correct navigation between slides
- Restart functionality
- Handles the slides array prop correctly