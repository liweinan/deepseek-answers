# TestDome - Java题 - Song

- https://www.testdome.com/library?page=1&skillArea=30&questionId=88836 

To determine if a playlist is repeating, we need to detect whether there’s a cycle in the linked list of songs, where a song points back to a previous song. A playlist is repeating if such a cycle exists; otherwise, it ends at a song with `nextSong` set to `null`. The most efficient way to detect a cycle in a linked list is by using Floyd’s Cycle-Finding Algorithm (also known as the "tortoise and hare" algorithm), which has a time complexity of O(n) and a space complexity of O(1).

### Explanation of the Approach
- **Floyd’s Cycle-Finding Algorithm**: Use two pointers, a "slow" pointer that moves one step at a time and a "fast" pointer that moves two steps at a time. If there’s a cycle, these pointers will eventually meet at some node. If there’s no cycle, the fast pointer will reach a `null` node.
- **Edge Cases**:
    - If the playlist is empty or has only one song with no next song (`nextSong == null`), it’s not repeating.
    - If a song points to itself or forms a cycle with other songs, it’s repeating.
- **Implementation**: In the `isInRepeatingPlaylist` method, apply Floyd’s algorithm to traverse the playlist and check for a cycle.

### Solution
Here’s the implementation of the `isInRepeatingPlaylist` method:

```java
public class Song {
    private String name;
    private Song nextSong;

    public Song(String name) {
        this.name = name;
    }

    public void setNextSong(Song nextSong) {
        this.nextSong = nextSong;
    }

    public boolean isInRepeatingPlaylist() {
        // Handle edge case: if no next song, playlist cannot be repeating
        if (this.nextSong == null) {
            return false;
        }

        // Initialize slow and fast pointers
        Song slow = this;
        Song fast = this.nextSong;

        // Move slow pointer by 1 and fast pointer by 2 until they meet or reach null
        while (fast != null && fast.nextSong != null) {
            if (slow == fast) {
                return true; // Cycle detected
            }
            slow = slow.nextSong;
            fast = fast.nextSong.nextSong;
        }

        // If fast reaches null, no cycle exists
        return false;
    }

    public static void main(String[] args) {
        Song first = new Song("Hello");
        Song second = new Song("Eye of the tiger");
        first.setNextSong(second);
        second.setNextSong(first);
        System.out.println(first.isInRepeatingPlaylist()); // Prints: true
    }
}
```

### How It Works
1. **Edge Case Check**: If the current song has no `nextSong` (`null`), return `false` since a cycle is impossible.
2. **Initialize Pointers**:
    - `slow` starts at the current song (`this`).
    - `fast` starts at the next song (`this.nextSong`).
3. **Floyd’s Algorithm**:
    - Move `slow` one step (`slow = slow.nextSong`).
    - Move `fast` two steps (`fast = fast.nextSong.nextSong`).
    - If `slow` and `fast` ever point to the same song, a cycle exists, so return `true`.
    - If `fast` or `fast.nextSong` becomes `null`, the playlist ends, so return `false`.
4. **Main Method**: The provided example creates a cycle (`first -> second -> first`), and the method correctly returns `true`.

### Time and Space Complexity
- **Time Complexity**: O(n), where n is the number of songs in the playlist. Floyd’s algorithm traverses the list in linear time, either finding a cycle or reaching the end.
- **Space Complexity**: O(1), as only two pointers (`slow` and `fast`) are used, regardless of the playlist size.

### Example Walkthrough
For the given example:
- `first` ("Hello") points to `second` ("Eye of the tiger").
- `second` points back to `first`.
- Starting with `slow = first`, `fast = second`:
    - First iteration: `slow = second`, `fast = first` (meet, cycle detected).
- Output: `true`.

For a non-repeating playlist (e.g., `first -> second -> null`):
- `slow` moves one step, `fast` moves two steps, and `fast` reaches `null`.
- Output: `false`.

This solution efficiently handles all cases and meets the requirement for minimal time complexity.

---

要证明 Floyd’s Cycle-Finding Algorithm（也称为“龟兔算法”）在检测循环播放列表（即单链表中是否存在环）中的正确性，我们需要从算法的原理出发，分析其在所有可能情况下的行为，确保它能正确区分有环和无环的情况。以下是逐步证明 Floyd’s Cycle-Finding Algorithm 在 `isInRepeatingPlaylist` 方法中正确性的详细推理。

