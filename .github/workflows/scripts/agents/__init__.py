#!/usr/bin/env python3
"""
AetherCore File Court - Adversarial File Analysis System

Three agents debate the fate of each file:
- Prosecutor: Argues for quarantine (proves redundancy)
- Defense: Argues for keeping (proves necessity)
- Judge: Delivers final verdict (weighs evidence)
- FileCourt: Orchestrates the adversarial trial process

Usage:
    from agents import FileCourt
    
    court = FileCourt("/path/to/repo", conservative=True)
    suspects = court.identify_suspects(threshold=0.5)
    court.run_all_trials(suspects)
    
    print(court.generate_full_report())
"""

from .prosecutor import ProsecutorAgent, ProsecutionCase
from .defense import DefenseAgent, DefenseCase
from .judge import JudgeAgent, Verdict
from .court import FileCourt, TrialRecord

__all__ = [
    # Main orchestrator
    'FileCourt',
    'TrialRecord',
    
    # Individual agents
    'ProsecutorAgent',
    'ProsecutionCase',
    'DefenseAgent', 
    'DefenseCase',
    'JudgeAgent',
    'Verdict',
]

__version__ = '1.0.0'
__author__ = 'AetherCore Repository Analysis'
