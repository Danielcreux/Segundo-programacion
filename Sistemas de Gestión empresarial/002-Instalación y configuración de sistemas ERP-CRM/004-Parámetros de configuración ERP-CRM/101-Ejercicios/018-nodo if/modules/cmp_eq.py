
# modules/cmp_eq.py
TOOL = {
    "type": "cmp_eq",
    "label": "== (equals)",
    "description": "Compara texto/num con una constante y devuelve true/false.",
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
    return {"result": a == b}