### 1. **问题背景与算法概述**
- **问题定义**：给定 `Song` 类表示的单链表（播放列表），每个 `Song` 节点有一个 `nextSong` 指针，指向下一个歌曲或 `null`。如果链表中存在环（即某个节点的 `nextSong` 指向链表中的一个先前节点），则播放列表是循环的，返回 `true`；否则，播放列表最终到达 `null`，返回 `false`。
- **Floyd’s Cycle-Finding Algorithm**：
    - 使用两个指针：`slow`（龟）每次移动一步，`fast`（兔）每次移动两步。
    - 如果两指针在某个节点相遇，说明链表有环。
    - 如果 `fast` 或 `fast.nextSong` 遇到 `null`，说明链表无环。
- **目标**：证明该算法在所有情况下都能正确判断链表是否有环。

### 2. **证明的两个主要部分**
要证明算法的正确性，我们需要证明以下两点：
1. **如果链表有环，算法一定能检测到环**（无漏报，False Negative）。
2. **如果链表无环，算法一定返回 false**（无误报，False Positive）。

### 3. **证明：如果链表有环，算法一定检测到环**
假设播放列表（单链表）存在一个环。我们需要证明 `slow` 和 `fast` 指针最终会在环内相遇。

#### **假设与定义**
- 链表有一个环，环的起点是某个节点（称为环入口）。
- 令：
    - \( L \) 为从链表头到环入口的节点数（非环部分的长度，可能为 0）。
    - \( C \) 为环的长度（环中节点数）。
    - 链表总结构为：从头节点经过 \( L \) 个节点到达环入口，然后环内有 \( C \) 个节点循环。
- `slow` 指针每次移动 1 步，`fast` 指针每次移动 2 步。
- 初始时，`slow` 指向当前节点（`this`），`fast` 指向 `this.nextSong`。

#### **分析指针移动**
- 每经过一个时间步，`fast` 比 `slow` 多移动 1 步（相对速度为 1）。
- 当 `slow` 进入环（经过 \( L \) 步到达环入口）时，`fast` 已移动 \( 2L \) 步。假设环入口为节点 \( S \)，`fast` 可能在环内的某个位置（因为 \( 2L \) 可能大于 \( L + C \)）。
- 在环内，`fast` 相对于 `slow` 的速度为 1 步/时间步，因此 `fast` 会逐渐追上 `slow`。
- 关键点：在一个长度为 \( C \) 的环内，如果两个指针以相对速度 1 移动，它们一定会在最多 \( C \) 步内相遇（因为环是有限的，追赶问题在循环结构中必然有解）。

#### **数学推导**
- 假设 `slow` 进入环时，`fast` 在环内的位置为 \( k \)（相对于环入口，\( 0 \leq k < C \)）。
- 在环内，设经过 \( t \) 步后相遇：
    - `slow` 的位置（在环内）：\( t \mod C \)（从环入口开始移动 \( t \) 步）。
    - `fast` 的位置（在环内）：\( (k + 2t) \mod C \)（从初始位置 \( k \) 开始，以速度 2 移动 \( t \) 步）。
- 相遇条件：\( t \equiv k + 2t \pmod{C} \)。
- 整理：\( t \equiv k + 2t \implies 0 \equiv k + t \pmod{C} \implies t \equiv -k \pmod{C} \)。
- 由于 \( k < C \)，存在一个 \( t \leq C \) 使得 \( t = C - k \)（或其倍数），因此指针必然在有限步内相遇。

#### **初始条件的影响**
- 代码中，`fast` 初始指向 `this.nextSong`，这相当于 `fast` 比 `slow` 领先一步。这种初始偏移不会影响结论，因为它只改变了 \( k \) 的初始值，仍然保证在环内追赶时会相遇。

#### **结论**
无论环的大小 \( C \) 或非环部分长度 \( L \)，只要链表有环，`slow` 和 `fast` 指针一定会在环内某个节点相遇，算法返回 `true`，正确检测到循环播放列表。

### 4. **证明：如果链表无环，算法一定返回 false**
假设播放列表（单链表）没有环，即链表最终以 `null` 终止。我们需要证明 `slow` 和 `fast` 指针不会相遇，且算法会返回 `false`。

#### **分析指针移动**
- 链表无环，结构为：\( S_1 \to S_2 \to \dots \to S_n \to \text{null} \)，共 \( n \) 个节点。
- `slow` 每次移动 1 步，`fast` 每次移动 2 步。
- `fast` 比 `slow` 移动快，因此 `fast` 会先到达链表末尾（`null`）。
- 在代码中，循环条件为 `while (fast != null && fast.nextSong != null)`，确保 `fast` 移动两步时不会访问空指针。
- 当 `fast` 到达最后一个节点（`nextSong == null`）或 `null`，循环终止，算法返回 `false`。

