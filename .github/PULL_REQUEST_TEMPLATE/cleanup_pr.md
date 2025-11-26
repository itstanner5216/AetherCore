## 🧹 Repository Cleanup: Quarantine Suggestions

### Summary

This automated PR identifies files that may be unused, orphaned, or redundant based on:
- **Dependency Analysis**: Code import/reference tracking
- **Semantic Similarity**: Keyword and topic-based relationship detection
- **File Relevance Scoring**: Combined metrics for file importance

### ⚠️ Important Notes

- **No files are deleted** - they are moved to the `/quarantine` folder
- **Review each file** before approving this PR
- **Restore is easy** - use the restore script in the quarantine folder

---

### Files Marked for Quarantine

<!-- The workflow will populate this section with the analysis results -->

| File | Type | Relevance Score | Reason |
|------|------|-----------------|--------|
| _See attached report for details_ | | | |

---

### How to Review

1. **Check the detailed report** in the workflow artifacts
2. **Verify each flagged file** isn't actually in use
3. **Test the application** to ensure nothing breaks
4. **Restore any false positives** using:
   ```bash
   cd quarantine/<session_id>
   ./restore_files.sh
   ```

### Dependency Graph

See the full dependency analysis in the attached JSON report.

---

### After Merging

- Files remain in `/quarantine` for 30 days
- Run `quarantine_manager.py --cleanup` to permanently remove old files
- Consider adding `.gitkeep` files if directories become empty

---

### Related Links

- [Analysis Report](../actions) - View full workflow run
- [Quarantine Manager Docs](.github/workflows/scripts/README.md)

---

/cc @{{ assignee }}

<!-- Labels: cleanup, automated, needs-review -->
