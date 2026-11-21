"""
semantic.py - Semantic Analyzer for CodeSnap.
Enforces type safety, scope rules, variable declaration before use,
duplicate declaration prevention, boolean condition validation, and symbol table tracking.
"""

from typing import List, Dict, Any, Optional, Tuple
from backend.ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, AssignmentNode, PrintNode,
    IfNode, WhileNode, ForNode, BinaryOpNode, UnaryOpNode,
    LiteralNode, VariableNode
)
from backend.symbol_table import SymbolTable, Symbol
from backend.errors import SemanticError


class SemanticAnalyzer:
    """
    Traverses the Abstract Syntax Tree to verify semantic correctness.
    Maintains and populates the Symbol Table.
    """

    def __init__(self):
        self.global_symbol_table = SymbolTable(scope_level=0)
        self.current_scope = self.global_symbol_table
        self.errors: List[SemanticError] = []

    def analyze(self, program: ProgramNode) -> Tuple[SymbolTable, List[SemanticError]]:
        """
        Executes semantic analysis on the Program AST.
        Returns (symbol_table, errors).
        """
        self.errors = []
        self.visit(program)
        return self.global_symbol_table, self.errors

    def visit(self, node: ASTNode) -> Any:
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        raise NotImplementedError(f"No semantic visitor method for {type(node).__name__}")

    def visit_ProgramNode(self, node: ProgramNode):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDeclNode(self, node: VarDeclNode):
        # 1. Check if already declared in current scope
        if self.current_scope.is_in_current_scope(node.name):
            prev = self.current_scope.symbols[node.name]
            err = SemanticError(
                f"Duplicate declaration of variable '{node.name}'",
                node.line,
                node.column,
                f"Variable '{node.name}' was already declared at line {prev.line}. Use assignment '{node.name} = ...' to reassign."
            )
            self.errors.append(err)
            return

        # 2. Evaluate expression type
        expr_type = self.visit(node.expr)

        # 3. Define in symbol table
        self.current_scope.define(
            name=node.name,
            type_name=expr_type or "ANY",
            value=getattr(node.expr, 'value', None) if isinstance(node.expr, LiteralNode) else None,
            line=node.line
        )

    def visit_AssignmentNode(self, node: AssignmentNode):
        # 1. Check if variable exists
        sym = self.current_scope.lookup(node.name)
        if sym is None:
            err = SemanticError(
                f"Variable '{node.name}' is not declared",
                node.line,
                node.column,
                f"Declare '{node.name}' using 'LET {node.name} = <value>' before assigning to it."
            )
            self.errors.append(err)
            return

        # 2. Evaluate expression type
        expr_type = self.visit(node.expr)

        # 3. Check type compatibility (e.g. numeric promotion is allowed, but not string to int)
        if sym.type_name != "ANY" and expr_type != "ANY":
            numeric_types = {"INTEGER", "FLOAT"}
            if sym.type_name in numeric_types and expr_type not in numeric_types:
                err = SemanticError(
                    f"Type mismatch: Cannot assign '{expr_type}' to variable '{node.name}' of type '{sym.type_name}'",
                    node.line,
                    node.column,
                    f"Provide an expression of type '{sym.type_name}' or declare a new variable."
                )
                self.errors.append(err)
            elif sym.type_name not in numeric_types and sym.type_name != expr_type:
                err = SemanticError(
                    f"Type mismatch: Cannot assign '{expr_type}' to variable '{node.name}' of type '{sym.type_name}'",
                    node.line,
                    node.column,
                    f"Provide an expression of type '{sym.type_name}'."
                )
                self.errors.append(err)

        # Update symbol table type if float promotion
        if expr_type == "FLOAT" and sym.type_name == "INTEGER":
            sym.type_name = "FLOAT"

    def visit_PrintNode(self, node: PrintNode):
        self.visit(node.expr)

    def visit_IfNode(self, node: IfNode):
        # 1. Validate condition is boolean
        cond_type = self.visit(node.condition)
        if cond_type is not None and cond_type != "BOOLEAN" and cond_type != "ANY":
            err = SemanticError(
                f"Condition in IF statement must evaluate to BOOLEAN, got '{cond_type}'",
                node.line,
                node.column,
                "Use comparison operators (==, !=, <, <=, >, >=) or boolean literals."
            )
            self.errors.append(err)

        # 2. Visit branches with child scope
        child_scope = SymbolTable(parent=self.current_scope, scope_level=self.current_scope.scope_level + 1)
        prev_scope = self.current_scope
        self.current_scope = child_scope
        for stmt in node.then_branch:
            self.visit(stmt)
        self.current_scope = prev_scope

        if node.else_branch:
            child_scope_else = SymbolTable(parent=self.current_scope, scope_level=self.current_scope.scope_level + 1)
            self.current_scope = child_scope_else
            for stmt in node.else_branch:
                self.visit(stmt)
            self.current_scope = prev_scope

    def visit_WhileNode(self, node: WhileNode):
        cond_type = self.visit(node.condition)
        if cond_type is not None and cond_type != "BOOLEAN" and cond_type != "ANY":
            err = SemanticError(
                f"Condition in WHILE loop must evaluate to BOOLEAN, got '{cond_type}'",
                node.line,
                node.column,
                "Use comparison operators (==, !=, <, <=, >, >=) or boolean literals."
            )
            self.errors.append(err)

        child_scope = SymbolTable(parent=self.current_scope, scope_level=self.current_scope.scope_level + 1)
        prev_scope = self.current_scope
        self.current_scope = child_scope
        for stmt in node.body:
            self.visit(stmt)
        self.current_scope = prev_scope

    def visit_ForNode(self, node: ForNode):
        start_type = self.visit(node.start_expr)
        end_type = self.visit(node.end_expr)
        numeric_types = {"INTEGER", "FLOAT", "ANY"}

        if start_type not in numeric_types:
            err = SemanticError(
                f"FOR loop start bound must be numeric, got '{start_type}'",
                node.line,
                node.column,
                "Provide an integer or float for the loop starting value."
            )
            self.errors.append(err)

        if end_type not in numeric_types:
            err = SemanticError(
                f"FOR loop end bound must be numeric, got '{end_type}'",
                node.line,
                node.column,
                "Provide an integer or float for the loop terminating value."
            )
            self.errors.append(err)

        if node.step_expr:
            step_type = self.visit(node.step_expr)
            if step_type not in numeric_types:
                err = SemanticError(
                    f"FOR loop STEP must be numeric, got '{step_type}'",
                    node.line,
                    node.column,
                    "Provide a numeric step size."
                )
                self.errors.append(err)

        # Loop variable auto-declaration in loop scope
        child_scope = SymbolTable(parent=self.current_scope, scope_level=self.current_scope.scope_level + 1)
        child_scope.define(node.var_name, "INTEGER", line=node.line)
        prev_scope = self.current_scope
        self.current_scope = child_scope
        for stmt in node.body:
            self.visit(stmt)
        self.current_scope = prev_scope

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        op = node.op

        numeric_types = {"INTEGER", "FLOAT"}

        # Logical operations (AND, OR)
        if op in ("AND", "OR"):
            if left_type not in ("BOOLEAN", "ANY") or right_type not in ("BOOLEAN", "ANY"):
                err = SemanticError(
                    f"Logical operator '{op}' requires BOOLEAN operands, got '{left_type}' and '{right_type}'",
                    node.line,
                    node.column,
                    f"Ensure both sides of '{op}' evaluate to TRUE or FALSE."
                )
                self.errors.append(err)
            return "BOOLEAN"

        # Relational comparisons (==, !=, <, <=, >, >=)
        if op in ("==", "!="):
            # Equality allowed between matching types or between numeric types
            if left_type != right_type and not (left_type in numeric_types and right_type in numeric_types):
                if left_type != "ANY" and right_type != "ANY":
                    err = SemanticError(
                        f"Cannot compare incompatible types '{left_type}' and '{right_type}' using '{op}'",
                        node.line,
                        node.column,
                        "Compare values of the same type."
                    )
                    self.errors.append(err)
            return "BOOLEAN"

        if op in ("<", "<=", ">", ">="):
            # Ordering allowed between numeric types or between two strings
            both_numeric = left_type in numeric_types and right_type in numeric_types
            both_strings = left_type == "STRING" and right_type == "STRING"
            if not both_numeric and not both_strings:
                if left_type != "ANY" and right_type != "ANY":
                    err = SemanticError(
                        f"Comparison operator '{op}' requires numeric or string operands, got '{left_type}' and '{right_type}'",
                        node.line,
                        node.column,
                        "Both operands must be numeric (INTEGER, FLOAT) or both STRING."
                    )
                    self.errors.append(err)
            return "BOOLEAN"

        # Arithmetic operations (+, -, *, /, %)
        if op == "+":
            # String concatenation
            if left_type == "STRING" and right_type == "STRING":
                return "STRING"
            # Numeric addition
            if left_type in numeric_types and right_type in numeric_types:
                if left_type == "FLOAT" or right_type == "FLOAT":
                    return "FLOAT"
                return "INTEGER"
            # Type error for '+'
            if left_type != "ANY" and right_type != "ANY":
                err = SemanticError(
                    f"Operator '+' is not supported between '{left_type}' and '{right_type}'",
                    node.line,
                    node.column,
                    "Use '+' between two numbers or two strings."
                )
                self.errors.append(err)
            return "ANY"

        if op in ("-", "*", "/", "%"):
            # Check static division / modulo by zero
            if op in ("/", "%") and isinstance(node.right, LiteralNode) and node.right.value == 0:
                err = SemanticError(
                    f"Division by zero detected statically in '{op}' operation",
                    node.line,
                    node.column,
                    "Divisor must not be 0."
                )
                self.errors.append(err)

            if left_type in numeric_types and right_type in numeric_types:
                if op == "/":
                    return "FLOAT"  # Division in CodeSnap yields float
                if op == "%":
                    return "INTEGER"
                if left_type == "FLOAT" or right_type == "FLOAT":
                    return "FLOAT"
                return "INTEGER"

            if left_type != "ANY" and right_type != "ANY":
                err = SemanticError(
                    f"Operator '{op}' is not supported for types '{left_type}' and '{right_type}'",
                    node.line,
                    node.column,
                    "Both operands must be numeric (INTEGER or FLOAT)."
                )
                self.errors.append(err)
            return "ANY"

        return "ANY"

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        expr_type = self.visit(node.expr)
        if node.op == "NOT":
            if expr_type not in ("BOOLEAN", "ANY"):
                err = SemanticError(
                    f"Operator 'NOT' requires a BOOLEAN operand, got '{expr_type}'",
                    node.line,
                    node.column,
                    "Use 'NOT' with a boolean expression."
                )
                self.errors.append(err)
            return "BOOLEAN"

        if node.op in ("+", "-"):
            if expr_type not in ("INTEGER", "FLOAT", "ANY"):
                err = SemanticError(
                    f"Unary '{node.op}' requires a numeric operand, got '{expr_type}'",
                    node.line,
                    node.column,
                    "Unary + and - can only precede numbers."
                )
                self.errors.append(err)
            return expr_type

        return "ANY"

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        return node.val_type

    def visit_VariableNode(self, node: VariableNode) -> str:
        sym = self.current_scope.lookup(node.name)
        if sym is None:
            err = SemanticError(
                f"Variable '{node.name}' is not declared",
                node.line,
                node.column,
                f"Declare '{node.name}' with 'LET {node.name} = <value>' before using it."
            )
            self.errors.append(err)
            return "ANY"
        return sym.type_name
