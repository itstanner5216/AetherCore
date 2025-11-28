#!/usr/bin/env python3
"""
Quarantine Manager
Handles moving files to quarantine folder and tracking changes.

Part of AetherCore Repository Cleanup System
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class QuarantineManager:
    """
    Manages file quarantine operations:
    - Moving files to quarantine folder
    - Creating quarantine manifest
    - Generating restore scripts
    - Tracking file history
    """

    QUARANTINE_DIR = "quarantine"
    MANIFEST_FILE = "quarantine_manifest.json"
    RESTORE_SCRIPT = "restore_files.sh"

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path).resolve()
        self.quarantine_path = self.repo_path / self.QUARANTINE_DIR
        self.manifest_path = self.quarantine_path / self.MANIFEST_FILE
        self.manifest: Dict = self._load_manifest()

    def _load_manifest(self) -> Dict:
        """Load existing manifest or create new one"""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load manifest: {e}")

        return {
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "quarantine_sessions": [],
            "files": {},
        }

    def _save_manifest(self):
        """Save manifest to file"""
        self.manifest["last_updated"] = datetime.now().isoformat()

        self.quarantine_path.mkdir(parents=True, exist_ok=True)

        with open(self.manifest_path, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def move_to_quarantine(
        self,
        files: List[str],
        reasons: Dict[str, List[str]] = None,
        session_id: str = None,
        dry_run: bool = False,
    ) -> List[Dict]:
        """
        Move files to quarantine folder.

        Args:
            files: List of relative file paths to quarantine
            reasons: Dict mapping file paths to list of reasons
            session_id: Optional session identifier
            dry_run: If True, don't actually move files

        Returns:
            List of dicts with move results
        """
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        results = []
        session_files = []

        for file_path in files:
            result = self._move_single_file(
                file_path, reasons.get(file_path, []) if reasons else [], session_id, dry_run
            )
            results.append(result)

            if result["success"]:
                session_files.append(result)

        # Record session
        if session_files and not dry_run:
            self.manifest["quarantine_sessions"].append(
                {
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "files_count": len(session_files),
                    "files": [f["original_path"] for f in session_files],
                }
            )
            self._save_manifest()
            self._generate_restore_script(session_id, session_files)

        return results

    def _move_single_file(
        self, file_path: str, reasons: List[str], session_id: str, dry_run: bool
    ) -> Dict:
        """Move a single file to quarantine"""
        source = self.repo_path / file_path

        if not source.exists():
            return {"original_path": file_path, "success": False, "error": "File not found"}

        # Create quarantine path preserving directory structure
        quarantine_subdir = self.quarantine_path / session_id
        dest = quarantine_subdir / file_path

        try:
            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(dest))

                # Clean up empty parent directories
                self._cleanup_empty_dirs(source.parent)

            # Update manifest
            file_record = {
                "original_path": file_path,
                "quarantine_path": str(dest.relative_to(self.repo_path)),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "reasons": reasons,
                "restored": False,
            }

            if not dry_run:
                self.manifest["files"][file_path] = file_record

            return {
                "original_path": file_path,
                "quarantine_path": str(dest.relative_to(self.repo_path)),
                "success": True,
                "dry_run": dry_run,
            }

        except Exception as e:
            logger.error(f"Error moving {file_path}: {e}")
            return {"original_path": file_path, "success": False, "error": str(e)}

    def _cleanup_empty_dirs(self, dir_path: Path):
        """Remove empty directories up to repo root"""
        try:
            while dir_path != self.repo_path:
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    logger.debug(f"Removed empty directory: {dir_path}")
                    dir_path = dir_path.parent
                else:
                    break
        except Exception as e:
            logger.warning(f"Error cleaning directories: {e}")

    def restore_file(self, file_path: str, dry_run: bool = False) -> Dict:
        """Restore a single file from quarantine"""
        if file_path not in self.manifest["files"]:
            return {
                "file_path": file_path,
                "success": False,
                "error": "File not found in quarantine manifest",
            }

        record = self.manifest["files"][file_path]

        if record.get("restored"):
            return {"file_path": file_path, "success": False, "error": "File already restored"}

        quarantine_path = self.repo_path / record["quarantine_path"]
        original_path = self.repo_path / file_path

        if not quarantine_path.exists():
            return {"file_path": file_path, "success": False, "error": "Quarantined file not found"}

        try:
            if not dry_run:
                original_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(quarantine_path), str(original_path))
                record["restored"] = True
                record["restored_at"] = datetime.now().isoformat()
                self._save_manifest()

            return {"file_path": file_path, "success": True, "dry_run": dry_run}

        except Exception as e:
            logger.error(f"Error restoring {file_path}: {e}")
            return {"file_path": file_path, "success": False, "error": str(e)}

    def restore_session(self, session_id: str, dry_run: bool = False) -> List[Dict]:
        """Restore all files from a quarantine session"""
        session = None
        for s in self.manifest["quarantine_sessions"]:
            if s["session_id"] == session_id:
                session = s
                break

        if not session:
            return [{"success": False, "error": f"Session {session_id} not found"}]

        results = []
        for file_path in session["files"]:
            result = self.restore_file(file_path, dry_run)
            results.append(result)

        return results

    def _generate_restore_script(self, session_id: str, files: List[Dict]):
        """Generate shell script to restore quarantined files"""
        script_path = self.quarantine_path / session_id / self.RESTORE_SCRIPT

        lines = [
            "#!/bin/bash",
            "# Restore script for quarantine session: " + session_id,
            "# Generated: " + datetime.now().isoformat(),
            "",
            "set -e",
            "",
            'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"',
            'REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"',
            "",
            'echo "Restoring files from quarantine session: ' + session_id + '"',
            "",
        ]

        for f in files:
            original = f["original_path"]
            quarantined = f["quarantine_path"]

            lines.extend(
                [
                    f"# Restore: {original}",
                    f'mkdir -p "$REPO_ROOT/{Path(original).parent}"',
                    f'mv "$REPO_ROOT/{quarantined}" "$REPO_ROOT/{original}"',
                    f'echo "Restored: {original}"',
                    "",
                ]
            )

        lines.extend(
            [
                'echo ""',
                'echo "All files restored successfully!"',
                f'echo "Remember to remove the quarantine/{session_id} directory after verification"',
            ]
        )

        script_path.parent.mkdir(parents=True, exist_ok=True)
        with open(script_path, "w") as f:
            f.write("\n".join(lines))

        # Make executable
        os.chmod(script_path, 0o755)
        logger.info(f"Generated restore script: {script_path}")

    def get_quarantine_summary(self) -> Dict:
        """Get summary of quarantine status"""
        total_files = len(self.manifest["files"])
        restored_files = sum(1 for f in self.manifest["files"].values() if f.get("restored"))

        return {
            "total_quarantined": total_files,
            "restored": restored_files,
            "pending": total_files - restored_files,
            "sessions": len(self.manifest["quarantine_sessions"]),
            "last_updated": self.manifest.get("last_updated"),
        }

    def list_quarantined_files(self, session_id: str = None) -> List[Dict]:
        """List all quarantined files, optionally filtered by session"""
        files = []

        for path, record in self.manifest["files"].items():
            if session_id and record.get("session_id") != session_id:
                continue

            files.append(
                {
                    "path": path,
                    "quarantine_path": record["quarantine_path"],
                    "session_id": record["session_id"],
                    "timestamp": record["timestamp"],
                    "reasons": record.get("reasons", []),
                    "restored": record.get("restored", False),
                }
            )

        return sorted(files, key=lambda x: x["timestamp"], reverse=True)

    def permanently_delete(self, file_path: str) -> Dict:
        """Permanently delete a quarantined file"""
        if file_path not in self.manifest["files"]:
            return {
                "file_path": file_path,
                "success": False,
                "error": "File not found in quarantine manifest",
            }

        record = self.manifest["files"][file_path]
        quarantine_path = self.repo_path / record["quarantine_path"]

        try:
            if quarantine_path.exists():
                quarantine_path.unlink()

            # Mark as deleted in manifest
            record["deleted"] = True
            record["deleted_at"] = datetime.now().isoformat()
            self._save_manifest()

            return {"file_path": file_path, "success": True}

        except Exception as e:
            return {"file_path": file_path, "success": False, "error": str(e)}

    def cleanup_old_sessions(self, days: int = 30) -> Dict:
        """Clean up quarantine sessions older than specified days"""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for session in self.manifest["quarantine_sessions"]:
            session_time = datetime.fromisoformat(session["timestamp"])

            if session_time < cutoff:
                # Delete session directory
                session_dir = self.quarantine_path / session["session_id"]
                if session_dir.exists():
                    shutil.rmtree(session_dir)
                    deleted_count += 1

                    # Mark files as cleaned
                    for file_path in session["files"]:
                        if file_path in self.manifest["files"]:
                            self.manifest["files"][file_path]["cleaned"] = True

        self._save_manifest()

        return {"sessions_cleaned": deleted_count, "cutoff_date": cutoff.isoformat()}


def generate_quarantine_report(manager: QuarantineManager) -> str:
    """Generate markdown report of quarantine status"""
    summary = manager.get_quarantine_summary()
    files = manager.list_quarantined_files()

    lines = [
        "# Quarantine Status Report",
        "",
        f"**Generated:** {datetime.now().isoformat()}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f'| Total Quarantined | {summary["total_quarantined"]} |',
        f'| Restored | {summary["restored"]} |',
        f'| Pending Review | {summary["pending"]} |',
        f'| Sessions | {summary["sessions"]} |',
        "",
    ]

    if files:
        lines.extend(
            [
                "## Quarantined Files",
                "",
            ]
        )

        # Group by session
        sessions = {}
        for f in files:
            sid = f["session_id"]
            if sid not in sessions:
                sessions[sid] = []
            sessions[sid].append(f)

        for session_id, session_files in sessions.items():
            lines.append(f"### Session: {session_id}")
            lines.append("")

            for f in session_files:
                status = "✅ Restored" if f["restored"] else "⏳ Pending"
                lines.append(f'- `{f["path"]}` - {status}')
                if f["reasons"]:
                    for reason in f["reasons"]:
                        lines.append(f"  - {reason}")
            lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage quarantined files")
    parser.add_argument("--repo", "-r", default=".", help="Repository path")
    parser.add_argument("--list", "-l", action="store_true", help="List quarantined files")
    parser.add_argument("--restore", help="Restore file by path")
    parser.add_argument("--restore-session", help="Restore all files from session")
    parser.add_argument("--summary", "-s", action="store_true", help="Show summary")
    parser.add_argument("--report", action="store_true", help="Generate markdown report")

    args = parser.parse_args()

    manager = QuarantineManager(Path(args.repo))

    if args.list:
        files = manager.list_quarantined_files()
        for f in files:
            status = "restored" if f["restored"] else "pending"
            print(f"[{status}] {f['path']} (session: {f['session_id']})")

    elif args.restore:
        result = manager.restore_file(args.restore)
        print(f"Restore {'succeeded' if result['success'] else 'failed'}: {args.restore}")
        if not result["success"]:
            print(f"  Error: {result.get('error')}")

    elif args.restore_session:
        results = manager.restore_session(args.restore_session)
        success = sum(1 for r in results if r["success"])
        print(f"Restored {success}/{len(results)} files from session {args.restore_session}")

    elif args.summary:
        summary = manager.get_quarantine_summary()
        print("Quarantine Summary:")
        print(f"  Total: {summary['total_quarantined']}")
        print(f"  Restored: {summary['restored']}")
        print(f"  Pending: {summary['pending']}")
        print(f"  Sessions: {summary['sessions']}")

    elif args.report:
        report = generate_quarantine_report(manager)
        print(report)
