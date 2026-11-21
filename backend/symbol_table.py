"""
symbol_table.py - Symbol Table management for CodeSnap.
Maintains scope hierarchies, variable identifiers, their inferred/runtime types,
declaration line numbers, and values.
"""

from typing import Dict, Optional, Any, List


class Symbol:
    """Represents a single symbol entry in the Symbol Table."""

    def __init__(self, name: str, type_name: str, value: Any = None, line: int = 1, scope_level: int = 0):
        self.name = name
        self.type_name = type_name
        self.value = value
        self.line = line
        self.scope_level = scope_level

    def to_dict(self) -> Dict[str, Any]:
        display_val = self.value
        if self.type_name == "STRING" and self.value is not None:
            display_val = f'"{self.value}"'
        return {
            "name": self.name,
            "type": self.type_name,
            "value": display_val if self.value is not None else "unassigned",
            "line": self.line,
            "scope": f"Scope {self.scope_level}" if self.scope_level > 0 else "Global"
        }


class SymbolTable:
    """Scoped Symbol Table supporting nested blocks and hierarchical lookup."""

    def __init__(self, parent: Optional['SymbolTable'] = None, scope_level: int = 0):
        self.symbols: Dict[str, Symbol] = {}
        self.parent = parent
        self.scope_level = scope_level

    def define(self, name: str, type_name: str, value: Any = None, line: int = 1) -> Symbol:
        symbol = Symbol(name, type_name, value, line, self.scope_level)
        self.symbols[name] = symbol
        return symbol

    def is_in_current_scope(self, name: str) -> bool:
        return name in self.symbols

    def lookup(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def update(self, name: str, value: Any, type_name: Optional[str] = None) -> bool:
        if name in self.symbols:
            self.symbols[name].value = value
            if type_name:
                self.symbols[name].type_name = type_name
            return True
        if self.parent:
            return self.parent.update(name, value, type_name)
        return False

    def get_all_symbols(self) -> List[Dict[str, Any]]:
        """Collects all symbols from root down to current scope."""
        all_syms: Dict[str, Dict[str, Any]] = {}
        curr: Optional[SymbolTable] = self
        chain = []
        while curr:
            chain.append(curr)
            curr = curr.parent

        # Process from root down to most specific
        for table in reversed(chain):
            for name, sym in table.symbols.items():
                all_syms[name] = sym.to_dict()

        return list(all_syms.values())
