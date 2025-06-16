# 要高效刷LeetCode（力扣）算法题，盲目刷题确实效率低下。以下是一个分类总结的高效自学刷题方案，适合自学者，包含学习路径、分类重点、刷题策略和推荐题目链接。方案以结构化、循序渐进的方式帮助你提升算法能力，同时避免陷入低效的题海战术。

---

### 一、总体学习路径
1. **建立基础（1-2 周）**：
    - 学习基本数据结构与算法概念（如数组、链表、栈、队列、树、图、排序、搜索、动态规划等）。
    - 推荐资源：
        - 书籍：《算法（第四版）》或《算法导论》（基础部分）。
        - 视频：B站或YouTube上的算法入门课程（如“算法可视化”或“NeetCode”）。
        - LeetCode Explore模块：免费的“Learning”板块，涵盖基础知识点。
    - 目标：理解核心概念，掌握时间复杂度和空间复杂度分析。

2. **分类刷题（2-3 个月）**：
    - 按算法和数据结构分类刷题，聚焦高频题型。
    - 每类题目先易后难，逐步深入。
    - 每周专注1-2个专题，总结规律和模板。

3. **进阶与模拟（1-2 个月）**：
    - 刷中高难度题目，强化综合能力。
    - 参加LeetCode周赛、双周赛，模拟真实面试环境。
    - 复习错题，整理错题本。

4. **巩固与优化（持续进行）**：
    - 定期回顾经典题目，优化代码。
    - 学习优秀解法（如LeetCode官方题解或讨论区高赞答案）。
    - 针对薄弱专题加强练习。

---

### 二、分类刷题重点与推荐题目
以下是LeetCode常见算法和数据结构的分类总结，包含推荐题目和链接。建议按顺序学习，每类题目刷10-20道，覆盖简单、中等、困难。

#### 1. 数组与字符串
- **核心知识**：双指针、滑动窗口、前缀和、哈希表。
- **学习重点**：
    - 双指针：快慢指针、左右指针。
    - 滑动窗口：处理子数组或子字符串问题。
    - 哈希表：快速查找和计数。
