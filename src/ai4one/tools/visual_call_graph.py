import ast
import os
import argparse
from collections import defaultdict
from typing import Dict, List, Optional


class DefinitionVisitor(ast.NodeVisitor):
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.definitions = {"functions": set(), "classes": defaultdict(set)}

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.definitions["functions"].add(f"{self.module_name}.{node.name}")

    def visit_ClassDef(self, node: ast.ClassDef):
        class_name = f"{self.module_name}.{node.name}"
        self.definitions["classes"][class_name] = set()
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_name = f"{class_name}.{item.name}"
                self.definitions["classes"][class_name].add(method_name)


class CallVisitor(ast.NodeVisitor):
    def __init__(
        self,
        module_name: str,
        imports: Dict,
        from_imports: Dict,
        analyzer: "ProjectAnalyzer",
    ):
        self.module_name = module_name
        self.imports = imports
        self.from_imports = from_imports
        self.analyzer = analyzer
        self.graph = defaultdict(set)
        self.scope_stack: List[Dict[str, str]] = [{}]
        self.current_path: List[str] = []

    def _get_current_fqn(self) -> Optional[str]:
        if not self.current_path:
            return self.module_name
        return f"{self.module_name}.{'.'.join(self.current_path)}"

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.current_path.append(node.name)
        self.scope_stack.append({})
        for arg in node.args.args:
            if arg.arg != "self":
                self.scope_stack[-1][arg.arg] = "typing.Any"
        self.generic_visit(node)
        self.scope_stack.pop()
        self.current_path.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef):
        self.current_path.append(node.name)
        self.generic_visit(node)
        self.current_path.pop()

    def visit_Assign(self, node: ast.Assign):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id
            if isinstance(node.value, ast.Call):
                callee_fqn = self._resolve_call_fqn(node.value.func)
                if callee_fqn and self.analyzer._is_class(callee_fqn):
                    self.scope_stack[-1][target_name] = callee_fqn
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        caller_fqn = self._get_current_fqn()
        callee_fqn_candidate = self._resolve_call_fqn(node.func)
        if caller_fqn and callee_fqn_candidate:
            final_callee = self.analyzer._filter_and_resolve_callee(
                callee_fqn_candidate
            )
            if final_callee:
                self.graph[caller_fqn].add(final_callee)
        self.generic_visit(node)

    def _resolve_call_fqn(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Name):
            name = node.id
            for scope in reversed(self.scope_stack):
                if name in scope:
                    return scope[name]
            if name in self.from_imports:
                return f"{self.from_imports[name]}.{name}"
            if name in self.imports:
                return self.imports[name]
            return f"{self.module_name}.{name}"
        elif isinstance(node, ast.Attribute):
            prefix_type_fqn = self._resolve_call_fqn(node.value)
            if isinstance(node.value, ast.Name) and node.value.id == "self":
                prefix_type_fqn = (
                    f"{self.module_name}.{'.'.join(self.current_path[:-1])}"
                )
            return f"{prefix_type_fqn}.{node.attr}" if prefix_type_fqn else None
        return None


class ProjectAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
        self.call_graph = defaultdict(set)
        self.file_info: Dict[str, Dict] = {}
        self.project_definitions: Dict[str, Dict] = {}

    def analyze(self, files_to_analyze: Optional[List[str]] = None):
        """
        分析项目。如果提供了files_to_analyze列表，则只分析这些文件。
        否则，自动发现项目根目录下的所有文件。
        """
        if files_to_analyze:
            py_files_to_scan = (
                self._discover_files()
            )  # 仍然扫描所有文件以建立完整的定义
            py_files_to_analyze = files_to_analyze
        else:
            py_files_to_scan = self._discover_files()
            py_files_to_analyze = py_files_to_scan

        for filepath in py_files_to_scan:
            self._gather_definitions(filepath)
        for filepath in py_files_to_scan:
            self._pre_analyze_imports(filepath)
        for filepath in py_files_to_analyze:  # 只对指定的文件进行调用分析
            self._analyze_file_calls(filepath)

    def _is_class(self, fqn: str) -> bool:
        module_name = ".".join(fqn.split(".")[:-1])
        return (
            module_name in self.project_definitions
            and fqn in self.project_definitions[module_name].get("classes", {})
        )

    def _is_method(self, fqn: str) -> bool:
        parts = fqn.split(".")
        if len(parts) < 2:
            return False
        class_fqn = ".".join(parts[:-1])
        class_module_name = ".".join(class_fqn.split(".")[:-1])
        if (
            class_module_name in self.project_definitions
            and class_fqn
            in self.project_definitions[class_module_name].get("classes", {})
        ):
            return (
                fqn in self.project_definitions[class_module_name]["classes"][class_fqn]
            )
        return False

    def _filter_and_resolve_callee(self, fqn: str) -> Optional[str]:
        parts = fqn.split(".")
        module_name = ".".join(parts[:-1])
        if module_name in self.project_definitions and fqn in self.project_definitions[
            module_name
        ].get("functions", set()):
            return fqn
        if self._is_method(fqn):
            return fqn
        if self._is_class(fqn):
            init_method_fqn = f"{fqn}.__init__"
            if self._is_method(init_method_fqn):
                return init_method_fqn
        return None

    def _discover_files(self) -> List[str]:
        py_files = []
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))
        return py_files

    def _filepath_to_module(self, filepath: str) -> str:
        rel_path = os.path.relpath(filepath, self.project_root)
        if os.path.basename(rel_path) == "__init__.py":
            rel_path = os.path.dirname(rel_path) or ""
        module_path = os.path.splitext(rel_path)[0]
        return module_path.replace(os.path.sep, ".")

    def _gather_definitions(self, filepath: str):
        module_name = self._filepath_to_module(filepath)
        self.project_definitions[module_name] = {
            "functions": set(),
            "classes": defaultdict(set),
        }
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
                visitor = DefinitionVisitor(module_name)
                visitor.visit(tree)
                self.project_definitions[module_name] = visitor.definitions
            except SyntaxError as e:
                print(f"Skipping file with syntax error: {filepath}\n{e}")

    def _pre_analyze_imports(self, filepath: str):
        imports: Dict[str, str] = {}
        from_imports: Dict[str, str] = {}
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                return
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.asname or alias.name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    for alias in node.names:
                        from_imports[alias.asname or alias.name] = node.module
        self.file_info[filepath] = {"imports": imports, "from_imports": from_imports}

    def _analyze_file_calls(self, filepath: str):
        if filepath not in self.file_info:
            return
        module_name = self._filepath_to_module(filepath)
        info = self.file_info[filepath]

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                # 如果文件有语法错误，则跳过
                return

        # 传递 analyzer 实例 (self) 给 visitor
        visitor = CallVisitor(module_name, info["imports"], info["from_imports"], self)
        visitor.visit(tree)  # 现在 'tree' 变量已经被正确定义了

        for caller, callees in visitor.graph.items():
            self.call_graph[caller].update(callees)

    def generate_dot_file(self, output_path: str):
        # (This part is unchanged, so I'll omit it for brevity, but it should be copied from the previous version)
        lines = [
            "digraph CallGraph {",
            "    rankdir=LR;",
            '    node [shape=box, style=rounded, fontname="Arial"];',
            '    edge [fontname="Arial", fontsize=10];',
            "    graph [splines=ortho];\n",
        ]
        all_nodes = set(self.call_graph.keys())
        for callees in self.call_graph.values():
            all_nodes.update(callees)
        module_contents = defaultdict(
            lambda: {"classes": defaultdict(list), "functions": []}
        )
        for fqn in all_nodes:
            parts = fqn.split(".")
            is_method = self._is_method(fqn)
            if is_method:
                module_name = ".".join(parts[:-2])
                class_name = ".".join(parts[:-1])
                module_contents[module_name]["classes"][class_name].append(fqn)
            else:
                module_name = ".".join(parts[:-1]) if "." in fqn else fqn
                module_contents[module_name]["functions"].append(fqn)
        for i, (module_name, contents) in enumerate(module_contents.items()):
            if not module_name:
                continue
            lines.append(f"    subgraph cluster_module_{i} {{")
            lines.append(f'        label = "Module: {module_name}";')
            lines.append('        style=filled; color="#EFEFEF";')
            for func_fqn in contents["functions"]:
                func_name = func_fqn.split(".")[-1]
                lines.append(f'        "{func_fqn}" [label="{func_name}"];')
            for j, (class_name, methods) in enumerate(contents["classes"].items()):
                lines.append(f"        subgraph cluster_class_{i}_{j} {{")
                lines.append(
                    f"            label = \"Class: {class_name.split('.')[-1]}\";"
                )
                lines.append('            style=filled; color="#DDEEFF";')
                lines.append("            node [style=filled, fillcolor=white];")
                for method_fqn in methods:
                    method_short_name = ".".join(method_fqn.split(".")[-2:])
                    lines.append(
                        f'            "{method_fqn}" [label="{method_short_name}"];'
                    )
                lines.append("        }")
            lines.append("    }\n")
        for caller, callees in self.call_graph.items():
            if not callees:
                continue
            for callee in callees:
                lines.append(f'    "{caller}" -> "{callee}";')
        lines.append("}")
        dot_content = "\n".join(lines)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dot_content)
        print(f"✅ DOT source file generated: {output_path}")
