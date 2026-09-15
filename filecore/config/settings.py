"""
FileCore Configuration Manager
"""
import os
import json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "filecore_data", "config.json")

DEFAULTS = {
    "indexed_paths": [],
    "theme": "dark",
    "max_cpu_percent": 30,
    "pause_on_battery": True,
    "enable_semantic_search": False,
    "log_level": "INFO"
}

def load_config() -> dict:
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            data = json.load(f)
        # Fill in any missing keys from defaults
        for k, v in DEFAULTS.items():
            data.setdefault(k, v)
        return data
    return dict(DEFAULTS)

def save_config(config: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

def get(key: str):
    return load_config().get(key, DEFAULTS.get(key))

def set(key: str, value):
    config = load_config()
    config[key] = value
    save_config(config)
