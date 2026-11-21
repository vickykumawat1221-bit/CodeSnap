"""
tokens.py - Token definitions and Token class for CodeSnap compiler.
Theory of Computation: Tokens represent the terminal symbols in the formal grammar,
produced by the Lexical Analyzer (Finite Automaton / Regular Expressions).
"""

from enum import Enum
from typing import Any, Dict


class TokenType(str, Enum):
    # Program Boundaries
    KEYWORD_START = "KEYWORD_START"
    KEYWORD_STOP = "KEYWORD_STOP"

    # Declarations and Statements
    KEYWORD_LET = "KEYWORD_LET"
    KEYWORD_PRINT = "KEYWORD_PRINT"

    # Control Flow
    KEYWORD_IF = "KEYWORD_IF"
    KEYWORD_ELSE = "KEYWORD_ELSE"
    KEYWORD_WHILE = "KEYWORD_WHILE"
    KEYWORD_FOR = "KEYWORD_FOR"
    KEYWORD_TO = "KEYWORD_TO"
    KEYWORD_STEP = "KEYWORD_STEP"
    KEYWORD_END = "KEYWORD_END"

    # Booleans and Logical Operators
    KEYWORD_TRUE = "KEYWORD_TRUE"
    KEYWORD_FALSE = "KEYWORD_FALSE"
    KEYWORD_AND = "KEYWORD_AND"
    KEYWORD_OR = "KEYWORD_OR"
    KEYWORD_NOT = "KEYWORD_NOT"

    # Identifiers and Literals
    IDENTIFIER = "IDENTIFIER"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"

    # Arithmetic Operators
    PLUS = "PLUS"          # +
    MINUS = "MINUS"        # -
    MULTIPLY = "MULTIPLY"  # *
    DIVIDE = "DIVIDE"      # /
    MODULO = "MODULO"      # %

    # Relational Operators
    EQUAL = "EQUAL"                  # ==
    NOT_EQUAL = "NOT_EQUAL"          # !=
    GREATER = "GREATER"              # >
    LESS = "LESS"                    # <
    GREATER_EQUAL = "GREATER_EQUAL"  # >=
    LESS_EQUAL = "LESS_EQUAL"        # <=

    # Assignment Operator
    ASSIGN = "ASSIGN"      # =

    # Delimiters and Punctuation
    LPAREN = "LPAREN"      # (
    RPAREN = "RPAREN"      # )
    COMMA = "COMMA"        # ,

    # Special
    EOF = "EOF"
    NEWLINE = "NEWLINE"


# Map keywords to their corresponding TokenType
KEYWORDS = {
    "START": TokenType.KEYWORD_START,
    "STOP": TokenType.KEYWORD_STOP,
    "LET": TokenType.KEYWORD_LET,
    "PRINT": TokenType.KEYWORD_PRINT,
    "IF": TokenType.KEYWORD_IF,
    "ELSE": TokenType.KEYWORD_ELSE,
    "WHILE": TokenType.KEYWORD_WHILE,
    "FOR": TokenType.KEYWORD_FOR,
    "TO": TokenType.KEYWORD_TO,
    "STEP": TokenType.KEYWORD_STEP,
    "END": TokenType.KEYWORD_END,
    "TRUE": TokenType.KEYWORD_TRUE,
    "FALSE": TokenType.KEYWORD_FALSE,
    "AND": TokenType.KEYWORD_AND,
    "OR": TokenType.KEYWORD_OR,
    "NOT": TokenType.KEYWORD_NOT,
}

