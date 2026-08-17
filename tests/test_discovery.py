from pathlib import Path

from agentaudit.scanner.discovery import discover_files


def test_discovers_files(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "README.md").write_text("# Test")

    files = discover_files(tmp_path)

    assert tmp_path / "main.py" in files
    assert tmp_path / "README.md" in files


def test_ignores_virtual_environment(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')")

    venv = tmp_path / ".venv"
    venv.mkdir()
    (venv / "fake.py").write_text("print('ignored')")

    files = discover_files(tmp_path)

    assert venv / "fake.py" not in files


def test_ignores_git_directory(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')")

    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("fake git config")

    files = discover_files(tmp_path)

    assert git_dir / "config" not in files


def test_ignores_python_cache(tmp_path: Path):
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "module.pyc").write_bytes(b"fake")

    (tmp_path / "main.py").write_text("print('hello')")

    files = discover_files(tmp_path)

    assert cache / "module.pyc" not in files


def test_ignores_egg_info(tmp_path: Path):
    egg_info = tmp_path / "project.egg-info"
    egg_info.mkdir()
    (egg_info / "PKG-INFO").write_text("generated metadata")

    (tmp_path / "main.py").write_text("print('hello')")

    files = discover_files(tmp_path)

    assert egg_info / "PKG-INFO" not in files


def test_results_are_deterministic(tmp_path: Path):
    (tmp_path / "z.py").write_text("")
    (tmp_path / "a.py").write_text("")
    (tmp_path / "m.py").write_text("")

    files = discover_files(tmp_path)

    assert files == sorted(files)
