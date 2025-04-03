# Ent Framework in Go: A Modern Entity Framework

## Overview
Ent is an **entity framework** for Go that simplifies building and maintaining applications with complex data models. Developed by Facebook (now Meta), it provides a type-safe, expressive API for interacting with databases while maintaining the simplicity and performance Go is known for.

## Key Features

1. **Schema-as-Code**:
    - Define your data model directly in Go code
    - Compile-time safety for your data structures
    - No need for separate SQL migration files (though it supports them)

2. **Code Generation**:
    - Generates type-safe Go code from your schema definitions
    - Produces clean, idiomatic Go code
    - Reduces boilerplate code significantly

3. **Database Support**:
    - MySQL, PostgreSQL, SQLite, Gremlin (graph)
    - CockroachDB, TiDB support via PostgreSQL dialect

## Basic Example

```go
// Define a User entity
func (User) Fields() []ent.Field {
    return []ent.Field{
        field.String("name"),
        field.Int("age").Optional(),
        field.Time("created_at").
            Default(time.Now),
    }
}

// Generate a client
client, err := ent.Open("sqlite3", "file:ent?mode=memory&cache=shared&_fk=1")
if err != nil {
    log.Fatalf("failed opening connection to sqlite: %v", err)
}
defer client.Close()

// Create a user
user := client.User.
    Create().
    SetName("Alice").
    SetAge(30).
    SaveX(context.Background())
```

## Why Use Ent?

1. **Productivity**:
    - Rapid development with code generation
    - Automatic CRUD operations
    - Built-in support for eager loading, pagination

2. **Type Safety**:
    - Compile-time checking of queries
    - No SQL injection vulnerabilities from string concatenation

3. **Extensibility**:
    - Hooks for business logic
    - Privacy layer for data access control
    - Custom templates for generated code

4. **Graph Features**:
    - Easy modeling of relationships (edges)
    - Efficient querying of connected data

## Comparison with Alternatives

Compared to GORM or sqlx:
- More structured approach
- Better type safety
- More explicit about relationships
- More code generation (less runtime reflection)

## Getting Started

1. Install the CLI:
```bash
go install entgo.io/ent/cmd/ent@latest
```

2. Create a new schema:
```bash
ent init User
```

3. Generate code:
```bash
go generate ./ent
```

Ent is particularly well-suited for applications with complex data models and relationships, where maintaining type safety and reducing boilerplate are priorities.

---

# Using Ent with PostgreSQL

Ent integrates seamlessly with PostgreSQL, offering full support for its features including advanced data types, transactions, and performance optimizations. Here's how to set up and use Ent with PostgreSQL:

## 1. Installation and Setup

First, ensure you have the Ent CLI installed:

```bash
go install entgo.io/ent/cmd/ent@latest
```

Add the PostgreSQL driver to your project:

```bash
go get github.com/lib/pq
# or for more modern applications:
go get github.com/jackc/pgx/v5
```

## 2. Initialize Your Schema

Create a new Ent schema:

```bash
ent init User
```

This generates a schema file at `ent/schema/user.go`.

## 3. Define Your PostgreSQL-Compatible Schema

Edit your schema with PostgreSQL-specific features:

```go
// ent/schema/user.go
package schema

import (
	"entgo.io/ent"
	"entgo.io/ent/schema/field"
	"entgo.io/ent/schema/index"
)

type User struct {
	ent.Schema
}

func (User) Fields() []ent.Field {
	return []ent.Field{
		field.String("username").Unique(),
		field.String("email").Unique(),
		field.Text("bio").Optional(),
		field.JSON("preferences", map[string]interface{}{}).Optional(),
		field.Time("created_at").Default(time.Now),
		field.Enum("status").Values("active", "inactive", "banned"),
		field.Array("tags").OfType(string).Optional(), // PostgreSQL arrays
	}
}

func (User) Indexes() []ent.Index {
	return []ent.Index{
		index.Fields("username", "email"),
	}
}
```

## 4. Generate Your Code

Run the code generator:

```bash
go generate ./ent
```

