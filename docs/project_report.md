# CodeSnap: Design and Implementation of a Mini Programming Language Compiler
**Department of Computer Science & Engineering**  
**Theory of Computation (TOC) Mini-Project Report**

---

## Table of Contents
1. Abstract
2. Introduction
3. Problem Statement
4. Objectives
5. Existing System
6. Proposed System
7. Software and Hardware Requirements
8. System Architecture
9. Compiler Design
10. Language Specification
11. Context-Free Grammar (CFG)
12. Lexical Analysis (Phase 1)
13. Syntax Analysis (Phase 2)
14. Semantic Analysis (Phase 3)
15. Abstract Syntax Tree Generation (Phase 4)
16. Interpreter Design (Phase 5)
17. Automata Concepts and TOC Alignment
18. Implementation Details
19. Testing and Validation
20. Results and Performance Metrics
21. Limitations
22. Future Scope
23. Conclusion
24. References

---

## 1. Abstract

Understanding the theoretical foundations of computer science—specifically formal languages, automata theory, and compiler design—presents significant pedagogical challenges when studied purely through abstract mathematics. **CodeSnap** bridges this gap by providing a fully functional, interactive, web-based compiler and IDE for a custom imperative programming language. Developed in Python and modern web standards, CodeSnap demonstrates each distinct phase of modern language translation: Lexical Analysis via Regular Expressions and Deterministic Finite Automata (DFA), Syntax Analysis via a Recursive Descent Parser implementing a Context-Free Grammar (CFG), Semantic Analysis with hierarchical Symbol Table management, Abstract Syntax Tree (AST) construction, and safe tree-walking interpretation without reliance on dynamic evaluation functions like Python's `eval()` or `exec()`. An interactive Theory of Computation Studio provides step-by-step state transition animations and formal 5-tuple demonstrations, establishing CodeSnap as both an instructional tool and a rigorous undergraduate computer engineering project.

---

## 2. Introduction

Compilers form the foundational bedrock of computing, bridging high-level human problem-solving and low-level machine execution. The study of compilers synthesizes topics across discrete mathematics, formal grammars, automata theory, and software engineering.

CodeSnap is developed as a CSE undergraduate Theory of Computation mini-project. It introduces the **CodeSnap programming language**, featuring explicit keywords (`START`, `STOP`, `LET`, `PRINT`, `IF`, `WHILE`, `FOR`), strong type inference across Integer, Float, String, and Boolean primitives, compound boolean logic, and structured control flow. Rather than delegating language parsing to existing engines, CodeSnap implements an autonomous, modular compilation pipeline in Python from scratch.

---

## 3. Problem Statement

Theoretical courses in Computer Science frequently suffer from abstraction disconnect:
- Students calculate DFA state transitions and write Context-Free Grammars on paper without observing how these mathematical constructs govern practical software compilers.
- Commercial compilers (GCC, Clang, Python, V8) are vast industrial codebases spanning millions of lines of code, making it difficult for learners to isolate individual translation phases.
- Online playgrounds typically run existing languages (C++, Python) as black-box execution environments without exposing intermediate data structures such as Token streams, Parse Trees, ASTs, and Symbol Tables.

There is a clear educational need for a self-contained, transparent mini-compiler with an intuitive visual dashboard that explicitly surfaces every compiler phase.

---

## 4. Objectives

The primary objectives of the CodeSnap project are:
1. **Design a Custom Programming Language:** Define consistent lexical tokens, operators, and grammatical productions.
2. **Implement Lexical Analysis:** Tokenize raw source text into typed tokens using regular expressions while tracking 1-indexed line and column coordinates.
3. **Formalize Automata Theory:** Model token recognition as Deterministic Finite Automata (DFA) with formal 5-tuples and step-by-step string validation.
4. **Develop a Syntax Analyzer:** Construct a non-backtracking Recursive Descent Parser based on an unambiguous Context-Free Grammar.
5. **Construct an Abstract Syntax Tree (AST):** Convert parse trees into clean, hierarchical AST structures capable of interactive SVG visualization.
6. **Enforce Semantic Rules:** Perform static validation of variable declaration, scope boundaries, duplicate names, type compatibility, and static division by zero.
7. **Build a Safe Tree-Walking Interpreter:** Execute the program directly on AST nodes without using dynamic code evaluation.
8. **Provide a Modern IDE:** Present the compiler within a dark-themed interface with sample programs, live syntax highlighting, and an automata simulation workbench.

