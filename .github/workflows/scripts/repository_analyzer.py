#!/usr/bin/env python3
"""
Repository Analyzer - Main Orchestrator
Analyzes repository structure using an ADVERSARIAL AGENT SYSTEM:
- Prosecutor Agent: Argues files should be removed
- Defense Agent: Argues files should be kept
- Judge Agent: Renders final verdict

Part of AetherCore Repository Cleanup System
"""

import json
import logging
import os
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Import companion modules
from dependency_graph import DependencyGraphBuilder
from quarantine_manager import QuarantineManager
from semantic_analyzer import SemanticAnalyzer

# Import adversarial agents
try:
    from agents import FileCourt

    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    print("⚠️  Adversarial agents not available, using basic analysis")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class FileAnalysis:
    """Analysis result for a single file"""

    path: str
    file_type: str
    size_bytes: int
    last_modified: str

    # Dependency analysis
    imports: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    referenced_by: List[str] = field(default_factory=list)

    # Semantic analysis
    keywords: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    semantic_links: List[Dict] = field(default_factory=list)

    # Relevance scoring
    relevance_score: float = 0.0
    confidence: float = 0.0
    is_orphaned: bool = False
    is_duplicate: bool = False
    is_outdated: bool = False
    is_partial: bool = False

    # Quarantine decision
    quarantine_recommended: bool = False
    quarantine_reasons: List[str] = field(default_factory=list)


@dataclass
class RepositoryReport:
    """Complete repository analysis report"""

    timestamp: str
    repository_path: str
    total_files: int
    analyzed_files: int

    # Statistics
    file_type_counts: Dict[str, int] = field(default_factory=dict)
    orphaned_count: int = 0
    quarantine_count: int = 0

    # File analyses
    files: Dict[str, FileAnalysis] = field(default_factory=dict)

    # Dependency graph
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    reverse_dependency_graph: Dict[str, List[str]] = field(default_factory=dict)

    # Semantic relationships
    semantic_clusters: List[Dict] = field(default_factory=list)
    code_doc_links: List[Dict] = field(default_factory=list)

    # Quarantine recommendations
    quarantine_files: List[Dict] = field(default_factory=list)

    # Warnings and inconsistencies
    warnings: List[str] = field(default_factory=list)
    inconsistencies: List[Dict] = field(default_factory=list)


