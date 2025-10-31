# modules/cmp_neq.py
TOOL = {
    "type": "cmp_neq",
    "label": "!= (not equals)",
    "description": "Devuelve true si input != constante.",
    "config": {
        "value": {"type":"string","label":"Constante","default":""}
    }
}

def _coerce(a, b):
    try:
        return float(a), float(b), True
    except Exception:
        return str(a), str(b), False

def execute(config, context):
    target = config.get("value","")
    ins = context.get("inputs",[])
    x = ins[0] if ins else ""
    a,b,_ = _coerce(x, target)
    return {"result": a != b}
