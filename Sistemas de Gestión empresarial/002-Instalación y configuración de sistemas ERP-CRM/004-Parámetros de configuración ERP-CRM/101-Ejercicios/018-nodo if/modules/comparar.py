# modules/comparar.py
from typing import Dict, Any

TOOL = {
    "type": "comparar",
    "label": "Comparar",
    "description": "Compara la entrada con un valor (rhs). Devuelve true/false.",
    "config": {
        "op":  {"type": "string", "label": "Operador", "default": "=="},
        "rhs": {"type": "string", "label": "Valor (rhs)", "default": ""}
    }
}

def _coerce_number(s: str):
    try:
        if "." in s:
            return float(s)
        return int(s)
    except Exception:
        return None

def execute(config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    op   = (config.get("op") or "==").strip()
    rhs  = str(config.get("rhs") if config.get("rhs") is not None else "")
    ins  = context.get("inputs", [])

    # toma el primer input simple/escalares (si llega un dict/list, lo convertimos a str)
    x = None
    for it in ins or []:
        x = it
        break

    # Soporta comparar string/num. Para < y > intentamos numérico.
    if op in ("<", ">",):
        x_num   = None
        rhs_num = _coerce_number(rhs)
        if isinstance(x, (int, float)): x_num = x
        else:
            try:
                x_num = _coerce_number(str(x))
            except Exception:
                x_num = None
        if x_num is None or rhs_num is None:
            result = False
        else:
            result = (x_num < rhs_num) if op == "<" else (x_num > rhs_num)

    elif op in ("==", "!="):
        result = (str(x) == rhs) if op == "==" else (str(x) != rhs)

    elif op in ("contains", "substr", "includes"):
        result = (rhs in str(x))

    else:
        # Operador no reconocido: false
        result = False

    return {"data": bool(result)}