class RepositoryAnalyzer:
    """
    Main repository analyzer that orchestrates dependency analysis,
    semantic similarity detection, and quarantine recommendations.
    """

    # File extensions to analyze
    CODE_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".go",
        ".rs",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".cs",
        ".rb",
        ".php",
        ".sh",
        ".bash",
    }

    DOC_EXTENSIONS = {".md", ".txt", ".rst", ".adoc", ".yaml", ".yml", ".json", ".toml"}

    CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env", ".conf"}

    # Directories to ignore
    IGNORE_DIRS = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        ".idea",
        ".vscode",
        "dist",
        "build",
        "target",
        ".cache",
        "quarantine",
        ".github/workflows/scripts",  # Don't analyze ourselves
    }

    # Files to ignore
    IGNORE_FILES = {
        ".gitignore",
        ".gitattributes",
        "package-lock.json",
        "yarn.lock",
        "Pipfile.lock",
        "poetry.lock",
        ".DS_Store",
        "Thumbs.db",
    }

    # Entry point files that are always relevant
    ENTRY_POINTS = {
        "main.py",
        "index.js",
        "server.js",
        "app.py",
        "gateway.py",
        "index.ts",
        "main.js",
        "setup.py",
        "manage.py",
        "__main__.py",
        "Dockerfile",
        "docker-compose.yml",
        "Procfile",
        "Makefile",
        "package.json",
        "requirements.txt",
        "pyproject.toml",
    }

    def __init__(self, repo_path: str, output_dir: str = None):
        self.repo_path = Path(repo_path).resolve()
        self.output_dir = (
            Path(output_dir) if output_dir else self.repo_path / ".github" / "cleanup_reports"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize analyzers
        self.dep_builder = DependencyGraphBuilder(self.repo_path)
        self.semantic_analyzer = SemanticAnalyzer(self.repo_path)
        self.quarantine_manager = QuarantineManager(self.repo_path)

        # Analysis state
        self.all_files: List[Path] = []
        self.file_analyses: Dict[str, FileAnalysis] = {}
        self.report: Optional[RepositoryReport] = None

    def discover_files(self) -> List[Path]:
        """Discover all analyzable files in the repository"""
        logger.info(f"Discovering files in {self.repo_path}")
        files = []

        for item in self.repo_path.rglob("*"):
            if item.is_file():
                # Check if in ignored directory
                rel_path = item.relative_to(self.repo_path)
                parts = rel_path.parts

                if any(ignored in parts for ignored in self.IGNORE_DIRS):
                    continue

                if item.name in self.IGNORE_FILES:
                    continue

                # Only analyze known extensions
                ext = item.suffix.lower()
                if ext in self.CODE_EXTENSIONS | self.DOC_EXTENSIONS | self.CONFIG_EXTENSIONS:
                    files.append(item)
                elif item.name in self.ENTRY_POINTS:
                    files.append(item)

        self.all_files = files
        logger.info(f"Discovered {len(files)} files to analyze")
        return files

    def classify_file(self, file_path: Path) -> str:
        """Classify file type based on extension and name"""
        ext = file_path.suffix.lower()
        name = file_path.name.lower()

        if ext in self.CODE_EXTENSIONS:
            return "code"
        elif ext in {".md", ".txt", ".rst", ".adoc"}:
            return "documentation"
        elif ext in self.CONFIG_EXTENSIONS or name in {"dockerfile", "procfile", "makefile"}:
            return "config"
        else:
            return "other"

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Perform complete analysis on a single file"""
        rel_path = str(file_path.relative_to(self.repo_path))
        stat = file_path.stat()

        analysis = FileAnalysis(
            path=rel_path,
            file_type=self.classify_file(file_path),
            size_bytes=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
        )

        # Check if entry point (always relevant)
        if file_path.name in self.ENTRY_POINTS:
            analysis.relevance_score = 1.0
            analysis.confidence = 1.0
            return analysis

        return analysis

    def run_analysis(self) -> RepositoryReport:
        """Run complete repository analysis"""
        logger.info("Starting repository analysis...")

        # Phase 1: Discover files
        self.discover_files()

        # Phase 2: Basic file analysis
        logger.info("Phase 2: Analyzing individual files...")
        file_type_counts = defaultdict(int)

        for file_path in self.all_files:
            analysis = self.analyze_file(file_path)
            self.file_analyses[analysis.path] = analysis
            file_type_counts[analysis.file_type] += 1

        # Phase 3: Build dependency graph
        logger.info("Phase 3: Building dependency graph...")
        dep_graph, reverse_graph = self.dep_builder.build_graph(self.all_files)

        # Update file analyses with dependency info
        for file_path, deps in dep_graph.items():
            if file_path in self.file_analyses:
                self.file_analyses[file_path].imports = list(deps)

        for file_path, importers in reverse_graph.items():
            if file_path in self.file_analyses:
                self.file_analyses[file_path].imported_by = list(importers)

        # Phase 4: Semantic analysis
        logger.info("Phase 4: Running semantic analysis...")
        semantic_results = self.semantic_analyzer.analyze_all(self.all_files)

        # Update file analyses with semantic info
        for file_path, sem_data in semantic_results.get("file_data", {}).items():
            if file_path in self.file_analyses:
                self.file_analyses[file_path].keywords = sem_data.get("keywords", [])
                self.file_analyses[file_path].topics = sem_data.get("topics", [])
                self.file_analyses[file_path].semantic_links = sem_data.get("links", [])

        # Phase 5: Calculate relevance scores
        logger.info("Phase 5: Calculating relevance scores...")
        self._calculate_relevance_scores(dep_graph, reverse_graph, semantic_results)

        # Phase 6: Identify quarantine candidates
        logger.info("Phase 6: Identifying quarantine candidates...")
        quarantine_files = self._identify_quarantine_candidates()

        # Phase 7: Detect inconsistencies
        logger.info("Phase 7: Detecting inconsistencies...")
        inconsistencies = self._detect_inconsistencies(semantic_results)

        # Build final report
        self.report = RepositoryReport(
            timestamp=datetime.now().isoformat(),
            repository_path=str(self.repo_path),
            total_files=len(self.all_files),
            analyzed_files=len(self.file_analyses),
            file_type_counts=dict(file_type_counts),
            orphaned_count=sum(1 for f in self.file_analyses.values() if f.is_orphaned),
            quarantine_count=len(quarantine_files),
            files=self.file_analyses,
            dependency_graph={k: list(v) for k, v in dep_graph.items()},
            reverse_dependency_graph={k: list(v) for k, v in reverse_graph.items()},
            semantic_clusters=semantic_results.get("clusters", []),
            code_doc_links=semantic_results.get("code_doc_links", []),
            quarantine_files=quarantine_files,
            warnings=semantic_results.get("warnings", []),
            inconsistencies=inconsistencies,
        )

        logger.info("Analysis complete!")
        return self.report

    def _calculate_relevance_scores(
        self,
        dep_graph: Dict[str, Set[str]],
        reverse_graph: Dict[str, Set[str]],
        semantic_results: Dict,
    ):
        """Calculate relevance score for each file"""

        for path, analysis in self.file_analyses.items():
            score = 0.0
            confidence = 0.0
            factors = []

            # Factor 1: Entry point bonus
            file_name = Path(path).name
            if file_name in self.ENTRY_POINTS:
                score += 0.4
                confidence += 0.3
                factors.append("entry_point")

            # Factor 2: Dependency connections
            imports_count = len(analysis.imports)
            imported_by_count = len(analysis.imported_by)

            if imported_by_count > 0:
                score += min(0.3, imported_by_count * 0.1)
                confidence += 0.2
                factors.append(f"imported_by_{imported_by_count}")

            if imports_count > 0:
                score += min(0.1, imports_count * 0.02)
                factors.append(f"imports_{imports_count}")

            # Factor 3: Semantic links
            semantic_links = len(analysis.semantic_links)
            if semantic_links > 0:
                score += min(0.2, semantic_links * 0.05)
                confidence += 0.1
                factors.append(f"semantic_links_{semantic_links}")

            # Factor 4: File type relevance
            if analysis.file_type == "config":
                score += 0.1  # Configs are usually important
                factors.append("config_file")
            elif analysis.file_type == "documentation":
                # Docs need semantic links to be relevant
                if semantic_links == 0:
                    score -= 0.1
                    factors.append("unlinked_doc")

            # Factor 5: Check for orphaned status
            if imported_by_count == 0 and semantic_links == 0:
                if file_name not in self.ENTRY_POINTS:
                    analysis.is_orphaned = True
                    score -= 0.2
                    factors.append("orphaned")

            # Normalize score
            analysis.relevance_score = max(0.0, min(1.0, score))
            analysis.confidence = max(0.0, min(1.0, confidence + 0.3))  # Base confidence

    def _identify_quarantine_candidates(self) -> List[Dict]:
        """Identify files that should be quarantined"""
        quarantine_list = []

        for path, analysis in self.file_analyses.items():
            reasons = []

            # Reason 1: Orphaned file
            if analysis.is_orphaned:
                reasons.append("Not referenced by any other file (orphaned)")

            # Reason 2: Very low relevance
            if analysis.relevance_score < 0.2 and analysis.confidence > 0.5:
                reasons.append(f"Low relevance score ({analysis.relevance_score:.2f})")

            # Reason 3: Duplicate detection (from semantic analysis)
            if analysis.is_duplicate:
                reasons.append("Appears to be a duplicate of another file")

            # Reason 4: Outdated markers
            if analysis.is_outdated:
                reasons.append("Contains outdated version markers")

            # Reason 5: Partial implementation
            if analysis.is_partial:
                reasons.append("Partial/incomplete implementation with no references")

            # Reason 6: File naming patterns suggesting obsolescence
            file_name = Path(path).name.lower()
            if any(
                marker in file_name
                for marker in ["_old", "_backup", "_copy", ".bak", "_deprecated"]
            ):
                reasons.append("File name suggests obsolete/backup status")

            if reasons:
                analysis.quarantine_recommended = True
                analysis.quarantine_reasons = reasons
                quarantine_list.append(
                    {
                        "path": path,
                        "file_type": analysis.file_type,
                        "relevance_score": analysis.relevance_score,
                        "confidence": analysis.confidence,
                        "reasons": reasons,
                    }
                )

        # Sort by confidence (most confident recommendations first)
        quarantine_list.sort(key=lambda x: x["confidence"], reverse=True)
        return quarantine_list

    def _detect_inconsistencies(self, semantic_results: Dict) -> List[Dict]:
        """Detect inconsistencies between code and documentation"""
        inconsistencies = []

        # Check for documented features without code implementation
        for link in semantic_results.get("code_doc_links", []):
            if link.get("type") == "doc_without_code":
                inconsistencies.append(
                    {
                        "type": "missing_implementation",
                        "doc_file": link.get("doc_file"),
                        "expected_code": link.get("expected"),
                        "description": f"Documentation mentions '{link.get('topic')}' but no corresponding code found",
                    }
                )
            elif link.get("type") == "code_without_doc":
                inconsistencies.append(
                    {
                        "type": "missing_documentation",
                        "code_file": link.get("code_file"),
                        "description": "Code file has no corresponding documentation",
                    }
                )

        return inconsistencies

    def generate_report_markdown(self) -> str:
        """Generate markdown report from analysis"""
        if not self.report:
            raise ValueError("No analysis has been run yet")

        lines = [
            "# Repository Analysis Report",
            "",
            f"**Generated:** {self.report.timestamp}",
            f"**Repository:** {self.report.repository_path}",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Files Analyzed | {self.report.analyzed_files} |",
            f"| Orphaned Files | {self.report.orphaned_count} |",
            f"| Quarantine Candidates | {self.report.quarantine_count} |",
            "",
        ]

        # File type breakdown
        lines.extend(["### File Types", ""])
        for ftype, count in self.report.file_type_counts.items():
            lines.append(f"- **{ftype}:** {count}")
        lines.append("")

        # Quarantine recommendations
        if self.report.quarantine_files:
            lines.extend(
                [
                    "## Quarantine Recommendations",
                    "",
                    "The following files are recommended for quarantine:",
                    "",
                ]
            )

            for item in self.report.quarantine_files:
                lines.append(f"### `{item['path']}`")
                lines.append(f"- **Type:** {item['file_type']}")
                lines.append(f"- **Relevance Score:** {item['relevance_score']:.2f}")
                lines.append(f"- **Confidence:** {item['confidence']:.2f}")
                lines.append("- **Reasons:**")
                for reason in item["reasons"]:
                    lines.append(f"  - {reason}")
                lines.append("")

        # Dependency overview
        lines.extend(["## Dependency Overview", "", "### Most Referenced Files", ""])

        # Get top referenced files
        ref_counts = []
        for path, analysis in self.report.files.items():
            ref_counts.append((path, len(analysis.imported_by)))
        ref_counts.sort(key=lambda x: x[1], reverse=True)

        for path, count in ref_counts[:10]:
            if count > 0:
                lines.append(f"- `{path}`: {count} references")
        lines.append("")

        # Inconsistencies
        if self.report.inconsistencies:
            lines.extend(["## Inconsistencies Detected", ""])
            for inc in self.report.inconsistencies:
                lines.append(f"- **{inc['type']}:** {inc['description']}")
            lines.append("")

        # Warnings
        if self.report.warnings:
            lines.extend(["## Warnings", ""])
            for warning in self.report.warnings:
                lines.append(f"- {warning}")
            lines.append("")

        return "\n".join(lines)

    def save_reports(self) -> Tuple[Path, Path]:
        """Save analysis reports to files"""
        if not self.report:
            raise ValueError("No analysis has been run yet")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON report
        json_path = self.output_dir / f"analysis_{timestamp}.json"
        with open(json_path, "w") as f:
            # Convert dataclasses to dicts
            report_dict = asdict(self.report)
            # Convert FileAnalysis objects
            report_dict["files"] = {k: asdict(v) for k, v in self.report.files.items()}
            json.dump(report_dict, f, indent=2, default=str)

        # Save Markdown report
        md_path = self.output_dir / f"analysis_{timestamp}.md"
        with open(md_path, "w") as f:
            f.write(self.generate_report_markdown())

        logger.info(f"Reports saved to {self.output_dir}")
        return json_path, md_path


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze repository structure and dependencies")
    parser.add_argument("--repo", "-r", default=".", help="Repository path")
    parser.add_argument("--output", "-o", help="Output directory for reports")
    parser.add_argument("--quarantine", "-q", action="store_true", help="Move files to quarantine")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Dry run (no file moves)")
    parser.add_argument(
        "--adversarial",
        "-a",
        action="store_true",
        default=True,
        help="Use adversarial agent system (default: True)",
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=0.5,
        help="Suspicion threshold for trials (default: 0.5)",
    )
    parser.add_argument(
        "--conservative",
        action="store_true",
        default=True,
        help="Conservative mode - err on side of keeping files",
    )

    args = parser.parse_args()

    # Determine output directory
    repo_path = Path(args.repo).resolve()
    output_dir = Path(args.output) if args.output else repo_path / ".github" / "cleanup_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Check if we should use adversarial system
    use_adversarial = args.adversarial and AGENTS_AVAILABLE

    if use_adversarial:
        print("")
        print("╔" + "═" * 68 + "╗")
        print("║" + "⚖️  ADVERSARIAL FILE ANALYSIS SYSTEM".center(68) + "║")
        print("║" + "Prosecutor vs Defense - Judge Decides".center(68) + "║")
        print("╚" + "═" * 68 + "╝")
        print("")

        # Run adversarial analysis
        court = FileCourt(repo_root=str(repo_path), conservative=args.conservative, verbose=True)

        # Identify suspects and run trials
        suspects = court.identify_suspects(threshold=args.threshold)

        if suspects:
            court.run_all_trials(suspects)

            # Generate reports
            text_report = court.generate_full_report()
            json_report = court.generate_json_report()

            # Save reports
            md_path = output_dir / f"court_report_{timestamp}.md"
            with open(md_path, "w") as f:
                f.write(text_report)

            json_path = output_dir / f"court_report_{timestamp}.json"
            with open(json_path, "w") as f:
                json.dump(json_report, f, indent=2)

            # Print the full report to stdout for GitHub Actions visibility
            print(text_report)

            # Get action items
            verdicts = court.get_verdicts_by_decision()
            quarantine_files = verdicts["QUARANTINE"] + verdicts["DELETE"]
            review_files = verdicts["REVIEW_NEEDED"]

            # Optionally move files to quarantine
            if args.quarantine and quarantine_files:
                qm = QuarantineManager(repo_path)
                if args.dry_run:
                    print("\n[DRY RUN] Would move the following files to quarantine:")
                    for f in quarantine_files:
                        print(f"  - {f}")
                else:
                    print("\nMoving files to quarantine...")
                    moved = qm.move_to_quarantine(quarantine_files)
                    print(f"Moved {len(moved)} files to quarantine/")

            # Set output for GitHub Actions
            if os.environ.get("GITHUB_OUTPUT"):
                with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                    f.write(f"report_json={json_path}\n")
                    f.write(f"report_md={md_path}\n")
                    f.write(f"quarantine_count={len(quarantine_files)}\n")
                    f.write(f"review_count={len(review_files)}\n")
                    f.write(f"trials_conducted={len(court.trials)}\n")

            print("\n📄 Reports saved:")
            print(f"   Markdown: {md_path}")
            print(f"   JSON: {json_path}")

        else:
            print("\n✅ No suspicious files identified - repository looks clean!")

            # Still create a report
            clean_report = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "repository": str(repo_path),
                    "status": "clean",
                },
                "summary": {
                    "keep": court.all_files if hasattr(court, "all_files") else 0,
                    "quarantine": 0,
                    "delete": 0,
                    "review_needed": 0,
                },
                "message": "No files warranted adversarial review",
            }

            json_path = output_dir / f"court_report_{timestamp}.json"
            with open(json_path, "w") as f:
                json.dump(clean_report, f, indent=2)

            if os.environ.get("GITHUB_OUTPUT"):
                with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                    f.write(f"report_json={json_path}\n")
                    f.write("quarantine_count=0\n")
                    f.write("review_count=0\n")

    else:
        # Fallback to basic analysis
        print("Running basic analysis (adversarial agents not available)")

        analyzer = RepositoryAnalyzer(args.repo, args.output)
        report = analyzer.run_analysis()

        # Save reports
        json_path, md_path = analyzer.save_reports()

        print(f"\n{'='*60}")
        print("Repository Analysis Complete")
        print(f"{'='*60}")
        print(f"Files analyzed: {report.analyzed_files}")
        print(f"Orphaned files: {report.orphaned_count}")
        print(f"Quarantine candidates: {report.quarantine_count}")
        print("\nReports saved to:")
        print(f"  JSON: {json_path}")
        print(f"  Markdown: {md_path}")

        # Optionally move files to quarantine
        if args.quarantine and report.quarantine_files:
            if args.dry_run:
                print("\n[DRY RUN] Would move the following files to quarantine:")
                for item in report.quarantine_files:
                    print(f"  - {item['path']}")
            else:
                print("\nMoving files to quarantine...")
                moved = analyzer.quarantine_manager.move_to_quarantine(
                    [item["path"] for item in report.quarantine_files]
                )
                print(f"Moved {len(moved)} files to quarantine/")

        # Set output for GitHub Actions
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"report_json={json_path}\n")
                f.write(f"report_md={md_path}\n")
                f.write(f"quarantine_count={report.quarantine_count}\n")
                f.write(f"orphaned_count={report.orphaned_count}\n")

    # Always return 0 - finding candidates is not an error
    return 0


if __name__ == "__main__":
    sys.exit(main())
