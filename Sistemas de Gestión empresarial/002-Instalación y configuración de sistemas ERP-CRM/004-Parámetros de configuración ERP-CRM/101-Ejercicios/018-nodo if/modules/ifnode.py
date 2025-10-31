# modules/ifnode.py
from typing import Dict, Any, List

TOOL = {
    "type": "ifnode",
    "label": "IF (expresión)",
    "description": "Evalúa una expresión sobre la entrada (x) y ramifica por true/false.",
    "config": {
        "expr": {"type": "string", "label": "Expresión (Python) con x", "default": "bool(x)"}  # p.ej: x>10, 'ok' in x
    }
}

def _first_input(inputs: List[Any]):
    # Usa el primer dato upstream existente
    for it in inputs or []:
        if it is not None:
            return it
    return None

def _safe_eval(expr: str, x):
    # Eval súper acotado: nombre 'x' y algunos builtins seguros
    safe_globals = {"__builtins__": {}}
    safe_locals  = {"x": x, "len": len, "str": str, "int": int, "float": float, "bool": bool}
    return bool(eval(expr, safe_globals, safe_locals))

def execute(config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    expr   = (config.get("expr") or "bool(x)").strip()
    inputs = context.get("inputs", [])
    x      = _first_input(inputs)

    try:
        is_true = _safe_eval(expr, x)
    except Exception as e:
        # en error, consideramos false y reportamos
        return {
            "data": x,
            "meta": {"branch": "false", "error": str(e)}
        }

    # Passthrough del valor de entrada, y meta con la rama
    return {
        "data": x,
        "meta": {"branch": "true" if is_true else "false"}
    }