## 5. Connect to PostgreSQL

Create a client connection:

```go
package main

import (
	"context"
	"log"
	"os"

	"<your-project>/ent"
	
	_ "github.com/lib/pq" // or "github.com/jackc/pgx/v5/stdlib"
)

func main() {
	// Connection string format: "postgresql://user:pass@host:port/db?sslmode=disable"
	client, err := ent.Open("postgres", os.Getenv("DATABASE_URL"))
	if err != nil {
		log.Fatalf("failed opening connection to postgres: %v", err)
	}
	defer client.Close()
	
	// Run migrations
	if err := client.Schema.Create(context.Background()); err != nil {
		log.Fatalf("failed creating schema resources: %v", err)
	}
}
```

## 6. Basic CRUD Operations

### Create
```go
user, err := client.User.
	Create().
	SetUsername("alice").
	SetEmail("alice@example.com").
	SetStatus("active").
	Save(context.Background())
```

### Query
```go
// Get by ID
user, err := client.User.Get(ctx, 1)

// Query with conditions
users, err := client.User.
	Query().
	Where(user.StatusEQ("active")).
	All(ctx)
```

### Update
```go
user, err := client.User.
	UpdateOneID(1).
	SetBio("Hello world!").
	Save(ctx)
```

### Delete
```go
err := client.User.
	DeleteOneID(1).
	Exec(ctx)
```

## PostgreSQL-Specific Features

### 1. JSON/JSONB Support
```go
// In your schema
field.JSON("preferences", map[string]interface{}{}).Optional()

// Usage
user, err := client.User.
	Create().
	SetPreferences(map[string]interface{}{
		"theme": "dark",
		"notifications": true,
	}).
	Save(ctx)
```

### 2. Array Types
```go
// In your schema
field.Array("tags").OfType(string).Optional()

// Usage
user, err := client.User.
	Create().
	SetTags([]string{"golang", "backend", "ent"}).
	Save(ctx)
```

### 3. Custom Types (ENUM, UUID)
```go
// For UUIDs (requires additional setup)
field.UUID("id", uuid.UUID{}).Default(uuid.New)

// For custom ENUMs
field.Enum("role").Values("user", "admin", "moderator")
```

## Advanced PostgreSQL Features

### Transactions
```go
tx, err := client.Tx(ctx)
if err != nil {
	return err
}

user, err := tx.User.Create().SetUsername("bob").Save(ctx)
if err != nil {
	return tx.Rollback()
}

// Commit the transaction
return tx.Commit()
```

### Full-Text Search
```go
// Requires creating a custom migration to add the search index
users, err := client.User.Query().
	Where(func(s *sql.Selector) {
		s.Where(sql.ExprP("to_tsvector('english', bio) @@ to_tsquery('english', ?)", "search term"))
	}).
	All(ctx)
```

## Performance Tips

1. **Connection Pooling**: Configure in the connection string:
   ```go
   "postgres://user:pass@host:port/db?sslmode=disable&pool_max_conns=10"
   ```

2. **Use Prepared Statements**: Ent automatically prepares statements for common operations.

3. **Batch Operations**: For bulk inserts/updates:
   ```go
   bulk := make([]*ent.UserCreate, 100)
   for i := range bulk {
       bulk[i] = client.User.Create().SetUsername(fmt.Sprintf("user%d", i))
   }
   users, err := client.User.CreateBulk(bulk...).Save(ctx)
   ```

## Migrations

For production systems, you'll want more control over migrations:

1. Enable migration locking:
   ```go
   if err := client.Schema.Create(
       ctx,
       migrate.WithGlobalUniqueID(true),
       migrate.WithDropIndex(true),
       migrate.WithDropColumn(true),
   ); err != nil {
       // handle error
   }
   ```

2. For advanced migration needs, use `atlas` (Ent's migration engine):
   ```bash
   go run ariga.io/atlas/cmd/atlas migrate diff --env=local
   ```

Ent with PostgreSQL provides a powerful combination for building type-safe, performant applications while leveraging PostgreSQL's advanced features.