#### **为什么不会相遇**
- 在无环链表中，`fast` 总是领先 `slow`，且距离随时间线性增加（每步增加 1）。
- 相遇要求 `slow` 和 `fast` 在同一节点，但由于 `fast` 移动速度是 `slow` 的两倍，且链表是线性的（无循环），`fast` 会在 `slow` 到达之前先遇到 `null`。
- 例如：
    - 初始：`slow = S_1`, `fast = S_2`.
    - 一步后：`slow = S_2`, `fast = S_4`（如果存在）。
    - 继续移动，`fast` 总是领先，直到 `fast` 或 `fast.nextSong` 为 `null`。

#### **结论**
在无环情况下，`fast` 指针会先到达链表末尾，循环终止，返回 `false`，正确表示播放列表非循环。

### 5. **边际情况分析**
- **空链表或单一节点无下一节点**：
    - 如果 `this.nextSong == null`，代码直接返回 `false`，因为没有环的可能性。正确。
- **单一节点自环**：
    - 如果 `this.nextSong == this`，`slow = this`, `fast = this`，立即满足 `slow == fast`，返回 `true`。正确。
- **短环（如两个节点互指）**：
    - 示例：`S_1 -> S_2 -> S_1`。
    - 初始：`slow = S_1`, `fast = S_2`.
    - 一步后：`slow = S_2`, `fast = S_1`. 相遇，返回 `true`。正确。

### 6. **算法的终止性**
- **有环**：指针在有限步内相遇（最多 \( C \) 步，取决于环内相对位置）。
- **无环**：`fast` 在最多 \( n/2 \) 步内到达 `null`（因为每次移动 2 步）。
- 因此，算法总是终止。

### 7. **时间与空间复杂度**
- **时间复杂度**：O(n)，其中 \( n \) 是链表节点数。
    - 无环：`fast` 遍历最多 \( n \) 步。
    - 有环：指针在 \( L + kC \) 步内相遇（\( k \) 为常数，取决于相遇点）。
- **空间复杂度**：O(1)，仅使用两个指针。

### 8. **总结**
Floyd’s Cycle-Finding Algorithm 的正确性基于以下事实：
- **有环**：快慢指针的相对速度保证它们在环内相遇，检测到循环。
- **无环**：快指针先到达 `null`，避免误报。
- **边际情况**：代码正确处理空链表、单一节点、短环等情况。
- **终止性**：算法在有限步内终止。

因此，`isInRepeatingPlaylist` 方法使用 Floyd’s 算法能正确判断播放列表是否循环，适用于所有可能的输入情况。

### 9. **验证示例**
- **有环**：`first -> second -> first`。
    - `slow = first`, `fast = second`.
    - 一步后：`slow = second`, `fast = first`. 相遇，返回 `true`。
- **无环**：`S_1 -> S_2 -> S_3 -> null`。
    - `slow` 和 `fast` 移动，`fast` 先到达 `S_3` 或 `null`，返回 `false`。

这些示例验证了算法在典型情况下的正确性，符合题目要求。

---

To determine if a playlist (represented as a singly linked list of `Song` objects) is repeating, we need to detect a cycle in the list. Floyd’s Cycle-Finding Algorithm, as implemented in the previous response, is already one of the most efficient solutions with O(n) time complexity and O(1) space complexity. However, if the goal is to explore a "simpler" algorithm in terms of code simplicity or conceptual ease (possibly at the cost of efficiency), we can consider an alternative approach using a HashSet to track visited nodes. This method is simpler to understand and implement but trades off space complexity for ease of reasoning.

### Alternative Algorithm: HashSet-Based Cycle Detection
Instead of using two pointers, we can traverse the playlist and store each visited `Song` node in a HashSet. If we encounter a node that’s already in the set, a cycle exists, and the playlist is repeating. If we reach `null`, there’s no cycle.

#### Why It’s Simpler
- The logic is straightforward: keep track of visited nodes and check for repeats.
- No need to understand the "tortoise and hare" mechanics or relative pointer speeds.
- The code is concise and intuitive, especially for those familiar with hash-based data structures.

#### Trade-Offs
- **Time Complexity**: Still O(n), where n is the number of nodes, as we visit each node at most once.
- **Space Complexity**: O(n), as we store up to n nodes in the HashSet, unlike Floyd’s O(1) space usage.
- **Simplicity**: Easier to reason about for those unfamiliar with Floyd’s algorithm, but less memory-efficient.

