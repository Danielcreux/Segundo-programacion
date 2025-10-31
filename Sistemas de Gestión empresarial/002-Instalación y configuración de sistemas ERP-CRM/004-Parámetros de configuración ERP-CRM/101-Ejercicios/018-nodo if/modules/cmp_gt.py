# modules/cmp_gt.py
TOOL = {
    "type": "cmp_gt",
    "label": "> (greater than)",
    "description": "Devuelve true si input > constante (numérico si ambos números, si no lexicográfico).",
    "config": {
        "value": {"type":"string","label":"Constante","default":"0"}
    }
}

def _coerce(a, b):
    try:
        return float(a), float(b), True
    except Exception:
        return str(a), str(b), False

def execute(config, context):
    target = config.get("value","0")
    ins = context.get("inputs",[])
    x = ins[0] if ins else ""
    a,b,_ = _coerce(x, target)
    return {"result": a > b}
