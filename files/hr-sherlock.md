# Java Problem - Sherlock and the Valid String

- https://www.hackerrank.com/challenges/one-month-preparation-kit-sherlock-and-valid-string

Let's solve this problem. The task is to determine if a string is valid based on Sherlock's criteria: all characters
must appear the same number of times, or removing exactly one character makes it so. Here's the solution:

```java
class Result {

    public static String isValid(String s) {
        // Create frequency map for characters
        Map<Character, Integer> freq = new HashMap<>();
        for (char c : s.toCharArray()) {
            freq.put(c, freq.getOrDefault(c, 0) + 1);
        }

        // Get set of frequencies
        Set<Integer> frequencies = new HashSet<>(freq.values());

        // If all characters have same frequency, string is valid
        if (frequencies.size() == 1) {
            return "YES";
        }

        // If more than two different frequencies, can't be valid by removing one
        if (frequencies.size() > 2) {
            return "NO";
        }

        // Get the two different frequencies
        Integer[] freqArray = frequencies.toArray(new Integer[0]);
        int f1 = freqArray[0];
        int f2 = freqArray[1];

        // Count how many characters have each frequency
        int countF1 = 0, countF2 = 0;
        for (int f : freq.values()) {
            if (f == f1) countF1++;
            else countF2++;
        }

        // Check if removing one character can make all frequencies equal
        // Case 1: One character appears once and others have same frequency
        if ((f1 == 1 && countF1 == 1) || (f2 == 1 && countF2 == 1)) {
            return "YES";
        }

        // Case 2: One character appears one more time than others
        if ((f1 == f2 + 1 && countF1 == 1) || (f2 == f1 + 1 && countF2 == 1)) {
            return "YES";
        }

        return "NO";
    }
}
```

This solution works as follows:

1. Create a frequency map to count occurrences of each character.

2. Get the set of frequencies from the map values.

3. If there's only one frequency (all characters appear the same number of times), return "YES".

4. If there are more than two different frequencies, it's impossible to make the string valid by removing one character,
   so return "NO".

5. For exactly two different frequencies:
    - Count how many characters have each frequency
    - Check two valid cases:
      a. One character appears once (frequency=1) and all others have the same frequency
      b. One character appears one more time than all others (frequency difference=1)
    - In either case, removing one occurrence of that character makes all frequencies equal

6. If none of these conditions are met, return "NO".

The solution handles all the example cases:

- "abc" → "YES" (all characters appear once)
- "abcc" → "YES" (can remove one 'c' to get equal frequencies)
- "abccc" → "YES" (can remove one 'c' to get equal frequencies)
- "aabbcd" → "NO" (requires removing two characters)

The code is efficient with O(n) time complexity, where n is the length of the string, and meets all the constraints (
string length up to 10^5, lowercase ASCII characters).

---

Let's analyze the time and space complexity of the provided solution:

### **Time Complexity: O(n)**

- **Building the frequency map**: Iterating through the string `s` of length `n` to create the frequency map takes
  `O(n)` time, as each character is processed once.
- **Creating the set of frequencies**: Converting the values of the frequency map to a `HashSet` takes `O(k)` time,
  where `k` is the number of unique characters (at most 26 for lowercase ASCII letters, so effectively constant).
- **Checking the size of the frequency set**: Operations like checking `frequencies.size()` are `O(1)`.
- **Converting frequencies to an array**: Creating an array from the set of frequencies is `O(1)` since the set size is
  at most 2 (or constant in practice due to the limited character set).
- **Counting frequencies**: Iterating through the values of the frequency map to count how many characters have each
  frequency takes `O(k)`, where `k` is the number of unique characters (again, effectively constant as `k ≤ 26`).
- **Final checks**: The conditional checks (e.g., comparing frequencies, counts) are `O(1)`.

The dominant step is building the frequency map, which is `O(n)`. All other steps are either constant or bounded by a
small constant (due to the limited character set), so the overall time complexity is **O(n)**.

### **Space Complexity: O(k)**

- **Frequency map**: The `HashMap` stores at most `k` entries, where `k` is the number of unique characters in the
  string. Since the input is constrained to lowercase ASCII letters (a-z), `k ≤ 26`, making this effectively `O(1)`.
- **Set of frequencies**: The `HashSet` stores at most two frequencies (or a small constant number in practice), so this
  is `O(1)`.
- **Array of frequencies**: The array created from the set of frequencies is also `O(1)` (at most two elements).
- **Other variables**: Variables like `countF1`, `countF2`, `f1`, and `f2` use `O(1)` space.

Since `k` is bounded by a constant (26), the space complexity is effectively **O(1)**. However, in a general case where
the character set size isn't constrained, it would be **O(k)**, where `k` is the number of unique characters.

### **Summary**

- **Time Complexity**: **O(n)**, where `n` is the length of the input string.
- **Space Complexity**: **O(1)** (or **O(k)** in the general case, where `k` is the number of unique characters, but
  effectively constant due to the problem's constraint of lowercase ASCII letters).

This makes the solution efficient for the given constraints (`1 ≤ |s| ≤ 10^5`).