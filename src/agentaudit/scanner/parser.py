from dataclasses import dataclass, field
from pathlib import Path
import ast

@dataclass
class ParameterInfo:
    name: str
    annotation: str | None = None

@dataclass 
class FunctionInfo:
    name: str
    line: str
    parameters: list[ParameterInfo] = field(default_factory=list)
    return_annotation: str | None = None
    decorators: list[str] = field(default_factory=list)
    docstring: str | None = None
    calls: list[str] = field(default_factory=list)

@dataclass
class ClassInfo: 
    name: str
    line: str
    bases: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    docstring: str | None = None
    methods: list[FunctionInfo] = field(default_factory=list)

@dataclass
class ImportInfo:
    module: str
    name: str | None = None
    alias: str | None = None

@dataclass
class ParsedFile: 
    path: Path
    module_docstring: str | None
    imports: list[ImportInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)


#AST Helper Functions
def _get_source(node: ast.AST) -> str:
    #Convert an AST expressioni nto readable source
    return ast.unparse(node)

def _get_decorators(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> list[str]:
    return [_get_source(decorator) for decorator in node.decorator_list]

def _get_parameters(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ParameterInfo]:
    parameters = []
    all_args = [
        *node.args.posonlyargs,
        *node.args.args,
        *node.args.kwonlyargs
    ]

    if node.args.vararg:
        all_args.append(node.args.vararg)

    if node.args.kwarg:
        all_args.append(node.args.kwarg)

    for argument in all_args:
        annotation = (
            _get_source(argument.annotation)
            if argument.annotation is not None 
            else None
        )
        parameters.append(
            ParameterInfo(name = argument.arg,annotation = annotation)
        )
    return parameters

def _get_calls(node: ast.AST) -> list[str]:
    calls = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            calls.append(_get_source(child.func))
    return calls

#PARSE FUNCTION
def _parse_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
    return_annotation = (_get_source(node.returns) if node.returns is not None else None)

    return FunctionInfo(
        name = node.name,
        line = node.lineno,
        parameters = _get_parameters(node),
        return_annotation = return_annotation,
        decorators = _get_decorators(node),
        docstring = ast.get_docstring(node),
        calls = _get_calls(node)
    )

#PARSE CLASSES
def _parse_class(node: ast.ClassDef) -> ClassInfo:
    methods = []

    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append(_parse_function(child))

    return ClassInfo(
        name = node.name,
        line = node.lineno,
        bases = [_get_source(base) for base in node.bases],
        decorators = _get_decorators(node),
        docstring = ast.get_docstring(node),
        methods = methods
    )

#PARSE IMPORTS
def _parse_import(node: ast.Import) -> list[ImportInfo]:
    return [
        ImportInfo(
            module=alias.name,
            alias=alias.asname,
        )
        for alias in node.names
    ]

def _parse_import_from(node: ast.ImportFrom) -> list[ImportInfo]:
    module = node.module or ""

    return [
        ImportInfo(
            module=module,
            name=alias.name,
            alias=alias.asname,
        )
        for alias in node.names
    ]

#MAIN PARSER
def parse_file(path: Path) -> ParsedFile:
    """Parse a Python file and extract deterministic structural information."""

    source = path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise SyntaxError(
            f"Could not parse {path}: {exc}"
        ) from exc

    parsed = ParsedFile(
        path=path,
        module_docstring=ast.get_docstring(tree),
    )

    for node in tree.body:
        if isinstance(node, ast.Import):
            parsed.imports.extend(_parse_import(node))

        elif isinstance(node, ast.ImportFrom):
            parsed.imports.extend(_parse_import_from(node))

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            parsed.functions.append(_parse_function(node))

        elif isinstance(node, ast.ClassDef):
            parsed.classes.append(_parse_class(node))

    return parsed

