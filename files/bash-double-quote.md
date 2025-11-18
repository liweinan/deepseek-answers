# Bash Double Brackets `[[ ]]`

In Bash, double brackets `[[ ]]` are **extended test commands** (also known as conditional expressions), providing more powerful features and more flexible syntax compared to traditional single brackets `[ ]`. It is a Bash keyword (not an external command), so in some cases it is more efficient and safer.

---

### **Main Features**
1. **No need to quote variables**  
   `[[ ]]` automatically handles spaces and special characters in variables, avoiding unexpected word splitting.
   ```bash
   name="Hello World"
   [[ $name == "Hello World" ]]  # No need to write "$name"
   ```

2. **Supports more powerful pattern matching**  
   Can use `==` or `=~` for wildcard and regular expression matching:
   ```bash
   [[ "file.txt" == *.txt ]]      # Wildcard matching, returns true
   [[ "123" =~ ^[0-9]+$ ]]       # Regular expression matching, returns true
   ```

3. **More intuitive logical operators**  
   Supports `&&` (AND), `||` (OR) instead of `-a`, `-o`:
   ```bash
   [[ $x -gt 10 && $y -lt 20 ]]  # No need to write [ $x -gt 10 -a $y -lt 20 ]
   ```

4. **Supports lexicographical string comparison**  
   Directly use `>` or `<` to compare strings (lexicographically):
   ```bash
   [[ "apple" < "banana" ]]  # Returns true
   ```

5. **Avoids path expansion (globbing) issues**  
   In `[[ ]]`, the right side of `==` won't trigger filename expansion:
   ```bash
   [[ "file" == * ]]  # Just wildcard matching, won't expand to current directory filenames
   ```

---

### **Common Usage Examples**
| Function                | `[[ ]]` Syntax                          | Equivalent `[ ]` Syntax (for comparison)          |
|---------------------|---------------------------------------|----------------------------------|
| String equality          | `[[ "$str" == "value" ]]`             | `[ "$str" = "value" ]`           |
| String inequality        | `[[ "$str" != "value" ]]`             | `[ "$str" != "value" ]`          |
| Numeric comparison            | `[[ "$num" -gt 10 ]]`                 | `[ "$num" -gt 10 ]`              |
| File exists            | `[[ -e "file.txt" ]]`                 | `[ -e "file.txt" ]`              |
| Logical combination            | `[[ -f file && -r file ]]`            | `[ -f file -a -r file ]`         |
| Regular expression matching            | `[[ "$str" =~ ^[0-9]+$ ]]`            | Not available (requires external tools like `grep`)        |

---

### **Notes**
1. **Compatibility**  
   `[[ ]]` is a Bash extension feature, not available in POSIX Shell (such as `sh`). The script's first line should specify `#!/bin/bash`.

2. **Safety when variable is empty**  
   Even if variable is undefined or empty, `[[ ]]` won't report errors:
   ```bash
   [[ $undefined_var == "" ]]  # Safe, returns true
   [ $undefined_var = "" ]     # May error (recommended to write [ "${undefined_var}" = "" ])
   ```

3. **Avoid confusion with `[ ]`**
    - `[ ]` is traditional test command (actually an alias for `test` command), needs to strictly follow spaces and quotation rules.
    - `[[ ]]` is more modern, recommended for use in Bash.

---

