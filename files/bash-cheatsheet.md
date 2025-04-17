# Bash Shell 脚本速查表 (Cheatsheet)

## 基本语法

```bash
#!/bin/bash           # Shebang，指定解释器
# 这是注释            # 单行注释
: '
多行注释
'
```

## 变量

```bash
var="value"           # 定义变量
echo $var             # 使用变量
echo "${var}"         # 推荐使用花括号
readonly var          # 只读变量
unset var             # 删除变量
```

## 特殊变量

```bash
$0                   # 脚本名称
$1, $2, ..., $9      # 脚本参数
$#                   # 参数个数
$*                   # 所有参数(作为一个字符串)
$@                   # 所有参数(作为多个字符串)
$?                   # 上一条命令的退出状态
$$                   # 当前shell的PID
$!                   # 最后一个后台进程的PID
```

## 字符串操作

```bash
str="Hello World"
length=${#str}        # 字符串长度
sub=${str:6:5}        # 子字符串(从索引6开始，取5个字符)
new=${str/World/Bash} # 替换字符串
```

## 数组

```bash
arr=("a" "b" "c")     # 定义数组
echo ${arr[1]}        # 访问元素(索引从0开始)
echo ${arr[@]}        # 访问所有元素
echo ${#arr[@]}       # 数组长度
arr+=("d")            # 添加元素
```

## 运算符

```bash
# 算术运算
$((a + b))           # 加法
$((a - b))           # 减法
$((a * b))           # 乘法
$((a / b))           # 除法
$((a % b))           # 取模
$((a++))             # 自增
$((a--))             # 自减

# 关系运算(在条件表达式中)
[ $a -eq $b ]        # 等于
[ $a -ne $b ]        # 不等于
[ $a -gt $b ]        # 大于
[ $a -lt $b ]        # 小于
[ $a -ge $b ]        # 大于等于
[ $a -le $b ]        # 小于等于
```

## 条件判断

```bash
# if语句
if [ condition ]; then
    commands
elif [ condition ]; then
    commands
else
    commands
fi

# case语句
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

## 循环

```bash
# for循环
for var in list; do
    commands
done

# C风格for循环
for ((i=0; i<10; i++)); do
    commands
done

# while循环
while [ condition ]; do
    commands
done

# until循环
until [ condition ]; do
    commands
done

# 循环控制
break                # 跳出循环
continue             # 跳过当前迭代
```

## 函数

```bash
function_name() {
    commands
    [return value]
}

# 调用函数
function_name arg1 arg2

# 函数参数
$1, $2, ..., $9      # 函数内部访问参数
$#                   # 参数个数
```

## 输入/输出

```bash
echo "text"           # 输出文本
printf "format" args  # 格式化输出
read var              # 读取用户输入
read -p "Prompt: " var # 带提示的输入
read -s var           # 静默输入(适合密码)
```

## 文件操作

```bash
# 文件测试
[ -e file ]          # 文件/目录是否存在
[ -f file ]          # 是普通文件
[ -d file ]          # 是目录
[ -r file ]          # 可读
[ -w file ]          # 可写
[ -x file ]          # 可执行
[ -s file ]          # 文件大小>0

# 重定向
command > file       # 标准输出重定向到文件(覆盖)
command >> file      # 标准输出重定向到文件(追加)
command < file       # 从文件读取标准输入
command 2> file      # 标准错误重定向到文件
command &> file      # 标准输出和错误都重定向到文件
```

## 进程控制

```bash
command &            # 后台运行
command1 | command2  # 管道
command1 && command2 # 命令1成功则执行命令2
command1 || command2 # 命令1失败则执行命令2
sleep 5              # 暂停5秒
wait                 # 等待所有后台进程完成
```

## 调试

```bash
bash -n script.sh    # 检查语法错误
bash -x script.sh    # 跟踪执行过程
set -x               # 在脚本中启用调试
set +x               # 关闭调试
trap 'commands' EXIT # 脚本退出时执行命令
```

## 常用命令

```bash
# 字符串处理
grep pattern file    # 搜索文本
sed 's/old/new/g'    # 流编辑器
awk '{print $1}'     # 文本处理

# 文件处理
cat file             # 显示文件内容
head -n 5 file       # 显示前5行
tail -n 5 file       # 显示最后5行
wc -l file           # 统计行数

# 系统信息
date                 # 当前日期时间
whoami               # 当前用户
uname -a             # 系统信息
df -h                # 磁盘使用情况
free -h              # 内存使用情况
```

## 示例脚本

```bash
#!/bin/bash

# 带参数的脚本示例
if [ $# -lt 1 ]; then
    echo "Usage: $0 <name>"
    exit 1
fi

name=$1
echo "Hello, $name!"

# 循环示例
for i in {1..5}; do
    echo "Iteration $i"
done

# 函数示例
greet() {
    local message="Welcome, $1!"
    echo "$message"
}

greet "$name"
```

希望这个速查表对您有所帮助！根据需要可以进一步扩展或定制。

