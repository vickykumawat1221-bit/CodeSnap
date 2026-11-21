"""
examples.py - Sample program library for CodeSnap.
Provides ready-to-run programs demonstrating core language features,
TOC concepts, control structures, and error diagnostics.
"""

from typing import List, Dict, Any

EXAMPLES: List[Dict[str, Any]] = [
    {
        "id": "hello_world",
        "title": "1. Hello World",
        "category": "Basic",
        "description": "Fundamental introductory program outputting a greeting message.",
        "code": """START
# Introductory CodeSnap Program
PRINT "Hello, World! Welcome to CodeSnap."
PRINT "TOC Mini Programming Language Compiler"
STOP"""
    },
    {
        "id": "variables",
        "title": "2. Variable Declarations & Types",
        "category": "Basic",
        "description": "Demonstrates declaration and assignment of Integer, Float, String, and Boolean data types.",
        "code": """START
# Variable declarations with LET
LET name = "Vikash"
LET age = 21
LET marks = 89.5
LET passed = TRUE

# Output values
PRINT name
PRINT age
PRINT marks
PRINT passed
STOP"""
    },
    {
        "id": "addition",
        "title": "3. Addition of Two Numbers",
        "category": "Arithmetic",
        "description": "Demonstrates arithmetic addition and variable evaluation.",
        "code": """START
# Addition of two variables
LET a = 20
LET b = 10
LET result = a + b
PRINT "Result of addition:"
PRINT result
STOP"""
    },
    {
        "id": "multiplication",
        "title": "4. Multiplication Calculator",
        "category": "Arithmetic",
        "description": "Demonstrates arithmetic multiplication, floating-point math, and precedence.",
        "code": """START
# Arithmetic operations and operator precedence
LET length = 15.5
LET width = 4
LET area = length * width
PRINT "Calculated Area:"
PRINT area
STOP"""
    },
    {
        "id": "even_odd",
        "title": "5. Even or Odd Checker",
        "category": "Conditionals",
        "description": "Uses modulo (%) operator and IF-ELSE conditional to test divisibility.",
        "code": """START
# Check if a number is even or odd
LET number = 14
LET remainder = number % 2

IF remainder == 0
    PRINT "Number is EVEN"
ELSE
    PRINT "Number is ODD"
END
STOP"""
    },
    {
        "id": "largest_two",
        "title": "6. Largest of Two Numbers",
        "category": "Conditionals",
        "description": "Compares two numbers using relational operators (> and ==).",
        "code": """START
# Determine maximum of two numbers
LET x = 45
LET y = 78

IF x > y
    PRINT "x is greater than y"
ELSE
    IF x == y
        PRINT "x and y are equal"
    ELSE
        PRINT "y is greater than x"
    END
END
STOP"""
    },
    {
        "id": "if_else_demo",
        "title": "7. Age Eligibility (IF / ELSE)",
        "category": "Conditionals",
        "description": "Evaluates relational condition to determine voting or participation eligibility.",
        "code": """START
LET age = 21

IF age >= 18
    PRINT "Eligible"
ELSE
    PRINT "Not Eligible"
END
STOP"""
    },
    {
        "id": "while_loop",
        "title": "8. While Loop Counter",
        "category": "Loops",
        "description": "Iterative loop incrementing a counter from 1 to 5.",
        "code": """START
LET count = 1

WHILE count <= 5
    PRINT count
    count = count + 1
END
STOP"""
    },
    {
        "id": "for_loop",
        "title": "9. For Loop Iteration",
        "category": "Loops",
        "description": "Demonstrates FOR loop with automatic counter increment.",
        "code": """START
# Range loop from 1 to 5
FOR i = 1 TO 5
    PRINT i
END
STOP"""
    },
    {
        "id": "logical_expressions",
        "title": "10. Logical Operations (AND, OR, NOT)",
        "category": "Logic",
        "description": "Compound boolean conditions combining multiple relational comparisons.",
        "code": """START
LET age = 21
LET marks = 85

IF age >= 18 AND marks >= 40
    PRINT "Qualified"
ELSE
    PRINT "Not Qualified"
END

LET is_weekend = FALSE
IF NOT is_weekend
    PRINT "It is a weekday. Keep coding!"
END
STOP"""
    },
    {
        "id": "factorial",
        "title": "11. Factorial Calculator",
        "category": "Algorithms",
        "description": "Computes factorial of a given integer using a WHILE loop.",
        "code": """START
# Factorial calculation: N!
LET n = 5
LET fact = 1
LET i = 1

WHILE i <= n
    fact = fact * i
    i = i + 1
END

PRINT "Factorial of 5:"
PRINT fact
STOP"""
    },
    {
        "id": "fibonacci",
        "title": "12. Fibonacci Series",
        "category": "Algorithms",
        "description": "Generates the first 7 numbers of the Fibonacci sequence.",
        "code": """START
# Generate Fibonacci numbers
LET terms = 7
LET a = 0
LET b = 1
LET count = 1

PRINT "Fibonacci sequence:"
WHILE count <= terms
    PRINT a
    LET next_term = a + b
    a = b
    b = next_term
    count = count + 1
END
STOP"""
    },
    {
        "id": "sum_n",
        "title": "13. Sum of Natural Numbers",
        "category": "Loops",
        "description": "Calculates the sum of numbers from 1 to 10 using a FOR loop.",
        "code": """START
# Sum = 1 + 2 + ... + 10
LET total = 0

FOR num = 1 TO 10
    total = total + num
END

PRINT "Sum of 1 to 10:"
PRINT total
STOP"""
    },
    {
        "id": "error_lexical",
        "title": "14. [Demo] Lexical Error Detection",
        "category": "Error Diagnostics",
        "description": "Demonstrates detection of illegal character '@' during scanning.",
        "code": """START
# This demonstrates Lexical Error detection
LET score = 95
LET bonus = @ 10
PRINT score + bonus
STOP"""
    },
    {
        "id": "error_syntax",
        "title": "15. [Demo] Syntax Error Detection",
        "category": "Error Diagnostics",
        "description": "Demonstrates detection of missing 'STOP' keyword violating the CFG.",
        "code": """START
LET message = "Missing STOP keyword test"
PRINT message
# Notice STOP is omitted intentionally"""
    },
    {
        "id": "error_semantic",
        "title": "16. [Demo] Semantic Error Detection",
        "category": "Error Diagnostics",
        "description": "Demonstrates detection of undeclared variable 'salary'.",
        "code": """START
LET age = 21
# Variable 'salary' is used without prior declaration
PRINT salary
STOP"""
    },
    {
        "id": "error_runtime",
        "title": "17. [Demo] Runtime Error (Div by Zero)",
        "category": "Error Diagnostics",
        "description": "Demonstrates runtime division by zero exception handling.",
        "code": """START
LET total = 100
LET count = 0
# Runtime evaluation will trigger Division by Zero
LET average = total / count
PRINT average
STOP"""
    }
]


def get_all_examples() -> List[Dict[str, Any]]:
    return EXAMPLES


def get_example_by_id(example_id: str) -> Dict[str, Any]:
    for ex in EXAMPLES:
        if ex["id"] == example_id:
            return ex
    return EXAMPLES[0]
