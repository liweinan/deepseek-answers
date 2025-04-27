# To convert an `int` array to a `List<Integer>` in Java, you can use one of the following approaches for your array

`int result[] = new int[]{0, 0};`:

1. **Using `Arrays.stream` (Java 8+)**:
   ```java
   List<Integer> list = Arrays.stream(result)
                             .boxed()
                             .collect(Collectors.toList());
   ```

2. **Using a loop (Manual conversion)**:
   ```java
   List<Integer> list = new ArrayList<>();
   for (int num : result) {
       list.add(num);
   }
   ```

3. **Using `Arrays.asList` with mapping (Less common)**:
   ```java
   List<Integer> list = new ArrayList<>();
   list.addAll(Arrays.stream(result)
                     .boxed()
                     .collect(Collectors.toList()));
   ```

**Explanation**:

- `Arrays.stream(result)` creates a stream of `int` values.
- `.boxed()` converts the `IntStream` to a `Stream<Integer>` by boxing the primitive `int` to `Integer`.
- `Collectors.toList()` collects the stream elements into a `List<Integer>`.

The first method (using `Arrays.stream`) is the most concise and recommended for modern Java. The resulting
`List<Integer>` for your example will be `[0, 0]`.

---

# 在 Java 中，初始化一个 `List` 并包含初始值有以下几种常用方法。以下以 `List<Integer>` 为例，展示如何初始化并包含初始值（如

`[0, 0]`）：

### 1. **使用 `Arrays.asList`（适合固定初始值）**

```java
List<Integer> list = new ArrayList<>(Arrays.asList(0, 0));
```

- `Arrays.asList(0, 0)` 创建一个固定长度的 `List`。
- 包装在 `new ArrayList<>()` 中以创建可修改的 `List`（因为 `Arrays.asList` 返回的 `List` 是不可修改的）。
- 结果：`list` 包含 `[0, 0]`。

### 2. **使用 `List.of`（Java 9+，不可修改）**

```java
List<Integer> list = new ArrayList<>(List.of(0, 0));
```

- `List.of(0, 0)` 创建一个不可修改的 `List`。
- 包装在 `new ArrayList<>()` 中以创建可修改的 `List`。
- 结果：`list` 包含 `[0, 0]`。

### 3. **使用 `new ArrayList<>()` 并手动添加**

```java
List<Integer> list = new ArrayList<>();
list.

add(0);
list.

add(0);
```

- 直接创建空 `ArrayList`，然后逐个添加初始值。
- 结果：`list` 包含 `[0, 0]`。

### 4. **使用 `Stream`（适合动态初始值）**

```java
List<Integer> list = Stream.of(0, 0)
        .collect(Collectors.toCollection(ArrayList::new));
```

- `Stream.of(0, 0)` 创建包含指定值的流。
- 收集到 `ArrayList` 中。
- 结果：`list` 包含 `[0, 0]`。

### 5. **使用匿名内部类（较少使用）**

```java
List<Integer> list = new ArrayList<>() {{
    add(0);
    add(0);
}};
```

- 使用双括号初始化，直接在构造时添加初始值。
- 结果：`list` 包含 `[0, 0]`。

### 注意事项

- 如果需要一个**不可修改的 `List`**，可以直接使用 `Arrays.asList(0, 0)` 或 `List.of(0, 0)`，但不能对其进行添加或删除操作。
- 如果需要**可修改的 `List`**，推荐使用方法 1 或 2，将 `Arrays.asList` 或 `List.of` 的结果包装在 `new ArrayList<>()` 中。
- 方法 1（`Arrays.asList`）和方法 2（`List.of`）是最简洁且常用的方式。

**示例输出**：

```java
List<Integer> list = new ArrayList<>(Arrays.asList(0, 0));
System.out.

println(list); // 输出: [0, 0]
```

根据你的需求（比如是否需要可修改的 `List`），选择合适的方法即可。

---

List<Integer> list = Stream.of(0, 0)
.collect(Collectors.toList()); // 使用 Collectors
Collections.sort(list); // 使用 Collections
System.out.println(list); // 输出: [0, 0]