---

## 5. Existing System

Traditional approaches in undergraduate TOC and Compiler Construction laboratories include:
- Manual state transition drawing on pen and paper.
- Using complex toolchains like Flex (Lex) and Bison (Yacc) that generate impenetrable C code.
- Utilizing commercial online IDEs (Replit, Compiler Explorer) that do not expose intermediate ASTs, symbol tables, or DFA traces.

**Disadvantages of Existing Systems:**
- Steep learning curves obscured by external build tools.
- Black-box execution concealing intermediate representations.
- Lack of interactive visual feedback during error conditions.

---

## 6. Proposed System

The proposed **CodeSnap Compiler and IDE** provides:
- A completely transparent pipeline where every stage produces structured, inspectable JSON data.
- Visual token explorer detailing the regex pattern and DFA rule used to match each lexeme.
- Interactive SVG AST explorer with node inspection.
- Symbol table viewer displaying identifier names, inferred data types, values, and scope hierarchies.
- Automata Studio providing interactive string testing on DFAs with animated state transitions.
- Categorized diagnostics offering actionable remediation hints for Lexical, Syntax, Semantic, and Runtime errors.

---

## 7. Software and Hardware Requirements

### Software Requirements
- **Operating System:** macOS, Linux, or Windows 10/11
- **Language/Runtime:** Python 3.10+ (tested on Python 3.13)
- **Web Framework:** Flask 3.0+
- **Frontend Technologies:** HTML5, CSS3, JavaScript (ES6+), Scalable Vector Graphics (SVG)
- **Editor Fonts:** Fira Code, JetBrains Mono, Inter

### Hardware Requirements
- **Processor:** Dual-Core x86_64 or Apple Silicon CPU (1.5 GHz or higher)
- **RAM:** Minimum 2 GB (4 GB recommended)
- **Storage:** 100 MB free disk space

---

## 8. System Architecture

The CodeSnap architecture comprises three decoupled layers:

```
[ CLIENT BROWSER: Frontend IDE ]
       |
       | HTTP / REST API (JSON)
       v
[ FLASK APPLICATION SERVER: backend/app.py ]
       |
       +---> Lexical Analyzer (backend/lexer.py)
       |
       +---> Recursive Descent Parser (backend/parser.py)
       |
       +---> Semantic Analyzer (backend/semantic.py)
       |
       +---> Tree-Walking Interpreter (backend/interpreter.py)
       |
       +---> Automata Simulation Engine (backend/automata.py)
```

Data flows unidirectionally from source code text through lexical, syntax, and semantic validation into the interpreter.

---

## 9. Compiler Design

CodeSnap adheres to classical compiler design principles:
1. **Front-End (Analysis):** Lexer, Parser, and Semantic Analyzer produce an intermediate decorated Abstract Syntax Tree.
2. **Back-End (Synthesis/Execution):** The Tree-Walking Interpreter evaluates AST nodes in the context of scoped runtime environments.

---

## 10. Language Specification

### Keywords
`START`, `STOP`, `LET`, `PRINT`, `IF`, `ELSE`, `WHILE`, `FOR`, `TO`, `STEP`, `END`, `TRUE`, `FALSE`, `AND`, `OR`, `NOT`

### Types
- **INTEGER:** 32-bit/arbitrary precision signed integers.
- **FLOAT:** Double-precision IEEE 754 floating point.
- **STRING:** UTF-8 character sequences delimited by double quotes.
- **BOOLEAN:** Truth values `TRUE` and `FALSE`.

### Operators
- **Arithmetic:** `+`, `-`, `*`, `/`, `%`
- **Relational:** `==`, `!=`, `<`, `<=`, `>`, `>=`
- **Logical:** `AND`, `OR`, `NOT`
- **Assignment:** `=`

---

## 11. Context-Free Grammar (CFG)

Formally specified as $G = (V, \Sigma, R, S)$:

