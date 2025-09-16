"""
Search and metadata system for SnapshotPlot collections.

This module provides comprehensive search, indexing, and metadata management
for large collections of snapshots, enabling users to find and organize their analysis work.
"""

import sqlite3
import json
import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import hashlib


@dataclass
class SnapshotIndex:
    """Index entry for a snapshot."""
    id: str
    timestamp: str
    title: Optional[str]
    author: Optional[str]
    filename: str
    function_name: Optional[str]
    description: Optional[str]
    tags: List[str]
    code_content: str
    plot_paths: List[str]
    file_size_bytes: int
    creation_date: datetime
    last_modified: datetime
    metadata: Dict[str, Any]


class SearchQuery:
    """Represents a search query with multiple criteria."""
    
    def __init__(self):
        self.text_query: Optional[str] = None
        self.author_filter: Optional[str] = None
        self.tag_filters: List[str] = []
        self.date_range: Optional[Tuple[date, date]] = None
        self.filename_pattern: Optional[str] = None
        self.has_plots: Optional[bool] = None
        self.min_file_size: Optional[int] = None
        self.max_file_size: Optional[int] = None
    
    def with_text(self, query: str) -> 'SearchQuery':
        """Add text search query."""
        self.text_query = query
        return self
    
    def with_author(self, author: str) -> 'SearchQuery':
        """Filter by author."""
        self.author_filter = author
        return self
    
    def with_tags(self, tags: Union[str, List[str]]) -> 'SearchQuery':
        """Filter by tags."""
        if isinstance(tags, str):
            self.tag_filters = [tags]
        else:
            self.tag_filters = tags
        return self
    
    def with_date_range(self, start_date: date, end_date: date) -> 'SearchQuery':
        """Filter by date range."""
        self.date_range = (start_date, end_date)
        return self
    
    def with_filename_pattern(self, pattern: str) -> 'SearchQuery':
        """Filter by filename pattern (supports wildcards)."""
        self.filename_pattern = pattern
        return self
    
    def with_plots(self, has_plots: bool = True) -> 'SearchQuery':
        """Filter by whether snapshots have plots."""
        self.has_plots = has_plots
        return self
    
    def with_file_size_range(self, min_size: int = None, max_size: int = None) -> 'SearchQuery':
        """Filter by file size range."""
        self.min_file_size = min_size
        self.max_file_size = max_size
        return self


class SearchIndex(ABC):
    """Abstract base class for search index implementations."""
    
    @abstractmethod
    def add_snapshot(self, snapshot: SnapshotIndex) -> None:
        """Add a snapshot to the index."""
        pass
    
    @abstractmethod
    def update_snapshot(self, snapshot: SnapshotIndex) -> None:
        """Update an existing snapshot in the index."""
        pass
    
    @abstractmethod
    def remove_snapshot(self, snapshot_id: str) -> None:
        """Remove a snapshot from the index."""
        pass
    
    @abstractmethod
    def search(self, query: SearchQuery, limit: int = 50, offset: int = 0) -> List[SnapshotIndex]:
        """Search for snapshots matching the query."""
        pass
    
    @abstractmethod
    def get_snapshot(self, snapshot_id: str) -> Optional[SnapshotIndex]:
        """Get a specific snapshot by ID."""
        pass
    
    @abstractmethod
    def get_all_tags(self) -> List[str]:
        """Get all unique tags in the index."""
        pass
    
    @abstractmethod
    def get_all_authors(self) -> List[str]:
        """Get all unique authors in the index."""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        pass


