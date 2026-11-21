"""
errors.py - Custom error hierarchy for the CodeSnap compiler pipeline.
Categorizes errors cleanly into Lexical, Syntax, Semantic, and Runtime errors,
providing precise line/column locations and helpful remediation suggestions.
"""

from typing import Optional, Dict, Any


class CodeSnapError(Exception):
    """Base class for all compiler and runtime errors in CodeSnap."""

    def __init__(
        self,
        category: str,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        suggestion: Optional[str] = None
    ):
        super().__init__(message)
        self.category = category
        self.message = message
        self.line = line
        self.column = column
        self.suggestion = suggestion or "Check the syntax and language reference."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "suggestion": self.suggestion,
            "formatted": str(self)
        }

    def __str__(self) -> str:
        loc = []
        if self.line is not None:
            loc.append(f"line {self.line}")
        if self.column is not None:
            loc.append(f"column {self.column}")
        location_str = f" at {', '.join(loc)}" if loc else ""
        return f"{self.category}: {self.message}{location_str}"


class LexicalError(CodeSnapError):
    """Raised when an illegal character or malformed token is encountered."""

    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None, suggestion: Optional[str] = None):
        super().__init__("Lexical Error", message, line, column, suggestion)


class SyntaxError(CodeSnapError):
    """Raised when the token stream violates the Context-Free Grammar."""

    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None, suggestion: Optional[str] = None):
        super().__init__("Syntax Error", message, line, column, suggestion)


class SemanticError(CodeSnapError):
    """Raised when a program is syntactically valid but semantically invalid."""

    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None, suggestion: Optional[str] = None):
        super().__init__("Semantic Error", message, line, column, suggestion)


class RuntimeError(CodeSnapError):
    """Raised during AST evaluation / interpretation (e.g. division by zero, infinite loop)."""

    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None, suggestion: Optional[str] = None):
        super().__init__("Runtime Error", message, line, column, suggestion)
