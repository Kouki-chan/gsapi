import json
import os

REGISTRY_FILE = "file_registry.json"

def _load():
    if not os.path.exists(REGISTRY_FILE):
        return {}
    with open(REGISTRY_FILE, "r") as f:
        return json.load(f)

def _save(registry):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)

def register_file(name: str, path: str):
    if not os.path.exists(path):
        return {"error": f"Path does not exist: {path}"}
    registry = _load()
    registry[name] = path
    _save(registry)
    return {"status": "registered", "name": name, "path": path}

def get_file_path(name: str):
    registry = _load()
    return registry.get(name)

def list_files():
    return _load()

def remove_file(name: str):
    registry = _load()
    if name not in registry:
        return {"error": f"{name} not found"}
    del registry[name]
    _save(registry)
    return {"status": "removed", "name": name}