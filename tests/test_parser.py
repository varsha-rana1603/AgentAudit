from pathlib import Path

from agentaudit.scanner.parser import parse_file


def test_parse_function(tmp_path: Path):
    source = """
def predict(x: list[float], temperature: float = 1.0) -> float:
    \"\"\"Predict a value.\"\"\"
    result = model.predict(x)
    return result
"""

    path = tmp_path / "model.py"
    path.write_text(source)

    parsed = parse_file(path)

    assert len(parsed.functions) == 1

    function = parsed.functions[0]

    assert function.name == "predict"
    assert function.line == 2
    assert function.docstring == "Predict a value."
    assert function.return_annotation == "float"

    assert function.parameters[0].name == "x"
    assert function.parameters[0].annotation == "list[float]"

    assert function.parameters[1].name == "temperature"
    assert function.parameters[1].annotation == "float"

    assert "model.predict" in function.calls


def test_parse_class(tmp_path: Path):
    source = """
class Predictor(BaseModel):
    \"\"\"A prediction model.\"\"\"

    def predict(self, x: float) -> float:
        return x * 2
"""

    path = tmp_path / "model.py"
    path.write_text(source)

    parsed = parse_file(path)

    assert len(parsed.classes) == 1

    cls = parsed.classes[0]

    assert cls.name == "Predictor"
    assert cls.bases == ["BaseModel"]
    assert cls.docstring == "A prediction model."

    assert len(cls.methods) == 1
    assert cls.methods[0].name == "predict"


def test_parse_imports(tmp_path: Path):
    source = """
import torch
import numpy as np
from sklearn.model_selection import train_test_split
"""

    path = tmp_path / "imports.py"
    path.write_text(source)

    parsed = parse_file(path)

    assert len(parsed.imports) == 3

    assert parsed.imports[0].module == "torch"

    assert parsed.imports[1].module == "numpy"
    assert parsed.imports[1].alias == "np"

    assert parsed.imports[2].module == "sklearn.model_selection"
    assert parsed.imports[2].name == "train_test_split"


def test_module_docstring(tmp_path: Path):
    source = '''
"""This module trains a classifier."""

def train():
    pass
'''

    path = tmp_path / "train.py"
    path.write_text(source)

    parsed = parse_file(path)

    assert parsed.module_docstring == "This module trains a classifier."