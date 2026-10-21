import ast
from pathlib import Path

import pytest


@pytest.mark.parametrize("layer", ["domain", "application"])
def test_inner_layers_do_not_import_http_or_infrastructure(layer):
    root = Path(__file__).resolve().parents[1] / "app" / layer
    forbidden = ("fastapi", "starlette", "sqlalchemy", "app.infrastructure", "app.api", "app.core")
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            modules = (
                [node.module or ""]
                if isinstance(node, ast.ImportFrom)
                else [item.name for item in node.names]
                if isinstance(node, ast.Import)
                else []
            )
            assert not any(module.startswith(forbidden) for module in modules), (
                f"Inversão de dependência violada em {path.name}"
            )
