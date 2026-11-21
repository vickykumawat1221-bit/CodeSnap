"""
interpreter.py - Tree-Walking AST Interpreter for CodeSnap.
Executes the Abstract Syntax Tree directly without python eval() or exec().
Includes step bounding for infinite loop protection, execution timing,
and standard output capturing.
"""

import time
from typing import List, Dict, Any, Optional
from backend.ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, AssignmentNode, PrintNode,
    IfNode, WhileNode, ForNode, BinaryOpNode, UnaryOpNode,
    LiteralNode, VariableNode
)
from backend.symbol_table import SymbolTable
from backend.errors import RuntimeError


class ExecutionEnvironment:
    """Manages runtime variable values and scope during interpretation."""

    def __init__(self, parent: Optional['ExecutionEnvironment'] = None):
        self.values: Dict[str, Any] = {}
        self.types: Dict[str, str] = {}
        self.parent = parent

    def define(self, name: str, value: Any, type_name: str):
        self.values[name] = value
        self.types[name] = type_name

    def lookup(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.lookup(name)
        raise RuntimeError(f"Runtime variable lookup failed: '{name}' not found.")

    def assign(self, name: str, value: Any) -> bool:
        if name in self.values:
            self.values[name] = value
            # Infer runtime type
            if isinstance(value, bool):
                self.types[name] = "BOOLEAN"
            elif isinstance(value, int):
                self.types[name] = "INTEGER"
            elif isinstance(value, float):
                self.types[name] = "FLOAT"
            elif isinstance(value, str):
                self.types[name] = "STRING"
            return True
        if self.parent:
            return self.parent.assign(name, value)
        return False

    def get_all_variables(self) -> List[Dict[str, Any]]:
        all_vars = {}
        curr: Optional[ExecutionEnvironment] = self
        chain = []
        while curr:
            chain.append(curr)
            curr = curr.parent

        for env in reversed(chain):
            for name, val in env.values.items():
                t = env.types.get(name, "ANY")
                disp = f'"{val}"' if t == "STRING" else str(val)
                all_vars[name] = {
                    "name": name,
                    "type": t,
                    "value": disp
                }
        return list(all_vars.values())


class Interpreter:
    """
    Tree-walking AST Interpreter.
    Evaluates expressions and executes control flow nodes safely.
    """

    MAX_STEPS = 50000  # Guard against infinite loops

    def __init__(self):
        self.global_env = ExecutionEnvironment()
        self.current_env = self.global_env
        self.output: List[str] = []
        self.step_count = 0
        self.execution_time_ms = 0.0

    def check_step_limit(self, line: int = 1, column: int = 1):
        self.step_count += 1
        if self.step_count > self.MAX_STEPS:
            raise RuntimeError(
                f"Maximum execution step limit ({self.MAX_STEPS}) exceeded. Possible infinite loop detected.",
                line,
                column,
                "Ensure your WHILE or FOR loop condition eventually terminates."
            )

    def interpret(self, program: ProgramNode) -> Dict[str, Any]:
        """
        Executes the given Program AST.
        Returns execution result dictionary with stdout, time, steps, and symbol table.
        """
        self.global_env = ExecutionEnvironment()
        self.current_env = self.global_env
        self.output = []
        self.step_count = 0

        start_time = time.perf_counter()

        try:
            self.visit(program)
            elapsed = (time.perf_counter() - start_time) * 1000.0
            self.execution_time_ms = round(elapsed, 3)

            return {
                "success": True,
                "output": self.output,
                "stdout": "\n".join(self.output),
                "execution_time_ms": self.execution_time_ms,
                "step_count": self.step_count,
                "variables": self.global_env.get_all_variables(),
                "error": None
            }
        except RuntimeError as err:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            self.execution_time_ms = round(elapsed, 3)
            return {
                "success": False,
                "output": self.output,
                "stdout": "\n".join(self.output),
                "execution_time_ms": self.execution_time_ms,
                "step_count": self.step_count,
                "variables": self.global_env.get_all_variables(),
                "error": err.to_dict()
            }

    def visit(self, node: ASTNode) -> Any:
        self.check_step_limit(node.line, node.column)
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name)
        return visitor(node)

    def visit_ProgramNode(self, node: ProgramNode):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDeclNode(self, node: VarDeclNode):
        val = self.visit(node.expr)
        type_name = "ANY"
        if isinstance(val, bool):
            type_name = "BOOLEAN"
        elif isinstance(val, int):
            type_name = "INTEGER"
        elif isinstance(val, float):
            type_name = "FLOAT"
        elif isinstance(val, str):
            type_name = "STRING"

        self.current_env.define(node.name, val, type_name)

    def visit_AssignmentNode(self, node: AssignmentNode):
        val = self.visit(node.expr)
        self.current_env.assign(node.name, val)

    def visit_PrintNode(self, node: PrintNode):
        val = self.visit(node.expr)
        # Format for output
        if isinstance(val, bool):
            str_val = "TRUE" if val else "FALSE"
        elif isinstance(val, float):
            # If whole number float (e.g. 5.0), display cleanly or standard
            str_val = f"{val:g}" if val.is_integer() else str(val)
        else:
            str_val = str(val)

        self.output.append(str_val)

    def visit_IfNode(self, node: IfNode):
        cond_val = self.visit(node.condition)
        if cond_val is True:
            prev_env = self.current_env
            self.current_env = ExecutionEnvironment(parent=prev_env)
            for stmt in node.then_branch:
                self.visit(stmt)
            self.current_env = prev_env
        elif node.else_branch:
            prev_env = self.current_env
            self.current_env = ExecutionEnvironment(parent=prev_env)
            for stmt in node.else_branch:
                self.visit(stmt)
            self.current_env = prev_env

    def visit_WhileNode(self, node: WhileNode):
        while True:
            cond_val = self.visit(node.condition)
            if not cond_val:
                break
            prev_env = self.current_env
            self.current_env = ExecutionEnvironment(parent=prev_env)
            for stmt in node.body:
                self.visit(stmt)
            self.current_env = prev_env

    def visit_ForNode(self, node: ForNode):
        start_val = self.visit(node.start_expr)
        end_val = self.visit(node.end_expr)
        step_val = self.visit(node.step_expr) if node.step_expr else 1

        if not isinstance(start_val, (int, float)) or not isinstance(end_val, (int, float)):
            raise RuntimeError(
                "FOR loop bounds must be numeric values.",
                node.line, node.column,
                "Ensure start and end bounds evaluate to numbers."
            )

        if not isinstance(step_val, (int, float)) or step_val == 0:
            raise RuntimeError(
                "FOR loop step size must be non-zero numeric value.",
                node.line, node.column,
                "STEP must not be 0."
            )

        curr_i = start_val
        prev_env = self.current_env
        self.current_env = ExecutionEnvironment(parent=prev_env)

        if step_val > 0:
            while curr_i <= end_val:
                self.current_env.define(node.var_name, curr_i, "INTEGER" if isinstance(curr_i, int) else "FLOAT")
                for stmt in node.body:
                    self.visit(stmt)
                curr_i += step_val
        else:
            while curr_i >= end_val:
                self.current_env.define(node.var_name, curr_i, "INTEGER" if isinstance(curr_i, int) else "FLOAT")
                for stmt in node.body:
                    self.visit(stmt)
                curr_i += step_val

        self.current_env = prev_env

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        # Short-circuit logical operations
        if node.op == "AND":
            left_val = self.visit(node.left)
            if not left_val:
                return False
            right_val = self.visit(node.right)
            return bool(right_val)

        if node.op == "OR":
            left_val = self.visit(node.left)
            if left_val:
                return True
            right_val = self.visit(node.right)
            return bool(right_val)

        left_val = self.visit(node.left)
        right_val = self.visit(node.right)

        # Relational operators
        if node.op == "==":
            return left_val == right_val
        if node.op == "!=":
            return left_val != right_val
        if node.op == "<":
            return left_val < right_val
        if node.op == "<=":
            return left_val <= right_val
        if node.op == ">":
            return left_val > right_val
        if node.op == ">=":
            return left_val >= right_val

        # Arithmetic operators
        if node.op == "+":
            return left_val + right_val
        if node.op == "-":
            return left_val - right_val
        if node.op == "*":
            return left_val * right_val
        if node.op == "/":
            if right_val == 0:
                raise RuntimeError(
                    "Division by zero",
                    node.line,
                    node.column,
                    "Divisor expression evaluated to zero. Ensure divisor is non-zero."
                )
            res = left_val / right_val
            return int(res) if res.is_integer() and isinstance(left_val, int) and isinstance(right_val, int) else res
        if node.op == "%":
            if right_val == 0:
                raise RuntimeError(
                    "Modulo by zero",
                    node.line,
                    node.column,
                    "Divisor in modulo expression evaluated to zero."
                )
            return left_val % right_val

        raise RuntimeError(f"Unsupported binary operator: '{node.op}'", node.line, node.column)

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> Any:
        val = self.visit(node.expr)
        if node.op == "NOT":
            return not val
        if node.op == "-":
            return -val
        if node.op == "+":
            return +val
        raise RuntimeError(f"Unsupported unary operator: '{node.op}'", node.line, node.column)

    def visit_LiteralNode(self, node: LiteralNode) -> Any:
        return node.value

    def visit_VariableNode(self, node: VariableNode) -> Any:
        return self.current_env.lookup(node.name)