```bnf
<Program>          ::= 'START' <StatementList> 'STOP'
<StatementList>    ::= <Statement> <StatementList> | ε
<Statement>        ::= <VarDeclaration> | <Assignment> | <PrintStatement>
                     | <IfStatement> | <WhileStatement> | <ForStatement>
<VarDeclaration>   ::= 'LET' IDENTIFIER '=' <Expression>
<Assignment>       ::= IDENTIFIER '=' <Expression>
<PrintStatement>   ::= 'PRINT' <Expression>
<IfStatement>      ::= 'IF' <Expression> <StatementList> [ 'ELSE' <StatementList> ] 'END'
<WhileStatement>   ::= 'WHILE' <Expression> <StatementList> 'END'
<ForStatement>     ::= 'FOR' IDENTIFIER '=' <Expression> 'TO' <Expression> [ 'STEP' <Expression> ] <StatementList> 'END'
<Expression>       ::= <LogicalOr>
<LogicalOr>        ::= <LogicalAnd> ( 'OR' <LogicalAnd> )*
<LogicalAnd>       ::= <LogicalNot> ( 'AND' <LogicalNot> )*
<LogicalNot>       ::= 'NOT' <LogicalNot> | <Comparison>
<Comparison>       ::= <ArithmeticExpr> [ ( '==' | '!=' | '<' | '<=' | '>' | '>=' ) <ArithmeticExpr> ]
<ArithmeticExpr>   ::= <Term> ( ( '+' | '-' ) <Term> )*
<Term>             ::= <Factor> ( ( '*' | '/' | '%' ) <Factor> )*
<Factor>           ::= ( '+' | '-' ) <Factor> | <Primary>
<Primary>          ::= INTEGER | FLOAT | STRING | 'TRUE' | 'FALSE' | IDENTIFIER | '(' <Expression> ')'
```

---

## 12. Lexical Analysis (Phase 1)

The scanner reads continuous characters and yields discrete token records:
$$\text{Token} = \langle \text{Type}, \text{Value}, \text{Lexeme}, \text{Line}, \text{Column} \rangle$$

Whitespace and `#` comments are filtered. Unterminated strings, illegal symbols (e.g. `@`, `$`), and malformed numbers are trapped and reported as `LexicalError`.

---

## 13. Syntax Analysis (Phase 2)

Syntax analysis implements a recursive descent parser. Because each production begins with distinct tokens (or lookahead $\le 1$), the grammar is $LL(1)$ and avoids backtracking. Operator precedence is enforced through production nesting:
$\text{Primary} \succ \text{Unary} \succ \text{Multiplicative} \succ \text{Additive} \succ \text{Relational} \succ \text{Logical NOT} \succ \text{Logical AND} \succ \text{Logical OR}$.

---

## 14. Semantic Analysis (Phase 3)

The semantic analyzer traverses the AST with an environment-based Symbol Table:
- **Undeclared Variables:** Identifiers must be declared with `LET` before reading.
- **Duplicate Declarations:** Multiple `LET` statements for the same name in the same scope are prohibited.
- **Type Checking:** Ensures boolean expressions for `IF` and `WHILE` conditions, numeric operands for arithmetic operations (with string concatenation permitted for `+`), and type compatibility upon assignment.
- **Static Division by Zero:** Detects explicit constant divisors evaluating to 0.

---

## 15. Abstract Syntax Tree Generation (Phase 4)

AST nodes discard syntactic sugar (such as delimiters and punctuation) while preserving computational hierarchy:
- `ProgramNode`
- `VarDeclNode`
- `AssignmentNode`
- `PrintNode`
- `IfNode`
- `WhileNode`
- `ForNode`
- `BinaryOpNode`
- `UnaryOpNode`
- `LiteralNode`
- `VariableNode`

Nodes provide recursive `.to_dict()` methods for JSON rendering on the frontend SVG canvas.

---

## 16. Interpreter Design (Phase 5)

The interpreter traverses the validated AST using the Visitor design pattern:
- **Environment Management:** Tracks variable values and bindings across lexical scopes.
- **No `eval()` / `exec()`:** Safe, manual dispatch evaluates binary and unary nodes using native Python arithmetic.
- **Bounded Execution:** Tracks total steps with a hard cap of $50,000$ operations, preventing denial of service via accidental infinite loops (`WHILE TRUE`).
- **Standard Output Redirection:** Captures output lines into an array and measures elapsed time with `time.perf_counter()`.

