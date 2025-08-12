# TestDome - Java题 - Binary Search Tree

- https://www.testdome.com/library?page=1&skillArea=30&questionId=77789

Let me help you solve this Binary Search Tree (BST) problem. Since we need to check if a given value exists in a BST efficiently, we can leverage the BST property: for any node, all values in the left subtree are less than or equal to the node's value, and all values in the right subtree are greater.

Here's the solution with a clear explanation:

1. If the root is null, the value cannot be in the tree, so return false.
2. If the current node's value equals the target value, return true.
3. If the target value is less than or equal to the current node's value, search the left subtree.
4. If the target value is greater than the current node's value, search the right subtree.
5. We can use recursion to traverse the tree, as each recursive call processes a smaller subtree.

This approach is efficient because it eliminates half the tree at each step, giving us O(log n) time complexity for a balanced BST (or O(h) where h is the height of the tree).

Here's the implementation:

```java
class Node {
    public int value;
    public Node left, right;
    public Node(int value, Node left, Node right) {
        this.value = value;
        this.left = left;
        this.right = right;
    }
}

public class BinarySearchTree {
    public static boolean contains(Node root, int value) {
        // Base case: if root is null, value is not found
        if (root == null) {
            return false;
        }
        
        // If current node's value matches the target, we found it
        if (root.value == value) {
            return true;
        }
        
        // If value is less than or equal to current node's value, search left subtree
        if (value <= root.value) {
            return contains(root.left, value);
        }
        // If value is greater than current node's value, search right subtree
        else {
            return contains(root.right, value);
        }
    }

    public static void main(String[] args) {
        Node n1 = new Node(1, null, null);
        Node n3 = new Node(3, null, null);
        Node n2 = new Node(2, n1, n3);
       
        System.out.println(contains(n2, 3)); // Output: true
    }
}
```

### Explanation:
- **Base Case**: If `root` is null, return `false` since the value can't be found.
- **Match Found**: If `root.value` equals the target `value`, return `true`.
- **Recursive Decision**:
    - If `value <= root.value`, recurse on the left subtree (`root.left`).
    - Otherwise, recurse on the right subtree (`root.right`).
- **Time Complexity**: O(h) where h is the height of the tree. For a balanced BST, this is O(log n), where n is the number of nodes. In the worst case (a skewed tree), it could be O(n).
- **Space Complexity**: O(h) due to the recursive call stack, where h is the tree height.

For the given example:
- Tree: `n2 (value: 2, left: n1 (1), right: n3 (3))`
- Call: `contains(n2, 3)`
    - At `n2`, `3 > 2`, so go to right subtree (`n3`).
    - At `n3`, `3 == 3`, return `true`.

The function correctly returns `true` for the example case.