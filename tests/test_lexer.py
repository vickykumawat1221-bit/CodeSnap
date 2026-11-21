"""
test_lexer.py - Unit tests for the Lexical Analyzer (Scanner).
"""

import unittest
from backend.lexer import Lexer
from backend.tokens import TokenType


class TestLexer(unittest.TestCase):

    def test_keywords_and_identifiers(self):
        code = "START STOP LET PRINT IF ELSE WHILE FOR TO STEP END TRUE FALSE AND OR NOT my_var"
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()
        self.assertEqual(len(errors), 0)
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        expected = [
            TokenType.KEYWORD_START, TokenType.KEYWORD_STOP, TokenType.KEYWORD_LET,
            TokenType.KEYWORD_PRINT, TokenType.KEYWORD_IF, TokenType.KEYWORD_ELSE,
            TokenType.KEYWORD_WHILE, TokenType.KEYWORD_FOR, TokenType.KEYWORD_TO,
            TokenType.KEYWORD_STEP, TokenType.KEYWORD_END, TokenType.BOOLEAN,
            TokenType.BOOLEAN, TokenType.KEYWORD_AND, TokenType.KEYWORD_OR,
            TokenType.KEYWORD_NOT, TokenType.IDENTIFIER
        ]
        self.assertEqual(types, expected)
        self.assertEqual(tokens[-2].lexeme, "my_var")

    def test_numeric_literals(self):
        code = "100 3.1415 0 999.0"
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()
        self.assertEqual(len(errors), 0)
        self.assertEqual(tokens[0].value, 100)
        self.assertEqual(tokens[0].type, TokenType.INTEGER)
        self.assertEqual(tokens[1].value, 3.1415)
        self.assertEqual(tokens[1].type, TokenType.FLOAT)

    def test_string_literals(self):
        code = '"Hello, World!" "With \\"quote\\" and \\n newline"'
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()
        self.assertEqual(len(errors), 0)
        self.assertEqual(tokens[0].value, "Hello, World!")
        self.assertEqual(tokens[1].value, 'With "quote" and \n newline')

    def test_operators(self):
        code = "+ - * / % == != < <= > >= ="
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()
        self.assertEqual(len(errors), 0)
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        expected = [
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO,
            TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL,
            TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.ASSIGN
        ]
        self.assertEqual(types, expected)

    def test_comments(self):
        code = """START
# This is a full-line comment
LET x = 10 # Inline comment
STOP"""
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()
        self.assertEqual(len(errors), 0)
        # Verify no comment tokens exist
        lexemes = [t.lexeme for t in tokens if t.type != TokenType.NEWLINE and t.type != TokenType.EOF]
        self.assertEqual(lexemes, ["START", "LET", "x", "=", "10", "STOP"])

    def test_lexical_errors(self):
        code = "LET x = @ 50"
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()
        self.assertEqual(len(errors), 1)
        self.assertIn("Invalid character '@'", errors[0].message)
        self.assertEqual(errors[0].line, 1)

    def test_unterminated_string_error(self):
        code = 'LET msg = "Unclosed string'
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()
        self.assertEqual(len(errors), 1)
        self.assertIn("Unterminated string", errors[0].message)


if __name__ == "__main__":
    unittest.main()
