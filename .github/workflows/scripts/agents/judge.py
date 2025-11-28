#!/usr/bin/env python3
"""
Judge Agent - Makes FINAL verdict after hearing Prosecutor and Defense

The Judge Agent is impartial and weighs evidence from both sides.
It considers:
1. Strength of prosecution evidence vs defense evidence
2. Risk of removal vs cost of keeping
3. Reversibility of decision
4. Project-wide impact
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class JudgmentReasoning:
    """Detailed reasoning for the judgment"""

    prosecution_weight: float
    defense_weight: float
    key_factors: List[str]
    risk_assessment: str
    dissenting_points: List[str]


@dataclass
class Verdict:
    """Final verdict on a file"""

    file_path: str
    decision: str  # "KEEP", "QUARANTINE", "DELETE", "REVIEW_NEEDED"
    confidence: float
    reasoning: JudgmentReasoning
    summary: str
    recommendation: str

    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "decision": self.decision,
            "confidence": self.confidence,
            "reasoning": {
                "prosecution_weight": self.reasoning.prosecution_weight,
                "defense_weight": self.reasoning.defense_weight,
                "key_factors": self.reasoning.key_factors,
                "risk_assessment": self.reasoning.risk_assessment,
                "dissenting_points": self.reasoning.dissenting_points,
            },
            "summary": self.summary,
            "recommendation": self.recommendation,
        }


class JudgeAgent:
    """
    ⚖️ JUDGE AGENT - Impartial Final Arbiter

    The Judge weighs ALL evidence and makes the final call.
    It must consider both prosecution AND defense cases fairly.
    """

    # Thresholds for verdicts
    QUARANTINE_THRESHOLD = 0.65  # Prosecution must be this much stronger
    KEEP_THRESHOLD = 0.55  # Defense must be this much stronger
    REVIEW_THRESHOLD = 0.15  # If difference is this small, needs review

    # High-risk file patterns that require extra scrutiny before removal
    HIGH_RISK_PATTERNS = [
        "auth",
        "security",
        "config",
        "main",
        "index",
        "server",
        "app",
        "core",
        "base",
        "util",
        "helper",
        "api",
        "gateway",
        "__init__",
        "setup",
        "install",
        "deploy",
        "build",
    ]

    # Evidence categories that carry extra weight
    CRITICAL_PROSECUTION = ["NO_IMPORTS", "NO_REFERENCES", "STALE", "EXACT_DUPLICATE"]
    CRITICAL_DEFENSE = ["IMPORT_DEPENDENCY", "ENTRY_POINT", "CONFIGURATION_FILE", "INTEGRATION"]

    def __init__(self, conservative_mode: bool = True):
        """
        Initialize the Judge.

        Args:
            conservative_mode: If True, err on the side of keeping files
        """
        self.conservative_mode = conservative_mode
        self.verdicts: List[Verdict] = []

    def judge(self, prosecution_case: Dict, defense_case: Dict) -> Verdict:
        """
        Render judgment after hearing both cases.

        Args:
            prosecution_case: The ProsecutionCase as dict
            defense_case: The DefenseCase as dict

        Returns:
            Final Verdict
        """
        file_path = prosecution_case["file_path"]

        # Calculate weighted scores for each side
        prosecution_score = self._calculate_prosecution_score(prosecution_case)
        defense_score = self._calculate_defense_score(defense_case)

        # Check for high-risk file
        is_high_risk = self._is_high_risk(file_path)

        # Apply conservative mode adjustments
        if self.conservative_mode:
            defense_score *= 1.15  # 15% boost to defense in conservative mode

        if is_high_risk:
            defense_score *= 1.25  # Additional 25% boost for high-risk files

        # Normalize scores
        total = prosecution_score + defense_score
        if total > 0:
            prosecution_weight = prosecution_score / total
            defense_weight = defense_score / total
        else:
            prosecution_weight = defense_weight = 0.5

        # Gather key factors
        key_factors = self._identify_key_factors(prosecution_case, defense_case)

        # Identify dissenting points (strong evidence on losing side)
        dissenting_points = self._identify_dissenting_points(
            prosecution_case, defense_case, prosecution_weight > defense_weight
        )

        # Assess risk
        risk_assessment = self._assess_risk(file_path, prosecution_case, defense_case, is_high_risk)

        # Make decision
        decision, confidence = self._make_decision(
            prosecution_weight, defense_weight, is_high_risk, dissenting_points
        )

        # Build reasoning
        reasoning = JudgmentReasoning(
            prosecution_weight=round(prosecution_weight, 3),
            defense_weight=round(defense_weight, 3),
            key_factors=key_factors,
            risk_assessment=risk_assessment,
            dissenting_points=dissenting_points,
        )

        # Generate summary and recommendation
        summary = self._generate_summary(file_path, decision, reasoning)
        recommendation = self._generate_recommendation(file_path, decision, reasoning)

        verdict = Verdict(
            file_path=file_path,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            summary=summary,
            recommendation=recommendation,
        )

        self.verdicts.append(verdict)
        return verdict

    def _calculate_prosecution_score(self, case: Dict) -> float:
        """Calculate weighted prosecution score"""
        score = 0.0

        for evidence in case.get("evidence", []):
            strength = evidence.get("strength", 0)
            category = evidence.get("category", "")

            # Critical prosecution evidence gets bonus
            if category in self.CRITICAL_PROSECUTION:
                strength *= 1.5

            score += strength

        # Boost if multiple independent evidence types
        evidence_categories = set(e.get("category") for e in case.get("evidence", []))
        if len(evidence_categories) >= 3:
            score *= 1.2

        return score

    def _calculate_defense_score(self, case: Dict) -> float:
        """Calculate weighted defense score"""
        score = 0.0

        for evidence in case.get("evidence", []):
            strength = evidence.get("strength", 0)
            category = evidence.get("category", "")

            # Critical defense evidence gets bonus
            if category in self.CRITICAL_DEFENSE:
                strength *= 1.5

            score += strength

        # Boost based on import chain length
        import_chain = case.get("import_chain", [])
        if len(import_chain) > 0:
            score += min(1.0, len(import_chain) * 0.2)

        # Boost based on references
        referenced_by = case.get("referenced_by", [])
        if len(referenced_by) > 0:
            score += min(0.8, len(referenced_by) * 0.15)

        return score

    def _is_high_risk(self, file_path: str) -> bool:
        """Check if file is high-risk for removal"""
        filename = Path(file_path).name.lower()
        stem = Path(file_path).stem.lower()

        return any(pattern in filename or pattern in stem for pattern in self.HIGH_RISK_PATTERNS)

    def _identify_key_factors(self, prosecution: Dict, defense: Dict) -> List[str]:
        """Identify the most important factors in the decision"""
        factors = []

        # Top prosecution evidence
        pros_evidence = sorted(
            prosecution.get("evidence", []), key=lambda e: e.get("strength", 0), reverse=True
        )
        if pros_evidence:
            factors.append(f"🔴 Prosecution: {pros_evidence[0].get('description', 'N/A')}")

        # Top defense evidence
        def_evidence = sorted(
            defense.get("evidence", []), key=lambda e: e.get("strength", 0), reverse=True
        )
        if def_evidence:
            factors.append(f"🟢 Defense: {def_evidence[0].get('description', 'N/A')}")

        # Import analysis
        if defense.get("import_chain"):
            factors.append(f"📊 Has {len(defense['import_chain'])} import dependencies")

        # Staleness
        staleness = prosecution.get("staleness_days", 0)
        if staleness > 180:
            factors.append(f"📅 Not modified in {staleness} days")

        return factors[:5]

    def _identify_dissenting_points(
        self, prosecution: Dict, defense: Dict, prosecution_won: bool
    ) -> List[str]:
        """Identify strong points from the losing side"""
        dissent = []

        losing_case = defense if prosecution_won else prosecution
        for evidence in losing_case.get("evidence", []):
            if evidence.get("strength", 0) >= 0.7:
                dissent.append(f"{'⚠️' if prosecution_won else '⚡'} {evidence.get('description')}")

        return dissent[:3]

    def _assess_risk(
        self, file_path: str, prosecution: Dict, defense: Dict, is_high_risk: bool
    ) -> str:
        """Assess risk level of removing the file"""
        risks = []

        if is_high_risk:
            risks.append("HIGH: File name suggests critical functionality")

        if defense.get("import_chain"):
            risks.append(f"MEDIUM: {len(defense['import_chain'])} files may be affected")

        if any(e.get("category") == "INTEGRATION" for e in defense.get("evidence", [])):
            risks.append("HIGH: File appears to be an integration point")

        if any(e.get("category") == "ENTRY_POINT" for e in defense.get("evidence", [])):
            risks.append("CRITICAL: File appears to be an entry point")

        if not risks:
            return "LOW: No significant risks identified"

        return " | ".join(risks)

    def _make_decision(
        self,
        prosecution_weight: float,
        defense_weight: float,
        is_high_risk: bool,
        dissenting_points: List[str],
    ) -> Tuple[str, float]:
        """Make the final decision"""

        difference = prosecution_weight - defense_weight

        # Strong prosecution case
        if difference > self.QUARANTINE_THRESHOLD:
            if is_high_risk and len(dissenting_points) > 0:
                return "REVIEW_NEEDED", 0.6
            return "QUARANTINE", min(0.95, 0.5 + difference)

        # Strong defense case
        if difference < -self.KEEP_THRESHOLD:
            return "KEEP", min(0.95, 0.5 + abs(difference))

        # Close call - needs human review
        if abs(difference) < self.REVIEW_THRESHOLD:
            return "REVIEW_NEEDED", 0.5

        # Moderate prosecution edge but not overwhelming
        if difference > 0:
            if is_high_risk:
                return "REVIEW_NEEDED", 0.55
            return "QUARANTINE", 0.6 + (difference * 0.3)

        # Moderate defense edge
        return "KEEP", 0.6 + (abs(difference) * 0.3)

    def _generate_summary(self, file_path: str, decision: str, reasoning: JudgmentReasoning) -> str:
        """Generate human-readable summary"""
        filename = Path(file_path).name

        emoji_map = {"KEEP": "✅", "QUARANTINE": "📦", "DELETE": "🗑️", "REVIEW_NEEDED": "👀"}

        summary = f"{emoji_map.get(decision, '❓')} **{decision}**: `{filename}`\n"
        summary += f"   Prosecution: {reasoning.prosecution_weight:.0%} | Defense: {reasoning.defense_weight:.0%}\n"

        if reasoning.key_factors:
            summary += f"   Key: {reasoning.key_factors[0]}\n"

        return summary

    def _generate_recommendation(
        self, file_path: str, decision: str, reasoning: JudgmentReasoning
    ) -> str:
        """Generate actionable recommendation"""
        filename = Path(file_path).name

        if decision == "KEEP":
            return f"✅ KEEP `{filename}` - Defense presented compelling evidence for retention."

        if decision == "QUARANTINE":
            rec = (
                f"📦 QUARANTINE `{filename}` - Move to quarantine folder for observation period.\n"
            )
            if reasoning.dissenting_points:
                rec += f"   ⚠️ Note: {reasoning.dissenting_points[0]}"
            return rec

        if decision == "DELETE":
            return f"🗑️ DELETE `{filename}` - Strong evidence of redundancy with no dependencies."

        # REVIEW_NEEDED
        rec = f"👀 REVIEW NEEDED for `{filename}` - Evidence is inconclusive.\n"
        rec += f"   Risk: {reasoning.risk_assessment}\n"
        rec += "   Recommended: Manual inspection before any action."
        return rec

    def get_court_summary(self) -> Dict:
        """Get summary of all verdicts"""
        if not self.verdicts:
            return {"error": "No verdicts rendered"}

        summary = {
            "total_cases": len(self.verdicts),
            "verdicts": {"KEEP": 0, "QUARANTINE": 0, "DELETE": 0, "REVIEW_NEEDED": 0},
            "high_confidence_decisions": 0,
            "files_by_decision": {"KEEP": [], "QUARANTINE": [], "DELETE": [], "REVIEW_NEEDED": []},
        }

        for v in self.verdicts:
            summary["verdicts"][v.decision] += 1
            summary["files_by_decision"][v.decision].append(v.file_path)
            if v.confidence >= 0.8:
                summary["high_confidence_decisions"] += 1

        return summary

    def render_report(self) -> str:
        """Render a full court report"""
        report = []
        report.append("=" * 70)
        report.append("⚖️  FILE COURT - FINAL VERDICTS")
        report.append("=" * 70)
        report.append(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📁 Cases Heard: {len(self.verdicts)}")
        report.append("")

        # Summary stats
        summary = self.get_court_summary()
        report.append("📊 VERDICT SUMMARY:")
        report.append(f"   ✅ KEEP:          {summary['verdicts']['KEEP']}")
        report.append(f"   📦 QUARANTINE:    {summary['verdicts']['QUARANTINE']}")
        report.append(f"   🗑️  DELETE:        {summary['verdicts']['DELETE']}")
        report.append(f"   👀 REVIEW_NEEDED: {summary['verdicts']['REVIEW_NEEDED']}")
        report.append("")

        report.append("-" * 70)
        report.append("📜 INDIVIDUAL VERDICTS:")
        report.append("-" * 70)

        for verdict in self.verdicts:
            report.append("")
            report.append(verdict.summary)
            if verdict.reasoning.dissenting_points:
                for point in verdict.reasoning.dissenting_points:
                    report.append(f"      {point}")

        report.append("")
        report.append("=" * 70)
        report.append("📌 RECOMMENDED ACTIONS:")
        report.append("=" * 70)

        # Group by decision
        for decision in ["QUARANTINE", "DELETE", "REVIEW_NEEDED"]:
            files = summary["files_by_decision"][decision]
            if files:
                report.append(f"\n{decision}:")
                for f in files[:20]:  # Limit display
                    report.append(f"  • {f}")
                if len(files) > 20:
                    report.append(f"  ... and {len(files) - 20} more")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)


if __name__ == "__main__":
    # Test the judge with mock cases
    judge = JudgeAgent(conservative_mode=True)

    mock_prosecution = {
        "file_path": "test_file.py",
        "verdict": "REDUNDANT",
        "confidence": 0.7,
        "evidence": [
            {
                "category": "NO_IMPORTS",
                "description": "File is not imported anywhere",
                "strength": 0.8,
            },
            {"category": "STALE", "description": "Not modified in 200 days", "strength": 0.6},
        ],
        "staleness_days": 200,
    }

    mock_defense = {
        "file_path": "test_file.py",
        "verdict": "USEFUL",
        "confidence": 0.5,
        "evidence": [
            {"category": "SUBSTANTIAL_CODE", "description": "File has 150 lines", "strength": 0.5}
        ],
        "import_chain": [],
        "referenced_by": [],
    }

    verdict = judge.judge(mock_prosecution, mock_defense)
    print(judge.render_report())
