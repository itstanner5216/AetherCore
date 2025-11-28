#!/usr/bin/env python3
"""
Defense Agent - Proves files are NECESSARY and should be KEPT

The Defense Agent's job is to find EVERY possible reason a file should be kept.
It builds the strongest possible case for file retention by:
1. Finding all import chains and dependencies
2. Identifying documentation cross-references
3. Detecting configuration relationships
4. Calculating business/project value
5. Finding potential future use indicators
"""

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class DefenseEvidence:
    """Evidence supporting file retention"""

    category: str
    description: str
    strength: float  # 0.0 to 1.0
    source: str
    details: Dict = field(default_factory=dict)


@dataclass
class DefenseCase:
    """Complete defense case for a file"""

    file_path: str
    verdict: str  # "ESSENTIAL", "IMPORTANT", "USEFUL", "MARGINAL"
    confidence: float
    evidence: List[DefenseEvidence]
    import_chain: List[str]
    referenced_by: List[str]
    argument: str

    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "evidence": [
                {
                    "category": e.category,
                    "description": e.description,
                    "strength": e.strength,
                    "source": e.source,
                    "details": e.details,
                }
                for e in self.evidence
            ],
            "import_chain": self.import_chain,
            "referenced_by": self.referenced_by,
            "argument": self.argument,
        }


