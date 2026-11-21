"""
ast_nodes.py - Abstract Syntax Tree node definitions for CodeSnap.
Represents the hierarchical syntactic structure of valid CodeSnap programs.
Each node provides JSON serialization with metadata for frontend visualization.
"""

from typing import List, Optional, Any, Dict


class ASTNode:
    """Base class for all Abstract Syntax Tree nodes."""

    def __init__(self, line: int = 1, column: int = 1):
        self.line = line
        self.column = column

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement to_dict()")


class ProgramNode(ASTNode):
    """Root node representing the entire CodeSnap program (START ... STOP)."""

    def __init__(self, statements: List[ASTNode], line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.statements = statements

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ProgramNode",
            "category": "Program",
            "label": "Program (START ... STOP)",
            "line": self.line,
            "column": self.column,
            "children": [stmt.to_dict() for stmt in self.statements]
        }


class VarDeclNode(ASTNode):
    """Variable Declaration node (LET <name> = <expr>)."""

    def __init__(self, name: str, expr: ASTNode, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.name = name
        self.expr = expr

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "VarDeclNode",
            "category": "Declaration",
            "label": f"LET {self.name} =",
            "name": self.name,
            "line": self.line,
            "column": self.column,
            "children": [self.expr.to_dict()]
        }


class AssignmentNode(ASTNode):
    """Variable Re-assignment node (<name> = <expr>)."""

    def __init__(self, name: str, expr: ASTNode, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.name = name
        self.expr = expr

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "AssignmentNode",
            "category": "Assignment",
            "label": f"{self.name} =",
            "name": self.name,
            "line": self.line,
            "column": self.column,
            "children": [self.expr.to_dict()]
        }


class PrintNode(ASTNode):
    """Print Statement node (PRINT <expr>)."""

    def __init__(self, expr: ASTNode, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.expr = expr

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "PrintNode",
            "category": "Statement",
            "label": "PRINT",
            "line": self.line,
            "column": self.column,
            "children": [self.expr.to_dict()]
        }


class IfNode(ASTNode):
    """Conditional node (IF <condition> <then_branch> [ELSE <else_branch>] END)."""

    def __init__(
        self,
        condition: ASTNode,
        then_branch: List[ASTNode],
        else_branch: Optional[List[ASTNode]] = None,
        line: int = 1,
        column: int = 1
    ):
        super().__init__(line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch or []

    def to_dict(self) -> Dict[str, Any]:
        children = [
            {
                "type": "ConditionNode",
                "category": "Condition",
                "label": "Condition",
                "children": [self.condition.to_dict()]
            },
            {
                "type": "ThenNode",
                "category": "Block",
                "label": "THEN",
                "children": [stmt.to_dict() for stmt in self.then_branch]
            }
        ]
        if self.else_branch:
            children.append({
                "type": "ElseNode",
                "category": "Block",
                "label": "ELSE",
                "children": [stmt.to_dict() for stmt in self.else_branch]
            })
        return {
            "type": "IfNode",
            "category": "ControlFlow",
            "label": "IF ... END",
            "line": self.line,
            "column": self.column,
            "children": children
        }


class WhileNode(ASTNode):
    """While Loop node (WHILE <condition> <body> END)."""

    def __init__(self, condition: ASTNode, body: List[ASTNode], line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.condition = condition
        self.body = body

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "WhileNode",
            "category": "ControlFlow",
            "label": "WHILE Loop",
            "line": self.line,
            "column": self.column,
            "children": [
                {
                    "type": "ConditionNode",
                    "category": "Condition",
                    "label": "Condition",
                    "children": [self.condition.to_dict()]
                },
                {
                    "type": "BodyNode",
                    "category": "Block",
                    "label": "Body",
                    "children": [stmt.to_dict() for stmt in self.body]
                }
            ]
        }


class ForNode(ASTNode):
    """For Loop node (FOR <var> = <start> TO <end> [STEP <step>] <body> END)."""

    def __init__(
        self,
        var_name: str,
        start_expr: ASTNode,
        end_expr: ASTNode,
        step_expr: Optional[ASTNode],
        body: List[ASTNode],
        line: int = 1,
        column: int = 1
    ):
        super().__init__(line, column)
        self.var_name = var_name
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.step_expr = step_expr
        self.body = body

    def to_dict(self) -> Dict[str, Any]:
        header_children = [
            {"type": "StartBound", "category": "Bound", "label": f"Start ({self.var_name})", "children": [self.start_expr.to_dict()]},
            {"type": "EndBound", "category": "Bound", "label": "End", "children": [self.end_expr.to_dict()]}
        ]
        if self.step_expr:
            header_children.append(
                {"type": "StepBound", "category": "Bound", "label": "Step", "children": [self.step_expr.to_dict()]}
            )
        return {
            "type": "ForNode",
            "category": "ControlFlow",
            "label": f"FOR {self.var_name}",
            "var_name": self.var_name,
            "line": self.line,
            "column": self.column,
            "children": [
                *header_children,
                {
                    "type": "BodyNode",
                    "category": "Block",
                    "label": "Body",
                    "children": [stmt.to_dict() for stmt in self.body]
                }
            ]
        }


class BinaryOpNode(ASTNode):
    """Binary Operator node (left <op> right)."""

    def __init__(self, left: ASTNode, op: str, right: ASTNode, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.left = left
        self.op = op
        self.right = right

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "BinaryOpNode",
            "category": "Operator",
            "label": f"Op: {self.op}",
            "op": self.op,
            "line": self.line,
            "column": self.column,
            "children": [self.left.to_dict(), self.right.to_dict()]
        }


class UnaryOpNode(ASTNode):
    """Unary Operator node (<op> expr)."""

    def __init__(self, op: str, expr: ASTNode, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.op = op
        self.expr = expr

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "UnaryOpNode",
            "category": "Operator",
            "label": f"Unary: {self.op}",
            "op": self.op,
            "line": self.line,
            "column": self.column,
            "children": [self.expr.to_dict()]
        }


class LiteralNode(ASTNode):
    """Literal values: Integer, Float, String, Boolean."""

    def __init__(self, value: Any, val_type: str, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.value = value
        self.val_type = val_type

    def to_dict(self) -> Dict[str, Any]:
        display_val = f'"{self.value}"' if self.val_type == "STRING" else str(self.value)
        return {
            "type": "LiteralNode",
            "category": "Literal",
            "label": f"{self.val_type}: {display_val}",
            "value": self.value,
            "val_type": self.val_type,
            "line": self.line,
            "column": self.column,
            "children": []
        }


class VariableNode(ASTNode):
    """Variable reference node."""

    def __init__(self, name: str, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "VariableNode",
            "category": "Variable",
            "label": f"Var: {self.name}",
            "name": self.name,
            "line": self.line,
            "column": self.column,
            "children": []
        }
