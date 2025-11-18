# Bash Shell Script Cheat Sheet

## Basic Syntax

```bash
#!/bin/bash           # Shebang, specifies interpreter
# This is a comment            # Single line comment
: '
Multi-line comment
'
```

## Variables

```bash
var="value"           # Define variable
echo $var             # Use variable
echo "${var}"         # Recommended to use curly braces
readonly var          # Read-only variable
unset var             # Delete variable
```

## Special Variables

```bash
$0                   # Script name
$1, $2, ..., $9      # Script parameters
$#                   # Number of parameters
$*                   # All parameters (as a single string)
$@                   # All parameters (as multiple strings)
$?                   # Exit status of last command
$$                   # Current shell PID
$!                   # PID of last background process
```

## String Operations

```bash
str="Hello World"
length=${#str}        # String length
sub=${str:6:5}        # Substring (start at index 6, take 5 characters)
new=${str/World/Bash} # String replacement
```

## Arrays

```bash
arr=("a" "b" "c")     # Define array
echo ${arr[1]}        # Access element (index starts at 0)
echo ${arr[@]}        # Access all elements
echo ${#arr[@]}       # Array length
arr+=("d")            # Add element
```

## Operators

```bash
# Arithmetic operations
$((a + b))           # Addition
$((a - b))           # Subtraction
$((a * b))           # Multiplication
$((a / b))           # Division
$((a % b))           # Modulo
$((a++))             # Increment
$((a--))             # Decrement

# Relational operations (in conditional expressions)
[ $a -eq $b ]        # Equal
[ $a -ne $b ]        # Not equal
[ $a -gt $b ]        # Greater than
[ $a -lt $b ]        # Less than
[ $a -ge $b ]        # Greater than or equal
[ $a -le $b ]        # Less than or equal
```

## Conditional Statements

```bash
# if statement
if [ condition ]; then
    commands
elif [ condition ]; then
    commands
else
    commands
fi

# case statement
case $var in
    pattern1)
        commands
        ;;
    pattern2)
        commands
        ;;
    *)
        commands
        ;;
esac
```

## Loops

```bash
# for loop
for var in list; do
    commands
done

# C-style for loop
for ((i=0; i<10; i++)); do
    commands
done

# while loop
while [ condition ]; do
    commands
done

# until loop
until [ condition ]; do
    commands
done

# Loop control
break                # Break out of loop
continue             # Skip current iteration
```

## Functions

```bash
function_name() {
    commands
    [return value]
}

# Call function
function_name arg1 arg2

# Function parameters
$1, $2, ..., $9      # Access parameters inside function
$#                   # Number of parameters
```

## Input/Output

```bash
echo "text"           # Output text
printf "format" args  # Formatted output
read var              # Read user input
read -p "Prompt: " var # Prompted input
read -s var           # Silent input (suitable for passwords)
```

## File Operations

```bash
# File testing
[ -e file ]          # File/directory exists
[ -f file ]          # Is a regular file
[ -d file ]          # Is a directory
[ -r file ]          # Readable
[ -w file ]          # Writable
[ -x file ]          # Executable
[ -s file ]          # File size > 0

# Redirection
command > file       # Redirect standard output to file (overwrite)
command >> file      # Redirect standard output to file (append)
command < file       # Read standard input from file
command 2> file      # Redirect standard error to file
command &> file      # Redirect both standard output and error to file
```

## Process Control

```bash
command &            # Run in background
command1 | command2  # Pipe
command1 && command2 # Execute command2 only if command1 succeeds
command1 || command2 # Execute command2 only if command1 fails
sleep 5              # Pause for 5 seconds
wait                 # Wait for all background processes to complete
```

## Debugging

```bash
bash -n script.sh    # Check syntax errors
bash -x script.sh    # Trace execution process
set -x               # Enable debugging in script
set +x               # Disable debugging
trap 'commands' EXIT # Execute commands when script exits
```

## Common Commands

```bash
# String processing
grep pattern file    # Search text
sed 's/old/new/g'    # Stream editor
awk '{print $1}'     # Text processing

# File processing
cat file             # Display file content
head -n 5 file       # Display first 5 lines
tail -n 5 file       # Display last 5 lines
wc -l file           # Count lines

# System information
date                 # Current date and time
whoami               # Current user
uname -a             # System information
df -h                # Disk usage
free -h              # Memory usage
```

## Example Scripts

```bash
#!/bin/bash

# Script example with parameters
if [ $# -lt 1 ]; then
    echo "Usage: $0 <name>"
    exit 1
fi

name=$1
echo "Hello, $name!"

# Loop example
for i in {1..5}; do
    echo "Iteration $i"
done

# Function example
greet() {
    local message="Welcome, $1!"
    echo "$message"
}

greet "$name"
```

Hope this cheat sheet is helpful to you! It can be further expanded or customized as needed.