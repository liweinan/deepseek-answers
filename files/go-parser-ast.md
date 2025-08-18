# Go AST 节点类型层级结构

### 1. 顶层节点 (Top-Level Nodes)

#### `*ast.File` - 文件节点
这是 AST 的根节点，代表整个 Go 源文件：
```go
type File struct {
    Doc     *CommentGroup // 文件级文档注释
    Package token.Pos     // package 关键字位置
    Name    *Ident        // 包名
    Decls   []Decl        // 声明列表
    Scope   *Scope        // 包作用域
    Imports []*ImportSpec // 导入声明
    Unresolved []*Ident   // 未解析的标识符
    Comments []*CommentGroup // 注释组
}
```

### 2. 声明节点 (Declaration Nodes)

#### `*ast.GenDecl` - 通用声明
包含 import、const、var、type 声明：
```go
type GenDecl struct {
    Doc    *CommentGroup // 文档注释
    TokPos token.Pos     // 关键字位置
    Tok    token.Token   // 关键字类型 (IMPORT, CONST, VAR, TYPE)
    Lparen token.Pos     // '(' 位置
    Specs  []Spec        // 规格列表
    Rparen token.Pos     // ')' 位置
}
```

#### `*ast.FuncDecl` - 函数声明
```go
type FuncDecl struct {
    Doc  *CommentGroup // 文档注释
    Recv *FieldList    // 接收者 (方法)
    Name *Ident        // 函数名
    Type *FuncType     // 函数类型
    Body *BlockStmt    // 函数体
}
```

### 3. 规格节点 (Specification Nodes)

#### `*ast.ImportSpec` - 导入规格
```go
type ImportSpec struct {
    Doc  *CommentGroup // 文档注释
    Name *Ident        // 别名 (可选)
    Path *BasicLit     // 导入路径
    EndPos token.Pos   // 结束位置
}
```

#### `*ast.ValueSpec` - 值规格 (const, var)
```go
type ValueSpec struct {
    Doc     *CommentGroup // 文档注释
    Names   []*Ident      // 变量名列表
    Type    Expr          // 类型表达式
    Values  []Expr        // 值表达式列表
    Comment *CommentGroup // 行注释
}
```

#### `*ast.TypeSpec` - 类型规格
```go
type TypeSpec struct {
    Doc     *CommentGroup // 文档注释
    Name    *Ident        // 类型名
    TypeParams *FieldList // 类型参数 (Go 1.18+)
    Type    Expr          // 类型定义
    Comment *CommentGroup // 行注释
}
```

### 4. 表达式节点 (Expression Nodes)

#### 基础表达式
- `*ast.Ident` - 标识符
- `*ast.BasicLit` - 基本字面量 (字符串、数字、布尔值)
- `*ast.BinaryExpr` - 二元表达式
- `*ast.UnaryExpr` - 一元表达式

#### 复合表达式
- `*ast.CallExpr` - 函数调用
- `*ast.SelectorExpr` - 选择器表达式 (x.y)
- `*ast.IndexExpr` - 索引表达式 (x[i])
- `*ast.SliceExpr` - 切片表达式 (x[i:j])
- `*ast.TypeAssertExpr` - 类型断言 (x.(T))

#### 类型表达式
- `*ast.ArrayType` - 数组类型
- `*ast.StructType` - 结构体类型
- `*ast.FuncType` - 函数类型
- `*ast.InterfaceType` - 接口类型
- `*ast.MapType` - 映射类型
- `*ast.ChanType` - 通道类型
- `*ast.StarExpr` - 指针类型 (*T)

### 5. 语句节点 (Statement Nodes)

#### 简单语句
- `*ast.ExprStmt` - 表达式语句
- `*ast.IncDecStmt` - 自增自减语句
- `*ast.AssignStmt` - 赋值语句
- `*ast.GoStmt` - go 语句
- `*ast.DeferStmt` - defer 语句
- `*ast.ReturnStmt` - return 语句
- `*ast.BranchStmt` - 分支语句 (break, continue, goto, fallthrough)
- `*ast.BlockStmt` - 块语句

