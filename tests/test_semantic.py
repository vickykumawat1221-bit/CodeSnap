"""
test_semantic.py - Unit tests for the Semantic Analyzer.
"""

import unittest
from backend.lexer import Lexer
from backend.parser import Parser
from backend.semantic import SemanticAnalyzer


class TestSemantic(unittest.TestCase):

    def analyze_code(self, code: str):
        lexer = Lexer(code)
        tokens, lex_errs = lexer.tokenize()
        if lex_errs:
            raise lex_errs[0]
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        return analyzer.analyze(ast)

    def test_valid_program(self):
        code = """START
LET a = 20
LET b = 10.5
LET name = "Vikash"
LET is_ok = TRUE
LET sum = a + b
STOP"""
        sym_table, errors = self.analyze_code(code)
        self.assertEqual(len(errors), 0)
        symbols = {s["name"]: s["type"] for s in sym_table.get_all_symbols()}
        self.assertEqual(symbols["a"], "INTEGER")
        self.assertEqual(symbols["b"], "FLOAT")
        self.assertEqual(symbols["name"], "STRING")
        self.assertEqual(symbols["is_ok"], "BOOLEAN")

    def test_undeclared_variable(self):
        code = """START
LET age = 21
PRINT salary
STOP"""
        sym_table, errors = self.analyze_code(code)
        self.assertEqual(len(errors), 1)
        self.assertIn("Variable 'salary' is not declared", errors[0].message)

    def test_duplicate_declaration(self):
        code = """START
LET total = 100
LET total = 200
STOP"""
        sym_table, errors = self.analyze_code(code)
        self.assertEqual(len(errors), 1)
        self.assertIn("Duplicate declaration of variable 'total'", errors[0].message)

    def test_invalid_type_operation(self):
        code = """START
LET text = "Score: "
LET num = 10
LET bad = text - num
STOP"""
        sym_table, errors = self.analyze_code(code)
        self.assertEqual(len(errors), 1)
        self.assertIn("Operator '-' is not supported", errors[0].message)

    def test_static_division_by_zero(self):
        code = """START
LET res = 50 / 0
STOP"""
        sym_table, errors = self.analyze_code(code)
        self.assertEqual(len(errors), 1)
        self.assertIn("Division by zero", errors[0].message)


if __name__ == "__main__":
    unittest.main()
