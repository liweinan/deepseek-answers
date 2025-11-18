# Python Cheat Sheet

## Basic Syntax

```python
# Print Output
print("Hello, World!")

# Variable Assignment
x = 10
name = "Alice"

# Get Input
user_input = input("Enter something: ")

# Comments
# This is a single-line comment
"""
This is a multi-line comment
that can span multiple lines
"""
```

## Data Types

```python
# Numbers
int_num = 42        # integer
float_num = 3.14    # float
complex_num = 2 + 3j # complex number

# Boolean Values
true_val = True
false_val = False

# Strings
str1 = "Hello"
str2 = 'World'
multiline_str = """This is a
multi-line string"""

# Lists
my_list = [1, 2, 3, "a", "b"]
empty_list = []

# Tuples
my_tuple = (1, 2, 3)  # immutable
empty_tuple = ()

# Dictionaries
my_dict = {"name": "Alice", "age": 25}
empty_dict = {}

# Sets
my_set = {1, 2, 3}  # unique elements
empty_set = set()
```

## Operators

```python
# Arithmetic Operators
x + y    # addition
x - y    # subtraction
x * y    # multiplication
x / y    # division
x // y   # floor division
x % y    # modulo
x ** y   # exponentiation

# Comparison Operators
x == y   # equal to
x != y   # not equal to
x > y    # greater than
x < y    # less than
x >= y   # greater than or equal to
x <= y   # less than or equal to

# Logical Operators
x and y  # and
x or y   # or
not x    # not

# Membership Operators
x in y       # returns True if x is found in y
x not in y   # returns True if x is not found in y

# Identity Operators
x is y       # returns True if x and y are the same object
x is not y   # returns True if x and y are not the same object
```

## Control Flow

```python
# if statement
if x > 0:
    print("Positive")
elif x == 0:
    print("Zero")
else:
    print("Negative")

# for loop
for i in range(5):  # 0 to 4
    print(i)

for item in my_list:
    print(item)

# while loop
while x > 0:
    print(x)
    x -= 1

# Loop Control
break      # exit loop
continue   # skip current iteration
```

## Functions

```python
# Define function
def greet(name):
    """This is a greeting function"""
    return f"Hello, {name}!"

# Call function
result = greet("Alice")

# Default parameters
def power(x, n=2):
    return x ** n

# Variable arguments
def sum_all(*args):
    return sum(args)

# Keyword arguments
def person_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

# Lambda functions
square = lambda x: x ** 2
```

## List Operations

```python
# Create lists
numbers = [1, 2, 3, 4, 5]

# Access elements
first = numbers[0]      # 1
last = numbers[-1]      # 5
sublist = numbers[1:3]  # [2, 3]

# Modify lists
numbers.append(6)       # [1, 2, 3, 4, 5, 6]
numbers.insert(0, 0)    # [0, 1, 2, 3, 4, 5, 6]
numbers.remove(3)       # [0, 1, 2, 4, 5, 6]
del numbers[0]          # [1, 2, 4, 5, 6]

# List operations
len(numbers)            # length
numbers.sort()          # sort
numbers.reverse()       # reverse
numbers.index(4)        # find index
numbers.count(2)        # count

# List comprehensions
squares = [x**2 for x in range(10)]
even_squares = [x**2 for x in range(10) if x % 2 == 0]
```

## String Operations

```python
# String methods
s = "hello world"
s.upper()           # "HELLO WORLD"
s.lower()           # "hello world"
s.capitalize()      # "Hello world"
s.title()           # "Hello World"
s.strip()           # remove whitespace from both ends
s.split()           # ['hello', 'world']
"-".join(["a", "b"]) # "a-b"

# String formatting
name = "Alice"
age = 25
f"Name: {name}, Age: {age}"  # f-string (Python 3.6+)
"Name: {}, Age: {}".format(name, age)
"Name: %s, Age: %d" % (name, age)

# String checks
s.startswith("hello")  # True
s.endswith("world")    # True
s.isalpha()           # False (contains spaces)
s.isdigit()           # False
```

## File Operations

```python
# Read files
with open("file.txt", "r") as f:
    content = f.read()  # read all content
    lines = f.readlines()  # read all lines

# Write files
with open("output.txt", "w") as f:
    f.write("Hello\n")
    f.writelines(["Line 1\n", "Line 2\n"])

# File modes
# "r" - read (default)
# "w" - write (overwrites)
# "a" - append
# "r+" - read and write
# "b" - binary mode (e.g., "rb")
```

## Exception Handling

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

# Raise exceptions
if x < 0:
    raise ValueError("x cannot be negative")
```

## Object-Oriented Programming

```python
# Class definition
class Person:
    # Class attribute
    species = "Homo sapiens"
    
    # Initialization method
    def __init__(self, name, age):
        self.name = name  # instance attribute
        self.age = age
    
    # Instance method
    def greet(self):
        return f"Hello, my name is {self.name}"
    
    # Class method
    @classmethod
    def from_birth_year(cls, name, birth_year):
        age = 2023 - birth_year
        return cls(name, age)
    
    # Static method
    @staticmethod
    def is_adult(age):
        return age >= 18

# Create instance
person = Person("Alice", 25)
print(person.greet())

# Inheritance
class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)
        self.student_id = student_id
    
    def greet(self):
        return f"Hi, I'm student {self.student_id}, my name is {self.name}"
```

## Common Modules

```python
# math module
import math
math.sqrt(16)       # 4.0
math.pi             # 3.141592653589793
math.ceil(3.2)      # 4
math.floor(3.8)     # 3

# random module
import random
random.random()     # random number between 0.0 and 1.0
random.randint(1, 10)  # random integer between 1 and 10
random.choice(["a", "b", "c"])  # random choice

# datetime module
from datetime import datetime, date, timedelta
now = datetime.now()
today = date.today()
future = now + timedelta(days=7)

# os module
import os
os.getcwd()         # current working directory
os.listdir()        # list directory contents
os.path.exists("file.txt")  # check if file exists

# sys module
import sys
sys.argv            # command line arguments
sys.exit()          # exit program

# json module
import json
json_str = json.dumps({"name": "Alice"})  # dict to JSON
data = json.loads(json_str)               # JSON to dict
```

## Virtual Environment

```bash
# Create virtual environment
python -m venv myenv

# Activate virtual environment (Windows)
myenv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source myenv/bin/activate

# Deactivate virtual environment
deactivate

# Install packages
pip install package_name

# List installed packages
pip list

# Generate requirements.txt
pip freeze > requirements.txt

# Install from requirements.txt
pip install -r requirements.txt
```

## PEP 8 Coding Style Guide Key Points

- Use 4 spaces for indentation
- Maximum 79 characters per line
- Imports should usually be on separate lines:
  ```python
  import os
  import sys
  ```
- Class names use CamelCase: `MyClass`
- Function and variable names use lowercase with underscores: `my_function`
- Constants use all uppercase: `CONSTANT_NAME`
- Use spaces around operators and after commas:
  ```python
  x = 1 + 2
  my_list = [1, 2, 3]
  ```

This cheat sheet covers the main features of Python and is suitable for quick reference. Depending on your specific needs, you may require more detailed information or domain-specific knowledge.