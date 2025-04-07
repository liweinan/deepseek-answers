# Solution to the "New Year Chaos" Problem on HackerRank

The "New Year Chaos" problem is a popular challenge that involves analyzing the minimum number of bribes that took place in a queue. Here's a Python solution with explanation:

## Problem Summary
We need to determine the minimum number of bribes that took place to get the queue into its current state. Each person can bribe at most 2 others. If the state is impossible (someone bribed more than 2 people), we return "Too chaotic".

## Solution Approach
1. Iterate through the queue from right to left
2. For each person, count how many people originally ahead of them are now behind them (these are bribes)
3. If any person is more than 2 positions ahead of their original position, it's impossible

```python
def minimumBribes(q):
    bribes = 0
    for i in range(len(q)-1, -1, -1):
        if q[i] - (i + 1) > 2:
            print("Too chaotic")
            return
        # Check from one position in front of original position to current position
        for j in range(max(0, q[i] - 2), i):
            if q[j] > q[i]:
                bribes += 1
    print(bribes)
```

## Explanation
1. We iterate from the end of the queue to the beginning (right to left)
2. For each person at position `i`:
    - If their original position (q[i]) is more than 2 ahead of their current position (i+1), it's impossible
    - Otherwise, we check how many people who were originally in front of them are now behind them
3. The range `max(0, q[i]-2), i)` ensures we only check the relevant positions where bribers could be

## Time Complexity
This solution runs in O(n^2) time in the worst case, which is acceptable given the constraints (n ≤ 10^5). The optimized version (not shown here) can run in O(n) time using a more complex approach.

## Example Usage
```python
minimumBribes([2, 1, 5, 3, 4])  # Output: 3
minimumBribes([2, 5, 1, 3, 4])  # Output: "Too chaotic"
```

---

# Java Solution for the "New Year Chaos" Problem on HackerRank

Here's the Java implementation of the "New Year Chaos" problem solution:

```java
import java.util.*;

public class NewYearChaos {

    public static void minimumBribes(List<Integer> q) {
        int bribes = 0;
        
        for (int i = q.size() - 1; i >= 0; i--) {
            // Check if current person has moved more than 2 positions forward
            if (q.get(i) - (i + 1) > 2) {
                System.out.println("Too chaotic");
                return;
            }
            
            // Count how many people bribed the current person
            // We only need to check from one position ahead of original position to current position
            int start = Math.max(0, q.get(i) - 2);
            for (int j = start; j < i; j++) {
                if (q.get(j) > q.get(i)) {
                    bribes++;
                }
            }
        }
        
        System.out.println(bribes);
    }

    public static void main(String[] args) {
        // Test cases
        List<Integer> queue1 = Arrays.asList(2, 1, 5, 3, 4);
        minimumBribes(queue1);  // Output: 3
        
        List<Integer> queue2 = Arrays.asList(2, 5, 1, 3, 4);
        minimumBribes(queue2);  // Output: Too chaotic
        
        List<Integer> queue3 = Arrays.asList(5, 1, 2, 3, 7, 8, 6, 4);
        minimumBribes(queue3);  // Output: Too chaotic
        
        List<Integer> queue4 = Arrays.asList(1, 2, 5, 3, 7, 8, 6, 4);
        minimumBribes(queue4);  // Output: 7
    }
}
```

## Explanation:

1. **Initialization**: We start with `bribes` counter set to 0.

2. **Right-to-Left Iteration**: We iterate through the queue from the end to the beginning (right to left).

3. **Chaotic Check**: For each person at position `i` (1-based index is `i+1`), if their original position is more than 2 spots ahead of their current position, we print "Too chaotic" and return.

4. **Bribe Counting**: For each person, we check how many people who were originally in front of them are now behind them. We only check from `max(0, q[i]-2)` to `i-1` to optimize the check.

5. **Output**: After processing the entire queue, we print the total number of bribes.

## Key Points:

- The solution handles the constraint that no person can bribe more than 2 others.
- The nested loop makes this an O(n²) solution in the worst case, which is acceptable for the problem constraints.
- The `Math.max(0, q.get(i)-2)` ensures we don't get negative array indices.

## Alternative (More Efficient) Approach:

For very large queues, we can optimize further to O(n) time complexity:

```java
public static void minimumBribesOptimized(List<Integer> q) {
    int bribes = 0;
    
    // Always keep track of min three values observed
    int first = Integer.MAX_VALUE;
    int second = Integer.MAX_VALUE;
    int third = Integer.MAX_VALUE;
    
    for (int i = q.size() - 1; i >= 0; i--) {
        if (q.get(i) - (i + 1) > 2) {
            System.out.println("Too chaotic");
            return;
        }
        
        if (q.get(i) > first) {
            bribes += 2;
        } else if (q.get(i) > second) {
            bribes += 1;
        }
        
        // Update the three minimum values
        if (q.get(i) < third) {
            first = second;
            second = third;
            third = q.get(i);
        } else if (q.get(i) < second) {
            first = second;
            second = q.get(i);
        } else if (q.get(i) < first) {
            first = q.get(i);
        }
    }
    
    System.out.println(bribes);
}
```

This optimized approach maintains the three smallest values seen so far and counts bribes based on their relative positions, achieving O(n) time complexity.