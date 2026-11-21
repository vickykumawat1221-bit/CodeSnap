# CodeSnap: Mini Programming Language Compiler & IDE

> **Department of Computer Science & Engineering (CSE)**  
> **Theory of Computation (TOC) Mini-Project**

CodeSnap is an interactive, web-based compiler and IDE for a custom imperative mini programming language designed from scratch in Python. It provides visual, transparent insight into every phase of compiler construction—from regular expressions and finite automata to recursive descent parsing, symbol tables, abstract syntax tree generation, and safe tree-walking interpretation.

---

## 🌟 Key Features

- **Custom Programming Language:** Keywords `START`, `STOP`, `LET`, `PRINT`, `IF`, `ELSE`, `WHILE`, `FOR`, `TO`, `STEP`, `END`, `TRUE`, `FALSE`, `AND`, `OR`, `NOT`.
- **Lexical Analysis (Scanner):** Character scanning and regex-based tokenization with line/column tracking. Detects lexical errors with remediation hints.
- **Syntax Analysis (Parser):** Unambiguous Recursive Descent Parser implementing an $LL(1)$ Context-Free Grammar with precedence climbing.
- **Semantic Analyzer:** Hierarchical Symbol Table validating variable declarations, scope levels, duplicate identifiers, type checking, and static division by zero.
- **Abstract Syntax Tree (AST):** Hierarchical syntactic representations visualized in real-time as an interactive SVG tree diagram or inspectable JSON.
- **Tree-Walking Interpreter:** Safe, direct AST evaluation without `eval()` or `exec()`. Includes infinite loop prevention (step bounding).
- **Theory of Computation Automata Studio:** Interactive Deterministic Finite Automata (DFA) simulator demonstrating state transitions, formal 5-tuples $(Q, \Sigma, \delta, q_0, F)$, and transition tables.
- **Professional Dark IDE:** VS Code / Replit-inspired theme with custom syntax highlighting, line numbers gutter, and diagnostic error cards.
- **17 Ready-to-Run Sample Programs:** Spanning Hello World, arithmetic, conditionals, loops, algorithms (Factorial, Fibonacci), and error diagnostics.

---

## 🏗️ Compiler Architecture

```
                  +-----------------------+
                  |  SOURCE CODE STRING   |
                  +-----------------------+
                              |
                              v
                  +-----------------------+
                  |   LEXICAL ANALYZER    |  <-- Regular Expressions & DFAs
                  +-----------------------+
                              |
                              v [Token Stream]
                  +-----------------------+
                  |    SYNTAX ANALYZER    |  <-- Recursive Descent Parser (CFG)
                  +-----------------------+
                              |
                              v [Abstract Syntax Tree]
                  +-----------------------+
                  |   SEMANTIC ANALYZER   |  <-- Symbol Table & Scope Resolution
                  +-----------------------+
                              |
                              v [Decorated AST]
                  +-----------------------+
                  | TREE-WALK INTERPRETER |  <-- Safe AST Execution & Step Limits
                  +-----------------------+
                              |
                              v
                  +-----------------------+
                  |    CONSOLE OUTPUT     |
                  +-----------------------+
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### 2. Run the Application
Launch the compiler server:
```bash
python3 run.py
```

Open your browser at:
```
http://localhost:5000
```

### 3. Run Automated Unit Tests
Run the comprehensive test suite (33 tests):
```bash
python3 -m unittest discover -s tests -v
```

---

## 📂 Project Structure

```
CodeSnap/
├── backend/
│   ├── app.py            # Flask REST API server & static file host
│   ├── lexer.py          # Lexical Analyzer (Scanner)
│   ├── tokens.py         # Token definitions & TokenType enum
│   ├── parser.py         # Recursive Descent Parser
│   ├── grammar.py        # Formal Context-Free Grammar specification
│   ├── ast_nodes.py      # Abstract Syntax Tree node classes
│   ├── semantic.py       # Semantic Analyzer & type checker
│   ├── symbol_table.py   # Hierarchical Symbol Table
│   ├── interpreter.py    # Tree-Walking AST Interpreter
│   ├── automata.py       # DFA simulation engine (5-tuple & trace)
│   ├── errors.py         # Error hierarchy (Lexical, Syntax, Semantic, Runtime)
│   └── examples.py       # Sample program library (17 programs)
│
├── frontend/
│   ├── index.html        # IDE interface & dashboard layout
│   ├── css/
│   │   └── style.css     # Dark IDE theme & visualizer styles
│   ├── js/
│   │   ├── api.js        # REST API client
│   │   ├── editor.js     # Code editor with syntax highlighting & line numbers
│   │   ├── visualizer.js # Interactive SVG AST & DFA graph renderers
│   │   └── app.js        # Main UI orchestrator & event controller
│   └── assets/           # Static icons and assets
│
├── tests/
│   ├── test_lexer.py       # Unit tests for scanner
│   ├── test_parser.py      # Unit tests for parser & CFG
│   ├── test_semantic.py    # Unit tests for semantic analyzer
│   ├── test_interpreter.py # Unit tests for interpreter & runtime
│   └── test_api.py         # Integration tests for REST endpoints
│
├── docs/
│   ├── grammar.md           # Formal CFG in BNF & operator precedence table
│   ├── language_reference.md# CodeSnap language manual
│   ├── architecture.md      # Detailed compiler architecture documentation
│   ├── toc_theory.md        # Academic Theory of Computation alignment
│   └── project_report.md    # Complete 24-section undergraduate project report
│
├── requirements.txt      # Python dependencies (Flask)
├── run.py                # Server launcher script
├── README.md             # Project documentation
└── .gitignore            # Git exclusion rules
```

---

## 💻 Sample Program in CodeSnap

```codesnap
START
# Variable declaration with LET
LET name = "Vikash"
LET age = 21
LET marks = 89.5

PRINT "Student Name:"
PRINT name

# Conditional evaluation
IF age >= 18 AND marks >= 40
    PRINT "Status: Qualified & Passed!"
ELSE
    PRINT "Status: Not Qualified"
END

# Range loop
FOR i = 1 TO 3
    PRINT i * 10
END
STOP
```

**Output:**
```
Student Name:
Vikash
Status: Qualified & Passed!
10
20
30
```

---

## 🎓 Theory of Computation Mapping

1. **Regular Languages (Type-3):** Tokens (identifiers, numbers, operators) are regular expressions recognized by Deterministic Finite Automata (DFA).
2. **Context-Free Grammars (Type-2):** CodeSnap syntax requires pushdown storage for balancing constructs (`START...STOP`, `IF...END`, `(...)`), which cannot be recognized by finite automata alone.
3. **Pumping Lemma Justification:** Demonstrates why nesting cannot be parsed with pure regular expressions.
4. **Halting Problem:** Bounded execution illustrates the theoretical impossibility of statically predicting loop termination.

---

## 📜 Academic Attribution
Developed as a Computer Science & Engineering Theory of Computation Mini-Project.
Designed for educational transparency, correctness, and pedagogical impact.
