# Support Library
# For modifies and reads configurations.
import json

CONFIG_FILE = "data/config.json"


def read_config() -> dict:
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def get_config(key, default_value=None) -> str | bool | int:
    config = read_config()
    key = key.split(".")
    for k in key:
        if k in config:
            return config[k]
        else:
            return default_value


def write_config(config) -> None:
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)


def write_single_config(key, value) -> None:
    config = read_config()
    config[key] = value
    write_config(config)


def reset_config() -> None:
    write_config({})