---

## 17. Automata Concepts and TOC Alignment

CodeSnap directly embodies TOC principles:
1. **Regular Languages (Type-3):** Tokens defined via regular expressions correspond to Deterministic Finite Automata $M = (Q, \Sigma, \delta, q_0, F)$.
2. **Context-Free Languages (Type-2):** CodeSnap syntax requires pushdown storage for balancing constructs (`START...STOP`, `IF...END`, `(...)`), which cannot be recognized by finite automata alone.
3. **Pumping Lemma Justification:** Demonstrates why nesting cannot be parsed with pure regular expressions.
4. **Halting Problem:** Bounded execution illustrates the theoretical impossibility of statically predicting loop termination.

---

## 18. Implementation Details

- **Backend Structure:** Modular architecture across `tokens.py`, `lexer.py`, `parser.py`, `ast_nodes.py`, `semantic.py`, `symbol_table.py`, `interpreter.py`, `automata.py`, `errors.py`, `examples.py`, and `app.py`.
- **Frontend Architecture:** Custom synchronized code editor with syntax highlighting, line numbers gutter, and responsive layouts.
- **Interactive SVG:** Custom tree-drawing algorithm calculating parent-child coordinates and Bézier curves.

---

## 19. Testing and Validation

Comprehensive automated unit testing was executed across 33 test cases:

| Test Suite | File | Focus | Test Count | Result |
| :--- | :--- | :--- | :---: | :---: |
| **Lexer Tests** | `tests/test_lexer.py` | Keywords, literals, strings, comments, lexical errors | 7 | PASSED |
| **Parser Tests** | `tests/test_parser.py` | Program boundaries, precedence, loops, syntax errors | 7 | PASSED |
| **Semantic Tests** | `tests/test_semantic.py` | Undeclared vars, duplicates, type mismatches, static div by 0 | 5 | PASSED |
| **Interpreter Tests** | `tests/test_interpreter.py` | Arithmetic, control flow, loops, runtime errors, infinite loop cap | 7 | PASSED |
| **API Integration Tests** | `tests/test_api.py` | Endpoints, compilation, DFA test, grammar, run | 7 | PASSED |
| **Total** | | | **33** | **100% PASSED** |

Execution time for the entire test suite: **0.066 seconds**.

---

## 20. Results and Performance Metrics

- **Compilation Speed:** Average complete pipeline execution (Lexing + Parsing + Semantic validation) takes under $1.5 \text{ ms}$ for standard programs.
- **Execution Speed:** Sample programs (Factorial, Fibonacci, Loop counters) execute in under $0.1 \text{ ms}$.
- **Accuracy:** Zero false positives in syntax and semantic diagnostic tests.

---

## 21. Limitations

- Does not currently support user-defined functions or subroutines.
- Does not support array or composite collection types.
- Single-threaded interpretation without bytecode generation.

---

## 22. Future Scope

1. **User-Defined Functions:** Implement `FUNC name(args) ... RETURN ... END`.
2. **Arrays and Maps:** Add indexed data collections.
3. **Intermediate Code Generation (IR):** Generate Three-Address Code (TAC) and Quadruples.
4. **Bytecode Virtual Machine:** Replace AST tree walking with a stack-based virtual machine (VM).
5. **Code Optimization Phase:** Constant folding, dead code elimination, and loop-invariant code motion.

---

## 23. Conclusion

The CodeSnap project successfully fulfills all objectives of a comprehensive Computer Science & Engineering Theory of Computation mini-project. By constructing an entire compiler from regular expressions to tree-walking interpretation and pairing it with an interactive web dashboard and DFA simulator, the project transforms abstract theoretical principles into an engaging, practical learning experience.

---

## 24. References

1. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley (The "Dragon Book").
2. Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages, and Computation* (3rd ed.). Pearson.
3. Sipser, M. (2012). *Introduction to the Theory of Computation* (3rd ed.). Cengage Learning.
4. Cooper, K. D., & Torczon, L. (2011). *Engineering a Compiler* (2nd ed.). Morgan Kaufmann.
5. Nystrom, R. (2021). *Crafting Interpreters*. Genever Benning.
