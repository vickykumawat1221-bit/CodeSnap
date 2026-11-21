"""
grammar.py - Context-Free Grammar (CFG) specification for CodeSnap.
Theory of Computation:
A context-free grammar is defined as a 4-tuple G = (V, Σ, R, S) where:
- V: Finite set of non-terminal symbols
- Σ: Finite set of terminal symbols (disjoint from V)
- R: Finite set of production rules (A -> α where A ∈ V, α ∈ (V ∪ Σ)*)
- S: Start symbol (S ∈ V)
"""

from typing import Dict, List, Any

GRAMMAR_BNF = """
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
"""

PRECEDENCE_TABLE = [
    {"level": 1, "operators": ["OR"], "associativity": "Left-to-Right", "description": "Logical OR"},
    {"level": 2, "operators": ["AND"], "associativity": "Left-to-Right", "description": "Logical AND"},
    {"level": 3, "operators": ["NOT"], "associativity": "Right-to-Left", "description": "Logical NOT (Unary)"},
    {"level": 4, "operators": ["==", "!=", "<", "<=", ">", ">="], "associativity": "Non-associative / Left", "description": "Relational Comparisons"},
    {"level": 5, "operators": ["+", "-"], "associativity": "Left-to-Right", "description": "Addition and Subtraction"},
    {"level": 6, "operators": ["*", "/", "%"], "associativity": "Left-to-Right", "description": "Multiplication, Division, Modulo"},
    {"level": 7, "operators": ["+ (unary)", "- (unary)"], "associativity": "Right-to-Left", "description": "Unary Signs"},
    {"level": 8, "operators": ["( )", "Literals", "Identifiers"], "associativity": "N/A", "description": "Grouping and Primary Expressions"}
]

def get_grammar_info() -> Dict[str, Any]:
    """Returns structured grammar metadata for frontend and documentation."""
    return {
        "title": "CodeSnap Context-Free Grammar (CFG)",
        "formal_definition": {
            "start_symbol": "Program",
            "non_terminals": [
                "Program", "StatementList", "Statement", "VarDeclaration",
                "Assignment", "PrintStatement", "IfStatement", "WhileStatement",
                "ForStatement", "Expression", "LogicalOr", "LogicalAnd",
                "LogicalNot", "Comparison", "ArithmeticExpr", "Term", "Factor", "Primary"
            ],
            "terminals": [
                "START", "STOP", "LET", "PRINT", "IF", "ELSE", "WHILE", "FOR",
                "TO", "STEP", "END", "TRUE", "FALSE", "AND", "OR", "NOT",
                "IDENTIFIER", "INTEGER", "FLOAT", "STRING",
                "+", "-", "*", "/", "%", "==", "!=", "<", "<=", ">", ">=", "=", "(", ")"
            ]
        },
        "bnf": GRAMMAR_BNF.strip(),
        "precedence": PRECEDENCE_TABLE
    }
