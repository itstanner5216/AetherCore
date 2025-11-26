"""
AetherCore Repository Cleanup System

Automated repository analysis and file quarantine management.
"""

from .repository_analyzer import RepositoryAnalyzer, FileAnalysis, RepositoryReport
from .dependency_graph import DependencyGraphBuilder
from .semantic_analyzer import SemanticAnalyzer
from .quarantine_manager import QuarantineManager

# Import adversarial agents
try:
    from .agents import (
        FileCourt,
        TrialRecord,
        ProsecutorAgent,
        ProsecutionCase,
        DefenseAgent,
        DefenseCase,
        JudgeAgent,
        Verdict,
    )
    _AGENTS_AVAILABLE = True
except ImportError:
    _AGENTS_AVAILABLE = False

__version__ = '1.0.0'
__all__ = [
    'RepositoryAnalyzer',
    'FileAnalysis', 
    'RepositoryReport',
    'DependencyGraphBuilder',
    'SemanticAnalyzer',
    'QuarantineManager',
    # Agents
    'FileCourt',
    'TrialRecord',
    'ProsecutorAgent',
    'ProsecutionCase',
    'DefenseAgent',
    'DefenseCase',
    'JudgeAgent',
    'Verdict',
]
