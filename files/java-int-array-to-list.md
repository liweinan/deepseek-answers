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