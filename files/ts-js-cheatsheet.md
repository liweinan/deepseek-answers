# TypeScript + JavaScript Cheatsheet

## 基本语法

### 变量声明
```typescript
// JavaScript
var oldWay = "deprecated";
let mutable = "can change";
const immutable = "can't change";

// TypeScript
let name: string = "John";
const age: number = 30;
let isActive: boolean = true;
```

### 数据类型
```typescript
// 原始类型
let str: string;
let num: number;
let bool: boolean;
let nul: null;
let undef: undefined;
let sym: symbol;
let big: bigint;

// 对象类型
let obj: object;
let arr: number[]; // or Array<number>
let tuple: [string, number];
let anyType: any;
let unknownType: unknown;
let voidType: void;
let neverType: never;
```

## 函数

### 函数定义
```typescript
// JavaScript
function add(a, b) {
  return a + b;
}

// TypeScript
function add(a: number, b: number): number {
  return a + b;
}

// 箭头函数
const multiply = (a: number, b: number): number => a * b;

// 可选参数
function greet(name: string, greeting?: string): string {
  return `${greeting || 'Hello'}, ${name}`;
}

// 默认参数
function createUser(name: string, role: string = 'user') {
  return { name, role };
}
```

## 对象和类

### 对象
```typescript
// JavaScript
const person = {
  name: "Alice",
  age: 25
};

// TypeScript
const person: { name: string; age: number } = {
  name: "Alice",
  age: 25
};

// 接口
interface Person {
  name: string;
  age: number;
  email?: string; // 可选属性
}

const alice: Person = {
  name: "Alice",
  age: 25
};
```

### 类
```typescript
// JavaScript
class Animal {
  constructor(name) {
    this.name = name;
  }
  
  speak() {
    console.log(`${this.name} makes a noise.`);
  }
}

// TypeScript
class Animal {
  name: string;
  
  constructor(name: string) {
    this.name = name;
  }
  
  speak(): void {
    console.log(`${this.name} makes a noise.`);
  }
}

// 继承
class Dog extends Animal {
  breed: string;
  
  constructor(name: string, breed: string) {
    super(name);
    this.breed = breed;
  }
  
  speak(): void {
    console.log(`${this.name} barks.`);
  }
}
```

## 数组操作

### 常用方法
```typescript
const numbers: number[] = [1, 2, 3, 4, 5];

// 映射
const doubled = numbers.map(n => n * 2);

// 过滤
const evens = numbers.filter(n => n % 2 === 0);

// 查找
const firstEven = numbers.find(n => n % 2 === 0);

// 归约
const sum = numbers.reduce((acc, curr) => acc + curr, 0);

// 展开运算符
const newNumbers = [...numbers, 6, 7, 8];
```

## 异步编程

### Promises
```typescript
// JavaScript
fetch('https://api.example.com/data')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error));

// TypeScript
interface ApiResponse {
  id: number;
  name: string;
}

fetch('https://api.example.com/data')
  .then(response => response.json() as Promise<ApiResponse>)
  .then((data: ApiResponse) => console.log(data))
  .catch((error: Error) => console.error(error));
```

### Async/Await
```typescript
// JavaScript
async function getData() {
  try {
    const response = await fetch('https://api.example.com/data');
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// TypeScript
async function getData(): Promise<void> {
  try {
    const response = await fetch('https://api.example.com/data');
    const data: ApiResponse = await response.json();
    console.log(data);
  } catch (error: unknown) {
    if (error instanceof Error) {
      console.error(error.message);
    }
  }
}
```

## 类型操作

### 类型别名
```typescript
type Point = {
  x: number;
  y: number;
};

type ID = string | number;
```

### 泛型
```typescript
function identity<T>(arg: T): T {
  return arg;
}

// 泛型接口
interface GenericArray<T> {
  [index: number]: T;
}

// 泛型类
class GenericNumber<T> {
  zeroValue: T;
  add: (x: T, y: T) => T;
}
```

