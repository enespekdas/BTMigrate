import os

def set_env_variable(key: str, value: str):
    os.environ[key] = value

def get_env_variable(key: str, default=None):
    return os.environ.get(key, default)