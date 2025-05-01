import os
import importlib

# Auto-import all Python files in this folder (except __init__.py)
for filename in os.listdir(os.path.dirname(__file__)):
    if filename.endswith('.py') and filename != '__init__.py':
        module_name = f'{__name__}.{filename[:-3]}'
        importlib.import_module(module_name)