### 类型断言
```typescript
const someValue: unknown = "this is a string";
const strLength: number = (someValue as string).length;

// 另一种语法
const strLength2: number = (<string>someValue).length;
```

## 模块系统

### 导出/导入
```typescript
// 导出
export const pi = 3.14;
export function calculateCircumference(diameter: number) {
  return diameter * pi;
}

// 默认导出
export default class Circle {
  // ...
}

// 导入
import { pi, calculateCircumference } from './math';
import Circle from './Circle';
```

## 实用工具类型

```typescript
interface User {
  id: number;
  name: string;
  age: number;
  email: string;
}

// Partial - 所有属性变为可选
type PartialUser = Partial<User>;

// Readonly - 所有属性变为只读
type ReadonlyUser = Readonly<User>;

// Pick - 选择部分属性
type UserNameAndEmail = Pick<User, 'name' | 'email'>;

// Omit - 忽略部分属性
type UserWithoutEmail = Omit<User, 'email'>;

// Record - 创建键值类型
type UserMap = Record<string, User>;
```

## ES6+ 特性

### 解构赋值
```typescript
// 数组解构
const [first, second, ...rest] = [1, 2, 3, 4, 5];

// 对象解构
const { name, age, ...details } = { name: 'John', age: 30, city: 'NY' };
```

### 模板字符串
```typescript
const greeting = `Hello, ${name}! You are ${age} years old.`;
```

### 可选链
```typescript
const street = user?.address?.street;
```

### 空值合并
```typescript
const displayName = username ?? 'Anonymous';
```

### 动态导入
```typescript
async function loadModule() {
  const module = await import('./module');
  module.doSomething();
}
```

这个速查表涵盖了 TypeScript 和 JavaScript 中最常用的功能。根据你的具体需求，可以进一步扩展或深入研究特定领域。

---

这段代码定义了一个 TypeScript **泛型接口** `GenericArray<T>`，它描述了一个**索引签名**，表示一个可以通过数字索引访问的数组结构，其中数组元素的类型为泛型参数 `T`。

### 逐部分解析：

1. **`interface GenericArray<T>`**
    - 定义了一个名为 `GenericArray` 的接口。
    - `<T>` 表示这是一个**泛型接口**，`T` 是一个类型参数（Type Parameter），在使用时可以替换为具体的类型（如 `number`、`string` 或自定义类型）。

2. **`[index: number]: T;`**
    - 这是一个**索引签名**（Index Signature），表示这个接口允许通过 `number` 类型的索引（即数组的下标）来访问元素。
    - `index: number`：索引必须是 `number` 类型（类似于常规数组的索引方式）。
    - `: T`：索引对应的值的类型是 `T`（即泛型参数指定的类型）。

---

### 它的作用是什么？
这个接口描述了一个类似于数组的结构：
- 可以通过数字索引（如 `arr[0]`、`arr[1]`）访问元素。
- 所有元素的类型都是 `T`。

### 示例用法：
```typescript
// 使用 GenericArray 定义一个数字数组
const numberArray: GenericArray<number> = [1, 2, 3];
console.log(numberArray[0]); // 1 (类型是 number)

// 使用 GenericArray 定义一个字符串数组
const stringArray: GenericArray<string> = ["a", "b", "c"];
console.log(stringArray[1]); // "b" (类型是 string)
```

---

### 对比普通数组类型
它和 TypeScript 中直接使用 `T[]` 或 `Array<T>` 是等价的：
```typescript
// 以下两种定义是等效的：
type GenericArray<T> = {
  [index: number]: T;
};

type GenericArray2<T> = T[];
type GenericArray3<T> = Array<T>;
```

但通过索引签名的方式可以更灵活地定义类似数组的结构（比如混合类型或特殊约束）。

---

### 总结
这段代码定义了一个通用的数组接口，允许通过数字索引访问元素，且元素的类型由泛型 `T` 决定。它是 TypeScript 中描述数组结构的一种底层实现方式。