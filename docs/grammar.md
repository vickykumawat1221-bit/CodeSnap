# Context-Free Grammar (CFG) Specification for CodeSnap

## 1. Formal Definition

In the Theory of Computation, a **Context-Free Grammar (CFG)** is formally defined as a 4-tuple:

$$G = (V, \Sigma, R, S)$$

Where:
- **$V$ (Variables / Non-terminals):** The finite set of syntactic categories that can be expanded using production rules.
- **$\Sigma$ (Terminals / Alphabet):** The finite set of literal characters and token types emitted by the Lexical Analyzer ($V \cap \Sigma = \emptyset$).
- **$R$ (Production Rules):** Finite relation of the form $A \to \alpha$, where $A \in V$ and $\alpha \in (V \cup \Sigma)^*$.
- **$S$ (Start Symbol):** The distinguished non-terminal representing the complete program ($S \in V$).

---

## 2. Non-Terminals ($V$)

```
V = {
  Program, StatementList, Statement, VarDeclaration, Assignment,
  PrintStatement, IfStatement, WhileStatement, ForStatement,
  Expression, LogicalOr, LogicalAnd, LogicalNot, Comparison,
  ArithmeticExpr, Term, Factor, Primary
}
```

---

## 3. Terminals ($\Sigma$)

```
Σ = {
  'START', 'STOP', 'LET', 'PRINT', 'IF', 'ELSE', 'WHILE', 'FOR',
  'TO', 'STEP', 'END', 'TRUE', 'FALSE', 'AND', 'OR', 'NOT',
  IDENTIFIER, INTEGER, FLOAT, STRING,
  '+', '-', '*', '/', '%', '==', '!=', '<', '<=', '>', '>=', '=', '(', ')'
}
```

---

## 4. Production Rules in Backus-Naur Form (BNF)

```bnf
<Program>          ::= 'START' <StatementList> 'STOP'

<StatementList>    ::= <Statement> <StatementList>
                     | ε

<Statement>        ::= <VarDeclaration>
                     | <Assignment>
                     | <PrintStatement>
                     | <IfStatement>
                     | <WhileStatement>
                     | <ForStatement>

<VarDeclaration>   ::= 'LET' IDENTIFIER '=' <Expression>

<Assignment>       ::= IDENTIFIER '=' <Expression>

<PrintStatement>   ::= 'PRINT' <Expression>

<IfStatement>      ::= 'IF' <Expression> <StatementList> [ 'ELSE' <StatementList> ] 'END'

<WhileStatement>   ::= 'WHILE' <Expression> <StatementList> 'END'

<ForStatement>     ::= 'FOR' IDENTIFIER '=' <Expression> 'TO' <Expression> [ 'STEP' <Expression> ] <StatementList> 'END'

<Expression>       ::= <LogicalOr>

<LogicalOr>        ::= <LogicalAnd> ( 'OR' <LogicalAnd> )*

<LogicalAnd>       ::= <LogicalNot> ( 'AND' <LogicalNot> )*

<LogicalNot>       ::= 'NOT' <LogicalNot>
                     | <Comparison>

<Comparison>       ::= <ArithmeticExpr> [ ( '==' | '!=' | '<' | '<=' | '>' | '>=' ) <ArithmeticExpr> ]

<ArithmeticExpr>   ::= <Term> ( ( '+' | '-' ) <Term> )*

<Term>             ::= <Factor> ( ( '*' | '/' | '%' ) <Factor> )*

<Factor>           ::= ( '+' | '-' ) <Factor>
                     | <Primary>

<Primary>          ::= INTEGER
                     | FLOAT
                     | STRING
                     | 'TRUE'
                     | 'FALSE'
                     | IDENTIFIER
                     | '(' <Expression> ')'
```

---

## 5. Operator Precedence and Associativity Table

To eliminate grammar ambiguity, the grammar is layered using precedence climbing:

| Level | Operator Category | Operators | Associativity | Parsing Production |
| :---: | :--- | :--- | :---: | :--- |
| **1 (Lowest)** | Logical Disjunction | `OR` | Left-to-Right | `<LogicalOr>` |
| **2** | Logical Conjunction | `AND` | Left-to-Right | `<LogicalAnd>` |
| **3** | Logical Negation | `NOT` | Right-to-Left | `<LogicalNot>` |
| **4** | Relational / Equality | `==`, `!=`, `<`, `<=`, `>`, `>=` | Left-to-Right | `<Comparison>` |
| **5** | Additive Arithmetic | `+`, `-` | Left-to-Right | `<ArithmeticExpr>` |
| **6** | Multiplicative Arithmetic | `*`, `/`, `%` | Left-to-Right | `<Term>` |
| **7** | Unary Sign | `+` (unary), `-` (unary) | Right-to-Left | `<Factor>` |
| **8 (Highest)** | Primaries & Grouping | `( ... )`, Identifiers, Literals | N/A | `<Primary>` |

---

## 6. Derivation Example

For the input expression:
```
result = a + b * 2
```

The leftmost derivation according to the grammar:

1. `<Statement> \Rightarrow <Assignment>`
2. `<Assignment> \Rightarrow \text{IDENTIFIER}(result) = <Expression>`
3. `<Expression> \Rightarrow <LogicalOr> \Rightarrow <LogicalAnd> \Rightarrow <LogicalNot> \Rightarrow <Comparison> \Rightarrow <ArithmeticExpr>`
4. `<ArithmeticExpr> \Rightarrow <Term> + <Term>`
5. Left `<Term> \Rightarrow <Factor> \Rightarrow <Primary> \Rightarrow \text{IDENTIFIER}(a)`
6. Right `<Term> \Rightarrow <Factor> * <Factor>`
7. First `<Factor> \Rightarrow <Primary> \Rightarrow \text{IDENTIFIER}(b)`
8. Second `<Factor> \Rightarrow <Primary> \Rightarrow \text{INTEGER}(2)`

Resulting in the correct AST structure:
```
       Assignment (=)
         /        \
    result         +
                 /   \
                a     *
                    /   \
                   b     2
```
This demonstrates proper operator binding where `*` has higher binding power than `+`.
