import importlib.util
import os
from typing import Dict, Any

def _import_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def load_backend_modules() -> Dict[str, Dict[str, Any]]:
    """
    Escanea el directorio actual (modules/) buscando archivos *.py (excepto __init__.py),
    importa cada uno y registra módulos que expongan:
      - TOOL: dict con {type,label,description,config}
      - execute(config:dict, context:dict) -> dict (resultado)
    Devuelve: dict[type] = {"TOOL":..., "execute":callable}
    """
    registry: Dict[str, Dict[str, Any]] = {}
    base_dir = os.path.dirname(__file__)

    for filename in os.listdir(base_dir):
        if not filename.endswith(".py"): 
            continue
        if filename == "__init__.py":
            continue

        path = os.path.join(base_dir, filename)
        mod_name = f"modules.{filename[:-3]}"
        mod = _import_module_from_path(mod_name, path)
        if not mod:
            continue

        tool = getattr(mod, "TOOL", None)
        execute = getattr(mod, "execute", None)

        if not isinstance(tool, dict) or not callable(execute):
            # No cumple el contrato mínimo
            continue

        tool_type = tool.get("type")
        if not tool_type:
            continue

        registry[tool_type] = {"TOOL": tool, "execute": execute}

    return registry
