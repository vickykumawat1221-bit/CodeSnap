"""
test_parser.py - Unit tests for the Syntax Analyzer (Parser).
"""

import unittest
from backend.lexer import Lexer
from backend.parser import Parser
from backend.errors import SyntaxError
from backend.ast_nodes import ProgramNode, VarDeclNode, IfNode, WhileNode, ForNode, BinaryOpNode


class TestParser(unittest.TestCase):

    def parse_code(self, code: str):
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()
        if errors:
            raise errors[0]
        parser = Parser(tokens)
        return parser.parse()

    def test_basic_program(self):
        code = """START
LET x = 42
PRINT x
STOP"""
        ast = self.parse_code(code)
        self.assertIsInstance(ast, ProgramNode)
        self.assertEqual(len(ast.statements), 2)
        self.assertIsInstance(ast.statements[0], VarDeclNode)
        self.assertEqual(ast.statements[0].name, "x")

    def test_operator_precedence(self):
        code = """START
LET res = 10 + 20 * 5
STOP"""
        ast = self.parse_code(code)
        decl = ast.statements[0]
        # 10 + (20 * 5)
        self.assertIsInstance(decl.expr, BinaryOpNode)
        self.assertEqual(decl.expr.op, "+")
        self.assertIsInstance(decl.expr.right, BinaryOpNode)
        self.assertEqual(decl.expr.right.op, "*")

    def test_if_else_statement(self):
        code = """START
IF age >= 18
    PRINT "Adult"
ELSE
    PRINT "Minor"
END
STOP"""
        ast = self.parse_code(code)
        self.assertIsInstance(ast.statements[0], IfNode)
        if_node = ast.statements[0]
        self.assertEqual(len(if_node.then_branch), 1)
        self.assertEqual(len(if_node.else_branch), 1)

    def test_loops(self):
        code = """START
WHILE count <= 5
    count = count + 1
END
FOR i = 1 TO 10
    PRINT i
END
STOP"""
        ast = self.parse_code(code)
        self.assertIsInstance(ast.statements[0], WhileNode)
        self.assertIsInstance(ast.statements[1], ForNode)
        self.assertEqual(ast.statements[1].var_name, "i")

    def test_missing_start_error(self):
        code = """LET x = 10
STOP"""
        with self.assertRaises(SyntaxError) as ctx:
            self.parse_code(code)
        self.assertIn("Expected 'START'", ctx.exception.message)

    def test_missing_stop_error(self):
        code = """START
LET x = 10"""
        with self.assertRaises(SyntaxError) as ctx:
            self.parse_code(code)
        self.assertIn("Expected 'STOP'", ctx.exception.message)

    def test_missing_end_in_if_error(self):
        code = """START
IF x > 5
    PRINT "Hello"
STOP"""
        with self.assertRaises(SyntaxError) as ctx:
            self.parse_code(code)
        self.assertIn("Expected 'END'", ctx.exception.message)


if __name__ == "__main__":
    unittest.main()