# TOC Pattern Descriptions explaining how the regular expression/DFA matches each token
PATTERN_DESCRIPTIONS = {
    TokenType.KEYWORD_START: "Exact keyword match: /^START$/",
    TokenType.KEYWORD_STOP: "Exact keyword match: /^STOP$/",
    TokenType.KEYWORD_LET: "Exact keyword match: /^LET$/",
    TokenType.KEYWORD_PRINT: "Exact keyword match: /^PRINT$/",
    TokenType.KEYWORD_IF: "Exact keyword match: /^IF$/",
    TokenType.KEYWORD_ELSE: "Exact keyword match: /^ELSE$/",
    TokenType.KEYWORD_WHILE: "Exact keyword match: /^WHILE$/",
    TokenType.KEYWORD_FOR: "Exact keyword match: /^FOR$/",
    TokenType.KEYWORD_TO: "Exact keyword match: /^TO$/",
    TokenType.KEYWORD_STEP: "Exact keyword match: /^STEP$/",
    TokenType.KEYWORD_END: "Exact keyword match: /^END$/",
    TokenType.KEYWORD_TRUE: "Boolean literal match: /^TRUE$/",
    TokenType.KEYWORD_FALSE: "Boolean literal match: /^FALSE$/",
    TokenType.KEYWORD_AND: "Logical AND operator: /^AND$/",
    TokenType.KEYWORD_OR: "Logical OR operator: /^OR$/",
    TokenType.KEYWORD_NOT: "Logical NOT operator: /^NOT$/",
    TokenType.IDENTIFIER: "Identifier pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/ (DFA state: q0 -> q1)",
    TokenType.INTEGER: "Integer literal: /^\\d+$/ (DFA state: q0 -> q1 on digit)",
    TokenType.FLOAT: "Floating-point literal: /^\\d+\\.\\d+$/ (DFA state: q0 -> q1 -> q2 -> q3)",
    TokenType.STRING: "String literal: /^\"([^\"\\\\]|\\\\.)*\"$/ (delimited by quotes)",
    TokenType.BOOLEAN: "Boolean literal: /^(TRUE|FALSE)$/",
    TokenType.PLUS: "Arithmetic addition operator: '+'",
    TokenType.MINUS: "Arithmetic subtraction operator: '-'",
    TokenType.MULTIPLY: "Arithmetic multiplication operator: '*'",
    TokenType.DIVIDE: "Arithmetic division operator: '/'",
    TokenType.MODULO: "Arithmetic modulo operator: '%'",
    TokenType.EQUAL: "Relational equality operator: '=='",
    TokenType.NOT_EQUAL: "Relational inequality operator: '!='",
    TokenType.GREATER: "Relational greater-than operator: '>'",
    TokenType.LESS: "Relational less-than operator: '<'",
    TokenType.GREATER_EQUAL: "Relational greater-or-equal: '>='",
    TokenType.LESS_EQUAL: "Relational less-or-equal: '<='",
    TokenType.ASSIGN: "Assignment operator: '='",
    TokenType.LPAREN: "Left parenthesis: '('",
    TokenType.RPAREN: "Right parenthesis: ')'",
    TokenType.COMMA: "Separator comma: ','",
    TokenType.EOF: "End of file marker",
    TokenType.NEWLINE: "Line terminator / statement separator",
}


class Token:
    """Represents a lexical token generated during Lexical Analysis."""

    def __init__(self, token_type: TokenType, value: Any, lexeme: str, line: int, column: int, pattern_desc: str = ""):
        self.type = token_type
        self.value = value
        self.lexeme = lexeme
        self.line = line
        self.column = column
        self.pattern_desc = pattern_desc or PATTERN_DESCRIPTIONS.get(token_type, "Regular token")

    def __repr__(self) -> str:
        return f"Token({self.type.name if isinstance(self.type, Enum) else self.type}, '{self.lexeme}', line={self.line}, col={self.column})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert token to JSON-friendly dictionary."""
        return {
            "type": self.type.value if isinstance(self.type, Enum) else str(self.type),
            "name": self.type.name if isinstance(self.type, Enum) else str(self.type),
            "value": self.value,
            "lexeme": self.lexeme,
            "line": self.line,
            "column": self.column,
            "pattern_desc": self.pattern_desc
        }
