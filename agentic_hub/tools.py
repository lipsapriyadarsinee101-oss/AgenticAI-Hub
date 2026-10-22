"""Shared, bounded, read-only tools. No shell or arbitrary filesystem access."""

import ast
import math
import operator
import re
from pathlib import Path

DEFAULT_KNOWLEDGE = Path(__file__).parent / "knowledge"


def search_knowledge(query: str, directory: Path = DEFAULT_KNOWLEDGE) -> str:
    """Search local Markdown evidence; return excerpts with source filenames."""
    terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    matches = []
    for path in sorted(directory.glob("*.md"))[:100]:
        if path.is_symlink() or path.stat().st_size > 200_000:
            continue
        text = path.read_text(encoding="utf-8")
        for paragraph in text.split("\n\n"):
            score = len(terms & set(re.findall(r"[a-z0-9]+", paragraph.lower())))
            if score:
                matches.append((score, path.name, paragraph[:1800]))
    matches.sort(key=lambda item: (-item[0], item[1]))
    return "\n\n".join(f"[{name}] {text}" for _, name, text in matches[:4]) or "No matching evidence found."


def calculate(expression: str) -> str:
    """Calculate finite numbers using +, -, *, / and parentheses; no code execution."""
    if len(expression) > 100:
        raise ValueError("Expression is too long")
    operators = {ast.Add: operator.add, ast.Sub: operator.sub,
                 ast.Mult: operator.mul, ast.Div: operator.truediv}

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in operators:
            value = operators[type(node.op)](visit(node.left), visit(node.right))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        else:
            raise ValueError("Only numbers and + - * / are allowed")
        if not math.isfinite(value) or abs(value) > 1e15:
            raise ValueError("Result exceeds the numeric limit")
        return value

    try:
        return str(visit(ast.parse(expression, mode="eval").body))
    except (SyntaxError, ZeroDivisionError, RecursionError, OverflowError) as exc:
        raise ValueError("Invalid arithmetic expression") from exc
