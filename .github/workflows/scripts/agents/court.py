#!/usr/bin/env python3
"""
File Court - Orchestrates the adversarial file analysis system

The Court runs a "trial" for each suspicious file:
1. Prosecutor presents case for removal
2. Defense presents case for keeping
3. Judge renders final verdict

This creates a robust, balanced decision-making process.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime
import concurrent.futures

from .prosecutor import ProsecutorAgent, ProsecutionCase
from .defense import DefenseAgent, DefenseCase
from .judge import JudgeAgent, Verdict


@dataclass
class TrialRecord:
    """Complete record of a file's trial"""
    file_path: str
    prosecution_case: Dict
    defense_case: Dict
    verdict: Dict
    trial_duration_ms: float
    
    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "prosecution": self.prosecution_case,
            "defense": self.defense_case,
            "verdict": self.verdict,
            "trial_duration_ms": self.trial_duration_ms
        }


class FileCourt:
    """
    ⚖️ FILE COURT - Where files face judgment
    
    The Court orchestrates the full adversarial process:
    1. Identifies suspicious files
    2. Runs trials with Prosecutor and Defense
    3. Collects Judge verdicts
    4. Generates comprehensive reports
    """
    
    # Files that should NEVER be considered for removal
    PROTECTED_PATTERNS = [
        '.git/', '.github/', 'node_modules/', '__pycache__/',
        '.env', 'package-lock.json', 'yarn.lock', 'poetry.lock',
        'LICENSE', 'CODEOWNERS', '.gitignore', '.gitattributes'
    ]
    
    # File extensions to analyze
    ANALYZABLE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.mjs', '.cjs',
        '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg',
        '.md', '.rst', '.txt',
        '.html', '.css', '.scss', '.less',
        '.sh', '.bash', '.zsh',
        '.sql', '.graphql'
    }
    
    def __init__(self, repo_root: str, conservative: bool = True, verbose: bool = True):
        """
        Initialize the File Court.
        
        Args:
            repo_root: Path to repository root
            conservative: If True, err on side of keeping files
            verbose: Print progress to stdout
        """
        self.repo_root = Path(repo_root).resolve()
        self.conservative = conservative
        self.verbose = verbose
        
        # Discover all files
        self.all_files = self._discover_files()
        
        # Initialize agents
        self.prosecutor = ProsecutorAgent(str(self.repo_root), self.all_files)
        self.defense = DefenseAgent(str(self.repo_root), self.all_files)
        self.judge = JudgeAgent(conservative_mode=conservative)
        
        # Trial records
        self.trials: List[TrialRecord] = []
        
        if self.verbose:
            print(f"⚖️  FILE COURT INITIALIZED")
            print(f"   Repository: {self.repo_root}")
            print(f"   Total files: {len(self.all_files)}")
            print(f"   Conservative mode: {conservative}")
            print("")
    
    def _discover_files(self) -> List[str]:
        """Discover all analyzable files in the repository"""
        files = []
        
        for root, dirs, filenames in os.walk(self.repo_root):
            # Skip protected directories
            dirs[:] = [d for d in dirs if not any(
                prot in d or d.startswith('.') 
                for prot in ['node_modules', '__pycache__', '.git', 'venv', 'env']
            )]
            
            for filename in filenames:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, self.repo_root)
                
                # Skip protected files
                if any(prot in rel_path for prot in self.PROTECTED_PATTERNS):
                    continue
                
                # Check extension
                ext = Path(filename).suffix.lower()
                if ext in self.ANALYZABLE_EXTENSIONS:
                    files.append(rel_path)
        
        return files
    
    def identify_suspects(self, threshold: float = 0.5) -> List[str]:
        """
        Identify files that warrant a full trial.
        
        Uses the Prosecutor for initial screening.
        """
        suspects = []
        
        if self.verbose:
            print("🔍 INITIAL SCREENING - Identifying Suspects...")
            print("-" * 50)
        
        for file_path in self.all_files:
            case = self.prosecutor.prosecute(file_path)
            
            # File is suspicious if prosecutor confidence is above threshold
            if case.confidence >= threshold:
                suspects.append(file_path)
                if self.verbose:
                    print(f"   🎯 {file_path}: {case.verdict} ({case.confidence:.0%})")
        
        if self.verbose:
            print("")
            print(f"📋 {len(suspects)} suspects identified for full trial")
            print("")
        
        return suspects
    
    def run_trial(self, file_path: str) -> TrialRecord:
        """Run a full adversarial trial for a single file"""
        start_time = datetime.now()
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"⚖️  TRIAL: {file_path}")
            print(f"{'='*60}")
        
        # Prosecution presents case
        if self.verbose:
            print("\n🔴 PROSECUTION:")
        prosecution_case = self.prosecutor.prosecute(file_path)
        if self.verbose:
            print(f"   Verdict: {prosecution_case.verdict} ({prosecution_case.confidence:.0%})")
            print(f"   {prosecution_case.argument[:200]}...")
        
        # Defense presents case
        if self.verbose:
            print("\n🟢 DEFENSE:")
        defense_case = self.defense.defend(file_path)
        if self.verbose:
            print(f"   Verdict: {defense_case.verdict} ({defense_case.confidence:.0%})")
            print(f"   {defense_case.argument[:200]}...")
        
        # Judge renders verdict
        if self.verbose:
            print("\n⚖️  JUDGMENT:")
        verdict = self.judge.judge(
            prosecution_case.to_dict(),
            defense_case.to_dict()
        )
        if self.verbose:
            print(f"   {verdict.summary}")
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        trial = TrialRecord(
            file_path=file_path,
            prosecution_case=prosecution_case.to_dict(),
            defense_case=defense_case.to_dict(),
            verdict=verdict.to_dict(),
            trial_duration_ms=duration
        )
        
        self.trials.append(trial)
        return trial
    
    def run_all_trials(self, suspects: Optional[List[str]] = None) -> List[TrialRecord]:
        """Run trials for all suspects"""
        if suspects is None:
            suspects = self.identify_suspects()
        
        if self.verbose:
            print(f"\n{'#'*60}")
            print(f"#  COURT IN SESSION - {len(suspects)} TRIALS")
            print(f"{'#'*60}")
        
        for file_path in suspects:
            self.run_trial(file_path)
        
        return self.trials
    
    def get_verdicts_by_decision(self) -> Dict[str, List[str]]:
        """Group files by verdict decision"""
        by_decision = {
            "KEEP": [],
            "QUARANTINE": [],
            "DELETE": [],
            "REVIEW_NEEDED": []
        }
        
        for trial in self.trials:
            decision = trial.verdict.get('decision', 'REVIEW_NEEDED')
            by_decision[decision].append(trial.file_path)
        
        return by_decision
    
    def generate_full_report(self) -> str:
        """Generate comprehensive court report"""
        report = []
        
        # Header
        report.append("")
        report.append("╔" + "═" * 68 + "╗")
        report.append("║" + "⚖️  FILE COURT - ADVERSARIAL ANALYSIS REPORT".center(68) + "║")
        report.append("╚" + "═" * 68 + "╝")
        report.append("")
        report.append(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📁 Repository: {self.repo_root}")
        report.append(f"📊 Files Analyzed: {len(self.all_files)}")
        report.append(f"⚖️  Trials Conducted: {len(self.trials)}")
        report.append("")
        
        # Summary statistics
        verdicts = self.get_verdicts_by_decision()
        report.append("┌" + "─" * 50 + "┐")
        report.append("│" + " VERDICT SUMMARY".ljust(50) + "│")
        report.append("├" + "─" * 50 + "┤")
        report.append(f"│  ✅ KEEP:           {len(verdicts['KEEP']):4d} files".ljust(51) + "│")
        report.append(f"│  📦 QUARANTINE:     {len(verdicts['QUARANTINE']):4d} files".ljust(51) + "│")
        report.append(f"│  🗑️  DELETE:         {len(verdicts['DELETE']):4d} files".ljust(51) + "│")
        report.append(f"│  👀 REVIEW NEEDED:  {len(verdicts['REVIEW_NEEDED']):4d} files".ljust(51) + "│")
        report.append("└" + "─" * 50 + "┘")
        report.append("")
        
        # Files to quarantine
        if verdicts['QUARANTINE']:
            report.append("╔" + "═" * 68 + "╗")
            report.append("║" + " 📦 FILES TO QUARANTINE".ljust(68) + "║")
            report.append("╚" + "═" * 68 + "╝")
            for trial in self.trials:
                if trial.verdict.get('decision') == 'QUARANTINE':
                    conf = trial.verdict.get('confidence', 0) * 100
                    report.append(f"  [{conf:3.0f}%] {trial.file_path}")
                    # Show key reasoning
                    key_factors = trial.verdict.get('reasoning', {}).get('key_factors', [])
                    if key_factors:
                        report.append(f"        └─ {key_factors[0]}")
            report.append("")
        
        # Files needing review
        if verdicts['REVIEW_NEEDED']:
            report.append("╔" + "═" * 68 + "╗")
            report.append("║" + " 👀 FILES NEEDING MANUAL REVIEW".ljust(68) + "║")
            report.append("╚" + "═" * 68 + "╝")
            for trial in self.trials:
                if trial.verdict.get('decision') == 'REVIEW_NEEDED':
                    report.append(f"  ⚠️  {trial.file_path}")
                    risk = trial.verdict.get('reasoning', {}).get('risk_assessment', '')
                    if risk:
                        report.append(f"      Risk: {risk[:60]}")
            report.append("")
        
        # Files to keep (summarized)
        if verdicts['KEEP']:
            report.append("╔" + "═" * 68 + "╗")
            report.append("║" + f" ✅ FILES CONFIRMED SAFE ({len(verdicts['KEEP'])} files)".ljust(68) + "║")
            report.append("╚" + "═" * 68 + "╝")
            # Show top 10 with highest defense scores
            kept_trials = [t for t in self.trials if t.verdict.get('decision') == 'KEEP']
            kept_trials.sort(
                key=lambda t: t.verdict.get('reasoning', {}).get('defense_weight', 0),
                reverse=True
            )
            for trial in kept_trials[:10]:
                def_weight = trial.verdict.get('reasoning', {}).get('defense_weight', 0) * 100
                report.append(f"  [{def_weight:3.0f}% defense] {trial.file_path}")
            if len(kept_trials) > 10:
                report.append(f"  ... and {len(kept_trials) - 10} more files")
            report.append("")
        
        # Detailed trial transcripts (optional section)
        report.append("┌" + "─" * 68 + "┐")
        report.append("│" + " DETAILED TRIAL TRANSCRIPTS".center(68) + "│")
        report.append("└" + "─" * 68 + "┘")
        
        for trial in self.trials:
            if trial.verdict.get('decision') in ['QUARANTINE', 'REVIEW_NEEDED', 'DELETE']:
                report.append("")
                report.append(f"{'─'*68}")
                report.append(f"📄 FILE: {trial.file_path}")
                report.append(f"{'─'*68}")
                
                # Prosecution summary
                pros = trial.prosecution_case
                report.append(f"🔴 PROSECUTION: {pros.get('verdict')} ({pros.get('confidence', 0):.0%})")
                for e in pros.get('evidence', [])[:3]:
                    report.append(f"   • {e.get('description')}")
                
                # Defense summary
                defe = trial.defense_case
                report.append(f"🟢 DEFENSE: {defe.get('verdict')} ({defe.get('confidence', 0):.0%})")
                for e in defe.get('evidence', [])[:3]:
                    report.append(f"   • {e.get('description')}")
                
                # Verdict
                verd = trial.verdict
                report.append(f"⚖️  VERDICT: {verd.get('decision')} ({verd.get('confidence', 0):.0%})")
                report.append(f"   {verd.get('recommendation', '')[:80]}")
        
        # Footer
        report.append("")
        report.append("═" * 70)
        report.append("END OF COURT REPORT")
        report.append("═" * 70)
        
        return "\n".join(report)
    
    def generate_json_report(self) -> Dict:
        """Generate structured JSON report"""
        verdicts = self.get_verdicts_by_decision()
        
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "repository": str(self.repo_root),
                "total_files": len(self.all_files),
                "trials_conducted": len(self.trials),
                "conservative_mode": self.conservative
            },
            "summary": {
                "keep": len(verdicts['KEEP']),
                "quarantine": len(verdicts['QUARANTINE']),
                "delete": len(verdicts['DELETE']),
                "review_needed": len(verdicts['REVIEW_NEEDED'])
            },
            "files_by_verdict": verdicts,
            "trials": [t.to_dict() for t in self.trials]
        }
    
    def get_quarantine_list(self) -> List[str]:
        """Get list of files recommended for quarantine"""
        return [
            trial.file_path 
            for trial in self.trials 
            if trial.verdict.get('decision') in ['QUARANTINE', 'DELETE']
        ]
    
    def get_action_items(self) -> Dict[str, List[Dict]]:
        """Get prioritized action items"""
        actions = {
            "immediate": [],  # High confidence quarantine/delete
            "review": [],     # Needs manual review
            "monitor": []     # Keep but watch
        }
        
        for trial in self.trials:
            decision = trial.verdict.get('decision')
            confidence = trial.verdict.get('confidence', 0)
            
            item = {
                "file": trial.file_path,
                "decision": decision,
                "confidence": confidence,
                "reasoning": trial.verdict.get('reasoning', {}).get('key_factors', [])[:2]
            }
            
            if decision in ['QUARANTINE', 'DELETE'] and confidence >= 0.8:
                actions["immediate"].append(item)
            elif decision == 'REVIEW_NEEDED' or (decision == 'QUARANTINE' and confidence < 0.8):
                actions["review"].append(item)
            elif decision == 'KEEP' and confidence < 0.7:
                actions["monitor"].append(item)
        
        return actions


