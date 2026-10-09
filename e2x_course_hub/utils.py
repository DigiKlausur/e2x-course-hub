import re
from typing import Any, Dict

import yaml


def load_yaml(yaml_file):
    """
    Loads a YAML file and returns its contents as a dictionary.

    Args:
        yaml_file (str): Path to the YAML file.
    Returns:
        dict: The contents of the YAML file.
    """

    def yaml_constructor(loader, node):
        # Preserve string type for date-like strings
        if isinstance(node.value, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", node.value):
            return node.value
        return loader.construct_scalar(node)

    yaml.add_implicit_resolver(
        "tag:yaml.org,2002:timestamp", re.compile(r"^\d{4}-\d{1,2}-\d{1,2}"), Loader=yaml.SafeLoader
    )
    yaml.add_constructor("tag:yaml.org,2002:timestamp", yaml_constructor, Loader=yaml.SafeLoader)

    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)


def resolve_placeholders(obj: Any, ctx: Dict[str, Any], namespace: str = "inputs") -> Any:
    """Recursively resolve ${{namespace.key}} placeholders in a data structure.

    Walks dicts, lists, and strings, replacing occurrences of
    ``${{<namespace>.<key>}}`` with the corresponding value from *ctx*.
    Non-string leaves are returned as-is.

    Args:
        obj: The data structure to resolve (dict, list, str, or scalar).
        ctx: Mapping of placeholder names to their replacement values.
        namespace: The namespace prefix used in placeholders (default: "inputs").

    Returns:
        A deep copy of *obj* with all matching placeholders substituted.

    Raises:
        ValueError: If a placeholder references a key not present in *ctx*.
    """
    if isinstance(obj, dict):
        return {k: resolve_placeholders(v, ctx, namespace) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_placeholders(v, ctx, namespace) for v in obj]
    elif isinstance(obj, str):

        def replace_param(match):
            param_name = match.group(1)
            if param_name not in ctx:
                raise ValueError(f"Parameter '{param_name}' not found in context")
            return str(ctx[param_name])

        return re.sub(r"\$\{\{\s*" + namespace + r"\.(\w+)\s*\}\}", replace_param, obj)
    else:
        return obj
