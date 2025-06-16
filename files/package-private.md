# 在 Java 中，**package-private interface**（包私有接口）是指一个接口没有显式地声明访问修饰符（如 `public`），因此它的访问级别默认是 **包级别私有**（package-private）。这意味着该接口只能在**同一个包（package）**内的类或接口中访问，而无法被其他包中的类访问。

### 详细解释
1. **默认访问修饰符**：
    - 在 Java 中，如果一个接口（或类、方法、字段等）没有指定访问修饰符（如 `public`、`private`、`protected`），则它的访问级别默认为 **package-private**。
    - 对于接口，声明如下：
      ```java
      interface MyInterface {
          void myMethod();
      }
      ```
      这里的 `MyInterface` 是 package-private，只能被同一包中的类访问。

2. **访问范围**：
    - **同一包内**：所有在同一包中的类、接口或其他代码都可以访问该 package-private 接口。
    - **不同包**：无法访问该接口，除非通过某种间接方式（如反射，但这不是常规做法）。

3. **使用场景**：
    - **模块化设计**：当你希望限制接口的可见性，仅允许同一包中的类实现或使用该接口时，可以使用 package-private 接口。这在模块化设计中非常有用，特别是在大型项目中需要隐藏实现细节时。
    - **内部实现**：package-private 接口常用于包内部的实现逻辑，防止外部代码直接依赖这些接口。

4. **与 public 接口的对比**：
    - 如果接口声明为 `public`：
      ```java
      public interface MyPublicInterface {
          void myMethod();
      }
      ```
      则它可以被任何包中的类访问和实现。
    - package-private 接口的限制更严格，适合需要封装的场景。

5. **注意事项**：
    - **方法默认 public**：在接口中，所有方法（包括默认方法和静态方法）默认是 `public`，即使接口本身是 package-private。这意味着实现类必须将这些方法声明为 `public`。
    - **嵌套接口**：如果接口是嵌套在类中（内部接口），它的访问修饰符可以是 `private`、`protected` 或 `public`，但顶层接口只能是 `public` 或 package-private。
    - **Java 模块化（JPMS）**：在 Java 9 引入的模块系统（JPMS）中，package-private 接口的可见性还会受到模块边界的限制。如果包没有在模块中导出（`exports`），即使是 public 接口也无法被其他模块访问。

### 示例代码
假设包结构如下：
```
com.example.myapp
├── MyInterface.java
├── MyClass.java
com.example.otherapp
├── OtherClass.java
```

**MyInterface.java**（package-private 接口）：
```java
package com.example.myapp;

interface MyInterface {
    void doSomething();
}
```

**MyClass.java**（同一包内，可以访问）：
```java
package com.example.myapp;

public class MyClass implements MyInterface {
    public void doSomething() {
        System.out.println("Doing something");
    }
}
```

**OtherClass.java**（不同包，无法访问）：
```java
package com.example.otherapp;

import com.example.myapp.MyClass;

public class OtherClass {
    // 无法直接访问 MyInterface，因为它是 package-private
    // 编译错误：MyInterface is not visible
    // MyInterface ref = new MyClass();
}
```

### 总结
- **package-private interface** 是没有显式访问修饰符的接口，默认只能在同一包内访问。
- 它适用于需要限制接口可见性的场景，如包内部的实现逻辑或模块化设计。
- 接口中的方法仍然是 `public`，实现类需要显式声明为 `public`。
- 在模块化系统中，包的导出状态会进一步影响接口的可见性。

如果你有更具体的问题或需要进一步的代码示例，请告诉我！