def main():
    """Main entry point for running the File Court"""
    import argparse
    
    parser = argparse.ArgumentParser(description="File Court - Adversarial File Analysis")
    parser.add_argument("repo_root", help="Path to repository root")
    parser.add_argument("--output", "-o", help="Output directory for reports")
    parser.add_argument("--conservative", action="store_true", default=True,
                        help="Conservative mode (default: True)")
    parser.add_argument("--aggressive", action="store_true",
                        help="Aggressive mode - more likely to recommend removal")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Quiet mode - minimal output")
    parser.add_argument("--threshold", "-t", type=float, default=0.5,
                        help="Suspicion threshold for trials (default: 0.5)")
    
    args = parser.parse_args()
    
    # Determine mode
    conservative = not args.aggressive
    verbose = not args.quiet
    
    # Initialize court
    court = FileCourt(
        repo_root=args.repo_root,
        conservative=conservative,
        verbose=verbose
    )
    
    # Run trials
    suspects = court.identify_suspects(threshold=args.threshold)
    court.run_all_trials(suspects)
    
    # Generate reports
    text_report = court.generate_full_report()
    json_report = court.generate_json_report()
    
    # Output
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Write text report
        text_path = output_dir / f"court_report_{timestamp}.md"
        with open(text_path, 'w') as f:
            f.write(text_report)
        print(f"\n📄 Text report: {text_path}")
        
        # Write JSON report
        json_path = output_dir / f"court_report_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(json_report, f, indent=2)
        print(f"📊 JSON report: {json_path}")
        
        # Write quarantine list
        quarantine_list = court.get_quarantine_list()
        if quarantine_list:
            list_path = output_dir / f"quarantine_list_{timestamp}.txt"
            with open(list_path, 'w') as f:
                f.write("\n".join(quarantine_list))
            print(f"📋 Quarantine list: {list_path}")
    else:
        # Print to stdout
        print(text_report)
    
    # Summary
    summary = json_report['summary']
    print(f"\n🏛️  COURT ADJOURNED")
    print(f"   Trials: {len(court.trials)}")
    print(f"   Quarantine: {summary['quarantine']}")
    print(f"   Review: {summary['review_needed']}")
    print(f"   Keep: {summary['keep']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
