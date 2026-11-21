# CodeSnap Language Reference Manual

CodeSnap is a structured, imperative mini programming language designed for computer science students and educators to study compiler construction and formal language theory.

---

## 1. Program Structure

Every CodeSnap program begins with `START` and terminates with `STOP`. Code outside these boundary keywords is rejected as a syntax error.

```codesnap
START
    # Statements go here
    PRINT "Hello, CodeSnap!"
STOP
```

---

## 2. Comments

Single-line comments begin with the `#` character and extend to the end of the line. Comments are discarded during lexical analysis.

```codesnap
# This is a full-line comment
LET x = 10 # This is an inline comment
```

---

## 3. Data Types

CodeSnap supports four primitive data types:

| Type | Description | Examples |
| :--- | :--- | :--- |
| **INTEGER** | Signed whole numbers | `42`, `-17`, `0` |
| **FLOAT** | Double-precision decimal numbers | `3.1415`, `89.5`, `0.05` |
| **STRING** | Text enclosed in double quotes | `"Vikash"`, `"Compiler Design"` |
| **BOOLEAN** | Logical truth values | `TRUE`, `FALSE` |

---

## 4. Variable Declaration & Assignment

### Declaration (`LET`)
Variables must be declared with the `LET` keyword prior to use:
```codesnap
LET name = "Vikash"
LET age = 21
LET gpa = 3.85
LET is_enrolled = TRUE
```

Attempting to declare the same variable twice in the same scope raises a **Semantic Error**.

### Re-Assignment
Existing variables can be modified without the `LET` keyword:
```codesnap
age = 22
gpa = 3.90
```

Attempting to assign to an undeclared variable raises a **Semantic Error**.

---

## 5. Standard Output (`PRINT`)

The `PRINT` statement evaluates an expression and streams the result to the console:
```codesnap
PRINT "The calculated score is:"
PRINT score + 10
```

---

## 6. Control Flow

### Conditional Execution (`IF` / `ELSE` / `END`)
Conditional branching evaluates a boolean expression:

```codesnap
IF age >= 18
    PRINT "Eligible to vote"
ELSE
    PRINT "Not eligible yet"
END
```

The `ELSE` block is optional:
```codesnap
IF score > 90
    PRINT "Grade: A"
END
```

### Iterative Loops

#### While Loop (`WHILE` ... `END`)
Repeats a statement block while the condition evaluates to `TRUE`:
```codesnap
LET counter = 1
WHILE counter <= 5
    PRINT counter
    counter = counter + 1
END
```

#### For Loop (`FOR` ... `TO` ... `END`)
Iterates an integer index over an inclusive range:
```codesnap
FOR i = 1 TO 5
    PRINT i
END
```

An optional `STEP` clause can be provided:
```codesnap
FOR i = 10 TO 0 STEP -2
    PRINT i
END
```

---

## 7. Operators & Expressions

### Arithmetic Operators
- `+` : Addition or String Concatenation (`"Code" + "Snap"` $\to$ `"CodeSnap"`)
- `-` : Subtraction
- `*` : Multiplication
- `/` : Floating-point Division (Guarded against division by zero)
- `%` : Modulo (Remainder)

### Relational Operators
- `==` : Equality
- `!=` : Inequality
- `<`  : Strictly less than
- `<=` : Less than or equal to
- `>`  : Strictly greater than
- `>=` : Greater than or equal to

### Logical Operators
- `AND` : Logical conjunction (Short-circuiting)
- `OR`  : Logical disjunction (Short-circuiting)
- `NOT` : Logical negation (Unary)
