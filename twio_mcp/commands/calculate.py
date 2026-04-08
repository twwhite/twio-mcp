import re

from sympy import Symbol, diff, integrate, limit, simplify, solve, sympify
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

ALLOWLIST = re.compile(r"^[\w\s\+\-\*\/\^\(\)\.,=<>!]+$")

TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def cmd_calculate(expression: str | None = None, **kwargs) -> str:
    if not expression:
        return 'Usage: provide an expression. Example: {"command": "calculate", "kwargs": {"expression": "solve(x**2 - 4, x)"}}'

    if not ALLOWLIST.match(expression):
        return "Error: expression contains invalid characters."

    try:
        result = parse_expr(expression, transformations=TRANSFORMATIONS)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"
