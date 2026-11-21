# CodeSnap Compiler Pipeline & Architecture

## 1. High-Level Compiler Pipeline

```
  +-----------------------------------------------------------+
  |                   SOURCE CODE STRING                      |
  +-----------------------------------------------------------+
                                |
                                v
  +-----------------------------------------------------------+
  |              PHASE 1: LEXICAL ANALYZER                    |
  |  - Regular expressions & DFA simulation                   |
  |  - Character scanning, line/column tracking               |
  |  - Lexical error detection (illegal characters)           |
  +-----------------------------------------------------------+
                                |
                                v [Token Stream]
  +-----------------------------------------------------------+
  |               PHASE 2: SYNTAX ANALYZER                    |
  |  - Recursive Descent Parser                               |
  |  - Context-Free Grammar (LL(1) lookahead)                 |
  |  - Precedence climbing expression parsing                 |
  +-----------------------------------------------------------+
                                |
                                v [Abstract Syntax Tree]
  +-----------------------------------------------------------+
  |              PHASE 3: SEMANTIC ANALYZER                   |
  |  - Scope hierarchy & Symbol Table construction            |
  |  - Variable declaration & duplicate detection             |
  |  - Type checking & static division-by-zero validation     |
  +-----------------------------------------------------------+
                                |
                                v [Decorated AST + Symbol Table]
  +-----------------------------------------------------------+
  |              PHASE 4: TREE-WALKING INTERPRETER            |
  |  - AST Visitor pattern execution (Safe, no eval/exec)     |
  |  - Bounded step execution (Infinite loop detection)       |
  |  - Stdout capturing & Execution time benchmarking         |
  +-----------------------------------------------------------+
                                |
                                v
  +-----------------------------------------------------------+
  |                OUTPUT STREAM / TERMINAL                   |
  +-----------------------------------------------------------+
```

---

## 2. Module Specifications

| Module | Location | Primary Responsibility |
| :--- | :--- | :--- |
| `tokens.py` | `backend/tokens.py` | Token types, keywords map, and TOC pattern explanations. |
| `lexer.py` | `backend/lexer.py` | Lexical analyzer recognizing tokens and handling comments/strings. |
| `parser.py` | `backend/parser.py` | Recursive descent parser producing AST nodes. |
| `ast_nodes.py` | `backend/ast_nodes.py` | Formal AST classes with JSON serialization for visualizer. |
| `semantic.py` | `backend/semantic.py` | Semantic checker enforcing scope, types, and conditions. |
| `symbol_table.py` | `backend/symbol_table.py` | Hierarchical symbol table managing scopes and types. |
| `interpreter.py` | `backend/interpreter.py` | Pure AST tree-walking interpreter with execution safety guards. |
| `automata.py` | `backend/automata.py` | Deterministic Finite Automata engine with 5-tuples and string simulation. |
| `app.py` | `backend/app.py` | Flask REST API server exposing endpoints and serving IDE frontend. |
| `visualizer.js` | `frontend/js/visualizer.js` | SVG-based AST tree visualizer and interactive DFA simulator. |

---

## 3. Key Design Decisions

1. **No External Interpreters:** All language parsing, validation, and execution is written entirely in custom Python without third-party parser generators (e.g. Yacc, Lex, ANTLR) or Python's `eval()` / `exec()`.
2. **Defensive Infinite Loop Prevention:** The interpreter tracks total AST execution steps and terminates with a detailed `RuntimeError` if an iteration limit (50,000 steps) is exceeded.
3. **Decoupled Architecture:** Each phase functions independently. Tokens can be inspected independently of AST, and AST can be inspected independently of execution.
4. **Theory of Computation Alignment:** Includes explicit DFA state transition engines, transition tables, and formal 5-tuple representations.
