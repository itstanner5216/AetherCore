#!/usr/bin/env python3
"""
Semantic Analyzer
Analyzes semantic similarity between files using keyword extraction,
topic modeling, and text similarity.

Part of AetherCore Repository Cleanup System
"""

import logging
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FileSemantics:
    """Semantic information extracted from a file"""

    path: str
    file_type: str
    keywords: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)  # Functions, classes, etc.
    word_freq: dict[str, int] = field(default_factory=dict)
    tf_idf: dict[str, float] = field(default_factory=dict)


class SemanticAnalyzer:
    """
    Analyzes semantic relationships between files using:
    - Keyword extraction (TF-IDF)
    - Topic detection
    - Code entity extraction
    - Text similarity (cosine similarity)
    """

    # Common English stop words
    STOP_WORDS = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "as",
        "is",
        "was",
        "are",
        "were",
        "been",
        "be",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "need",
        "dare",
        "ought",
        "used",
        "it",
        "its",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "we",
        "they",
        "what",
        "which",
        "who",
        "whom",
        "when",
        "where",
        "why",
        "how",
        "all",
        "each",
        "every",
        "both",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "just",
        "also",
        "now",
        "here",
        "there",
        "then",
        "once",
        "if",
        "else",
        "elif",
        "while",
        "return",
        "import",
        "def",
        "class",
        "function",
        "const",
        "let",
        "var",
        "true",
        "false",
        "none",
        "null",
        "undefined",
        "async",
        "await",
        "try",
        "catch",
        "except",
        "finally",
        "throw",
        "raise",
        "new",
        "self",
    }

    # Common code tokens to filter
    CODE_NOISE = {
        "str",
        "int",
        "float",
        "bool",
        "list",
        "dict",
        "set",
        "tuple",
        "array",
        "object",
        "string",
        "number",
        "boolean",
        "any",
        "void",
        "type",
        "interface",
        "enum",
        "export",
        "default",
        "public",
        "private",
        "protected",
        "static",
        "readonly",
        "abstract",
        "extends",
        "implements",
    }

    # Topic indicators
    TOPIC_PATTERNS = {
        "api": r"\b(api|endpoint|route|rest|graphql|request|response)\b",
        "database": r"\b(database|db|sql|query|table|schema|model|orm)\b",
        "auth": r"\b(auth|login|logout|password|token|jwt|oauth|session)\b",
        "test": r"\b(test|spec|mock|stub|fixture|assert|expect)\b",
        "config": r"\b(config|setting|environment|env|option|parameter)\b",
        "ui": r"\b(component|render|view|template|style|css|html|dom)\b",
        "util": r"\b(util|helper|common|shared|lib|tool)\b",
        "error": r"\b(error|exception|catch|throw|handle|log)\b",
        "async": r"\b(async|await|promise|callback|event|emit)\b",
        "data": r"\b(data|fetch|load|save|store|cache|parse)\b",
        "search": r"\b(search|find|query|filter|match|index)\b",
        "ai": r"\b(model|train|predict|inference|neural|embedding|vector)\b",
    }

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self.file_semantics: dict[str, FileSemantics] = {}
        self.document_freq: Counter = Counter()  # For IDF calculation
        self.total_docs = 0

    def analyze_all(self, files: list[Path]) -> dict:
        """
        Analyze all files and compute semantic relationships.

        Returns dict with:
        - file_data: semantic info per file
        - clusters: groups of related files
        - code_doc_links: links between code and documentation
        - duplicates: potential duplicate files
        - warnings: analysis warnings
        """
        logger.info(f"Starting semantic analysis of {len(files)} files")

        # Phase 1: Extract text and keywords from each file
        for file_path in files:
            try:
                semantics = self._analyze_file(file_path)
                self.file_semantics[semantics.path] = semantics
            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")

        self.total_docs = len(self.file_semantics)

        # Phase 2: Calculate TF-IDF scores
        self._calculate_tfidf()

        # Phase 3: Find semantic clusters
        clusters = self._find_clusters()

        # Phase 4: Link code to documentation
        code_doc_links = self._link_code_to_docs()

        # Phase 5: Detect potential duplicates
        duplicates = self._detect_duplicates()

        # Phase 6: Generate warnings
        warnings = self._generate_warnings()

        # Build result
        result = {
            "file_data": {},
            "clusters": clusters,
            "code_doc_links": code_doc_links,
            "duplicates": duplicates,
            "warnings": warnings,
        }

        for path, sem in self.file_semantics.items():
            result["file_data"][path] = {
                "keywords": sem.keywords[:20],  # Top 20 keywords
                "topics": sem.topics,
                "entities": sem.entities[:30],
                "links": self._get_semantic_links(path),
            }

        return result

    def _analyze_file(self, file_path: Path) -> FileSemantics:
        """Extract semantic information from a single file"""
        rel_path = str(file_path.relative_to(self.repo_path))
        ext = file_path.suffix.lower()

        semantics = FileSemantics(
            path=rel_path, file_type=self._classify_file(file_path)
        )

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return semantics

        # Extract based on file type
        if ext == ".py":
            self._analyze_python(content, semantics)
        elif ext in {".js", ".jsx", ".ts", ".tsx"}:
            self._analyze_javascript(content, semantics)
        elif ext == ".md":
            self._analyze_markdown(content, semantics)
        elif ext == ".json":
            self._analyze_json(content, semantics)
        elif ext in {".yaml", ".yml"}:
            self._analyze_yaml(content, semantics)
        else:
            self._analyze_generic(content, semantics)

        # Extract topics
        semantics.topics = self._extract_topics(content)

        # Update document frequency
        for word in set(semantics.word_freq.keys()):
            self.document_freq[word] += 1

        return semantics

    def _classify_file(self, file_path: Path) -> str:
        """Classify file type"""
        ext = file_path.suffix.lower()
        name = file_path.name.lower()

        if ext in {".py", ".js", ".ts", ".jsx", ".tsx"}:
            return "code"
        elif ext in {".md", ".txt", ".rst"}:
            return "documentation"
        elif ext in {".json", ".yaml", ".yml", ".toml"}:
            return "config"
        elif "test" in name or "spec" in name:
            return "test"
        else:
            return "other"

    def _analyze_python(self, content: str, semantics: FileSemantics):
        """Analyze Python file"""
        # Extract function and class names
        func_pattern = r"def\s+(\w+)\s*\("
        class_pattern = r"class\s+(\w+)\s*[\(:]"

        semantics.entities.extend(re.findall(func_pattern, content))
        semantics.entities.extend(re.findall(class_pattern, content))

        # Extract docstrings
        docstring_pattern = r'"""(.*?)"""|\'\'\'(.*?)\'\'\''
        docstrings = re.findall(docstring_pattern, content, re.DOTALL)
        doc_text = " ".join([d[0] or d[1] for d in docstrings])

        # Extract comments
        comment_pattern = r"#\s*(.+)$"
        comments = re.findall(comment_pattern, content, re.MULTILINE)
        comment_text = " ".join(comments)

        # Combine text for analysis
        full_text = f"{doc_text} {comment_text} {' '.join(semantics.entities)}"
        semantics.word_freq = self._extract_word_freq(full_text)

    def _analyze_javascript(self, content: str, semantics: FileSemantics):
        """Analyze JavaScript/TypeScript file"""
        # Extract function names
        func_patterns = [
            r"function\s+(\w+)\s*\(",
            r"const\s+(\w+)\s*=\s*(?:async\s*)?\(",
            r"(?:export\s+)?(?:async\s+)?function\s+(\w+)",
            r"(\w+)\s*:\s*(?:async\s*)?\([^)]*\)\s*=>",
        ]

        for pattern in func_patterns:
            semantics.entities.extend(re.findall(pattern, content))

        # Extract class names
        class_pattern = r"class\s+(\w+)"
        semantics.entities.extend(re.findall(class_pattern, content))

        # Extract JSDoc comments
        jsdoc_pattern = r"/\*\*(.*?)\*/"
        jsdocs = re.findall(jsdoc_pattern, content, re.DOTALL)

        # Extract single-line comments
        comment_pattern = r"//\s*(.+)$"
        comments = re.findall(comment_pattern, content, re.MULTILINE)

        full_text = (
            f"{' '.join(jsdocs)} {' '.join(comments)} {' '.join(semantics.entities)}"
        )
        semantics.word_freq = self._extract_word_freq(full_text)

    def _analyze_markdown(self, content: str, semantics: FileSemantics):
        """Analyze Markdown file"""
        # Extract headings
        heading_pattern = r"^#+\s+(.+)$"
        headings = re.findall(heading_pattern, content, re.MULTILINE)
        semantics.entities.extend(headings)

        # Remove code blocks for text analysis
        content_no_code = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        content_no_code = re.sub(r"`[^`]+`", "", content_no_code)

        semantics.word_freq = self._extract_word_freq(content_no_code)

    def _analyze_json(self, content: str, semantics: FileSemantics):
        """Analyze JSON file"""
        try:
            import json

            data = json.loads(content)

            # Extract all keys recursively
            keys = self._extract_json_keys(data)
            semantics.entities.extend(keys)

            # Extract string values
            values = self._extract_json_values(data)
            semantics.word_freq = self._extract_word_freq(" ".join(values))

        except Exception:
            semantics.word_freq = self._extract_word_freq(content)

    def _analyze_yaml(self, content: str, semantics: FileSemantics):
        """Analyze YAML file"""
        try:
            import yaml

            data = yaml.safe_load(content)

            if isinstance(data, dict):
                keys = self._extract_json_keys(data)
                semantics.entities.extend(keys)
                values = self._extract_json_values(data)
                semantics.word_freq = self._extract_word_freq(" ".join(values))
        except Exception:
            semantics.word_freq = self._extract_word_freq(content)

    def _analyze_generic(self, content: str, semantics: FileSemantics):
        """Generic text analysis"""
        semantics.word_freq = self._extract_word_freq(content)

    def _extract_json_keys(self, data, depth: int = 0) -> list[str]:
        """Recursively extract all keys from JSON/dict"""
        if depth > 10:
            return []

        keys = []
        if isinstance(data, dict):
            for key, value in data.items():
                keys.append(str(key))
                keys.extend(self._extract_json_keys(value, depth + 1))
        elif isinstance(data, list):
            for item in data:
                keys.extend(self._extract_json_keys(item, depth + 1))

        return keys

    def _extract_json_values(self, data, depth: int = 0) -> list[str]:
        """Recursively extract string values from JSON/dict"""
        if depth > 10:
            return []

        values = []
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, str):
                    values.append(value)
                else:
                    values.extend(self._extract_json_values(value, depth + 1))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    values.append(item)
                else:
                    values.extend(self._extract_json_values(item, depth + 1))

        return values

    def _extract_word_freq(self, text: str) -> dict[str, int]:
        """Extract word frequencies from text"""
        # Normalize text
        text = text.lower()

        # Split camelCase and snake_case
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
        text = text.replace("_", " ").replace("-", " ")

        # Extract words
        words = re.findall(r"\b[a-z]{3,}\b", text)

        # Filter stop words and noise
        words = [
            w for w in words if w not in self.STOP_WORDS and w not in self.CODE_NOISE
        ]

        return Counter(words)

    def _extract_topics(self, content: str) -> list[str]:
        """Extract topics from content using pattern matching"""
        content_lower = content.lower()
        topics = []

        for topic, pattern in self.TOPIC_PATTERNS.items():
            if re.search(pattern, content_lower):
                topics.append(topic)

        return topics

    def _calculate_tfidf(self):
        """Calculate TF-IDF scores for all documents"""
        for path, semantics in self.file_semantics.items():
            total_words = sum(semantics.word_freq.values()) or 1

            for word, freq in semantics.word_freq.items():
                tf = freq / total_words
                idf = math.log((self.total_docs + 1) / (self.document_freq[word] + 1))
                semantics.tf_idf[word] = tf * idf

            # Extract top keywords by TF-IDF
            sorted_keywords = sorted(
                semantics.tf_idf.items(), key=lambda x: x[1], reverse=True
            )
            semantics.keywords = [word for word, score in sorted_keywords[:30]]

    def _cosine_similarity(self, sem1: FileSemantics, sem2: FileSemantics) -> float:
        """Calculate cosine similarity between two files"""
        words1 = set(sem1.tf_idf.keys())
        words2 = set(sem2.tf_idf.keys())

        common_words = words1 & words2
        if not common_words:
            return 0.0

        # Calculate dot product
        dot_product = sum(sem1.tf_idf[w] * sem2.tf_idf[w] for w in common_words)

        # Calculate magnitudes
        mag1 = math.sqrt(sum(v**2 for v in sem1.tf_idf.values()))
        mag2 = math.sqrt(sum(v**2 for v in sem2.tf_idf.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def _topic_overlap(self, sem1: FileSemantics, sem2: FileSemantics) -> float:
        """Calculate topic overlap between two files"""
        if not sem1.topics or not sem2.topics:
            return 0.0

        common = set(sem1.topics) & set(sem2.topics)
        total = set(sem1.topics) | set(sem2.topics)

        return len(common) / len(total) if total else 0.0

    def _get_semantic_links(self, file_path: str) -> list[dict]:
        """Get semantic links for a file"""
        links = []
        source_sem = self.file_semantics.get(file_path)

        if not source_sem:
            return links

        for other_path, other_sem in self.file_semantics.items():
            if other_path == file_path:
                continue

            similarity = self._cosine_similarity(source_sem, other_sem)
            topic_overlap = self._topic_overlap(source_sem, other_sem)

            # Combined score
            score = (similarity * 0.7) + (topic_overlap * 0.3)

            if score > 0.3:  # Threshold for relevance
                links.append(
                    {
                        "target": other_path,
                        "similarity": round(similarity, 3),
                        "topic_overlap": round(topic_overlap, 3),
                        "score": round(score, 3),
                    }
                )

        # Sort by score
        links.sort(key=lambda x: x["score"], reverse=True)
        return links[:10]  # Top 10 links

    def _find_clusters(self) -> list[dict]:
        """Find clusters of semantically related files"""
        clusters = []
        assigned = set()

        # Sort files by number of topics (more specific first)
        sorted_files = sorted(
            self.file_semantics.items(), key=lambda x: len(x[1].topics), reverse=True
        )

        for path, semantics in sorted_files:
            if path in assigned:
                continue

            # Find similar files
            cluster_files = [path]
            assigned.add(path)

            for other_path, other_sem in self.file_semantics.items():
                if other_path in assigned:
                    continue

                similarity = self._cosine_similarity(semantics, other_sem)
                topic_overlap = self._topic_overlap(semantics, other_sem)

                if similarity > 0.5 or topic_overlap > 0.5:
                    cluster_files.append(other_path)
                    assigned.add(other_path)

            if len(cluster_files) > 1:
                # Determine cluster topic
                all_topics = []
                for f in cluster_files:
                    all_topics.extend(self.file_semantics[f].topics)

                topic_counts = Counter(all_topics)
                main_topic = (
                    topic_counts.most_common(1)[0][0] if topic_counts else "misc"
                )

                clusters.append(
                    {
                        "topic": main_topic,
                        "files": cluster_files,
                        "size": len(cluster_files),
                    }
                )

        return sorted(clusters, key=lambda x: x["size"], reverse=True)

    def _link_code_to_docs(self) -> list[dict]:
        """Find links between code and documentation files"""
        links = []

        code_files = {
            p: s for p, s in self.file_semantics.items() if s.file_type == "code"
        }
        doc_files = {
            p: s
            for p, s in self.file_semantics.items()
            if s.file_type == "documentation"
        }

        for doc_path, doc_sem in doc_files.items():
            doc_name = Path(doc_path).stem.lower()
            best_match = None
            best_score = 0

            for code_path, code_sem in code_files.items():
                code_name = Path(code_path).stem.lower()

                # Check name similarity
                name_match = doc_name in code_name or code_name in doc_name

                # Check semantic similarity
                similarity = self._cosine_similarity(doc_sem, code_sem)

                # Check entity mentions
                entity_mentions = sum(
                    1
                    for e in code_sem.entities
                    if e.lower() in " ".join(doc_sem.word_freq.keys())
                )

                score = (
                    (0.3 if name_match else 0)
                    + (similarity * 0.5)
                    + (min(entity_mentions, 5) * 0.04)
                )

                if score > best_score:
                    best_score = score
                    best_match = code_path

            if best_match and best_score > 0.3:
                links.append(
                    {
                        "doc_file": doc_path,
                        "code_file": best_match,
                        "score": round(best_score, 3),
                        "type": "doc_to_code",
                    }
                )
            elif not best_match or best_score < 0.2:
                # Documentation without clear code link
                links.append(
                    {
                        "doc_file": doc_path,
                        "type": "doc_without_code",
                        "topic": doc_sem.topics[0] if doc_sem.topics else "unknown",
                        "expected": f"Code implementing {doc_name}",
                    }
                )

        # Find code without documentation
        documented_code = {link["code_file"] for link in links if link.get("code_file")}

        for code_path in code_files:
            if code_path not in documented_code:
                code_sem = self.file_semantics[code_path]
                if len(code_sem.entities) > 5:  # Significant code file
                    links.append(
                        {
                            "code_file": code_path,
                            "type": "code_without_doc",
                            "entities_count": len(code_sem.entities),
                        }
                    )

        return links

    def _detect_duplicates(self) -> list[dict]:
        """Detect potential duplicate files"""
        duplicates = []
        checked = set()

        files = list(self.file_semantics.items())

        for i, (path1, sem1) in enumerate(files):
            if path1 in checked:
                continue

            for path2, sem2 in files[i + 1 :]:
                if path2 in checked:
                    continue

                # High similarity threshold for duplicates
                similarity = self._cosine_similarity(sem1, sem2)

                if similarity > 0.85:
                    # Check if same file type
                    if sem1.file_type == sem2.file_type:
                        duplicates.append(
                            {
                                "file1": path1,
                                "file2": path2,
                                "similarity": round(similarity, 3),
                                "file_type": sem1.file_type,
                            }
                        )
                        checked.add(path2)

        return duplicates

    def _generate_warnings(self) -> list[str]:
        """Generate warnings about potential issues"""
        warnings = []

        # Warning: Files with no keywords
        empty_files = [p for p, s in self.file_semantics.items() if not s.keywords]
        if empty_files:
            warnings.append(
                f"Found {len(empty_files)} files with no extractable content"
            )

        # Warning: Isolated files (no topic overlap with anything)
        for path, sem in self.file_semantics.items():
            has_overlap = False
            for other_path, other_sem in self.file_semantics.items():
                if path != other_path:
                    if self._topic_overlap(sem, other_sem) > 0.2:
                        has_overlap = True
                        break
            if not has_overlap and sem.file_type == "code":
                warnings.append(f"File '{path}' has no topic overlap with other files")

        return warnings


if __name__ == "__main__":
    import sys

    repo_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    analyzer = SemanticAnalyzer(repo_path)

    # Find files
    files = []
    for ext in ["*.py", "*.js", "*.md", "*.json"]:
        files.extend(repo_path.rglob(ext))

    results = analyzer.analyze_all(files)

    print("Semantic Analysis Results:")
    print(f"Files analyzed: {len(results['file_data'])}")
    print(f"Clusters found: {len(results['clusters'])}")
    print(f"Code-Doc links: {len(results['code_doc_links'])}")
    print(f"Potential duplicates: {len(results['duplicates'])}")
    print(f"Warnings: {len(results['warnings'])}")
