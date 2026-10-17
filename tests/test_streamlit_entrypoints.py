"""Guard against Streamlit startup import regressions.

Cloud may briefly load an older API helper module than a newly deployed page.
No entry point should directly require newly introduced helper exports.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_entry_point_is_independent_of_api_module():
    source = (ROOT / "streamlit_app.py").read_text()
    tree = ast.parse(source)
    top_level = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    assert all(
        not (
            isinstance(node, ast.ImportFrom) and
            node.module == "rve.openai_client"
        )
        for node in top_level
    )
    assert all(
        not (
            isinstance(node, ast.Import) and
            any(alias.name == "rve.openai_client" for alias in node.names)
        )
        for node in top_level
    )


def test_pages_do_not_import_version_specific_helpers_directly():
    for page in ("Recursive_Emergence_Framework.py", "Reflection_Session.py"):
        source = (ROOT / "pages" / page).read_text()
        tree = ast.parse(source)
        assert not any(
            isinstance(node, ast.ImportFrom)
            and node.module == "rve.openai_client"
            and any(alias.name in {"api_error_message", "get_api_key"} for alias in node.names)
            for node in ast.walk(tree)
        )


def test_streamlit_entrypoints_compile():
    for path in (
        ROOT / "streamlit_app.py",
        ROOT / "pages" / "Recursive_Emergence_Framework.py",
        ROOT / "pages" / "Reflection_Session.py",
    ):
        compile(path.read_text(), str(path), "exec")
