import ast
import sys
from pathlib import Path

from ..contracts import Storyboard

ALLOWED_IMPORTS = {"render_kit", "_shared", "numpy", "math", "manim"}
FORBIDDEN_NAMES = {"open", "exec", "eval", "compile", "__import__", "input", "globals", "locals", "breakpoint", "setattr", "delattr",
                   "os", "sys", "subprocess", "shutil", "socket", "Path", "urllib", "requests"}
FORBIDDEN_ATTRS = {"system", "popen", "unlink", "rmtree", "write_text", "write_bytes", "urlopen"}


def lint_scene(path: Path, sb: Storyboard) -> list[str]:
    issues = []
    sid = path.stem
    spec = next((s for s in sb.scenes if s.scene_id == sid), None)
    if spec is None:
        return [f"{sid}: no storyboard scene"]
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] not in ALLOWED_IMPORTS:
                    issues.append(f"{sid}: import {a.name} not allowed")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in ALLOWED_IMPORTS:
                issues.append(f"{sid}: from {node.module} import not allowed")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            issues.append(f"{sid}: name {node.id} not allowed")
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRS:
            issues.append(f"{sid}: attribute {node.attr} not allowed")
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    if [c.name for c in classes] != [sid]:
        issues.append(f"{sid}: file must define exactly one class named {sid}")
    elif not any(isinstance(b, ast.Name) and b.id == "Reel" for b in classes[0].bases):
        issues.append(f"{sid}: class must subclass Reel")
    says, finished = [], False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "say":
                if len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    says.append((node.lineno, node.args[0].value))
                else:
                    issues.append(f"{sid}: say() needs one literal line_id")
            if node.func.attr == "finish":
                finished = True
    order = [v for _, v in sorted(says)]
    expected = [ln.line_id for ln in spec.lines]
    if order != expected:
        issues.append(f"{sid}: say() order {order} != storyboard {expected}")
    if not finished:
        issues.append(f"{sid}: must end with self.finish()")
    return issues


def run(job: Path) -> list[str]:
    sb = Storyboard.model_validate_json((job / "storyboard.json").read_text())
    issues = []
    for s in sb.scenes:
        p = job / "scenes" / f"{s.scene_id}.py"
        issues += lint_scene(p, sb) if p.exists() else [f"{s.scene_id}: missing scene file"]
    return issues


if __name__ == "__main__":
    out = run(Path(sys.argv[1]))
    print("\n".join(out) if out else "lint ok")
    sys.exit(1 if out else 0)