class SQLiteSearchIndex(SearchIndex):
    """SQLite-based search index implementation."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "snapshots.db"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with proper schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    title TEXT,
                    author TEXT,
                    filename TEXT NOT NULL,
                    function_name TEXT,
                    description TEXT,
                    code_content TEXT NOT NULL,
                    plot_paths TEXT,  -- JSON array
                    file_size_bytes INTEGER,
                    creation_date TEXT,
                    last_modified TEXT,
                    metadata TEXT  -- JSON object
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshot_tags (
                    snapshot_id TEXT,
                    tag TEXT,
                    FOREIGN KEY (snapshot_id) REFERENCES snapshots (id),
                    PRIMARY KEY (snapshot_id, tag)
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_author ON snapshots (author)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON snapshots (timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_filename ON snapshots (filename)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_creation_date ON snapshots (creation_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tags ON snapshot_tags (tag)")
            
            # Full-text search index
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS snapshots_fts USING fts5(
                    id,
                    title,
                    description,
                    code_content,
                    author,
                    filename,
                    function_name
                )
            """)
            
            conn.commit()
    
    def add_snapshot(self, snapshot: SnapshotIndex) -> None:
        """Add a snapshot to the index."""
        with sqlite3.connect(self.db_path) as conn:
            # Insert main snapshot record
            conn.execute("""
                INSERT OR REPLACE INTO snapshots 
                (id, timestamp, title, author, filename, function_name, description, 
                 code_content, plot_paths, file_size_bytes, creation_date, last_modified, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot.id,
                snapshot.timestamp,
                snapshot.title,
                snapshot.author,
                snapshot.filename,
                snapshot.function_name,
                snapshot.description,
                snapshot.code_content,
                json.dumps(snapshot.plot_paths),
                snapshot.file_size_bytes,
                snapshot.creation_date.isoformat(),
                snapshot.last_modified.isoformat(),
                json.dumps(snapshot.metadata)
            ))
            
            # Insert tags
            conn.execute("DELETE FROM snapshot_tags WHERE snapshot_id = ?", (snapshot.id,))
            for tag in snapshot.tags:
                conn.execute(
                    "INSERT INTO snapshot_tags (snapshot_id, tag) VALUES (?, ?)",
                    (snapshot.id, tag)
                )
            
            # Update full-text search index
            conn.execute("""
                INSERT OR REPLACE INTO snapshots_fts 
                (id, title, description, code_content, author, filename, function_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot.id,
                snapshot.title or '',
                snapshot.description or '',
                snapshot.code_content,
                snapshot.author or '',
                snapshot.filename,
                snapshot.function_name or ''
            ))
            
            conn.commit()
    
    def update_snapshot(self, snapshot: SnapshotIndex) -> None:
        """Update an existing snapshot."""
        snapshot.last_modified = datetime.now()
        self.add_snapshot(snapshot)  # add_snapshot handles updates via REPLACE
    
    def remove_snapshot(self, snapshot_id: str) -> None:
        """Remove a snapshot from the index."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM snapshots WHERE id = ?", (snapshot_id,))
            conn.execute("DELETE FROM snapshot_tags WHERE snapshot_id = ?", (snapshot_id,))
            conn.execute("DELETE FROM snapshots_fts WHERE id = ?", (snapshot_id,))
            conn.commit()
    
    def search(self, query: SearchQuery, limit: int = 50, offset: int = 0) -> List[SnapshotIndex]:
        """Search for snapshots matching the query."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Build the SQL query
            where_clauses = []
            params = []
            joins = []
            
            # Text search using FTS
            if query.text_query:
                joins.append("JOIN snapshots_fts ON snapshots.id = snapshots_fts.id")
                where_clauses.append("snapshots_fts MATCH ?")
                params.append(query.text_query)
            
            # Author filter
            if query.author_filter:
                where_clauses.append("author = ?")
                params.append(query.author_filter)
            
            # Tag filters
            if query.tag_filters:
                for i, tag in enumerate(query.tag_filters):
                    alias = f"st_{i}"
                    joins.append(f"JOIN snapshot_tags {alias} ON snapshots.id = {alias}.snapshot_id")
                    where_clauses.append(f"{alias}.tag = ?")
                    params.append(tag)
            
            # Date range filter
            if query.date_range:
                where_clauses.append("creation_date BETWEEN ? AND ?")
                params.extend([
                    query.date_range[0].isoformat(),
                    query.date_range[1].isoformat()
                ])
            
            # Filename pattern filter
            if query.filename_pattern:
                # Convert wildcard pattern to SQL LIKE pattern
                sql_pattern = query.filename_pattern.replace('*', '%').replace('?', '_')
                where_clauses.append("filename LIKE ?")
                params.append(sql_pattern)
            
            # Plot existence filter
            if query.has_plots is not None:
                if query.has_plots:
                    where_clauses.append("plot_paths != '[]' AND plot_paths IS NOT NULL")
                else:
                    where_clauses.append("(plot_paths = '[]' OR plot_paths IS NULL)")
            
            # File size filters
            if query.min_file_size is not None:
                where_clauses.append("file_size_bytes >= ?")
                params.append(query.min_file_size)
            
            if query.max_file_size is not None:
                where_clauses.append("file_size_bytes <= ?")
                params.append(query.max_file_size)
            
            # Build final query
            base_query = "SELECT DISTINCT snapshots.* FROM snapshots"
            if joins:
                base_query += " " + " ".join(joins)
            
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
            
            base_query += " ORDER BY creation_date DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # Execute query
            cursor = conn.execute(base_query, params)
            rows = cursor.fetchall()
            
            # Convert to SnapshotIndex objects
            snapshots = []
            for row in rows:
                snapshot = SnapshotIndex(
                    id=row['id'],
                    timestamp=row['timestamp'],
                    title=row['title'],
                    author=row['author'],
                    filename=row['filename'],
                    function_name=row['function_name'],
                    description=row['description'],
                    tags=self._get_snapshot_tags(conn, row['id']),
                    code_content=row['code_content'],
                    plot_paths=json.loads(row['plot_paths'] or '[]'),
                    file_size_bytes=row['file_size_bytes'],
                    creation_date=datetime.fromisoformat(row['creation_date']),
                    last_modified=datetime.fromisoformat(row['last_modified']),
                    metadata=json.loads(row['metadata'] or '{}')
                )
                snapshots.append(snapshot)
            
            return snapshots
    
    def _get_snapshot_tags(self, conn: sqlite3.Connection, snapshot_id: str) -> List[str]:
        """Get tags for a specific snapshot."""
        cursor = conn.execute(
            "SELECT tag FROM snapshot_tags WHERE snapshot_id = ? ORDER BY tag",
            (snapshot_id,)
        )
        return [row[0] for row in cursor.fetchall()]
    
    def get_snapshot(self, snapshot_id: str) -> Optional[SnapshotIndex]:
        """Get a specific snapshot by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM snapshots WHERE id = ?",
                (snapshot_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return SnapshotIndex(
                id=row['id'],
                timestamp=row['timestamp'],
                title=row['title'],
                author=row['author'],
                filename=row['filename'],
                function_name=row['function_name'],
                description=row['description'],
                tags=self._get_snapshot_tags(conn, row['id']),
                code_content=row['code_content'],
                plot_paths=json.loads(row['plot_paths'] or '[]'),
                file_size_bytes=row['file_size_bytes'],
                creation_date=datetime.fromisoformat(row['creation_date']),
                last_modified=datetime.fromisoformat(row['last_modified']),
                metadata=json.loads(row['metadata'] or '{}')
            )
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags in the index."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT DISTINCT tag FROM snapshot_tags ORDER BY tag"
            )
            return [row[0] for row in cursor.fetchall()]
    
    def get_all_authors(self) -> List[str]:
        """Get all unique authors in the index."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT DISTINCT author FROM snapshots WHERE author IS NOT NULL ORDER BY author"
            )
            return [row[0] for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Basic counts
            total_snapshots = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
            unique_authors = conn.execute(
                "SELECT COUNT(DISTINCT author) FROM snapshots WHERE author IS NOT NULL"
            ).fetchone()[0]
            unique_tags = conn.execute("SELECT COUNT(DISTINCT tag) FROM snapshot_tags").fetchone()[0]
            
            # Date range
            date_range = conn.execute(
                "SELECT MIN(creation_date), MAX(creation_date) FROM snapshots"
            ).fetchone()
            
            # File size statistics
            size_stats = conn.execute("""
                SELECT 
                    AVG(file_size_bytes) as avg_size,
                    MIN(file_size_bytes) as min_size,
                    MAX(file_size_bytes) as max_size,
                    SUM(file_size_bytes) as total_size
                FROM snapshots 
                WHERE file_size_bytes IS NOT NULL
            """).fetchone()
            
            # Most common tags
            top_tags = conn.execute("""
                SELECT tag, COUNT(*) as count 
                FROM snapshot_tags 
                GROUP BY tag 
                ORDER BY count DESC 
                LIMIT 10
            """).fetchall()
            
            # Most active authors
            top_authors = conn.execute("""
                SELECT author, COUNT(*) as count 
                FROM snapshots 
                WHERE author IS NOT NULL
                GROUP BY author 
                ORDER BY count DESC 
                LIMIT 10
            """).fetchall()
            
            return {
                'total_snapshots': total_snapshots,
                'unique_authors': unique_authors,
                'unique_tags': unique_tags,
                'date_range': {
                    'earliest': date_range[0],
                    'latest': date_range[1]
                },
                'file_size': {
                    'average_bytes': size_stats[0] if size_stats[0] else 0,
                    'min_bytes': size_stats[1] if size_stats[1] else 0,
                    'max_bytes': size_stats[2] if size_stats[2] else 0,
                    'total_bytes': size_stats[3] if size_stats[3] else 0
                },
                'top_tags': [{'tag': tag, 'count': count} for tag, count in top_tags],
                'top_authors': [{'author': author, 'count': count} for author, count in top_authors]
            }


class SnapshotMetadataManager:
    """Manages metadata extraction and indexing for snapshots."""
    
    def __init__(self, index: SearchIndex):
        self.index = index
    
    def index_snapshot_directory(self, snapshot_dir: Path) -> List[str]:
        """
        Index all snapshots in a directory.
        
        Returns:
            List of indexed snapshot IDs
        """
        indexed_ids = []
        
        # Find all snapshot directories (format: snapshot_*)
        snapshot_dirs = [d for d in snapshot_dir.iterdir() 
                        if d.is_dir() and d.name.startswith('snapshot_')]
        
        for snap_dir in snapshot_dirs:
            try:
                snapshot_id = self._index_single_snapshot(snap_dir)
                if snapshot_id:
                    indexed_ids.append(snapshot_id)
            except Exception as e:
                warnings.warn(f"Failed to index {snap_dir}: {e}")
        
        return indexed_ids
    
    def _index_single_snapshot(self, snapshot_dir: Path) -> Optional[str]:
        """Index a single snapshot directory."""
        # Find files in the snapshot directory
        code_files = list(snapshot_dir.glob("*_code.py"))
        html_files = list(snapshot_dir.glob("*_snapshot.html"))
        plot_files = list(snapshot_dir.glob("*_plot.*"))
        
        if not code_files:
            return None
        
        code_file = code_files[0]  # Take the first code file
        timestamp = self._extract_timestamp_from_filename(code_file.name)
        
        # Read code content
        try:
            code_content = code_file.read_text(encoding='utf-8')
        except Exception:
            return None
        
        # Extract metadata from HTML file if available
        metadata = {}
        if html_files:
            metadata = self._extract_metadata_from_html(html_files[0])
        
        # Generate snapshot ID
        snapshot_id = self._generate_snapshot_id(snapshot_dir, timestamp)
        
        # Calculate file size
        total_size = sum(f.stat().st_size for f in snapshot_dir.iterdir() if f.is_file())
        
        # Create snapshot index entry
        snapshot_index = SnapshotIndex(
            id=snapshot_id,
            timestamp=timestamp,
            title=metadata.get('title'),
            author=metadata.get('author'),
            filename=metadata.get('filename', code_file.name),
            function_name=metadata.get('function_name'),
            description=metadata.get('description'),
            tags=metadata.get('tags', []),
            code_content=code_content,
            plot_paths=[str(p.relative_to(snapshot_dir)) for p in plot_files],
            file_size_bytes=total_size,
            creation_date=datetime.fromtimestamp(code_file.stat().st_ctime),
            last_modified=datetime.fromtimestamp(code_file.stat().st_mtime),
            metadata=metadata
        )
        
        self.index.add_snapshot(snapshot_index)
        return snapshot_id
    
    def _extract_timestamp_from_filename(self, filename: str) -> str:
        """Extract timestamp from snapshot filename."""
        # Pattern: YYYYMMDD_HHMMSS_mmm_code.py
        match = re.match(r'(\d{8}_\d{6}_\d{3})_code\.py', filename)
        if match:
            return match.group(1)
        return filename.replace('_code.py', '')
    
    def _extract_metadata_from_html(self, html_file: Path) -> Dict[str, Any]:
        """Extract metadata from HTML file."""
        try:
            html_content = html_file.read_text(encoding='utf-8')
            
            # Simple regex-based extraction (could be improved with BeautifulSoup)
            metadata = {}
            
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
            if title_match:
                metadata['title'] = title_match.group(1).strip()
            
            # Extract metadata from meta tags
            meta_patterns = [
                (r'<meta name="author" content="(.*?)"', 'author'),
                (r'<meta name="description" content="(.*?)"', 'description'),
                (r'<meta name="keywords" content="(.*?)"', 'tags'),
            ]
            
            for pattern, key in meta_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if key == 'tags':
                        metadata[key] = [tag.strip() for tag in value.split(',')]
                    else:
                        metadata[key] = value
            
            return metadata
            
        except Exception:
            return {}
    
    def _generate_snapshot_id(self, snapshot_dir: Path, timestamp: str) -> str:
        """Generate a unique snapshot ID."""
        # Use directory path + timestamp for uniqueness
        identifier = f"{snapshot_dir.name}_{timestamp}"
        return hashlib.md5(identifier.encode()).hexdigest()[:16]


class SnapshotSearchManager:
    """High-level search manager for SnapshotPlot."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.index_dir = data_dir / ".snapshotplot"
        self.index = SQLiteSearchIndex(self.index_dir)
        self.metadata_manager = SnapshotMetadataManager(self.index)
    
    def rebuild_index(self, snapshot_directories: List[Path] = None) -> Dict[str, Any]:
        """
        Rebuild the search index from snapshot directories.
        
        Args:
            snapshot_directories: List of directories to index (defaults to finding all)
            
        Returns:
            Indexing statistics
        """
        if snapshot_directories is None:
            snapshot_directories = self._find_snapshot_directories()
        
        total_indexed = 0
        errors = []
        
        for snap_dir in snapshot_directories:
            try:
                indexed_ids = self.metadata_manager.index_snapshot_directory(snap_dir)
                total_indexed += len(indexed_ids)
            except Exception as e:
                errors.append(f"{snap_dir}: {e}")
        
        return {
            'total_indexed': total_indexed,
            'directories_processed': len(snapshot_directories),
            'errors': errors,
            'index_path': str(self.index_path)
        }
    
    def _find_snapshot_directories(self) -> List[Path]:
        """Find all snapshot directories in the data directory."""
        snapshot_dirs = []
        
        # Look for directories matching snapshot patterns
        for item in self.data_dir.rglob("snapshot_*"):
            if item.is_dir():
                snapshot_dirs.append(item)
        
        return snapshot_dirs
    
    def search_snapshots(self, search_text: str = None, **filters) -> List[SnapshotIndex]:
        """
        Convenient search method with common filters.
        
        Args:
            search_text: Text to search in code, title, description
            **filters: Additional filters (author, tags, date_range, etc.)
        """
        query = SearchQuery()
        
        if search_text:
            query.with_text(search_text)
        
        if 'author' in filters:
            query.with_author(filters['author'])
        
        if 'tags' in filters:
            query.with_tags(filters['tags'])
        
        if 'date_range' in filters:
            query.with_date_range(*filters['date_range'])
        
        if 'filename_pattern' in filters:
            query.with_filename_pattern(filters['filename_pattern'])
        
        if 'has_plots' in filters:
            query.with_plots(filters['has_plots'])
        
        return self.index.search(query, limit=filters.get('limit', 50))
    
    def get_search_suggestions(self, partial_query: str) -> Dict[str, List[str]]:
        """Get search suggestions based on partial query."""
        suggestions = {
            'tags': [],
            'authors': [],
            'functions': []
        }
        
        # Get tag suggestions
        all_tags = self.index.get_all_tags()
        suggestions['tags'] = [tag for tag in all_tags 
                              if partial_query.lower() in tag.lower()][:10]
        
        # Get author suggestions  
        all_authors = self.index.get_all_authors()
        suggestions['authors'] = [author for author in all_authors 
                                 if partial_query.lower() in author.lower()][:10]
        
        # Get function name suggestions from metadata
        with sqlite3.connect(self.index.db_path) as conn:
            cursor = conn.execute("""
                SELECT DISTINCT function_name 
                FROM snapshots 
                WHERE function_name IS NOT NULL 
                AND function_name LIKE ?
                ORDER BY function_name
                LIMIT 10
            """, (f"%{partial_query}%",))
            
            suggestions['functions'] = [row[0] for row in cursor.fetchall()]
        
        return suggestions
    
    def create_collection_summary(self, tag: str = None, author: str = None) -> Dict[str, Any]:
        """Create a summary of snapshots for a collection."""
        query = SearchQuery()
        if tag:
            query.with_tags([tag])
        if author:
            query.with_author(author)
        
        snapshots = self.index.search(query, limit=1000)  # Large limit for analysis
        
        if not snapshots:
            return {'total': 0, 'snapshots': []}
        
        # Analyze snapshots
        total_plots = sum(len(s.plot_paths) for s in snapshots)
        total_size = sum(s.file_size_bytes for s in snapshots)
        date_range = (
            min(s.creation_date for s in snapshots),
            max(s.creation_date for s in snapshots)
        )
        
        # Group by time periods
        monthly_counts = {}
        for snapshot in snapshots:
            month_key = snapshot.creation_date.strftime('%Y-%m')
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
        
        return {
            'total': len(snapshots),
            'total_plots': total_plots,
            'total_size_bytes': total_size,
            'date_range': {
                'earliest': date_range[0].isoformat(),
                'latest': date_range[1].isoformat()
            },
            'monthly_activity': monthly_counts,
            'recent_snapshots': [
                {
                    'id': s.id,
                    'title': s.title or s.function_name,
                    'date': s.creation_date.isoformat(),
                    'author': s.author
                }
                for s in sorted(snapshots, key=lambda x: x.creation_date, reverse=True)[:10]
            ]
        }


# Convenience functions

def create_search_manager(data_dir: Path = None) -> SnapshotSearchManager:
    """Create a search manager for the current or specified directory."""
    if data_dir is None:
        data_dir = Path.cwd()
    
    return SnapshotSearchManager(data_dir)


def quick_search(search_text: str, data_dir: Path = None) -> List[SnapshotIndex]:
    """Quick search function for interactive use."""
    manager = create_search_manager(data_dir)
    return manager.search_snapshots(search_text)


def index_current_directory() -> Dict[str, Any]:
    """Index all snapshots in the current directory."""
    manager = create_search_manager()
    return manager.rebuild_index()