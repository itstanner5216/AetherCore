#!/usr/bin/env python3
"""
Prosecutor Agent
Builds the case for why a file should be quarantined/removed.

Investigates:
- Is the file orphaned (no imports/references)?
- Is it a duplicate of another file?
- Does it have stale/outdated markers?
- Is it dead code (functions never called)?
- Does it conflict with other files?
- Is it a partial/incomplete implementation?
"""

import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class Evidence:
    """A piece of evidence for/against a file"""
    type: str
    description: str
    severity: str  # critical, major, minor, info
    weight: float  # -1.0 to 1.0 (negative = keep, positive = quarantine)
    details: Dict = field(default_factory=dict)


@dataclass
class ProsecutionCase:
    """The prosecutor's case against a file"""
    file_path: str
    charges: List[str] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    prosecution_score: float = 0.0  # 0-100, higher = stronger case for removal
    summary: str = ""
    recommended_action: str = "keep"  # keep, quarantine, delete


class ProsecutorAgent:
    """
    The Prosecutor builds the case for removing files.
    Looks for every possible reason a file should be quarantined.
    """
    
    # Patterns that suggest a file is obsolete
    OBSOLETE_PATTERNS = [
        r'_old\b', r'_backup\b', r'_bak\b', r'\.bak$', r'_copy\b',
        r'_deprecated\b', r'_unused\b', r'_archive\b', r'_legacy\b',
        r'_temp\b', r'_tmp\b', r'\.tmp$', r'_test_old\b', r'_v\d+\b',
        r'Copy of', r'\(\d+\)', r'~$'
    ]
    
    # Content patterns suggesting abandonment
    ABANDONMENT_MARKERS = [
        r'TODO:\s*delete', r'TODO:\s*remove', r'FIXME:\s*delete',
        r'DEPRECATED', r'DO NOT USE', r'OBSOLETE', r'LEGACY',
        r'will be removed', r'scheduled for deletion', r'no longer used',
        r'replaced by', r'use .* instead', r'moved to'
    ]
    
    # Incomplete implementation markers
    INCOMPLETE_MARKERS = [
        r'not implemented', r'NotImplementedError', r'TODO:', r'FIXME:',
        r'XXX:', r'HACK:', r'pass\s*#', r'raise NotImplementedError',
        r'\.\.\.', r'stub', r'placeholder', r'skeleton'
    ]
    
    def __init__(self, repo_path: Path, all_files: List[Path], 
                 dependency_graph: Dict, reverse_graph: Dict,
                 file_contents: Dict[str, str] = None):
        self.repo_path = Path(repo_path)
        self.all_files = all_files
        self.all_file_paths = {str(f.relative_to(repo_path)) for f in all_files}
        self.dep_graph = dependency_graph
        self.reverse_graph = reverse_graph
        self.file_contents = file_contents or {}
        
        # Build content hashes for duplicate detection
        self.content_hashes: Dict[str, List[str]] = {}
        self._build_content_hashes()
        
    def _build_content_hashes(self):
        """Build hash index for duplicate detection"""
        for file_path in self.all_files:
            try:
                rel_path = str(file_path.relative_to(self.repo_path))
                content = self._get_content(rel_path)
                if content:
                    # Normalize whitespace for comparison
                    normalized = re.sub(r'\s+', ' ', content.strip())
                    content_hash = hashlib.md5(normalized.encode()).hexdigest()
                    
                    if content_hash not in self.content_hashes:
                        self.content_hashes[content_hash] = []
                    self.content_hashes[content_hash].append(rel_path)
            except Exception:
                pass
                
    def _get_content(self, rel_path: str) -> Optional[str]:
        """Get file content, from cache or disk"""
        if rel_path in self.file_contents:
            return self.file_contents[rel_path]
        
        try:
            full_path = self.repo_path / rel_path
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                self.file_contents[rel_path] = content
                return content
        except Exception:
            return None
            
    def build_case(self, file_path: str) -> ProsecutionCase:
        """Build the prosecution case against a file"""
        case = ProsecutionCase(file_path=file_path)
        
        # Gather all evidence
        self._check_orphan_status(file_path, case)
        self._check_duplicate_content(file_path, case)
        self._check_obsolete_naming(file_path, case)
        self._check_abandonment_markers(file_path, case)
        self._check_incomplete_implementation(file_path, case)
        self._check_dead_code(file_path, case)
        self._check_size_anomalies(file_path, case)
        self._check_staleness(file_path, case)
        self._check_location_anomalies(file_path, case)
        
        # Calculate prosecution score
        case.prosecution_score = self._calculate_score(case)
        
        # Build charges list
        case.charges = [e.description for e in case.evidence if e.weight > 0.3]
        
        # Determine recommended action
        if case.prosecution_score >= 70:
            case.recommended_action = "quarantine"
        elif case.prosecution_score >= 50:
            case.recommended_action = "review"
        else:
            case.recommended_action = "keep"
            
        # Build summary
        case.summary = self._build_summary(case)
        
        return case
    
    def _check_orphan_status(self, file_path: str, case: ProsecutionCase):
        """Check if file is orphaned (not imported by anything)"""
        importers = self.reverse_graph.get(file_path, set())
        imports = self.dep_graph.get(file_path, set())
        
        # Completely orphaned - no imports or importers
        if not importers and not imports:
            case.evidence.append(Evidence(
                type="orphan",
                description="File is completely isolated - no imports and nothing imports it",
                severity="critical",
                weight=0.8,
                details={"importers": 0, "imports": 0}
            ))
        # No importers but does import things
        elif not importers and imports:
            case.evidence.append(Evidence(
                type="orphan",
                description=f"Nothing imports this file (but it imports {len(imports)} files)",
                severity="major",
                weight=0.6,
                details={"importers": 0, "imports": len(imports)}
            ))
        # Very few importers
        elif len(importers) == 1:
            case.evidence.append(Evidence(
                type="low_usage",
                description=f"Only imported by 1 file: {list(importers)[0]}",
                severity="minor",
                weight=0.2,
                details={"importers": list(importers)}
            ))
            
    def _check_duplicate_content(self, file_path: str, case: ProsecutionCase):
        """Check if file is a duplicate of another"""
        content = self._get_content(file_path)
        if not content:
            return
            
        normalized = re.sub(r'\s+', ' ', content.strip())
        content_hash = hashlib.md5(normalized.encode()).hexdigest()
        
        duplicates = self.content_hashes.get(content_hash, [])
        other_duplicates = [d for d in duplicates if d != file_path]
        
        if other_duplicates:
            case.evidence.append(Evidence(
                type="duplicate",
                description=f"Exact duplicate of: {', '.join(other_duplicates)}",
                severity="critical",
                weight=0.9,
                details={"duplicates": other_duplicates, "hash": content_hash}
            ))
            
        # Check for near-duplicates (similar size, same extension)
        file_size = len(content)
        for other_path in self.all_file_paths:
            if other_path == file_path:
                continue
            if Path(other_path).suffix != Path(file_path).suffix:
                continue
                
            other_content = self._get_content(other_path)
            if not other_content:
                continue
                
            other_size = len(other_content)
            # Within 10% size and same extension
            if abs(file_size - other_size) / max(file_size, other_size, 1) < 0.1:
                # Check content similarity
                similarity = self._calculate_similarity(content, other_content)
                if similarity > 0.85:
                    case.evidence.append(Evidence(
                        type="near_duplicate",
                        description=f"Very similar ({similarity*100:.0f}%) to: {other_path}",
                        severity="major",
                        weight=0.7,
                        details={"similar_to": other_path, "similarity": similarity}
                    ))
                    break  # Only report one
                    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate Jaccard similarity between two texts"""
        words1 = set(re.findall(r'\w+', content1.lower()))
        words2 = set(re.findall(r'\w+', content2.lower()))
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
        
    def _check_obsolete_naming(self, file_path: str, case: ProsecutionCase):
        """Check if filename suggests obsolescence"""
        file_name = Path(file_path).name.lower()
        
        for pattern in self.OBSOLETE_PATTERNS:
            if re.search(pattern, file_name, re.IGNORECASE):
                case.evidence.append(Evidence(
                    type="obsolete_name",
                    description=f"Filename contains obsolete marker: {pattern}",
                    severity="major",
                    weight=0.7,
                    details={"pattern": pattern, "filename": file_name}
                ))
                return  # One is enough
                
    def _check_abandonment_markers(self, file_path: str, case: ProsecutionCase):
        """Check content for abandonment markers"""
        content = self._get_content(file_path)
        if not content:
            return
            
        found_markers = []
        for pattern in self.ABANDONMENT_MARKERS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                found_markers.extend(matches[:2])  # Limit to 2 per pattern
                
        if found_markers:
            case.evidence.append(Evidence(
                type="abandonment_markers",
                description=f"Contains abandonment markers: {', '.join(found_markers[:5])}",
                severity="major",
                weight=0.6,
                details={"markers": found_markers[:10]}
            ))
            
    def _check_incomplete_implementation(self, file_path: str, case: ProsecutionCase):
        """Check for incomplete/stub implementations"""
        content = self._get_content(file_path)
        if not content:
            return
            
        # Count incomplete markers
        incomplete_count = 0
        found_markers = []
        
        for pattern in self.INCOMPLETE_MARKERS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            incomplete_count += len(matches)
            if matches:
                found_markers.append(pattern)
                
        # Check ratio of incomplete markers to code
        lines = content.split('\n')
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        
        if code_lines and incomplete_count > 0:
            ratio = incomplete_count / len(code_lines)
            
            if ratio > 0.1:  # More than 10% incomplete markers
                case.evidence.append(Evidence(
                    type="incomplete",
                    description=f"High incomplete marker ratio ({ratio*100:.1f}%): {incomplete_count} markers in {len(code_lines)} lines",
                    severity="major",
                    weight=0.5,
                    details={"markers_found": incomplete_count, "code_lines": len(code_lines), "patterns": found_markers}
                ))
            elif incomplete_count > 5:
                case.evidence.append(Evidence(
                    type="incomplete",
                    description=f"Contains {incomplete_count} TODO/FIXME markers",
                    severity="minor",
                    weight=0.2,
                    details={"markers_found": incomplete_count}
                ))
                
    def _check_dead_code(self, file_path: str, case: ProsecutionCase):
        """Check for dead code patterns"""
        content = self._get_content(file_path)
        if not content:
            return
            
        ext = Path(file_path).suffix.lower()
        
        if ext == '.py':
            # Check for functions/classes that are defined but never called
            func_defs = re.findall(r'def\s+(\w+)\s*\(', content)
            class_defs = re.findall(r'class\s+(\w+)\s*[\(:]', content)
            
            # Check if these are used elsewhere in the repo
            unused_funcs = []
            for func in func_defs:
                if func.startswith('_') and not func.startswith('__'):
                    # Private function - check if used in same file
                    usage_count = len(re.findall(r'\b' + func + r'\s*\(', content)) - 1
                    if usage_count == 0:
                        unused_funcs.append(func)
                        
            if len(unused_funcs) > 3:
                case.evidence.append(Evidence(
                    type="dead_code",
                    description=f"Contains {len(unused_funcs)} potentially unused private functions",
                    severity="minor",
                    weight=0.3,
                    details={"unused_functions": unused_funcs[:10]}
                ))
                
        # Check for commented-out code blocks
        commented_code_patterns = [
            r'#.*def\s+\w+',  # Commented function
            r'#.*class\s+\w+',  # Commented class
            r'#.*import\s+',  # Commented import
            r'//.*function\s+',  # JS commented function
            r'/\*[\s\S]*?def\s+\w+[\s\S]*?\*/',  # Block comment with code
        ]
        
        commented_code_count = 0
        for pattern in commented_code_patterns:
            commented_code_count += len(re.findall(pattern, content))
            
        if commented_code_count > 5:
            case.evidence.append(Evidence(
                type="commented_code",
                description=f"Contains {commented_code_count} blocks of commented-out code",
                severity="minor",
                weight=0.25,
                details={"count": commented_code_count}
            ))
            
    def _check_size_anomalies(self, file_path: str, case: ProsecutionCase):
        """Check for size anomalies (too small to be useful)"""
        content = self._get_content(file_path)
        if not content:
            return
            
        lines = [l for l in content.split('\n') if l.strip()]
        
        # Very small files (might be stubs)
        if len(lines) < 5:
            case.evidence.append(Evidence(
                type="tiny_file",
                description=f"Very small file with only {len(lines)} non-empty lines",
                severity="minor",
                weight=0.3,
                details={"lines": len(lines)}
            ))
        # Empty or near-empty
        elif len(lines) == 0:
            case.evidence.append(Evidence(
                type="empty_file",
                description="File is empty or contains only whitespace",
                severity="critical",
                weight=0.9,
                details={"lines": 0}
            ))
            
    def _check_staleness(self, file_path: str, case: ProsecutionCase):
        """Check if file appears stale based on content patterns"""
        content = self._get_content(file_path)
        if not content:
            return
            
        # Check for old date references
        old_year_pattern = r'\b20(1[0-9]|20|21|22)\b'  # Years 2010-2022
        old_years = re.findall(old_year_pattern, content)
        
        if len(old_years) > 3:
            case.evidence.append(Evidence(
                type="stale_dates",
                description=f"Contains multiple references to old years (20{old_years[0]}, etc.)",
                severity="info",
                weight=0.15,
                details={"years_found": list(set(old_years))[:5]}
            ))
            
    def _check_location_anomalies(self, file_path: str, case: ProsecutionCase):
        """Check if file is in an unexpected location"""
        path = Path(file_path)
        
        # Test files outside test directories
        if 'test' in path.name.lower() and 'test' not in str(path.parent).lower():
            case.evidence.append(Evidence(
                type="misplaced",
                description="Test file located outside of test directory",
                severity="minor",
                weight=0.2,
                details={"location": str(path.parent)}
            ))
            
        # Config files in deep directories
        if path.suffix in ['.json', '.yaml', '.yml', '.toml']:
            if len(path.parts) > 4:  # Deep nesting
                # Check if it looks like a config that should be at root
                if 'config' in path.name.lower():
                    case.evidence.append(Evidence(
                        type="deep_config",
                        description=f"Config file nested {len(path.parts)} levels deep",
                        severity="info",
                        weight=0.1,
                        details={"depth": len(path.parts)}
                    ))
                    
    def _calculate_score(self, case: ProsecutionCase) -> float:
        """Calculate overall prosecution score (0-100)"""
        if not case.evidence:
            return 0.0
            
        # Weighted sum of evidence
        total_weight = sum(max(0, e.weight) for e in case.evidence)
        
        # Apply severity multipliers
        severity_multiplier = 1.0
        for e in case.evidence:
            if e.severity == "critical":
                severity_multiplier = max(severity_multiplier, 1.5)
            elif e.severity == "major":
                severity_multiplier = max(severity_multiplier, 1.2)
                
        score = min(100, total_weight * 40 * severity_multiplier)
        return round(score, 1)
        
    def _build_summary(self, case: ProsecutionCase) -> str:
        """Build prosecution summary"""
        if not case.evidence:
            return "No evidence against this file."
            
        critical = [e for e in case.evidence if e.severity == "critical"]
        major = [e for e in case.evidence if e.severity == "major"]
        
        summary_parts = []
        
        if critical:
            summary_parts.append(f"🚨 {len(critical)} CRITICAL issue(s)")
        if major:
            summary_parts.append(f"⚠️ {len(major)} major issue(s)")
            
        summary_parts.append(f"Prosecution score: {case.prosecution_score}/100")
        
        return " | ".join(summary_parts)
