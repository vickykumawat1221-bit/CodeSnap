"""
parser.py - Recursive Descent Parser for CodeSnap.
Constructs an Abstract Syntax Tree (AST) from a stream of tokens,
verifying that the input conforms strictly to the formal Context-Free Grammar.
"""

from typing import List, Optional
from backend.tokens import Token, TokenType
from backend.errors import SyntaxError
from backend.ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, AssignmentNode, PrintNode,
    IfNode, WhileNode, ForNode, BinaryOpNode, UnaryOpNode,
    LiteralNode, VariableNode
)


class Parser:
    """
    Recursive Descent Syntax Analyzer.
    Parses CodeSnap programs into Abstract Syntax Trees.
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]

    def peek_next(self) -> Optional[Token]:
        if self.pos + 1 >= len(self.tokens):
            return None
        return self.tokens[self.pos + 1]

    def is_at_end(self) -> bool:
        return self.current().type == TokenType.EOF

    def advance(self) -> Token:
        token = self.current()
        if not self.is_at_end():
            self.pos += 1
        return token

    def match(self, *types: TokenType) -> bool:
        if self.current().type in types:
            self.advance()
            return True
        return False

    def check(self, token_type: TokenType) -> bool:
        return self.current().type == token_type

    def consume(self, token_type: TokenType, error_msg: str, suggestion: Optional[str] = None) -> Token:
        if self.check(token_type):
            return self.advance()
        curr = self.current()
        raise SyntaxError(
            error_msg,
            curr.line,
            curr.column,
            suggestion or f"Expected {token_type.name}, found '{curr.lexeme}'."
        )

    def skip_newlines(self):
        """Discards newline separators between statements."""
        while self.match(TokenType.NEWLINE):
            pass

    def parse(self) -> ProgramNode:
        """
        Entry point: Parses <Program> ::= 'START' <StatementList> 'STOP'
        """
        self.skip_newlines()

        if self.is_at_end():
            raise SyntaxError(
                "Source file is empty",
                1, 1,
                "A CodeSnap program must start with 'START' and end with 'STOP'."
            )

        start_token = self.current()
        if not self.match(TokenType.KEYWORD_START):
            raise SyntaxError(
                f"Expected 'START' at beginning of program, found '{start_token.lexeme}'",
                start_token.line,
                start_token.column,
                "Every CodeSnap program must begin with the keyword 'START'."
            )

        statements = self.statement_list()

        stop_token = self.current()
        if not self.match(TokenType.KEYWORD_STOP):
            raise SyntaxError(
                f"Expected 'STOP' at end of program, found '{stop_token.lexeme}'",
                stop_token.line,
                stop_token.column,
                "Every CodeSnap program must terminate with the keyword 'STOP'."
            )

        self.skip_newlines()

        if not self.is_at_end():
            leftover = self.current()
            raise SyntaxError(
                f"Unexpected token '{leftover.lexeme}' after 'STOP'",
                leftover.line,
                leftover.column,
                "All statements must be placed between 'START' and 'STOP'. Remove trailing code."
            )

        return ProgramNode(statements, start_token.line, start_token.column)

    def statement_list(self) -> List[ASTNode]:
        """
        Parses a sequence of statements until a closing delimiter (STOP, END, ELSE, EOF).
        """
        statements = []
        self.skip_newlines()

        while not self.is_at_end() and self.current().type not in (
            TokenType.KEYWORD_STOP,
            TokenType.KEYWORD_END,
            TokenType.KEYWORD_ELSE
        ):
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()

        return statements

    def statement(self) -> ASTNode:
        """
        Parses a single statement:
        Declaration, Assignment, PrintStatement, IfStatement, WhileStatement, ForStatement.
        """
        curr = self.current()

        # Variable Declaration: LET <id> = <expr>
        if self.match(TokenType.KEYWORD_LET):
            var_token = self.consume(
                TokenType.IDENTIFIER,
                "Expected variable identifier after 'LET'",
                "Syntax: LET <variable_name> = <expression>"
            )
            self.consume(
                TokenType.ASSIGN,
                f"Expected '=' in declaration of '{var_token.lexeme}'",
                "Syntax: LET <variable_name> = <expression>"
            )
            expr = self.expression()
            return VarDeclNode(var_token.lexeme, expr, curr.line, curr.column)

        # Print Statement: PRINT <expr>
        if self.match(TokenType.KEYWORD_PRINT):
            expr = self.expression()
            return PrintNode(expr, curr.line, curr.column)

        # If Statement: IF <expr> ... [ELSE ...] END
        if self.match(TokenType.KEYWORD_IF):
            condition = self.expression()
            self.skip_newlines()
            then_branch = self.statement_list()
            else_branch = []
            if self.match(TokenType.KEYWORD_ELSE):
                self.skip_newlines()
                else_branch = self.statement_list()
            self.consume(
                TokenType.KEYWORD_END,
                "Expected 'END' to close IF statement",
                "Ensure every IF statement is closed with 'END'."
            )
            return IfNode(condition, then_branch, else_branch, curr.line, curr.column)

        # While Statement: WHILE <expr> ... END
        if self.match(TokenType.KEYWORD_WHILE):
            condition = self.expression()
            self.skip_newlines()
            body = self.statement_list()
            self.consume(
                TokenType.KEYWORD_END,
                "Expected 'END' to close WHILE loop",
                "Ensure every WHILE loop is closed with 'END'."
            )
            return WhileNode(condition, body, curr.line, curr.column)

        # For Statement: FOR <id> = <start> TO <end> [STEP <step>] ... END
        if self.match(TokenType.KEYWORD_FOR):
            var_token = self.consume(
                TokenType.IDENTIFIER,
                "Expected loop counter variable after 'FOR'",
                "Syntax: FOR <variable> = <start> TO <end> [STEP <step>] ... END"
            )
            self.consume(
                TokenType.ASSIGN,
                f"Expected '=' after loop variable '{var_token.lexeme}'",
                "Syntax: FOR <variable> = <start> TO <end> ... END"
            )
            start_expr = self.expression()
            self.consume(
                TokenType.KEYWORD_TO,
                "Expected 'TO' in FOR loop specification",
                "Syntax: FOR <variable> = <start> TO <end> ... END"
            )
            end_expr = self.expression()
            step_expr = None
            if self.match(TokenType.KEYWORD_STEP):
                step_expr = self.expression()
            self.skip_newlines()
            body = self.statement_list()
            self.consume(
                TokenType.KEYWORD_END,
                "Expected 'END' to close FOR loop",
                "Ensure every FOR loop is closed with 'END'."
            )
            return ForNode(var_token.lexeme, start_expr, end_expr, step_expr, body, curr.line, curr.column)

        # Variable Re-assignment: <id> = <expr>
        if curr.type == TokenType.IDENTIFIER and self.peek_next() and self.peek_next().type == TokenType.ASSIGN:
            var_token = self.advance()  # IDENTIFIER
            self.advance()              # ASSIGN
            expr = self.expression()
            return AssignmentNode(var_token.lexeme, expr, curr.line, curr.column)

        # Unrecognized statement start
        raise SyntaxError(
            f"Unexpected token '{curr.lexeme}' starting statement",
            curr.line,
            curr.column,
            "Valid statements begin with LET, PRINT, IF, WHILE, FOR, or variable assignment."
        )

    # ---------------- Expression Grammar (Precedence Climbing) ----------------

    def expression(self) -> ASTNode:
        return self.logical_or()

    def logical_or(self) -> ASTNode:
        left = self.logical_and()
        while self.match(TokenType.KEYWORD_OR):
            op_token = self.tokens[self.pos - 1]
            right = self.logical_and()
            left = BinaryOpNode(left, "OR", right, op_token.line, op_token.column)
        return left

    def logical_and(self) -> ASTNode:
        left = self.logical_not()
        while self.match(TokenType.KEYWORD_AND):
            op_token = self.tokens[self.pos - 1]
            right = self.logical_not()
            left = BinaryOpNode(left, "AND", right, op_token.line, op_token.column)
        return left

    def logical_not(self) -> ASTNode:
        if self.match(TokenType.KEYWORD_NOT):
            op_token = self.tokens[self.pos - 1]
            expr = self.logical_not()
            return UnaryOpNode("NOT", expr, op_token.line, op_token.column)
        return self.comparison()

    def comparison(self) -> ASTNode:
        left = self.arithmetic_expr()
        relational_ops = (
            TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.GREATER, TokenType.LESS,
            TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL
        )
        if self.current().type in relational_ops:
            op_token = self.advance()
            right = self.arithmetic_expr()
            return BinaryOpNode(left, op_token.lexeme, right, op_token.line, op_token.column)
        return left

    def arithmetic_expr(self) -> ASTNode:
        left = self.term()
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            right = self.term()
            left = BinaryOpNode(left, op_token.lexeme, right, op_token.line, op_token.column)
        return left

    def term(self) -> ASTNode:
        left = self.factor()
        while self.current().type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op_token = self.advance()
            right = self.factor()
            left = BinaryOpNode(left, op_token.lexeme, right, op_token.line, op_token.column)
        return left

    def factor(self) -> ASTNode:
        if self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            expr = self.factor()
            return UnaryOpNode(op_token.lexeme, expr, op_token.line, op_token.column)
        return self.primary()

    def primary(self) -> ASTNode:
        curr = self.current()

        if self.match(TokenType.INTEGER):
            return LiteralNode(curr.value, "INTEGER", curr.line, curr.column)

        if self.match(TokenType.FLOAT):
            return LiteralNode(curr.value, "FLOAT", curr.line, curr.column)

        if self.match(TokenType.STRING):
            return LiteralNode(curr.value, "STRING", curr.line, curr.column)

        if self.match(TokenType.BOOLEAN):
            return LiteralNode(curr.value, "BOOLEAN", curr.line, curr.column)

        if self.match(TokenType.IDENTIFIER):
            return VariableNode(curr.lexeme, curr.line, curr.column)

        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(
                TokenType.RPAREN,
                "Expected ')' closing parenthesized expression",
                "Check for matching opening '(' and closing ')'."
            )
            return expr

        raise SyntaxError(
            f"Unexpected token '{curr.lexeme}' in expression",
            curr.line,
            curr.column,
            "Expected literal value, variable, or parenthesized sub-expression."
        )
