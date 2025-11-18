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

# In Java, there are several common methods to initialize a `List` and include initial values. Below using `List<Integer>` as an example, showing how to initialize and include initial values (such as

`[0, 0]`)：

### 1. **Using `Arrays.asList` (suitable for fixed initial values)**

```java
List<Integer> list = new ArrayList<>(Arrays.asList(0, 0));
```

- `Arrays.asList(0, 0)` creates a fixed-length `List`.
- Wrapped in `new ArrayList<>()` to create a modifiable `List` (because the `List` returned by `Arrays.asList` is unmodifiable).
- Result: `list` contains `[0, 0]`.

### 2. **Using `List.of` (Java 9+, unmodifiable)**

```java
List<Integer> list = new ArrayList<>(List.of(0, 0));
```

- `List.of(0, 0)` creates an unmodifiable `List`.
- Wrapped in `new ArrayList<>()` to create a modifiable `List`.
- Result: `list` contains `[0, 0]`.

### 3. **Using `new ArrayList<>()` and manually adding**

```java
List<Integer> list = new ArrayList<>();
list.

add(0);
list.

add(0);
```

- Directly create an empty `ArrayList`, then add initial values one by one.
- Result: `list` contains `[0, 0]`.

### 4. **Using `Stream` (suitable for dynamic initial values)**

```java
List<Integer> list = Stream.of(0, 0)
        .collect(Collectors.toCollection(ArrayList::new));
```

- `Stream.of(0, 0)` creates a stream containing specified values.
- Collected into `ArrayList`.
- Result: `list` contains `[0, 0]`.

### 5. **Using anonymous inner class (rarely used)**

```java
List<Integer> list = new ArrayList<>() {{
    add(0);
    add(0);
}};
```

- Using double brace initialization, directly add initial values during construction.
- Result: `list` contains `[0, 0]`.

### Notes

- If you need an **unmodifiable `List`**, you can directly use `Arrays.asList(0, 0)` or `List.of(0, 0)`, but you cannot add or remove elements from them.
- If you need a **modifiable `List`**, it is recommended to use method 1 or 2, wrapping the result of `Arrays.asList` or `List.of` in `new ArrayList<>()`.
- Method 1 (`Arrays.asList`) and method 2 (`List.of`) are the most concise and commonly used ways.

**Example Output**:

```java
List<Integer> list = new ArrayList<>(Arrays.asList(0, 0));
System.out.

println(list); // Output: [0, 0]
```

Choose the appropriate method based on your needs (such as whether you need a modifiable `List`).

---

List<Integer> list = Stream.of(0, 0)
.collect(Collectors.toList()); // Using Collectors
Collections.sort(list); // Using Collections
System.out.println(list); // Output: [0, 0]