# Go AST Node Type Hierarchy Structure

### 1. Top-Level Nodes

#### `*ast.File` - File Node
This is the root node of the AST, representing the entire Go source file:
```go
type File struct {
    Doc     *CommentGroup // File-level documentation comments
    Package token.Pos     // package keyword position
    Name    *Ident        // Package name
    Decls   []Decl        // Declaration list
    Scope   *Scope        // Package scope
    Imports []*ImportSpec // Import declarations
    Unresolved []*Ident   // Unresolved identifiers
    Comments []*CommentGroup // Comment groups
}
```

### 2. Declaration Nodes

#### `*ast.GenDecl` - General Declaration
Contains import, const, var, type declarations:
```go
type GenDecl struct {
    Doc    *CommentGroup // Documentation comments
    TokPos token.Pos     // Keyword position
    Tok    token.Token   // Keyword type (IMPORT, CONST, VAR, TYPE)
    Lparen token.Pos     // '(' position
    Specs  []Spec        // Specification list
    Rparen token.Pos     // ')' position
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

### 3. Specification Nodes

#### `*ast.ImportSpec` - Import Specification
```go
type ImportSpec struct {
    Doc  *CommentGroup // 文档注释
    Name *Ident        // 别名 (可选)
    Path *BasicLit     // 导入路径
    EndPos token.Pos   // 结束位置
}
```

#### `*ast.ValueSpec` - Value Specification (const, var)
```go
type ValueSpec struct {
    Doc     *CommentGroup // 文档注释
    Names   []*Ident      // 变量名列表
    Type    Expr          // 类型表达式
    Values  []Expr        // 值表达式列表
    Comment *CommentGroup // 行注释
}
```

#### `*ast.TypeSpec` - Type Specification
```go
type TypeSpec struct {
    Doc     *CommentGroup // 文档注释
    Name    *Ident        // 类型名
    TypeParams *FieldList // 类型参数 (Go 1.18+)
    Type    Expr          // 类型定义
    Comment *CommentGroup // 行注释
}
```

### 4. Expression Nodes

#### Basic Expressions
- `*ast.Ident` - Identifier
- `*ast.BasicLit` - Basic literals (strings, numbers, booleans)
- `*ast.BinaryExpr` - Binary expressions
- `*ast.UnaryExpr` - Unary expressions

#### Compound Expressions
- `*ast.CallExpr` - Function calls
- `*ast.SelectorExpr` - Selector expressions (x.y)
- `*ast.IndexExpr` - Index expressions (x[i])
- `*ast.SliceExpr` - Slice expressions (x[i:j])
- `*ast.TypeAssertExpr` - Type assertions (x.(T))

#### Type Expressions
- `*ast.ArrayType` - Array types
- `*ast.StructType` - Struct types
- `*ast.FuncType` - Function types
- `*ast.InterfaceType` - Interface types
- `*ast.MapType` - Map types
- `*ast.ChanType` - Channel types
- `*ast.StarExpr` - Pointer types (*T)

### 5. Statement Nodes

#### Simple Statements
- `*ast.ExprStmt` - Expression statements
- `*ast.IncDecStmt` - Increment/decrement statements
- `*ast.AssignStmt` - Assignment statements
- `*ast.GoStmt` - go statements
- `*ast.DeferStmt` - defer statements
- `*ast.ReturnStmt` - return statements
- `*ast.BranchStmt` - Branch statements (break, continue, goto, fallthrough)
- `*ast.BlockStmt` - Block statements

#### Control Flow Statements
- `*ast.IfStmt` - if statements
- `*ast.CaseClause` - case clauses
- `*ast.SwitchStmt` - switch statements
- `*ast.TypeSwitchStmt` - Type switch statements
- `*ast.CommClause` - select communication clauses
- `*ast.SelectStmt` - select statements
- `*ast.ForStmt` - for statements
- `*ast.RangeStmt` - range statements

### 6. Struct-related Nodes

#### `*ast.StructType` - Struct Type
```go
type StructType struct {
    Struct     token.Pos  // struct 关键字位置
    Fields     *FieldList // 字段列表
    Incomplete bool       // 是否不完整
}
```

#### `*ast.FieldList` - Field List
```go
type FieldList struct {
    Opening token.Pos // '(' 位置
    List    []*Field  // 字段列表
    Closing token.Pos // ')' 位置
}
```

#### `*ast.Field` - Field
```go
type Field struct {
    Doc     *CommentGroup // 文档注释
    Names   []*Ident      // 字段名列表
    Type    Expr          // 字段类型
    Tag     *BasicLit     // 标签
    Comment *CommentGroup // 行注释
}
```

### 7. Comment Nodes

#### `*ast.CommentGroup` - Comment Group
```go
type CommentGroup struct {
    List []*Comment // 注释列表
}
```

#### `*ast.Comment` - Single Comment
```go
type Comment struct {
    Slash token.Pos // // 或 /* 位置
    Text  string    // 注释文本
}
```

## Hierarchy Example

```
*ast.File (Root node)
├── *ast.Ident (Package name)
├── []*ast.ImportSpec (Import list)
│   ├── *ast.ImportSpec
│   │   ├── *ast.Ident (Alias)
│   │   └── *ast.BasicLit (Path)
│   └── ...
└── []ast.Decl (Declaration list)
    ├── *ast.GenDecl (import/const/var/type)
    │   └── []ast.Spec
    │       ├── *ast.ImportSpec
    │       ├── *ast.ValueSpec
    │       └── *ast.TypeSpec
    │           └── *ast.StructType
    │               └── *ast.FieldList
    │                   └── []*ast.Field
    │                       ├── []*ast.Ident (Field names)
    │                       ├── ast.Expr (Field types)
    │                       └── *ast.BasicLit (Tags)
    └── *ast.FuncDecl (Function)
        ├── *ast.FieldList (Receiver)
        ├── *ast.Ident (Function name)
        ├── *ast.FuncType (Function type)
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

## Traversal Methods

### 1. Depth-First Traversal
Using `ast.Inspect()` function:
```go
ast.Inspect(node, func(n ast.Node) bool {
    // Process node
    return true // Continue traversing child nodes
})
```

### 2. Type Assertion Checking
```go
switch n := node.(type) {
case *ast.File:
    // Process file node
case *ast.FuncDecl:
    // Process function declaration
case *ast.TypeSpec:
    // Process type declaration
case *ast.StructType:
    // Process struct type
}
```

### 3. Position Information
Each node has position information:
- `node.Pos()` - Start position
- `node.End()` - End position
- `fset.Position(pos)` - Convert to line and column numbers

This hierarchical structure allows us to precisely analyze and manipulate various parts of Go code, from entire files to individual identifiers, all of which can be found as corresponding nodes in the AST.