#### 控制流语句
- `*ast.IfStmt` - if 语句
- `*ast.CaseClause` - case 子句
- `*ast.SwitchStmt` - switch 语句
- `*ast.TypeSwitchStmt` - 类型 switch 语句
- `*ast.CommClause` - select 通信子句
- `*ast.SelectStmt` - select 语句
- `*ast.ForStmt` - for 语句
- `*ast.RangeStmt` - range 语句

### 6. 结构体相关节点

#### `*ast.StructType` - 结构体类型
```go
type StructType struct {
    Struct     token.Pos  // struct 关键字位置
    Fields     *FieldList // 字段列表
    Incomplete bool       // 是否不完整
}
```

#### `*ast.FieldList` - 字段列表
```go
type FieldList struct {
    Opening token.Pos // '(' 位置
    List    []*Field  // 字段列表
    Closing token.Pos // ')' 位置
}
```

#### `*ast.Field` - 字段
```go
type Field struct {
    Doc     *CommentGroup // 文档注释
    Names   []*Ident      // 字段名列表
    Type    Expr          // 字段类型
    Tag     *BasicLit     // 标签
    Comment *CommentGroup // 行注释
}
```

### 7. 注释节点

#### `*ast.CommentGroup` - 注释组
```go
type CommentGroup struct {
    List []*Comment // 注释列表
}
```

#### `*ast.Comment` - 单个注释
```go
type Comment struct {
    Slash token.Pos // // 或 /* 位置
    Text  string    // 注释文本
}
```

## 层级关系示例

```
*ast.File (根节点)
├── *ast.Ident (包名)
├── []*ast.ImportSpec (导入列表)
│   ├── *ast.ImportSpec
│   │   ├── *ast.Ident (别名)
│   │   └── *ast.BasicLit (路径)
│   └── ...
└── []ast.Decl (声明列表)
    ├── *ast.GenDecl (import/const/var/type)
    │   └── []ast.Spec
    │       ├── *ast.ImportSpec
    │       ├── *ast.ValueSpec
    │       └── *ast.TypeSpec
    │           └── *ast.StructType
    │               └── *ast.FieldList
    │                   └── []*ast.Field
    │                       ├── []*ast.Ident (字段名)
    │                       ├── ast.Expr (字段类型)
    │                       └── *ast.BasicLit (标签)
    └── *ast.FuncDecl (函数)
        ├── *ast.FieldList (接收者)
        ├── *ast.Ident (函数名)
        ├── *ast.FuncType (函数类型)
        │   ├── *ast.FieldList (参数)
        │   └── *ast.FieldList (返回值)
        └── *ast.BlockStmt (函数体)
            └── []ast.Stmt (语句列表)
                ├── *ast.ExprStmt
                ├── *ast.AssignStmt
                ├── *ast.IfStmt
                ├── *ast.ForStmt
                └── ...
```

## 遍历方式

### 1. 深度优先遍历
使用 `ast.Inspect()` 函数：
```go
ast.Inspect(node, func(n ast.Node) bool {
    // 处理节点
    return true // 继续遍历子节点
})
```

### 2. 类型断言检查
```go
switch n := node.(type) {
case *ast.File:
    // 处理文件节点
case *ast.FuncDecl:
    // 处理函数声明
case *ast.TypeSpec:
    // 处理类型声明
case *ast.StructType:
    // 处理结构体类型
}
```

### 3. 位置信息
每个节点都有位置信息：
- `node.Pos()` - 开始位置
- `node.End()` - 结束位置
- `fset.Position(pos)` - 转换为行列号

这种层级结构使得我们可以精确地分析和操作 Go 代码的各个部分，从整个文件到单个标识符，都能在 AST 中找到对应的节点。