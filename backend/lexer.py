"""
lexer.py - Lexical Analyzer (Scanner) for the CodeSnap compiler.
Converts raw source code into a sequence of tokens using regular expressions,
finite automata concepts, and explicit character scanning.
"""

import re
from typing import List, Tuple, Optional
from backend.tokens import Token, TokenType, KEYWORDS, PATTERN_DESCRIPTIONS
from backend.errors import LexicalError


class Lexer:
    """
    Lexical Analyzer for CodeSnap.
    Implements token recognition based on Regular Expressions and Finite Automata.
    """

    def __init__(self, source_code: str):
        self.source = source_code
        self.length = len(source_code)
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.errors: List[LexicalError] = []

    def current_char(self) -> Optional[str]:
        if self.pos >= self.length:
            return None
        return self.source[self.pos]

    def peek_char(self, offset: int = 1) -> Optional[str]:
        target = self.pos + offset
        if target >= self.length:
            return None
        return self.source[target]

    def advance(self) -> Optional[str]:
        ch = self.current_char()
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def tokenize(self) -> Tuple[List[Token], List[LexicalError]]:
        """
        Scans the source code and produces a list of Token objects.
        Returns (tokens, errors).
        """
        self.tokens = []
        self.errors = []
        self.pos = 0
        self.line = 1
        self.column = 1

        while self.pos < self.length:
            ch = self.current_char()

            # 1. Whitespace handling (spaces, carriage returns, tabs)
            if ch in (' ', '\t', '\r'):
                self.advance()
                continue

            # 2. Newline handling
            if ch == '\n':
                start_col = self.column
                start_line = self.line
                self.advance()
                # Coalesce consecutive newlines to avoid noise in token stream
                if not self.tokens or self.tokens[-1].type != TokenType.NEWLINE:
                    self.tokens.append(
                        Token(TokenType.NEWLINE, "\n", "\\n", start_line, start_col)
                    )
                continue

            # 3. Single-line comments (# comment)
            if ch == '#':
                while self.current_char() is not None and self.current_char() != '\n':
                    self.advance()
                continue

            # 4. String literals ("...")
            if ch == '"':
                self.scan_string()
                continue

            # 5. Numbers (Integer and Floating-point)
            if ch.isdigit():
                self.scan_number()
                continue

            # 6. Identifiers and Keywords
            if ch.isalpha() or ch == '_':
                self.scan_identifier()
                continue

            # 7. Two-character and Single-character Operators
            if ch == '=':
                start_col = self.column
                start_line = self.line
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.EQUAL, "==", "==", start_line, start_col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.ASSIGN, "=", "=", start_line, start_col))
                continue

            if ch == '!':
                start_col = self.column
                start_line = self.line
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.NOT_EQUAL, "!=", "!=", start_line, start_col))
                else:
                    self.advance()
                    err = LexicalError(
                        "Unexpected character '!'",
                        start_line,
                        start_col,
                        "In CodeSnap, use '!=' for inequality or the keyword 'NOT' for logical negation."
                    )
                    self.errors.append(err)
                continue

            if ch == '>':
                start_col = self.column
                start_line = self.line
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, ">=", ">=", start_line, start_col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.GREATER, ">", ">", start_line, start_col))
                continue

            if ch == '<':
                start_col = self.column
                start_line = self.line
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.LESS_EQUAL, "<=", "<=", start_line, start_col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.LESS, "<", "<", start_line, start_col))
                continue

            # Single-character arithmetic and punctuation
            if ch == '+':
                self.tokens.append(Token(TokenType.PLUS, "+", "+", self.line, self.column))
                self.advance()
                continue
            if ch == '-':
                self.tokens.append(Token(TokenType.MINUS, "-", "-", self.line, self.column))
                self.advance()
                continue
            if ch == '*':
                self.tokens.append(Token(TokenType.MULTIPLY, "*", "*", self.line, self.column))
                self.advance()
                continue
            if ch == '/':
                self.tokens.append(Token(TokenType.DIVIDE, "/", "/", self.line, self.column))
                self.advance()
                continue
            if ch == '%':
                self.tokens.append(Token(TokenType.MODULO, "%", "%", self.line, self.column))
                self.advance()
                continue
            if ch == '(':
                self.tokens.append(Token(TokenType.LPAREN, "(", "(", self.line, self.column))
                self.advance()
                continue
            if ch == ')':
                self.tokens.append(Token(TokenType.RPAREN, ")", ")", self.line, self.column))
                self.advance()
                continue
            if ch == ',':
                self.tokens.append(Token(TokenType.COMMA, ",", ",", self.line, self.column))
                self.advance()
                continue

            # 8. Unrecognized / Illegal Character
            start_col = self.column
            start_line = self.line
            bad_char = self.advance()
            err = LexicalError(
                f"Invalid character '{bad_char}'",
                start_line,
                start_col,
                f"Remove '{bad_char}' or check if it's an unsupported symbol."
            )
            self.errors.append(err)

        # Append EOF Token
        # Clean trailing newlines
        while self.tokens and self.tokens[-1].type == TokenType.NEWLINE:
            self.tokens.pop()

        self.tokens.append(Token(TokenType.EOF, None, "<EOF>", self.line, self.column))
        return self.tokens, self.errors

    def scan_string(self):
        """Scans a quoted string literal: \"...\" with escape sequence support."""
        start_line = self.line
        start_col = self.column
        self.advance()  # Skip opening quote
        chars = []

        while True:
            ch = self.current_char()
            if ch is None or ch == '\n':
                err = LexicalError(
                    "Unterminated string literal",
                    start_line,
                    start_col,
                    "Close the string with a matching double-quote '\"' before the end of the line."
                )
                self.errors.append(err)
                return

            if ch == '"':
                self.advance()  # Skip closing quote
                break

            if ch == '\\':
                self.advance()  # Skip backslash
                escaped = self.current_char()
                if escaped == 'n':
                    chars.append('\n')
                elif escaped == 't':
                    chars.append('\t')
                elif escaped == '"':
                    chars.append('"')
                elif escaped == '\\':
                    chars.append('\\')
                elif escaped is not None:
                    chars.append(escaped)
                self.advance()
            else:
                chars.append(ch)
                self.advance()

        val = "".join(chars)
        self.tokens.append(
            Token(TokenType.STRING, val, f'"{val}"', start_line, start_col)
        )

    def scan_number(self):
        """Scans numeric literals: integers (\\d+) and floats (\\d+\\.\\d+)."""
        start_line = self.line
        start_col = self.column
        num_str = ""

        while self.current_char() is not None and self.current_char().isdigit():
            num_str += self.advance()

        # Check for fractional part
        if self.current_char() == '.' and self.peek_char() is not None and self.peek_char().isdigit():
            num_str += self.advance()  # include '.'
            while self.current_char() is not None and self.current_char().isdigit():
                num_str += self.advance()

            # Check for invalid multiple decimal points (e.g. 1.2.3)
            if self.current_char() == '.':
                num_str += self.advance()
                while self.current_char() is not None and (self.current_char().isdigit() or self.current_char() == '.'):
                    num_str += self.advance()
                err = LexicalError(
                    f"Malformed floating-point number '{num_str}'",
                    start_line,
                    start_col,
                    "Ensure numbers contain at most one decimal point (e.g. 12.34)."
                )
                self.errors.append(err)
                return

            self.tokens.append(
                Token(TokenType.FLOAT, float(num_str), num_str, start_line, start_col)
            )
        else:
            self.tokens.append(
                Token(TokenType.INTEGER, int(num_str), num_str, start_line, start_col)
            )

    def scan_identifier(self):
        """Scans identifiers and reserved keywords: [a-zA-Z_][a-zA-Z0-9_]*"""
        start_line = self.line
        start_col = self.column
        ident = ""

        while self.current_char() is not None and (self.current_char().isalnum() or self.current_char() == '_'):
            ident += self.advance()

        # Check if it matches a reserved keyword
        if ident in KEYWORDS:
            kw_type = KEYWORDS[ident]
            if kw_type == TokenType.KEYWORD_TRUE:
                self.tokens.append(Token(TokenType.BOOLEAN, True, ident, start_line, start_col))
            elif kw_type == TokenType.KEYWORD_FALSE:
                self.tokens.append(Token(TokenType.BOOLEAN, False, ident, start_line, start_col))
            else:
                self.tokens.append(Token(kw_type, ident, ident, start_line, start_col))
        else:
            # Check if user used lowercase for a keyword
            upper_ident = ident.upper()
            if upper_ident in KEYWORDS:
                # Still register as IDENTIFIER, but we can give a warning or suggest uppercase in parser/semantic
                pass
            self.tokens.append(
                Token(TokenType.IDENTIFIER, ident, ident, start_line, start_col)
            )