- **推荐题目**（由易到难）：
    1. [Two Sum](https://leetcode.com/problems/two-sum/)（简单，哈希表入门）
    2. [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/)（中等，滑动窗口）
    3. [Container With Most Water](https://leetcode.com/problems/container-with-most-water/)（中等，双指针）
    4. [3Sum](https://leetcode.com/problems/3sum/)（中等，双指针+排序）
    5. [Group Anagrams](https://leetcode.com/problems/group-anagrams/)（中等，哈希表）
- **刷题建议**：优先掌握双指针和滑动窗口的模板，总结字符串操作的技巧（如Python的字符串切片）。

#### 2. 链表
- **核心知识**：链表遍历、快慢指针、反转链表、合并链表。
- **学习重点**：
    - 快慢指针：用于找中点、检测环。
    - 反转链表：递归与迭代两种方法。
- **推荐题目**：
    1. [Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/)（简单，反转链表）
    2. [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/)（简单，链表合并）
    3. [Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/)（简单，快慢指针）
    4. [Remove Nth Node From End of List](https://leetcode.com/problems/remove-nth-node-from-end-of-list/)（中等，快慢指针）
    5. [Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/)（困难，优先队列）
- **刷题建议**：熟练手写链表操作代码，注意边界条件（如空链表、单节点）。

#### 3. 栈与队列
- **核心知识**：栈的LIFO、队列的FIFO、单调栈、优先队列。
- **学习重点**：
    - 单调栈：处理“下一个更大/更小元素”问题。
    - 优先队列：解决Top K问题。
- **推荐题目**：
    1. [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/)（简单，栈）
    2. [Min Stack](https://leetcode.com/problems/min-stack/)（中等，栈设计）
    3. [Next Greater Element I](https://leetcode.com/problems/next-greater-element-i/)（简单，单调栈）
    4. [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/)（中等，优先队列）
    5. [Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/)（困难，单调队列）
- **刷题建议**：掌握Python的`collections.deque`和`heapq`模块，理解单调栈的逻辑。

#### 4. 树与递归
- **核心知识**：二叉树遍历（前序、中序、后序、层序）、BST、递归、分治。
- **学习重点**：
    - 递归：分解问题，写出递归终止条件。
    - 层序遍历：使用队列。
- **推荐题目**：
    1. [Invert Binary Tree](https://leetcode.com/problems/invert-binary-tree/)（简单，递归）
    2. [Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/)（简单，递归）
    3. [Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/)（中等，层序遍历）
    4. [Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/)（中等，BST）
    5. [Lowest Common Ancestor of a Binary Tree](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/)（中等，递归）
- **刷题建议**：熟练三种遍历方式，总结递归模板（返回值、参数、终止条件）。

#### 5. 图
- **核心知识**：DFS、BFS、并查集、拓扑排序、最短路径。
- **学习重点**：
    - DFS/BFS：处理连通性、路径问题。
    - 并查集：解决分组问题。
- **推荐题目**：
    1. [Number of Islands](https://leetcode.com/problems/number-of-islands/)（中等，DFS/BFS）
    2. [Clone Graph](https://leetcode.com/problems/clone-graph/)（中等，DFS）
    3. [Course Schedule](https://leetcode.com/problems/course-schedule/)（中等，拓扑排序）
    4. [Union Find - Number of Provinces](https://leetcode.com/problems/number-of-provinces/)（中等，并查集）
    5. [Word Ladder](https://leetcode.com/problems/word-ladder/)（困难，BFS）
- **刷题建议**：掌握图的表示方式（邻接表、邻接矩阵），熟练并查集模板。

#### 6. 动态规划
- **核心知识**：状态定义、状态转移、DP数组/记忆化。
- **学习重点**：
    - 1D DP：背包问题、打家劫舍。
    - 2D DP：最长公共子序列、编辑距离。
- **推荐题目**：
    1. [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/)（简单，基础DP）
    2. [House Robber](https://leetcode.com/problems/house-robber/)（中等，1D DP）
    3. [Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/)（中等，2D DP）
    4. [Unique Paths](https://leetcode.com/problems/unique-paths/)（中等，2D DP）
    5. [Regular Expression Matching](https://leetcode.com/problems/regular-expression-matching/)（困难，DP+递归）
- **刷题建议**：总结状态转移方程的推导方法，画表格理解2D DP。

#### 7. 其他高频题型
- **二分查找**：
    1. [Binary Search](https://leetcode.com/problems/binary-search/)（简单）
    2. [Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/)（中等）
- **回溯**：
    1. [Subsets](https://leetcode.com/problems/subsets/)（中等）
    2. [Permutations](https://leetcode.com/problems/permutations/)（中等）
- **贪心**：
    1. [Jump Game](https://leetcode.com/problems/jump-game/)（中等）
    2. [Candy](https://leetcode.com/problems/candy/)（困难）

---

### 三、高效刷题策略
1. **制定计划**：
    - 每周刷15-20题（简单10道、中等7道、困难3道）。
    - 每天1-2小时，专注解题+总结。
    - 使用LeetCode的“Problem List”功能，创建专题列表。

2. **五步解题法**：
    - **理解题目**：读清输入输出，分析约束条件。
    - **思考思路**：先想暴力解法，再优化（时间/空间复杂度）。
    - **写代码**：清晰命名变量，写注释。
    - **测试用例**：手动验证边界情况（如空输入、最大值）。
    - **优化与总结**：看官方题解或讨论区，记录模板。

3. **优先高频题**：
    - LeetCode“Top 100 Liked Questions”或“Top Interview Questions”。
    - 参考NeetCode 150（https://neetcode.io/practice），覆盖面试高频。

4. **错题管理**：
    - 每周复习错题，记录解题思路和错误原因。
    - 使用LeetCode的“Favorite”功能标记重点题目。

5. **模拟面试**：
    - 使用LeetCode Premium的“Mock Interview”功能。
    - 参加周赛，练习限时解题。

---

### 四、推荐资源与工具
1. **LeetCode功能**：
    - Explore模块：免费学习卡片，涵盖基础到进阶。
    - Discuss板块：查看高赞解法和思路。
    - Premium（可选）：提供更多题目和模拟面试。

2. **外部资源**：
    - **NeetCode**：免费的高频题讲解视频（https://neetcode.io/）。
    - **labuladong的算法小抄**：总结算法模板（https://labuladong.github.io/algo/）。
    - **OI Wiki**：中文算法知识库（https://oi-wiki.org/）。
    - **力扣官方微信公众号**：每日一题和题解推送。

3. **工具**：
    - **LeetCode插件**：如“LeetCode Editor”插件，支持VSCode本地调试。
    - **Python/JAVA/C++**：选择熟悉的语言，Python推荐`collections`、`heapq`模块。

---

### 五、时间规划示例（3个月）
| 周数 | 专题 | 目标题目数 | 推荐活动 |
|------|------|------------|----------|
| 1-2  | 数组与字符串 | 20（10简单+8中等+2困难） | 学习双指针、滑动窗口模板 |
| 3-4  | 链表+栈队列 | 20（10简单+8中等+2困难） | 掌握快慢指针、单调栈 |
| 5-6  | 树与递归 | 15（8简单+5中等+2困难） | 总结递归三要素 |
| 7-8  | 图+二分查找 | 15（8简单+5中等+2困难） | 学习BFS/DFS/并查集 |
| 9-10 | 动态规划 | 15（8简单+5中等+2困难） | 画状态转移表格 |
| 11-12 | 回溯+贪心+综合 | 20（10中等+10困难） | 参加周赛，复习错题 |

---

### 六、注意事项
1. **避免题海战术**：刷题不在多，而在精。理解>数量。
2. **记录复杂度**：每道题总结时间和空间复杂度，培养优化意识。
3. **语言熟练度**：确保熟练使用Python/Java/C++的内置函数（如Python的`Counter`、`defaultdict`）。
4. **保持节奏**：每天坚持1-2题，积少成多。
5. **社区互动**：在LeetCode Discuss或X上参与算法讨论，获取灵感。

---

通过以上方案，你可以系统化地提升算法能力，高效备战面试或竞赛。如果需要特定专题的深入讲解或更多题目推荐，请告诉我！