### **Why recommend using `[[ ]]`?**
- More concise syntax (like directly using `&&`).
- Fewer quotation requirements (reduces errors).
- Supports advanced matching (regular expressions, wildcards).
- Higher execution efficiency (because it's a Bash built-in keyword).

---

### Classic Use Cases
```bash
if [[ "$file" == *.txt && -f "$file" ]]; then
    echo "This is a text file and exists"
fi

# Regular expression matching with group extraction
if [[ "2023-01-01" =~ ^([0-9]{4})-([0-9]{2}) ]]; then
    year=${BASH_REMATCH[1]}
    month=${BASH_REMATCH[2]}
    echo "Year: $year, Month: $month"
fi
```

In summary, prefer using `[[ ]]` in Bash scripts, unless POSIX Shell compatibility (like `sh`) is needed.

---

In Bash scripts, single brackets `[]` and double brackets `[[]]` are both used for conditional testing, but their usage, functionality, and behavior have significant differences. Here is a detailed explanation to help you determine when to use single brackets and when to use double brackets.

---

### 1. Single Brackets `[]`
- **Definition**: Single brackets are shorthand for Bash's built-in `test` command, used for conditional testing.
- **Features**:
    - Follows POSIX standard, strong compatibility, can be used in most shells (like sh).
    - Stricter syntax, needs careful handling of variable references and spaces.
    - Doesn't support advanced pattern matching (like regular expressions) and logical operators `&&`, `||`.
    - Undefined or empty variables may cause syntax errors, need quotation protection.
- **Usage**:
    - For basic comparisons (strings, integers, file attributes, etc.).
    - Common operators:
        - Strings: `=`, `!=`, `-z`, `-n`
        - Integers: `-eq`, `-ne`, `-lt`, `-le`, `-gt`, `-ge`
        - Files: `-e`, `-d`, `-f`, `-r`, `-w`, `-x`
    - Logical operations need to use `-a` (AND), `-o` (OR) or combine multiple `test` commands.
- **Syntax Requirements**:
    - Variables need to be enclosed in double quotes to avoid empty value errors.
    - Must have spaces on both sides, e.g. `[ "$var" = "value" ]`.
- **Example**:
  ```bash
  # Check if variable is empty
  if [ -z "$var" ]; then
      echo "var is empty"
  fi

  # Compare integers
  if [ "$num" -eq 10 ]; then
      echo "num is 10"
  fi

  # Logical AND
  if [ "$a" = "foo" ] && [ "$b" = "bar" ]; then
      echo "Both conditions are true"
  fi
  ```

- **Notes**:
    - If variable is undefined or empty, may cause syntax errors, e.g. `[ $var = "value" ]` will error when `$var` is empty.
    - Doesn't support wildcards (like `*`) or regular expressions.
    - String comparison uses `=` instead of `==` (though `==` is also compatible in Bash).

---

### 2. Double Brackets `[[]]`
- **Definition**: Double brackets are Bash extension features, specifically designed for Bash and ksh, with more powerful functions.
- **Features**:
    - Doesn't follow POSIX standard, only supported in modern shells like Bash, zsh.
    - Supports more flexible syntax, like regular expressions, wildcards, logical operators `&&` and `||`.
    - Variables don't always need to be quoted, safer handling of empty values.
    - Slightly better performance than single brackets, because it's a Bash keyword rather than external command.
- **Usage**:
    - Supports all operators of single brackets.
    - Additional support:
        - Logical operators: `&&` (AND), `||` (OR), `!` (NOT).
        - Regular expressions: `=~` operator.
        - Wildcards: Use `==` or `!=` to support glob patterns.
        - More flexible comparisons: supports `==` for strings, more intuitive integer comparisons.
- **Syntax Requirements**:
    - Still needs spaces on both sides, e.g. `[[ $var == "value" ]]`.
    - Variables can be unquoted, `[[ $var == value ]]` won't error when `$var` is empty.
- **Example**:
  ```bash
  # Check if string matches pattern
  if [[ $var == "test"* ]]; then
      echo "var starts with test"
  fi

  # Use regular expression
  if [[ $var =~ ^[0-9]+$ ]]; then
      echo "var is a number"
  fi

  # Logical operations
  if [[ $a == "foo" && $b == "bar" ]]; then
      echo "Both conditions are true"
  fi
  ```

- **Notes**:
    - Not compatible with POSIX shell (like sh), cannot be used in strict POSIX environments.
    - Supports more modern programming style, suitable for complex conditional judgments.

---

### When to use single brackets, when to use double brackets?

| Scenario                            | Single Brackets `[]`        | Double Brackets `[[]]` |
|-------------------------------|-----------------|---------------|
| **Need POSIX compatibility** (run in sh scripts) | ✅ Use            | ❌ Not supported |
| **Basic string/integer comparison**                | ✅ Suitable            | ✅ Suitable |
| **File attribute check** (like `-f`, `-d`)      | ✅ Common            | ✅ Also supported |
| **Logical operations** (`&&`, `\|\|`)        | ❌ Need external `&&` or `-a`/`-o` | ✅ Direct support |
| **Regular expression matching**                   | ❌ Not supported           | ✅ Use `=~` |
| **Wildcard matching** (like `*`, `?`)         | ❌ Not supported           | ✅ Use `==` |
| **Variable may be empty**                    | ❌ Need quotes          | ✅ Safer |
| **Complex conditional expressions**                   | ❌ Not flexible enough          | ✅ Recommended |
| **Performance-sensitive scenarios**                    | ❌ Slightly slower (calls test command) | ✅ Faster (Bash built-in) |

---

### Quick Summary
- **Use single brackets `[]`**:
    - Need to write portable scripts (POSIX compatible, run in sh or other basic shells).
    - Simple conditional testing (strings, integers, file attributes).
    - Environment restrictions prevent using Bash extension features.

- **Use double brackets `[[]]`**:
    - In Bash scripts, pursue more modern, flexible syntax.
    - Need regular expressions, wildcards, or logical operators `&&`, `||`.
    - Handle complex conditions or scenarios where variables may be empty.
    - Don't need to consider POSIX compatibility.

---

### Practical Example Comparison
```bash
# Single brackets: need to be careful with empty variables
var=""
if [ -n "$var" ]; then
    echo "var is not empty"
else
    echo "var is empty"
fi

# Double brackets: safer, variables don't need quotes
var=""
if [[ -n $var ]]; then
    echo "var is not empty"
else
    echo "var is empty"
fi

# Double brackets support regular expressions
var="123"
if [[ $var =~ ^[0-9]+$ ]]; then
    echo "var is a number"
fi
```

---

### Additional Tips
- If you're writing Bash scripts (`#!/bin/bash`), prefer double brackets `[[]]`, because they're more powerful and safer.
- If you need to be compatible with older systems or non-Bash environments (like Docker images with `/bin/sh`), use single brackets `[]`.
- Be careful to avoid common mistakes, like forgetting spaces or misusing operators (e.g., using `==` for regex matching in single brackets).

If you have specific Bash scripts or conditional testing questions, feel free to share the code and I'll help you analyze or optimize it!