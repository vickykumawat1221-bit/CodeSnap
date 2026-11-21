"""
app.py - Flask Web Application & REST API Server for CodeSnap.
Exposes compilation, execution, automata simulation, and sample library endpoints.
Serves the dark-themed IDE frontend.
"""

import os
import sys
import time
from typing import Dict, Any, List

# Ensure parent directory is in python module search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, request, jsonify, send_from_directory
from backend.lexer import Lexer
from backend.parser import Parser
from backend.semantic import SemanticAnalyzer
from backend.interpreter import Interpreter
from backend.grammar import get_grammar_info
from backend.automata import get_dfa_list, test_dfa_string
from backend.examples import get_all_examples, get_example_by_id
from backend.errors import CodeSnapError, LexicalError, SyntaxError, SemanticError

FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ---------------- Frontend Routes ----------------

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(FRONTEND_DIR, path)


# ---------------- API Endpoints ----------------

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "app": "CodeSnap Compiler",
        "version": "1.0.0",
        "timestamp": time.time()
    })


@app.route("/api/examples", methods=["GET"])
def list_examples():
    return jsonify({"success": True, "examples": get_all_examples()})


@app.route("/api/examples/<example_id>", methods=["GET"])
def get_example(example_id: str):
    ex = get_example_by_id(example_id)
    return jsonify({"success": True, "example": ex})


@app.route("/api/grammar", methods=["GET"])
def get_grammar():
    return jsonify({"success": True, "grammar": get_grammar_info()})


@app.route("/api/automata", methods=["GET"])
def list_automata():
    return jsonify({"success": True, "automata": get_dfa_list()})


@app.route("/api/automata/test", methods=["POST"])
def test_automata():
    data = request.get_json(silent=True) or {}
    dfa_id = data.get("dfa_id", "identifier")
    test_str = data.get("input_string", "")
    try:
        result = test_dfa_string(dfa_id, test_str)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/lex", methods=["POST"])
def lexical_analysis_endpoint():
    data = request.get_json(silent=True) or {}
    source_code = data.get("source_code", "")

    start_time = time.perf_counter()
    lexer = Lexer(source_code)
    tokens, errors = lexer.tokenize()
    duration_ms = round((time.perf_counter() - start_time) * 1000.0, 3)

    return jsonify({
        "success": len(errors) == 0,
        "tokens": [t.to_dict() for t in tokens],
        "errors": [e.to_dict() for e in errors],
        "count": len(tokens),
        "duration_ms": duration_ms
    })


@app.route("/api/parse", methods=["POST"])
def syntax_analysis_endpoint():
    data = request.get_json(silent=True) or {}
    source_code = data.get("source_code", "")

    lexer = Lexer(source_code)
    tokens, lex_errors = lexer.tokenize()
    if lex_errors:
        return jsonify({
            "success": False,
            "errors": [e.to_dict() for e in lex_errors],
            "ast": None
        })

    start_time = time.perf_counter()
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 3)
        return jsonify({
            "success": True,
            "ast": ast.to_dict(),
            "errors": [],
            "duration_ms": duration_ms
        })
    except SyntaxError as e:
        return jsonify({
            "success": False,
            "ast": None,
            "errors": [e.to_dict()]
        })


@app.route("/api/semantic", methods=["POST"])
def semantic_analysis_endpoint():
    data = request.get_json(silent=True) or {}
    source_code = data.get("source_code", "")

    lexer = Lexer(source_code)
    tokens, lex_errors = lexer.tokenize()
    if lex_errors:
        return jsonify({"success": False, "errors": [e.to_dict() for e in lex_errors], "symbols": []})

    try:
        parser = Parser(tokens)
        ast = parser.parse()
    except SyntaxError as e:
        return jsonify({"success": False, "errors": [e.to_dict()], "symbols": []})

    analyzer = SemanticAnalyzer()
    sym_table, sem_errors = analyzer.analyze(ast)

    return jsonify({
        "success": len(sem_errors) == 0,
        "symbols": sym_table.get_all_symbols(),
        "errors": [e.to_dict() for e in sem_errors]
    })


