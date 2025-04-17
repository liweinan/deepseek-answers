# Python Cheat Sheet

## 基础语法

```python
# 打印输出
print("Hello, World!")

# 变量赋值
x = 10
name = "Alice"

# 获取输入
user_input = input("Enter something: ")

# 注释
# 这是单行注释
"""
这是多行注释
可以跨越多行
"""
```

## 数据类型

```python
# 数字
int_num = 42        # 整数
float_num = 3.14    # 浮点数
complex_num = 2 + 3j # 复数

# 布尔值
true_val = True
false_val = False

# 字符串
str1 = "Hello"
str2 = 'World'
multiline_str = """This is a
multi-line string"""

# 列表
my_list = [1, 2, 3, "a", "b"]
empty_list = []

# 元组
my_tuple = (1, 2, 3)  # 不可变
empty_tuple = ()

# 字典
my_dict = {"name": "Alice", "age": 25}
empty_dict = {}

# 集合
my_set = {1, 2, 3}  # 唯一元素
empty_set = set()
```

## 运算符

```python
# 算术运算符
x + y    # 加法
x - y    # 减法
x * y    # 乘法
x / y    # 除法
x // y   # 整除
x % y    # 取模
x ** y   # 幂运算

# 比较运算符
x == y   # 等于
x != y   # 不等于
x > y    # 大于
x < y    # 小于
x >= y   # 大于等于
x <= y   # 小于等于

# 逻辑运算符
x and y  # 与
x or y   # 或
not x    # 非

# 成员运算符
x in y       # 如果在y中找到x返回True
x not in y   # 如果在y中没有找到x返回True

# 身份运算符
x is y       # 如果x和y是同一个对象返回True
x is not y   # 如果x和y不是同一个对象返回True
```

## 控制流

```python
# if语句
if x > 0:
    print("Positive")
elif x == 0:
    print("Zero")
else:
    print("Negative")

# for循环
for i in range(5):  # 0到4
    print(i)

for item in my_list:
    print(item)

# while循环
while x > 0:
    print(x)
    x -= 1

# 循环控制
break      # 退出循环
continue   # 跳过当前迭代
```

## 函数

```python
# 定义函数
def greet(name):
    """这是一个问候函数"""
    return f"Hello, {name}!"

# 调用函数
result = greet("Alice")

# 默认参数
def power(x, n=2):
    return x ** n

# 可变参数
def sum_all(*args):
    return sum(args)

# 关键字参数
def person_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

# lambda函数
square = lambda x: x ** 2
```

## 列表操作

```python
# 创建列表
numbers = [1, 2, 3, 4, 5]

# 访问元素
first = numbers[0]      # 1
last = numbers[-1]      # 5
sublist = numbers[1:3]  # [2, 3]

# 修改列表
numbers.append(6)       # [1, 2, 3, 4, 5, 6]
numbers.insert(0, 0)    # [0, 1, 2, 3, 4, 5, 6]
numbers.remove(3)       # [0, 1, 2, 4, 5, 6]
del numbers[0]          # [1, 2, 4, 5, 6]

# 列表操作
len(numbers)            # 长度
numbers.sort()          # 排序
numbers.reverse()       # 反转
numbers.index(4)        # 查找索引
numbers.count(2)        # 计数

# 列表推导式
squares = [x**2 for x in range(10)]
even_squares = [x**2 for x in range(10) if x % 2 == 0]
```

## 字符串操作

```python
# 字符串方法
s = "hello world"
s.upper()           # "HELLO WORLD"
s.lower()           # "hello world"
s.capitalize()      # "Hello world"
s.title()           # "Hello World"
s.strip()           # 去除两端空白
s.split()           # ['hello', 'world']
"-".join(["a", "b"]) # "a-b"

# 字符串格式化
name = "Alice"
age = 25
f"Name: {name}, Age: {age}"  # f-string (Python 3.6+)
"Name: {}, Age: {}".format(name, age)
"Name: %s, Age: %d" % (name, age)

# 字符串检查
s.startswith("hello")  # True
s.endswith("world")    # True
s.isalpha()           # False (包含空格)
s.isdigit()           # False
```

## 文件操作

```python
# 读取文件
with open("file.txt", "r") as f:
    content = f.read()  # 读取全部内容
    lines = f.readlines()  # 读取所有行

# 写入文件
with open("output.txt", "w") as f:
    f.write("Hello\n")
    f.writelines(["Line 1\n", "Line 2\n"])

# 文件模式
# "r" - 读取 (默认)
# "w" - 写入 (会覆盖)
# "a" - 追加
# "r+" - 读写
# "b" - 二进制模式 (如 "rb")
```

## 异常处理

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
except Exception as e:
    print(f"An error occurred: {e}")
else:
    print("No errors occurred")
finally:
    print("This always executes")

# 抛出异常
if x < 0:
    raise ValueError("x cannot be negative")
```

## 面向对象编程

```python
# 类定义
class Person:
    # 类属性
    species = "Homo sapiens"
    
    # 初始化方法
    def __init__(self, name, age):
        self.name = name  # 实例属性
        self.age = age
    
    # 实例方法
    def greet(self):
        return f"Hello, my name is {self.name}"
    
    # 类方法
    @classmethod
    def from_birth_year(cls, name, birth_year):
        age = 2023 - birth_year
        return cls(name, age)
    
    # 静态方法
    @staticmethod
    def is_adult(age):
        return age >= 18

# 创建实例
person = Person("Alice", 25)
print(person.greet())

# 继承
class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)
        self.student_id = student_id
    
    def greet(self):
        return f"Hi, I'm student {self.student_id}, my name is {self.name}"
```

## 常用模块

```python
# math模块
import math
math.sqrt(16)       # 4.0
math.pi             # 3.141592653589793
math.ceil(3.2)      # 4
math.floor(3.8)     # 3

# random模块
import random
random.random()     # 0.0到1.0之间的随机数
random.randint(1, 10)  # 1到10之间的随机整数
random.choice(["a", "b", "c"])  # 随机选择

# datetime模块
from datetime import datetime, date, timedelta
now = datetime.now()
today = date.today()
future = now + timedelta(days=7)

# os模块
import os
os.getcwd()         # 当前工作目录
os.listdir()        # 列出目录内容
os.path.exists("file.txt")  # 检查文件是否存在

# sys模块
import sys
sys.argv            # 命令行参数
sys.exit()          # 退出程序

# json模块
import json
json_str = json.dumps({"name": "Alice"})  # 字典转JSON
data = json.loads(json_str)               # JSON转字典
```

## 虚拟环境

```bash
# 创建虚拟环境
python -m venv myenv

# 激活虚拟环境 (Windows)
myenv\Scripts\activate

# 激活虚拟环境 (macOS/Linux)
source myenv/bin/activate

# 停用虚拟环境
deactivate

# 安装包
pip install package_name

# 列出已安装包
pip list

# 生成requirements.txt
pip freeze > requirements.txt

# 从requirements.txt安装
pip install -r requirements.txt
```

## PEP 8 编码风格指南要点

- 使用4个空格缩进
- 每行不超过79个字符
- 导入通常应该分行写：
  ```python
  import os
  import sys
  ```
- 类名使用驼峰命名法：`MyClass`
- 函数和变量名使用小写加下划线：`my_function`
- 常量使用全大写：`CONSTANT_NAME`
- 运算符周围和逗号后使用空格：
  ```python
  x = 1 + 2
  my_list = [1, 2, 3]
  ```

这个速查表涵盖了Python的主要功能，适合快速参考。根据你的具体需求，可能需要更详细的信息或特定领域的知识。