### Implementation
Here’s the `isInRepeatingPlaylist` method using a HashSet:

```java
import java.util.HashSet;

public class Song {
    private String name;
    private Song nextSong;

    public Song(String name) {
        this.name = name;
    }

    public void setNextSong(Song nextSong) {
        this.nextSong = nextSong;
    }

    public boolean isInRepeatingPlaylist() {
        HashSet<Song> visited = new HashSet<>();
        Song current = this;

        while (current != null) {
            if (visited.contains(current)) {
                return true; // Cycle detected
            }
            visited.add(current);
            current = current.nextSong;
        }

        return false; // Reached null, no cycle
    }

    public static void main(String[] args) {
        Song first = new Song("Hello");
        Song second = new Song("Eye of the tiger");
        first.setNextSong(second);
        second.setNextSong(first);
        System.out.println(first.isInRepeatingPlaylist()); // Prints: true
    }
}
```

### How It Works
1. **Initialize**:
    - Create a `HashSet<Song>` to store visited nodes.
    - Start with `current` pointing to the current song (`this`).
2. **Traverse**:
    - For each node, check if it’s in the `HashSet`.
        - If yes, a cycle is detected (the node was visited before), return `true`.
        - If no, add the node to the `HashSet` and move to `nextSong`.
    - If `current` becomes `null`, the playlist ends, return `false`.
3. **Edge Cases**:
    - Single node with `nextSong == null`: Returns `false` (no cycle).
    - Single node with `nextSong == this`: Returns `true` (self-loop).
    - Multi-node cycle (e.g., `first -> second -> first`): Returns `true`.

### Example Walkthrough
For the given example (`first -> second -> first`):
- Start: `current = first`, `visited = {}`.
- Add `first` to `visited`, move to `second`.
- Add `second` to `visited`, move to `first`.
- `first` is in `visited`, return `true`.

For a non-repeating playlist (`S1 -> S2 -> S3 -> null`):
- Visit `S1`, add to `visited`.
- Visit `S2`, add to `visited`.
- Visit `S3`, add to `visited`.
- Reach `null`, return `false`.

### Correctness
- **Cycle Exists**: A node will be visited twice, appearing in the `HashSet`, ensuring `true` is returned.
- **No Cycle**: Traversal reaches `null` without revisiting any node, ensuring `false` is returned.
- **Edge Cases**: Handles empty lists, single nodes, and self-loops correctly.

### Comparison with Floyd’s Algorithm
| Aspect                | Floyd’s Algorithm (Previous) | HashSet Algorithm (Proposed) |
|-----------------------|-----------------------------|-----------------------------|
| **Time Complexity**   | O(n)                        | O(n)                        |
| **Space Complexity**  | O(1)                        | O(n)                        |
| **Code Simplicity**   | More complex (two pointers, cycle mechanics) | Simpler (linear traversal, set lookup) |
| **Conceptual Ease**   | Requires understanding relative speeds | Intuitive (track visited nodes) |
| **Memory Usage**      | Minimal (constant)          | Higher (stores up to n nodes) |

### Is There an Even Simpler Algorithm?
- **Brute Force (Not Recommended)**: Traverse the list and for each node, check if it appears later in the list by doing another traversal. This is O(n²) time and O(1) space but highly inefficient.
- **Marking Nodes**: Modify the `Song` class to add a "visited" flag. This is simple but requires altering the data structure, which may not be allowed.
- **Recursive Approach**: Use recursion to track visited nodes, but this still requires O(n) space (stack or set) and isn’t simpler than the HashSet approach.

The HashSet-based algorithm is likely the simplest in terms of code readability and conceptual clarity without sacrificing reasonable performance (O(n) time). Beyond this, simpler approaches either require modifying the `Song` class or incur significantly worse time complexity (e.g., O(n²)).

### Why Not Simpler?
Floyd’s algorithm is optimal for space (O(1)), while the HashSet approach is optimal for simplicity and readability. Any "simpler" algorithm would likely compromise on time efficiency or violate problem constraints (e.g., modifying the `Song` class). The HashSet method strikes a balance by being easy to implement and understand while maintaining O(n) time complexity.

### Conclusion
The HashSet-based algorithm is a simpler alternative to Floyd’s Cycle-Finding Algorithm for detecting a repeating playlist. It’s more intuitive, easier to code, and equally efficient in time (O(n)), though it uses O(n) space. If memory is a concern and the problem emphasizes minimal space usage, Floyd’s algorithm remains superior. For the given problem, where simplicity is prioritized, the HashSet approach is a strong candidate.