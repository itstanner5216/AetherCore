# Repository Cleanup Analysis System

Automated repository analysis and cleanup system for identifying unused, orphaned, or redundant files.

## Features

- **Dependency Graph Analysis**: Tracks imports, requires, and references across Python, JavaScript/TypeScript, JSON, YAML, and Markdown files
- **Semantic Similarity Detection**: Uses TF-IDF and topic modeling to find related files
- **Code-Documentation Linking**: Identifies documentation without implementation and vice versa
- **Quarantine System**: Safely moves flagged files for review (no automatic deletion)
- **GitHub Actions Integration**: Automated analysis with PR creation

## Directory Structure

```
.github/
├── workflows/
│   ├── repository_cleanup.yml    # Main workflow file
│   └── scripts/
│       ├── repository_analyzer.py   # Main orchestrator
│       ├── dependency_graph.py      # Dependency analysis
│       ├── semantic_analyzer.py     # Semantic similarity
│       ├── quarantine_manager.py    # File quarantine handling
│       ├── requirements.txt         # Python dependencies
│       └── README.md               # This file
├── cleanup_reports/                 # Generated reports (gitignored)
└── PULL_REQUEST_TEMPLATE/
    └── cleanup_pr.md               # PR template for cleanup
```

## Installation

### Requirements

- Python 3.9+
- PyYAML (for YAML file parsing)

```bash
pip install -r .github/workflows/scripts/requirements.txt
```

## Usage

### GitHub Actions (Recommended)

1. Go to **Actions** tab in your repository
2. Select **Repository Cleanup Analysis** workflow
3. Click **Run workflow**
4. Configure options:
   - **Dry run**: Preview changes without moving files
   - **Create PR**: Automatically create a PR with suggestions
   - **Similarity threshold**: Adjust semantic matching sensitivity
   - **Relevance threshold**: Minimum score for file importance

### Local Usage

```bash
# Basic analysis
python .github/workflows/scripts/repository_analyzer.py --repo /path/to/repo

# With quarantine (moves files)
python .github/workflows/scripts/repository_analyzer.py --repo . --quarantine

# Dry run (preview only)
python .github/workflows/scripts/repository_analyzer.py --repo . --quarantine --dry-run

# Custom output directory
python .github/workflows/scripts/repository_analyzer.py --repo . --output ./reports
```

### Quarantine Management

```bash
# List quarantined files
python .github/workflows/scripts/quarantine_manager.py --list

# Restore a specific file
python .github/workflows/scripts/quarantine_manager.py --restore path/to/file.py

# Restore entire session
python .github/workflows/scripts/quarantine_manager.py --restore-session 20240101_120000

# View summary
python .github/workflows/scripts/quarantine_manager.py --summary

# Generate report
python .github/workflows/scripts/quarantine_manager.py --report
```

## How It Works

### 1. File Discovery

Scans repository for:
- **Code files**: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`, `.go`, etc.
- **Documentation**: `.md`, `.txt`, `.rst`
- **Configuration**: `.json`, `.yaml`, `.yml`, `.toml`

Ignores:
- `.git`, `node_modules`, `__pycache__`, `venv`
- Lock files (`package-lock.json`, `yarn.lock`, etc.)
- The quarantine folder itself

### 2. Dependency Analysis

Builds a dependency graph by analyzing:
- **Python**: `import` and `from ... import` statements (AST-based)
- **JavaScript/TypeScript**: ES6 imports, CommonJS requires, dynamic imports
- **JSON/YAML**: File path references in configuration
- **Markdown**: Links to other files

### 3. Semantic Analysis

Extracts semantic information:
- **Keywords**: TF-IDF weighted terms
- **Topics**: Pattern-matched categories (api, database, auth, test, etc.)
- **Entities**: Function names, class names, headings
- **Similarity**: Cosine similarity between file vectors

### 4. Relevance Scoring

Each file receives a relevance score based on:
- Entry point status (main.py, index.js, etc.)
- Number of files that import/reference it
- Semantic connections to other files
- File type (configs get bonus points)

### 5. Quarantine Decision

Files are flagged for quarantine if:
- Not referenced by any other file (orphaned)
- Very low relevance score with high confidence
- Name contains markers like `_old`, `_backup`, `_deprecated`
- Detected as duplicate of another file
- Partial/incomplete implementation without references

## Output Reports

### JSON Report

Complete analysis data including:
- File-by-file analysis results
- Full dependency graph
- Semantic clusters
- Code-documentation links
- Quarantine recommendations

### Markdown Report

Human-readable summary with:
- Statistics and metrics
- Quarantine recommendations with reasons
- Most referenced files
- Detected inconsistencies
- Warnings

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SIMILARITY_THRESHOLD` | `0.3` | Minimum similarity for semantic links |
| `RELEVANCE_THRESHOLD` | `0.2` | Minimum relevance score |

### Workflow Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `dry_run` | `true` | Preview without moving files |
| `create_pr` | `true` | Create PR with results |
| `similarity_threshold` | `0.3` | Semantic matching threshold |
| `relevance_threshold` | `0.2` | Relevance score threshold |

## Restoring Files

### Using Restore Script

Each quarantine session generates a restore script:

```bash
cd quarantine/<session_id>
./restore_files.sh
```

### Using Python Manager

```bash
# Restore single file
python quarantine_manager.py --restore path/to/file.py

# Restore entire session
python quarantine_manager.py --restore-session 20240101_120000
```

### Manual Restoration

Files maintain their directory structure in quarantine:

```bash
# Original: src/utils/helper.py
# Quarantine: quarantine/<session>/src/utils/helper.py

mv quarantine/<session>/src/utils/helper.py src/utils/helper.py
```

## Troubleshooting

### "File not found in quarantine manifest"

The manifest may have been modified. Check `quarantine/quarantine_manifest.json`.

### High false positive rate

Adjust thresholds:
- Increase `relevance_threshold` to be more conservative
- Decrease `similarity_threshold` for stricter matching

### Missing dependencies in analysis

Ensure the file extension is supported. Add custom extensions to `CODE_EXTENSIONS` in `repository_analyzer.py`.

### Workflow fails with permission error

Ensure the workflow has `contents: write` and `pull-requests: write` permissions.

## Contributing

To extend the analysis:

1. **Add new file types**: Update extension sets in `RepositoryAnalyzer`
2. **Add import patterns**: Extend `DependencyGraphBuilder` with new parsers
3. **Add topic patterns**: Update `TOPIC_PATTERNS` in `SemanticAnalyzer`
4. **Custom scoring**: Modify `_calculate_relevance_scores` logic

## License

Part of AetherCore project. See repository root for license information.