class DefenseAgent:
    """
    🛡️ DEFENSE AGENT - Advocate for File Retention

    This agent's SOLE PURPOSE is to prove files should be KEPT.
    It will search exhaustively for any reason to retain a file.
    """

    def __init__(self, repo_root: str, all_files: List[str]):
        self.repo_root = Path(repo_root)
        self.all_files = set(all_files)
        self.file_contents_cache: Dict[str, str] = {}
        self.import_graph: Dict[str, Set[str]] = {}  # file -> files that import it
        self.reference_graph: Dict[str, Set[str]] = {}  # file -> files that reference it

        # Build comprehensive reference maps
        self._build_import_graph()
        self._build_reference_graph()

    def _get_file_content(self, file_path: str) -> str:
        """Get file content with caching"""
        if file_path not in self.file_contents_cache:
            try:
                full_path = self.repo_root / file_path
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    self.file_contents_cache[file_path] = f.read()
            except:
                self.file_contents_cache[file_path] = ""
        return self.file_contents_cache[file_path]

    def _build_import_graph(self):
        """Build reverse import graph: which files import which"""
        for file_path in self.all_files:
            content = self._get_file_content(file_path)

            # Python imports
            if file_path.endswith(".py"):
                imports = self._extract_python_imports(content)
                for imp in imports:
                    if imp not in self.import_graph:
                        self.import_graph[imp] = set()
                    self.import_graph[imp].add(file_path)

            # JavaScript imports
            elif file_path.endswith((".js", ".ts", ".jsx", ".tsx")):
                imports = self._extract_js_imports(content, file_path)
                for imp in imports:
                    if imp not in self.import_graph:
                        self.import_graph[imp] = set()
                    self.import_graph[imp].add(file_path)

    def _extract_python_imports(self, content: str) -> Set[str]:
        """Extract Python import targets"""
        imports = set()

        # from X import Y
        for match in re.finditer(r"from\s+([\w.]+)\s+import", content):
            module = match.group(1)
            imports.add(module)
            imports.add(module.replace(".", "/") + ".py")

        # import X
        for match in re.finditer(r"^import\s+([\w.]+)", content, re.MULTILINE):
            module = match.group(1)
            imports.add(module)
            imports.add(module.replace(".", "/") + ".py")

        return imports

    def _extract_js_imports(self, content: str, source_file: str) -> Set[str]:
        """Extract JavaScript/TypeScript import targets"""
        imports = set()
        source_dir = str(Path(source_file).parent)

        # require() and import statements
        patterns = [
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                target = match.group(1)
                if target.startswith("."):
                    # Resolve relative path
                    resolved = os.path.normpath(os.path.join(source_dir, target))
                    imports.add(resolved)
                    for ext in ["", ".js", ".ts", ".jsx", ".tsx", "/index.js"]:
                        imports.add(resolved + ext)
                else:
                    imports.add(target)

        return imports

    def _build_reference_graph(self):
        """Build graph of file references (not just imports)"""
        for file_path in self.all_files:
            content = self._get_file_content(file_path)

            # Look for references to other files
            for other_file in self.all_files:
                if other_file == file_path:
                    continue

                # Check various reference patterns
                filename = Path(other_file).name
                stem = Path(other_file).stem

                # Direct filename mentions
                if filename in content or stem in content:
                    if other_file not in self.reference_graph:
                        self.reference_graph[other_file] = set()
                    self.reference_graph[other_file].add(file_path)

    def defend(self, file_path: str) -> DefenseCase:
        """
        Build the strongest possible defense case for keeping a file.
        """
        evidence = []

        # 1. Import Chain Analysis - Who depends on this file?
        import_evidence = self._analyze_importers(file_path)
        evidence.extend(import_evidence)

        # 2. Reference Analysis - Who mentions this file?
        reference_evidence = self._analyze_references(file_path)
        evidence.extend(reference_evidence)

        # 3. Configuration Role - Is this a config file?
        config_evidence = self._analyze_config_role(file_path)
        evidence.extend(config_evidence)

        # 4. Entry Point Analysis - Is this an entry point?
        entry_evidence = self._analyze_entry_point(file_path)
        evidence.extend(entry_evidence)

        # 5. Documentation Value - Does this provide docs/examples?
        doc_evidence = self._analyze_documentation_value(file_path)
        evidence.extend(doc_evidence)

        # 6. Git History Analysis - Has this been actively maintained?
        git_evidence = self._analyze_git_activity(file_path)
        evidence.extend(git_evidence)

        # 7. Naming Convention Analysis - Does the name suggest importance?
        naming_evidence = self._analyze_naming_importance(file_path)
        evidence.extend(naming_evidence)

        # 8. Content Quality Analysis - Is the content substantial?
        content_evidence = self._analyze_content_quality(file_path)
        evidence.extend(content_evidence)

        # 9. Integration Points - Does this connect systems?
        integration_evidence = self._analyze_integration_points(file_path)
        evidence.extend(integration_evidence)

        # 10. Future Value Analysis - Might this be needed later?
        future_evidence = self._analyze_future_value(file_path)
        evidence.extend(future_evidence)

        # Build import chain
        import_chain = self._build_import_chain(file_path)

        # Get files that reference this one
        referenced_by = list(self.reference_graph.get(file_path, set()))

        # Calculate verdict
        verdict, confidence = self._calculate_verdict(evidence)

        # Build argument
        argument = self._build_defense_argument(file_path, evidence, verdict)

        return DefenseCase(
            file_path=file_path,
            verdict=verdict,
            confidence=confidence,
            evidence=evidence,
            import_chain=import_chain,
            referenced_by=referenced_by,
            argument=argument,
        )

    def _analyze_importers(self, file_path: str) -> List[DefenseEvidence]:
        """Find all files that import this file"""
        evidence = []

        # Direct importers
        importers = self.import_graph.get(file_path, set())

        # Also check by stem name
        stem = Path(file_path).stem
        for key, importers_set in self.import_graph.items():
            if stem in key:
                importers = importers.union(importers_set)

        if importers:
            evidence.append(
                DefenseEvidence(
                    category="IMPORT_DEPENDENCY",
                    description=f"File is imported by {len(importers)} other file(s)",
                    strength=min(1.0, len(importers) * 0.3),
                    source="import_analysis",
                    details={"importers": list(importers)[:10]},
                )
            )

            # Check if any importers are entry points
            entry_point_importers = [
                f
                for f in importers
                if any(ep in f.lower() for ep in ["main", "index", "app", "server", "entry"])
            ]
            if entry_point_importers:
                evidence.append(
                    DefenseEvidence(
                        category="ENTRY_POINT_DEPENDENCY",
                        description=f"Imported by entry point files: {entry_point_importers}",
                        strength=0.9,
                        source="import_analysis",
                        details={"entry_points": entry_point_importers},
                    )
                )

        return evidence

    def _analyze_references(self, file_path: str) -> List[DefenseEvidence]:
        """Find all references to this file"""
        evidence = []
        references = self.reference_graph.get(file_path, set())

        if references:
            evidence.append(
                DefenseEvidence(
                    category="FILE_REFERENCE",
                    description=f"Referenced in {len(references)} other file(s)",
                    strength=min(0.8, len(references) * 0.2),
                    source="reference_analysis",
                    details={"referenced_by": list(references)[:10]},
                )
            )

        # Check for documentation references
        doc_references = [r for r in references if r.endswith((".md", ".rst", ".txt"))]
        if doc_references:
            evidence.append(
                DefenseEvidence(
                    category="DOCUMENTED",
                    description=f"Mentioned in documentation: {doc_references}",
                    strength=0.6,
                    source="reference_analysis",
                    details={"doc_files": doc_references},
                )
            )

        return evidence

    def _analyze_config_role(self, file_path: str) -> List[DefenseEvidence]:
        """Analyze if file is a configuration file"""
        evidence = []
        filename = Path(file_path).name.lower()

        config_indicators = [
            "config",
            "settings",
            "env",
            "rc",
            "options",
            "package.json",
            "tsconfig",
            "webpack",
            "babel",
            "docker",
            "yaml",
            "yml",
            "toml",
            "ini",
        ]

        if any(ind in filename for ind in config_indicators):
            evidence.append(
                DefenseEvidence(
                    category="CONFIGURATION_FILE",
                    description="File appears to be a configuration file",
                    strength=0.85,
                    source="naming_analysis",
                    details={"filename": filename},
                )
            )

        # Check content for config patterns
        content = self._get_file_content(file_path)
        if content:
            config_patterns = [
                r"^\s*[A-Z_]+\s*=",  # ENV_VAR = value
                r'"[a-z]+"\s*:\s*{',  # JSON object
                r"^\s*\[[a-z]+\]",  # INI section
            ]
            if any(re.search(p, content, re.MULTILINE) for p in config_patterns):
                evidence.append(
                    DefenseEvidence(
                        category="CONFIG_CONTENT",
                        description="File contains configuration patterns",
                        strength=0.7,
                        source="content_analysis",
                        details={},
                    )
                )

        return evidence

    def _analyze_entry_point(self, file_path: str) -> List[DefenseEvidence]:
        """Analyze if file is an entry point"""
        evidence = []
        filename = Path(file_path).name.lower()

        entry_indicators = [
            "main",
            "index",
            "app",
            "server",
            "entry",
            "__init__",
            "__main__",
            "cli",
            "run",
        ]

        if any(ind in filename for ind in entry_indicators):
            evidence.append(
                DefenseEvidence(
                    category="ENTRY_POINT",
                    description="File appears to be an entry point",
                    strength=0.9,
                    source="naming_analysis",
                    details={"filename": filename},
                )
            )

        # Check for shebang or main block
        content = self._get_file_content(file_path)
        if content:
            if content.startswith("#!") or "if __name__" in content:
                evidence.append(
                    DefenseEvidence(
                        category="EXECUTABLE",
                        description="File is executable (shebang or __main__)",
                        strength=0.85,
                        source="content_analysis",
                        details={},
                    )
                )

        return evidence

    def _analyze_documentation_value(self, file_path: str) -> List[DefenseEvidence]:
        """Analyze documentation value of file"""
        evidence = []
        ext = Path(file_path).suffix.lower()

        if ext in [".md", ".rst", ".txt"]:
            content = self._get_file_content(file_path)
            if content:
                word_count = len(content.split())
                if word_count > 100:
                    evidence.append(
                        DefenseEvidence(
                            category="DOCUMENTATION",
                            description=f"Documentation file with {word_count} words",
                            strength=min(0.8, word_count / 1000),
                            source="content_analysis",
                            details={"word_count": word_count},
                        )
                    )

                # Check for important doc types
                if "readme" in file_path.lower():
                    evidence.append(
                        DefenseEvidence(
                            category="README",
                            description="README file - essential for project documentation",
                            strength=0.95,
                            source="naming_analysis",
                            details={},
                        )
                    )

                if "changelog" in file_path.lower():
                    evidence.append(
                        DefenseEvidence(
                            category="CHANGELOG",
                            description="CHANGELOG file - tracks project history",
                            strength=0.85,
                            source="naming_analysis",
                            details={},
                        )
                    )

        return evidence

    def _analyze_git_activity(self, file_path: str) -> List[DefenseEvidence]:
        """Analyze git history for the file"""
        evidence = []

        try:
            # Get commit count
            result = subprocess.run(
                ["git", "log", "--oneline", "--", file_path],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )
            commits = result.stdout.strip().split("\n") if result.stdout.strip() else []
            commit_count = len(commits)

            if commit_count > 5:
                evidence.append(
                    DefenseEvidence(
                        category="ACTIVE_DEVELOPMENT",
                        description=f"File has {commit_count} commits - actively maintained",
                        strength=min(0.8, commit_count / 20),
                        source="git_analysis",
                        details={"commit_count": commit_count},
                    )
                )

            # Get last commit date
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ci", "--", file_path],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )
            if result.stdout.strip():
                last_commit = result.stdout.strip()
                evidence.append(
                    DefenseEvidence(
                        category="RECENT_ACTIVITY",
                        description=f"Last modified: {last_commit[:10]}",
                        strength=0.5,
                        source="git_analysis",
                        details={"last_commit": last_commit},
                    )
                )

            # Check for multiple contributors
            result = subprocess.run(
                ["git", "shortlog", "-sne", "--", file_path],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )
            contributors = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            if contributors > 1:
                evidence.append(
                    DefenseEvidence(
                        category="TEAM_OWNERSHIP",
                        description=f"File has {contributors} contributors - team asset",
                        strength=min(0.7, contributors * 0.2),
                        source="git_analysis",
                        details={"contributors": contributors},
                    )
                )

        except Exception:
            pass

        return evidence

    def _analyze_naming_importance(self, file_path: str) -> List[DefenseEvidence]:
        """Analyze if naming suggests importance"""
        evidence = []
        filename = Path(file_path).name.lower()

        important_names = {
            "auth": "Authentication/Authorization logic",
            "security": "Security-related code",
            "api": "API definitions",
            "gateway": "Service gateway",
            "core": "Core functionality",
            "base": "Base classes/utilities",
            "util": "Utility functions",
            "helper": "Helper functions",
            "model": "Data models",
            "schema": "Data schemas",
            "test": "Test files",
            "spec": "Specifications",
        }

        for indicator, description in important_names.items():
            if indicator in filename:
                evidence.append(
                    DefenseEvidence(
                        category="IMPORTANT_NAME",
                        description=f"File name suggests: {description}",
                        strength=0.6,
                        source="naming_analysis",
                        details={"indicator": indicator},
                    )
                )
                break

        return evidence

    def _analyze_content_quality(self, file_path: str) -> List[DefenseEvidence]:
        """Analyze content quality and substance"""
        evidence = []
        content = self._get_file_content(file_path)

        if not content:
            return evidence

        lines = content.split("\n")
        non_empty_lines = [l for l in lines if l.strip()]

        # Substantial code
        if len(non_empty_lines) > 50:
            evidence.append(
                DefenseEvidence(
                    category="SUBSTANTIAL_CODE",
                    description=f"File has {len(non_empty_lines)} lines of content",
                    strength=min(0.7, len(non_empty_lines) / 200),
                    source="content_analysis",
                    details={"line_count": len(non_empty_lines)},
                )
            )

        # Well-documented code
        comment_lines = len(
            [l for l in lines if l.strip().startswith(("#", "//", "/*", "*", '"""', "'''"))]
        )
        if comment_lines > 10:
            evidence.append(
                DefenseEvidence(
                    category="WELL_DOCUMENTED",
                    description=f"File has {comment_lines} comment/doc lines",
                    strength=min(0.6, comment_lines / 50),
                    source="content_analysis",
                    details={"comment_lines": comment_lines},
                )
            )

        # Contains classes/functions (structured code)
        class_count = len(re.findall(r"^class\s+\w+", content, re.MULTILINE))
        func_count = len(
            re.findall(r"^(def|function|async\s+function)\s+\w+", content, re.MULTILINE)
        )

        if class_count + func_count > 3:
            evidence.append(
                DefenseEvidence(
                    category="STRUCTURED_CODE",
                    description=f"Contains {class_count} classes, {func_count} functions",
                    strength=min(0.75, (class_count + func_count) / 15),
                    source="content_analysis",
                    details={"classes": class_count, "functions": func_count},
                )
            )

        return evidence

    def _analyze_integration_points(self, file_path: str) -> List[DefenseEvidence]:
        """Analyze if file connects systems"""
        evidence = []
        content = self._get_file_content(file_path)

        if not content:
            return evidence

        # API client indicators
        api_patterns = [
            (r"requests\.(get|post|put|delete)", "HTTP client - makes API calls"),
            (r"fetch\s*\(", "Fetch API - makes HTTP requests"),
            (r"axios", "Axios client - API integration"),
            (r"websocket|socket\.io", "WebSocket - real-time communication"),
            (r"redis|memcache", "Cache integration"),
            (r"sql|mongodb|postgres|mysql", "Database integration"),
        ]

        for pattern, description in api_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                evidence.append(
                    DefenseEvidence(
                        category="INTEGRATION",
                        description=description,
                        strength=0.75,
                        source="content_analysis",
                        details={"pattern": pattern},
                    )
                )

        return evidence

    def _analyze_future_value(self, file_path: str) -> List[DefenseEvidence]:
        """Analyze potential future value"""
        evidence = []
        content = self._get_file_content(file_path)
        filename = Path(file_path).name.lower()

        # Template/example files
        if "template" in filename or "example" in filename:
            evidence.append(
                DefenseEvidence(
                    category="TEMPLATE",
                    description="Template/example file - valuable for reference",
                    strength=0.65,
                    source="naming_analysis",
                    details={},
                )
            )

        # Test files
        if "test" in filename or "spec" in filename:
            evidence.append(
                DefenseEvidence(
                    category="TEST_FILE",
                    description="Test file - essential for code quality",
                    strength=0.8,
                    source="naming_analysis",
                    details={},
                )
            )

        # Check for TODO/FIXME comments (indicates planned work)
        if content:
            todos = len(re.findall(r"(TODO|FIXME|XXX|HACK):", content, re.IGNORECASE))
            if todos > 0:
                evidence.append(
                    DefenseEvidence(
                        category="PLANNED_WORK",
                        description=f"File has {todos} TODO/FIXME markers - planned improvements",
                        strength=0.4,
                        source="content_analysis",
                        details={"todo_count": todos},
                    )
                )

        return evidence

    def _build_import_chain(self, file_path: str) -> List[str]:
        """Build the import chain to this file"""
        chain = []
        visited = set()

        def trace_importers(fp: str, depth: int = 0):
            if fp in visited or depth > 5:
                return
            visited.add(fp)

            importers = self.import_graph.get(fp, set())
            for imp in importers:
                chain.append(f"{'  ' * depth}{imp} → {fp}")
                trace_importers(imp, depth + 1)

        trace_importers(file_path)
        return chain[:20]  # Limit chain length

    def _calculate_verdict(self, evidence: List[DefenseEvidence]) -> Tuple[str, float]:
        """Calculate defense verdict based on evidence"""
        if not evidence:
            return "MARGINAL", 0.3

        # Calculate weighted score
        total_strength = sum(e.strength for e in evidence)

        # Bonus for critical evidence types
        critical_categories = {
            "IMPORT_DEPENDENCY",
            "ENTRY_POINT_DEPENDENCY",
            "ENTRY_POINT",
            "README",
            "CONFIGURATION_FILE",
            "TEST_FILE",
        }
        has_critical = any(e.category in critical_categories for e in evidence)

        if has_critical or total_strength > 3.0:
            return "ESSENTIAL", min(0.95, total_strength / 4)
        elif total_strength > 2.0:
            return "IMPORTANT", min(0.85, total_strength / 3)
        elif total_strength > 1.0:
            return "USEFUL", min(0.7, total_strength / 2)
        else:
            return "MARGINAL", max(0.3, total_strength)

    def _build_defense_argument(
        self, file_path: str, evidence: List[DefenseEvidence], verdict: str
    ) -> str:
        """Build a compelling defense argument"""
        filename = Path(file_path).name

        if not evidence:
            return f"🛡️ While '{filename}' has limited visible dependencies, removing it may have unforeseen consequences. Recommend review before deletion."

        # Group evidence by strength
        strong_evidence = [e for e in evidence if e.strength >= 0.7]
        moderate_evidence = [e for e in evidence if 0.4 <= e.strength < 0.7]

        argument_parts = [f"🛡️ **DEFENSE FOR '{filename}'**\n"]

        if verdict == "ESSENTIAL":
            argument_parts.append("⭐ **This file is ESSENTIAL to the project.**\n")
        elif verdict == "IMPORTANT":
            argument_parts.append("📌 **This file is IMPORTANT and should be retained.**\n")
        elif verdict == "USEFUL":
            argument_parts.append("✅ **This file serves useful purposes.**\n")
        else:
            argument_parts.append(
                "📋 **This file has some value but limited evidence of active use.**\n"
            )

        if strong_evidence:
            argument_parts.append("\n**Strong Evidence:**")
            for e in strong_evidence[:3]:
                argument_parts.append(f"  • {e.description}")

        if moderate_evidence:
            argument_parts.append("\n**Supporting Evidence:**")
            for e in moderate_evidence[:3]:
                argument_parts.append(f"  • {e.description}")

        return "\n".join(argument_parts)


if __name__ == "__main__":
    # Test the defense agent
    import sys

    if len(sys.argv) < 2:
        print("Usage: defense.py <repo_root>")
        sys.exit(1)

    repo_root = sys.argv[1]

    # Get all files
    all_files = []
    for root, dirs, files in os.walk(repo_root):
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), repo_root)
            all_files.append(rel_path)

    agent = DefenseAgent(repo_root, all_files)

    # Test with first Python file
    py_files = [f for f in all_files if f.endswith(".py")]
    if py_files:
        case = agent.defend(py_files[0])
        print(json.dumps(case.to_dict(), indent=2))
