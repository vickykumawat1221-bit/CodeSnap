"""
test_interpreter.py - Unit tests for the Tree-Walking Interpreter.
"""

import unittest
from backend.lexer import Lexer
from backend.parser import Parser
from backend.semantic import SemanticAnalyzer
from backend.interpreter import Interpreter


class TestInterpreter(unittest.TestCase):

    def run_code(self, code: str):
        lexer = Lexer(code)
        tokens, lex_errs = lexer.tokenize()
        if lex_errs:
            raise lex_errs[0]
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        sym_table, sem_errs = analyzer.analyze(ast)
        if sem_errs:
            raise sem_errs[0]
        interpreter = Interpreter()
        return interpreter.interpret(ast)

    def test_arithmetic_execution(self):
        code = """START
LET a = 20
LET b = 10
LET result = a + b * 2
PRINT result
STOP"""
        res = self.run_code(code)
        self.assertTrue(res["success"])
        self.assertEqual(res["output"], ["40"])

    def test_conditionals_execution(self):
        code = """START
LET age = 21
IF age >= 18
    PRINT "Eligible"
ELSE
    PRINT "Not Eligible"
END
STOP"""
        res = self.run_code(code)
        self.assertTrue(res["success"])
        self.assertEqual(res["output"], ["Eligible"])

    def test_while_loop_execution(self):
        code = """START
LET count = 1
WHILE count <= 4
    PRINT count
    count = count + 1
END
STOP"""
        res = self.run_code(code)
        self.assertTrue(res["success"])
        self.assertEqual(res["output"], ["1", "2", "3", "4"])

    def test_for_loop_execution(self):
        code = """START
FOR i = 1 TO 3
    PRINT i * 5
END
STOP"""
        res = self.run_code(code)
        self.assertTrue(res["success"])
        self.assertEqual(res["output"], ["5", "10", "15"])

    def test_string_concatenation(self):
        code = """START
LET first = "Code"
LET second = "Snap"
PRINT first + second
STOP"""
        res = self.run_code(code)
        self.assertTrue(res["success"])
        self.assertEqual(res["output"], ["CodeSnap"])

    def test_runtime_division_by_zero(self):
        code = """START
LET a = 100
LET b = 5 - 5
PRINT a / b
STOP"""
        res = self.run_code(code)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"]["category"], "Runtime Error")
        self.assertIn("Division by zero", res["error"]["message"])

    def test_infinite_loop_protection(self):
        code = """START
LET x = 1
WHILE x == 1
    # Infinite loop
END
STOP"""
        res = self.run_code(code)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"]["category"], "Runtime Error")
        self.assertIn("Maximum execution step limit", res["error"]["message"])


if __name__ == "__main__":
    unittest.main()
