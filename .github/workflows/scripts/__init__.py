"""
AetherCore Repository Cleanup System

Automated repository analysis and file quarantine management.
"""

from .dependency_graph import DependencyGraphBuilder
from .quarantine_manager import QuarantineManager
from .repository_analyzer import FileAnalysis, RepositoryAnalyzer, RepositoryReport
from .semantic_analyzer import SemanticAnalyzer

# Import adversarial agents
try:
    from .agents import (
        DefenseAgent,
        DefenseCase,
        FileCourt,
        JudgeAgent,
        ProsecutionCase,
        ProsecutorAgent,
        TrialRecord,
        Verdict,
    )

    _AGENTS_AVAILABLE = True
except ImportError:
    _AGENTS_AVAILABLE = False

__version__ = "1.0.0"

# Base exports always available
__all__ = [
    "RepositoryAnalyzer",
    "FileAnalysis",
    "RepositoryReport",
    "DependencyGraphBuilder",
    "SemanticAnalyzer",
    "QuarantineManager",
]

# Only add agent exports when they are available
if _AGENTS_AVAILABLE:
    __all__.extend(
        [
            "FileCourt",
            "TrialRecord",
            "ProsecutorAgent",
            "ProsecutionCase",
            "DefenseAgent",
            "DefenseCase",
            "JudgeAgent",
            "Verdict",
        ]
    )
