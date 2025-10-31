# modules/if_router.py
from typing import Dict, Any, List

TOOL = {
    "type": "if_router",
    "label": "IF (cond → true/false)",
    "description": "Recibe entradas: una booleana (cond) y otra payload. Enruta payload por 'true' o 'false'.",
    "config": {}
}

def _flatten_inputs(inputs: List[Any]):
    # Toma la primera booleana que encuentre, y el último payload no booleano (o cualquiera)
    cond = None
    payload = None
    for it in inputs or []:
        if isinstance(it, dict) and "result" in it and isinstance(it["result"], bool):
            cond = it["result"]
        elif isinstance(it, bool) and cond is None:
            cond = it
        else:
            payload = it
    return cond, payload

def execute(config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    inputs = context.get("inputs", [])
    cond, payload = _flatten_inputs(inputs)

    # Por defecto, si no hay cond, tratamos como False y pasamos payload tal cual por 'false'
    cond_bool = bool(cond) if cond is not None else False

    return {
        "routes": {
            "true": payload if cond_bool else None,
            "false": payload if not cond_bool else None,
        },
        "result": cond_bool  # útil para debug/render
    }
