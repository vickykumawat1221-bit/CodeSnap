"""
automata.py - Finite Automata Engine & Visualizer for CodeSnap.
Theory of Computation Demonstration:
Defines Deterministic Finite Automata (DFA) 5-tuple M = (Q, Σ, δ, q0, F)
for token recognition in lexical analysis, with step-by-step tracing
and transition tables.
"""

from typing import Dict, List, Any, Optional, Tuple


class DFA:
    """
    Deterministic Finite Automaton (DFA) represented formally as:
    M = (Q, Σ, δ, q0, F)
    """

    def __init__(
        self,
        id_name: str,
        title: str,
        description: str,
        states: List[str],
        alphabet_desc: List[str],
        start_state: str,
        accept_states: List[str],
        state_labels: Dict[str, str],
        layout_positions: Dict[str, Dict[str, int]],
        transitions: Dict[str, List[Dict[str, Any]]],
        transition_table: Dict[str, Dict[str, str]],
        token_map: Optional[Dict[str, str]] = None
    ):
        self.id = id_name
        self.title = title
        self.description = description
        self.states = states
        self.alphabet_desc = alphabet_desc
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.state_labels = state_labels
        self.layout_positions = layout_positions
        self.transitions = transitions
        self.transition_table = transition_table
        self.token_map = token_map or {}

    def to_dict(self) -> Dict[str, Any]:
        """Serializes DFA definition for the frontend visualization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "formal_tuple": {
                "Q": self.states,
                "Sigma": self.alphabet_desc,
                "q0": self.start_state,
                "F": list(self.accept_states),
            },
            "state_labels": self.state_labels,
            "layout_positions": self.layout_positions,
            "transitions": self.transitions,
            "transition_table": self.transition_table,
            "accept_states": list(self.accept_states),
            "start_state": self.start_state,
            "token_map": self.token_map
        }

    def simulate(self, input_str: str) -> Dict[str, Any]:
        """
        Simulates the DFA on the input string step-by-step.
        Returns detailed execution trace with state transitions and acceptance status.
        """
        current_state = self.start_state
        steps = []
        is_trapped = False

        steps.append({
            "step": 0,
            "char": "ε (Start)",
            "from_state": None,
            "to_state": current_state,
            "remaining": input_str,
            "action": f"Begin at start state '{current_state}'",
            "is_accepting": current_state in self.accept_states
        })

        for idx, ch in enumerate(input_str):
            from_state = current_state
            next_state = self._get_next_state(current_state, ch)

            if next_state is None or next_state == "q_trap":
                current_state = "q_trap"
                is_trapped = True
                steps.append({
                    "step": idx + 1,
                    "char": ch,
                    "from_state": from_state,
                    "to_state": "q_trap",
                    "remaining": input_str[idx + 1:],
                    "action": f"Read '{ch}' → No valid transition. Transitioned to Trap / Dead state.",
                    "is_accepting": False
                })
                # Once in trap, remain in trap
                for rem_idx in range(idx + 1, len(input_str)):
                    rem_ch = input_str[rem_idx]
                    steps.append({
                        "step": rem_idx + 1,
                        "char": rem_ch,
                        "from_state": "q_trap",
                        "to_state": "q_trap",
                        "remaining": input_str[rem_idx + 1:],
                        "action": f"Read '{rem_ch}' → Trapped.",
                        "is_accepting": False
                    })
                break
            else:
                current_state = next_state
                is_acc = current_state in self.accept_states
                token_type = self.token_map.get(current_state, "TOKEN") if is_acc else None
                action_text = f"Read '{ch}' → Transition to '{current_state}'"
                if is_acc:
                    action_text += f" (Accepting state for {token_type})"

                steps.append({
                    "step": idx + 1,
                    "char": ch,
                    "from_state": from_state,
                    "to_state": current_state,
                    "remaining": input_str[idx + 1:],
                    "action": action_text,
                    "is_accepting": is_acc
                })

        accepted = (current_state in self.accept_states) and not is_trapped
        token_produced = self.token_map.get(current_state, None) if accepted else None

        return {
            "input": input_str,
            "accepted": accepted,
            "final_state": current_state,
            "token_produced": token_produced,
            "steps": steps,
            "explanation": (
                f"Input string '{input_str}' reached accepting state '{current_state}' (Token: {token_produced}). Recognized successfully by the DFA!"
                if accepted else
                f"Input string '{input_str}' ended in non-accepting state '{current_state}'. Rejected by the DFA."
            )
        }

    def _get_next_state(self, current: str, ch: str) -> Optional[str]:
        raise NotImplementedError()


class IdentifierDFA(DFA):
    """
    DFA recognizing CodeSnap Identifiers: [a-zA-Z_][a-zA-Z0-9_]*
    """

    def __init__(self):
        super().__init__(
            id_name="identifier_dfa",
            title="Identifier DFA: [a-zA-Z_][a-zA-Z0-9_]*",
            description="Recognizes variable and symbol identifiers. Must begin with a letter or underscore, followed by letters, digits, or underscores.",
            states=["q0", "q1", "q_trap"],
            alphabet_desc=["[a-zA-Z_] (Letter/Underscore)", "[0-9] (Digit)", "Other"],
            start_state="q0",
            accept_states=["q1"],
            state_labels={
                "q0": "Start (q0)",
                "q1": "Identifier (q1)",
                "q_trap": "Trap (q_dead)"
            },
            layout_positions={
                "q0": {"x": 100, "y": 140},
                "q1": {"x": 320, "y": 140},
                "q_trap": {"x": 210, "y": 280}
            },
            transitions={
                "edges": [
                    {"from": "q0", "to": "q1", "label": "[a-zA-Z_]"},
                    {"from": "q0", "to": "q_trap", "label": "Other / [0-9]"},
                    {"from": "q1", "to": "q1", "label": "[a-zA-Z0-9_] (loop)"},
                    {"from": "q1", "to": "q_trap", "label": "Other"},
                    {"from": "q_trap", "to": "q_trap", "label": "Any"}
                ]
            },
            transition_table={
                "q0": {"[a-zA-Z_]": "q1", "[0-9]": "q_trap", "other": "q_trap"},
                "q1": {"[a-zA-Z_]": "q1", "[0-9]": "q1", "other": "q_trap"},
                "q_trap": {"[a-zA-Z_]": "q_trap", "[0-9]": "q_trap", "other": "q_trap"}
            },
            token_map={"q1": "IDENTIFIER"}
        )

    def _get_next_state(self, current: str, ch: str) -> Optional[str]:
        if current == "q0":
            if ch.isalpha() or ch == '_':
                return "q1"
            return "q_trap"
        elif current == "q1":
            if ch.isalnum() or ch == '_':
                return "q1"
            return "q_trap"
        return "q_trap"


class NumberDFA(DFA):
    """
    DFA recognizing Numeric Literals:
    Integer: \\d+ (State q1)
    Float: \\d+\\.\\d+ (State q3)
    """

    def __init__(self):
        super().__init__(
            id_name="number_dfa",
            title="Numeric Literals DFA (Integer & Float)",
            description="Recognizes integer literals (q1) and floating-point literals with decimal fraction (q3).",
            states=["q0", "q1", "q2", "q3", "q_trap"],
            alphabet_desc=["[0-9] (Digit)", "'.' (Decimal Point)", "Other"],
            start_state="q0",
            accept_states=["q1", "q3"],
            state_labels={
                "q0": "Start (q0)",
                "q1": "Integer (q1)",
                "q2": "Decimal Dot (q2)",
                "q3": "Float (q3)",
                "q_trap": "Trap (q_dead)"
            },
            layout_positions={
                "q0": {"x": 80, "y": 140},
                "q1": {"x": 220, "y": 140},
                "q2": {"x": 370, "y": 140},
                "q3": {"x": 520, "y": 140},
                "q_trap": {"x": 300, "y": 270}
            },
            transitions={
                "edges": [
                    {"from": "q0", "to": "q1", "label": "[0-9]"},
                    {"from": "q0", "to": "q_trap", "label": "Other / '.'"},
                    {"from": "q1", "to": "q1", "label": "[0-9] (loop)"},
                    {"from": "q1", "to": "q2", "label": "'.'"},
                    {"from": "q1", "to": "q_trap", "label": "Other"},
                    {"from": "q2", "to": "q3", "label": "[0-9]"},
                    {"from": "q2", "to": "q_trap", "label": "Other / '.'"},
                    {"from": "q3", "to": "q3", "label": "[0-9] (loop)"},
                    {"from": "q3", "to": "q_trap", "label": "Other / '.'"},
                    {"from": "q_trap", "to": "q_trap", "label": "Any"}
                ]
            },
            transition_table={
                "q0": {"[0-9]": "q1", "'.'": "q_trap", "other": "q_trap"},
                "q1": {"[0-9]": "q1", "'.'": "q2", "other": "q_trap"},
                "q2": {"[0-9]": "q3", "'.'": "q_trap", "other": "q_trap"},
                "q3": {"[0-9]": "q3", "'.'": "q_trap", "other": "q_trap"},
                "q_trap": {"[0-9]": "q_trap", "'.'": "q_trap", "other": "q_trap"}
            },
            token_map={"q1": "INTEGER", "q3": "FLOAT"}
        )

    def _get_next_state(self, current: str, ch: str) -> Optional[str]:
        if current == "q0":
            if ch.isdigit():
                return "q1"
            return "q_trap"
        elif current == "q1":
            if ch.isdigit():
                return "q1"
            if ch == '.':
                return "q2"
            return "q_trap"
        elif current == "q2":
            if ch.isdigit():
                return "q3"
            return "q_trap"
        elif current == "q3":
            if ch.isdigit():
                return "q3"
            return "q_trap"
        return "q_trap"


class RelationalOpsDFA(DFA):
    """
    DFA recognizing Relational Operators: ==, !=, <, <=, >, >=
    """

    def __init__(self):
        super().__init__(
            id_name="relational_dfa",
            title="Relational Operators DFA (==, !=, <, <=, >, >=)",
            description="Recognizes single and multi-character relational comparison operators.",
            states=["q0", "q_eq", "q_eqeq", "q_not", "q_noteq", "q_lt", "q_lteq", "q_gt", "q_gteq", "q_trap"],
            alphabet_desc=["'='", "'!'", "'<'", "'>'", "Other"],
            start_state="q0",
            accept_states=["q_eqeq", "q_noteq", "q_lt", "q_lteq", "q_gt", "q_gteq", "q_eq"],
            state_labels={
                "q0": "Start (q0)",
                "q_eq": "ASSIGN (=)",
                "q_eqeq": "EQUAL (==)",
                "q_not": "! (prefix)",
                "q_noteq": "NOT_EQUAL (!=)",
                "q_lt": "LESS (<)",
                "q_lteq": "LESS_EQUAL (<=)",
                "q_gt": "GREATER (>)",
                "q_gteq": "GREATER_EQUAL (>=)",
                "q_trap": "Trap (q_dead)"
            },
            layout_positions={
                "q0": {"x": 80, "y": 200},
                "q_eq": {"x": 220, "y": 80},
                "q_eqeq": {"x": 380, "y": 80},
                "q_not": {"x": 220, "y": 160},
                "q_noteq": {"x": 380, "y": 160},
                "q_lt": {"x": 220, "y": 240},
                "q_lteq": {"x": 380, "y": 240},
                "q_gt": {"x": 220, "y": 320},
                "q_gteq": {"x": 380, "y": 320},
                "q_trap": {"x": 520, "y": 200}
            },
            transitions={
                "edges": [
                    {"from": "q0", "to": "q_eq", "label": "'='"},
                    {"from": "q_eq", "to": "q_eqeq", "label": "'='"},
                    {"from": "q0", "to": "q_not", "label": "'!'"},
                    {"from": "q_not", "to": "q_noteq", "label": "'='"},
                    {"from": "q0", "to": "q_lt", "label": "'<'"},
                    {"from": "q_lt", "to": "q_lteq", "label": "'='"},
                    {"from": "q0", "to": "q_gt", "label": "'>'"},
                    {"from": "q_gt", "to": "q_gteq", "label": "'='"},
                    {"from": "q0", "to": "q_trap", "label": "Other"}
                ]
            },
            transition_table={
                "q0": {"'='": "q_eq", "'!'": "q_not", "'<'": "q_lt", "'>'": "q_gt", "other": "q_trap"},
                "q_eq": {"'='": "q_eqeq", "'!'": "q_trap", "'<'": "q_trap", "'>'": "q_trap", "other": "q_trap"},
                "q_not": {"'='": "q_noteq", "other": "q_trap"},
                "q_lt": {"'='": "q_lteq", "other": "q_trap"},
                "q_gt": {"'='": "q_gteq", "other": "q_trap"}
            },
            token_map={
                "q_eq": "ASSIGN (=)",
                "q_eqeq": "EQUAL (==)",
                "q_noteq": "NOT_EQUAL (!=)",
                "q_lt": "LESS (<)",
                "q_lteq": "LESS_EQUAL (<=)",
                "q_gt": "GREATER (>)",
                "q_gteq": "GREATER_EQUAL (>=)"
            }
        )

    def _get_next_state(self, current: str, ch: str) -> Optional[str]:
        if current == "q0":
            if ch == '=':
                return "q_eq"
            if ch == '!':
                return "q_not"
            if ch == '<':
                return "q_lt"
            if ch == '>':
                return "q_gt"
            return "q_trap"
        elif current == "q_eq":
            if ch == '=':
                return "q_eqeq"
            return "q_trap"
        elif current == "q_not":
            if ch == '=':
                return "q_noteq"
            return "q_trap"
        elif current == "q_lt":
            if ch == '=':
                return "q_lteq"
            return "q_trap"
        elif current == "q_gt":
            if ch == '=':
                return "q_gteq"
            return "q_trap"
        return "q_trap"


AVAILABLE_DFAS = {
    "identifier": IdentifierDFA(),
    "number": NumberDFA(),
    "relational": RelationalOpsDFA()
}


def get_dfa_list() -> List[Dict[str, Any]]:
    return [dfa.to_dict() for dfa in AVAILABLE_DFAS.values()]


def test_dfa_string(dfa_id: str, test_str: str) -> Dict[str, Any]:
    if dfa_id not in AVAILABLE_DFAS:
        raise ValueError(f"Unknown DFA '{dfa_id}'. Available: {list(AVAILABLE_DFAS.keys())}")
    return AVAILABLE_DFAS[dfa_id].simulate(test_str)
