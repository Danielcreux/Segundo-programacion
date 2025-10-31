# modules/cmp_contains.py
TOOL = {
    "type": "cmp_contains",
    "label": "contains (substring)",
    "description": "Devuelve true si input contiene la subcadena.",
    "config": {
        "value": {"type":"string","label":"Subcadena","default":""}
    }
}

def execute(config, context):
    sub = str(config.get("value",""))
    ins = context.get("inputs",[])
    x = "" if not ins else str(ins[0])
    return {"result": (sub in x)}