@app.route("/api/compile", methods=["POST"])
def compile_endpoint():
    """
    Executes Lexical, Syntax, and Semantic analysis pipeline.
    Returns comprehensive compilation results with AST, Token stream, Symbol table, and phase timings.
    """
    data = request.get_json(silent=True) or {}
    source_code = data.get("source_code", "")

    all_errors = []
    phases = []

    # Phase 1: Lexical Analysis
    t0 = time.perf_counter()
    lexer = Lexer(source_code)
    tokens, lex_errors = lexer.tokenize()
    t_lex = round((time.perf_counter() - t0) * 1000.0, 3)

    if lex_errors:
        all_errors.extend([e.to_dict() for e in lex_errors])
        phases.append({
            "phase": "Lexical Analysis",
            "status": "FAILED",
            "time_ms": t_lex,
            "details": f"Found {len(lex_errors)} lexical error(s)"
        })
        return jsonify({
            "success": False,
            "phase_failed": "Lexical Analysis",
            "tokens": [t.to_dict() for t in tokens],
            "ast": None,
            "symbols": [],
            "errors": all_errors,
            "phases": phases
        })

    phases.append({
        "phase": "Lexical Analysis",
        "status": "PASSED",
        "time_ms": t_lex,
        "details": f"Generated {len(tokens)} tokens"
    })

    # Phase 2: Syntax Analysis & AST Generation
    t1 = time.perf_counter()
    ast = None
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        t_parse = round((time.perf_counter() - t1) * 1000.0, 3)
        phases.append({
            "phase": "Syntax Analysis & AST",
            "status": "PASSED",
            "time_ms": t_parse,
            "details": "Grammar verified, AST constructed"
        })
    except SyntaxError as e:
        t_parse = round((time.perf_counter() - t1) * 1000.0, 3)
        all_errors.append(e.to_dict())
        phases.append({
            "phase": "Syntax Analysis & AST",
            "status": "FAILED",
            "time_ms": t_parse,
            "details": e.message
        })
        return jsonify({
            "success": False,
            "phase_failed": "Syntax Analysis",
            "tokens": [t.to_dict() for t in tokens],
            "ast": None,
            "symbols": [],
            "errors": all_errors,
            "phases": phases
        })

    # Phase 3: Semantic Analysis
    t2 = time.perf_counter()
    analyzer = SemanticAnalyzer()
    sym_table, sem_errors = analyzer.analyze(ast)
    t_sem = round((time.perf_counter() - t2) * 1000.0, 3)

    symbols = sym_table.get_all_symbols()

    if sem_errors:
        all_errors.extend([e.to_dict() for e in sem_errors])
        phases.append({
            "phase": "Semantic Analysis",
            "status": "FAILED",
            "time_ms": t_sem,
            "details": f"Found {len(sem_errors)} semantic error(s)"
        })
        return jsonify({
            "success": False,
            "phase_failed": "Semantic Analysis",
            "tokens": [t.to_dict() for t in tokens],
            "ast": ast.to_dict(),
            "symbols": symbols,
            "errors": all_errors,
            "phases": phases
        })

    phases.append({
        "phase": "Semantic Analysis",
        "status": "PASSED",
        "time_ms": t_sem,
        "details": f"Verified {len(symbols)} symbol declarations & types"
    })

    return jsonify({
        "success": True,
        "tokens": [t.to_dict() for t in tokens],
        "ast": ast.to_dict(),
        "symbols": symbols,
        "errors": [],
        "phases": phases,
        "total_time_ms": round(t_lex + t_parse + t_sem, 3)
    })


@app.route("/api/run", methods=["POST"])
def run_endpoint():
    """
    Compiles and executes the CodeSnap program using the tree-walking interpreter.
    Returns standard output, execution time, steps count, and variable state.
    """
    data = request.get_json(silent=True) or {}
    source_code = data.get("source_code", "")

    # Step 1: Lexical Analysis
    lexer = Lexer(source_code)
    tokens, lex_errors = lexer.tokenize()
    if lex_errors:
        return jsonify({
            "success": False,
            "phase_failed": "Lexical Analysis",
            "output": [],
            "stdout": "",
            "errors": [e.to_dict() for e in lex_errors],
            "tokens": [t.to_dict() for t in tokens],
            "ast": None,
            "variables": []
        })

    # Step 2: Syntax Analysis
    try:
        parser = Parser(tokens)
        ast = parser.parse()
    except SyntaxError as e:
        return jsonify({
            "success": False,
            "phase_failed": "Syntax Analysis",
            "output": [],
            "stdout": "",
            "errors": [e.to_dict()],
            "tokens": [t.to_dict() for t in tokens],
            "ast": None,
            "variables": []
        })

    # Step 3: Semantic Analysis
    analyzer = SemanticAnalyzer()
    sym_table, sem_errors = analyzer.analyze(ast)
    if sem_errors:
        return jsonify({
            "success": False,
            "phase_failed": "Semantic Analysis",
            "output": [],
            "stdout": "",
            "errors": [e.to_dict() for e in sem_errors],
            "tokens": [t.to_dict() for t in tokens],
            "ast": ast.to_dict(),
            "variables": sym_table.get_all_symbols()
        })

    # Step 4: Interpretation and Execution
    interpreter = Interpreter()
    exec_result = interpreter.interpret(ast)

    errors = []
    if exec_result.get("error"):
        errors.append(exec_result["error"])

    return jsonify({
        "success": exec_result["success"],
        "phase_failed": "Runtime Execution" if not exec_result["success"] else None,
        "output": exec_result["output"],
        "stdout": exec_result["stdout"],
        "execution_time_ms": exec_result["execution_time_ms"],
        "step_count": exec_result["step_count"],
        "variables": exec_result["variables"],
        "tokens": [t.to_dict() for t in tokens],
        "ast": ast.to_dict(),
        "errors": errors
    })


if __name__ == "__main__":
    import socket
    def get_free_port(preferred_port=5050):
        env_port = os.environ.get("PORT")
        if env_port:
            try:
                p = int(env_port)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('0.0.0.0', p))
                    return p
            except OSError:
                pass
        for p in [preferred_port, 5001, 8080, 5000]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('0.0.0.0', p))
                    return p
            except OSError:
                continue
        return preferred_port

    port = get_free_port(5050)
    print(f"Starting CodeSnap Compiler Server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
