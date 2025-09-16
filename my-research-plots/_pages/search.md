---
title: Search and Organization
description: Find and organize your analyses with powerful search and tagging features
layout: default
permalink: /search/
---

# Search and Organization

SnapshotPlot provides powerful search and organization features to help you find and manage your analyses as your research grows. From simple tagging to full-text search across thousands of snapshots.

## Search Features

### 🔍 Full-Text Search
- **Content Search**: Search through code, titles, descriptions, and notes
- **Tag-Based Filtering**: Filter by one or multiple tags
- **Author Search**: Find analyses by specific team members
- **Date Range Filtering**: Search within specific time periods
- **Smart Ranking**: Results ranked by relevance and recency

### 🏷️ Tagging System
- **Hierarchical Tags**: Use dots for organization (`ml.classification`, `data.preprocessing`)
- **Auto-Completion**: Tag suggestions based on existing tags
- **Visual Organization**: Color-coded tags in the interface
- **Bulk Operations**: Apply tags to multiple snapshots

## Enabling Search

### Basic Setup

```python
from snapshotplot import snapshot

# Enable search for individual snapshots
@snapshot(
    title="Customer Analysis",
    tags=["customers", "segmentation", "ml"],
    enable_search=True  # Add to search index
)
def customer_analysis():
    # Your analysis code
    pass
```

### Database Location

Search data is stored in SQLite databases:
```
snapshots/
├── .snapshotplot/
│   └── snapshots.db        # Search database
└── snapshot_*/
    └── analysis files...
```

## Search Interface

### Programmatic Search

```python
from snapshotplot.core.search_system import SnapshotSearchManager
from pathlib import Path

# Initialize search manager
search_manager = SnapshotSearchManager(Path('snapshots'))

# Text search
results = search_manager.search_snapshots('machine learning')
print(f"Found {len(results)} ML analyses")

# Tag filtering
ml_results = search_manager.search_snapshots(tags=['ml', 'classification'])

# Combined search
results = search_manager.search_snapshots(
    query='customer churn',
    tags=['ml'],
    author='Data Science Team'
)

# Display results
for result in results:
    print(f"{result.title} - {result.author} - {result.score:.2f}")
```

### Web Interface Search

The static site generator includes a powerful client-side search:

```javascript
// Search is automatically available on generated sites
// Use the search bar in the header or visit /search.html

// Search features:
// - Instant results as you type
// - Fuzzy matching for typos
// - Keyboard navigation (arrow keys, enter)
// - Tag filtering by clicking tags
// - Shareable search URLs
```

## Organization Strategies

### Tagging Conventions

Establish consistent tagging patterns for your team:

```python
# By analysis type
ANALYSIS_TAGS = {
    'EXPLORATORY': ['eda', 'exploration', 'data-quality'],
    'MODELING': ['ml', 'modeling', 'prediction', 'training'],
    'EVALUATION': ['evaluation', 'metrics', 'performance', 'validation'],
    'BUSINESS': ['business', 'kpi', 'insights', 'revenue'],
    'EXPERIMENTAL': ['experiment', 'ab-test', 'hypothesis']
}

# By domain
DOMAIN_TAGS = {
    'FINANCE': ['finance', 'trading', 'risk', 'portfolio'],
    'MARKETING': ['marketing', 'campaigns', 'conversion', 'attribution'],
    'PRODUCT': ['product', 'features', 'usage', 'retention'],
    'OPERATIONS': ['operations', 'efficiency', 'costs', 'supply-chain']
}

# By methodology
METHOD_TAGS = {
    'STATS': ['statistics', 'hypothesis-testing', 'correlation'],
    'ML': ['ml', 'classification', 'regression', 'clustering'],
    'TIME_SERIES': ['time-series', 'forecasting', 'trends'],
    'VISUALIZATION': ['visualization', 'dashboard', 'reporting']
}

# Example usage
@snapshot(
    title="Customer Churn Prediction",
    tags=ANALYSIS_TAGS['MODELING'] + DOMAIN_TAGS['MARKETING'] + ['churn'],
    enable_search=True
)
def churn_analysis():
    pass
```

### Hierarchical Organization

Use dot notation for hierarchical tags:

```python
@snapshot(
    tags=[
        'ml.classification.random-forest',  # Method hierarchy
        'data.customers.b2b',               # Data hierarchy  
        'project.alpha.phase-1',            # Project hierarchy
        'team.data-science.ml-ops'          # Team hierarchy
    ],
    enable_search=True
)
def analysis():
    pass
```

### Collection-Based Organization

Organize analyses into logical collections:

```python
# Research collections
@snapshot(collection="experiments", tags=["research", "hypothesis"])
def experiment_1():
    pass

@snapshot(collection="publications", tags=["paper", "peer-review"])
def publication_analysis():
    pass

# Business collections  
@snapshot(collection="quarterly-reports", tags=["business", "kpi"])
def q4_report():
    pass

@snapshot(collection="ad-hoc", tags=["stakeholder", "urgent"])
def urgent_analysis():
    pass

# Team collections
@snapshot(collection="data-science", author="DS Team")
def ds_analysis():
    pass
```

## Advanced Search Features

### Search Scoring

Results are ranked using multiple factors:

```python
# Search scoring factors:
# 1. Text relevance (TF-IDF based)
# 2. Tag match count  
# 3. Exact phrase matches
# 4. Title vs content matches (title weighted higher)
# 5. Recency (newer results ranked higher)
# 6. Author relevance (if author specified)

# Example: These would rank in this order for "customer analysis"
snapshots = [
    # Score: 0.95 (exact title match, recent)
    snapshot(title="Customer Analysis", tags=["customers"]),
    
    # Score: 0.87 (title contains both words, older)  
    snapshot(title="Customer Behavior Analysis", tags=["behavior"]),
    
    # Score: 0.72 (content match, good tags)
    snapshot(title="Q4 Report", notes="Analysis of customer segments", tags=["customers"]),
    
    # Score: 0.45 (partial match in content)
    snapshot(title="Sales Data", notes="Some customer insights")
]
```

### Complex Queries

```python
# Boolean search (programmatic)
results = search_manager.search_snapshots(
    query='(machine learning OR ml) AND (classification OR prediction)',
    tags=['production', 'evaluation'],
    exclude_tags=['experimental', 'draft'],
    author_contains='Data Science',
    date_from='2024-01-01',
    date_to='2024-06-30',
    min_score=0.5
)

# Tag intersection and union
ml_or_stats = search_manager.search_by_tags(['ml'], operation='OR') 
ml_and_production = search_manager.search_by_tags(['ml', 'production'], operation='AND')
```

### Search Analytics

Track search patterns to improve organization:

```python
# Get search statistics
stats = search_manager.get_search_stats()
print(f"Total snapshots: {stats['total_snapshots']}")
print(f"Most common tags: {stats['top_tags'][:10]}")
print(f"Most active authors: {stats['top_authors'][:5]}")
print(f"Search index size: {stats['index_size_mb']:.1f} MB")

# Tag analytics
tag_stats = search_manager.get_tag_analytics()
for tag, count in tag_stats.most_common(10):
    print(f"{tag}: {count} snapshots")
```

## Maintenance and Performance

### Database Maintenance

```python
# Rebuild search index (if corrupted or after major changes)
search_manager.rebuild_index()

# Optimize database (compress and defragment)
search_manager.optimize_database()

# Clean up orphaned entries
search_manager.cleanup_orphaned_entries()

# Backup search database
search_manager.backup_database('search_backup.db')
```

### Performance Optimization

```python
# For large snapshot collections (1000+)
search_manager = SnapshotSearchManager(
    Path('snapshots'),
    max_results=50,           # Limit results for speed
    enable_caching=True,      # Cache frequent searches
    index_batch_size=100      # Batch index updates
)

# Async search for web interfaces
async def search_async(query):
    results = await search_manager.search_async(query)
    return results
```

### Search Index Export

```python
# Export search data for external tools
search_data = search_manager.export_search_data()

# Format: List of dictionaries with all searchable fields
for snapshot in search_data:
    print(f"{snapshot['title']} - {snapshot['tags']} - {snapshot['timestamp']}")

# Export to different formats
search_manager.export_to_json('snapshots_index.json')
search_manager.export_to_csv('snapshots_index.csv')
```

## Integration with External Tools

### Elasticsearch Integration

```python
# For enterprise search needs
from snapshotplot.integrations import ElasticsearchSync

es_sync = ElasticsearchSync(
    hosts=['localhost:9200'],
    index_name='snapshots'
)

# Sync all snapshots to Elasticsearch
es_sync.sync_all_snapshots(search_manager)

# Search using Elasticsearch
results = es_sync.search('machine learning', size=20)
```

### Database Export

```python
# Export to pandas for analysis
import pandas as pd

df = search_manager.to_dataframe()
print(df.head())

# Analyze tagging patterns
tag_analysis = df['tags'].str.split(',').explode().value_counts()
author_analysis = df['author'].value_counts()
timeline = df.groupby(df['timestamp'].dt.date).size()
```

## Best Practices

### Tagging Strategy
1. **Consistent Vocabulary**: Establish team-wide tag conventions
2. **Hierarchical Structure**: Use dots for nested categories
3. **Balance Specificity**: Not too broad, not too narrow
4. **Regular Cleanup**: Review and consolidate tags periodically

### Search Optimization
1. **Meaningful Titles**: Include key terms in snapshot titles
2. **Rich Descriptions**: Provide context in notes field
3. **Tag Everything**: Better to over-tag than under-tag
4. **Regular Indexing**: Enable search for important analyses

### Team Workflow
1. **Search Training**: Teach team members advanced search syntax
2. **Regular Reviews**: Use search to audit and organize work
3. **Documentation**: Keep search patterns and tag meanings documented
4. **Performance Monitoring**: Watch for slow searches in large collections

## Troubleshooting

### Search Not Working
```bash
# Check if search database exists
ls snapshots/.snapshotplot/snapshots.db

# Verify search is enabled
python -c "
from snapshotplot.core.search_system import SnapshotSearchManager
from pathlib import Path
sm = SnapshotSearchManager(Path('snapshots'))
print(f'Total snapshots in index: {len(sm.search_snapshots())}')
"
```

### Performance Issues
```bash
# Check database size
du -h snapshots/.snapshotplot/

# Optimize database
python -c "
from snapshotplot.core.search_system import SnapshotSearchManager
from pathlib import Path
sm = SnapshotSearchManager(Path('snapshots'))
sm.optimize_database()
"
```

### Index Corruption
```bash
# Rebuild search index from scratch
python -c "
from snapshotplot.core.search_system import SnapshotSearchManager
from pathlib import Path
sm = SnapshotSearchManager(Path('snapshots'))
sm.rebuild_index()
print('Search index rebuilt successfully')
"
```

The search and organization features make SnapshotPlot scale from personal research tools to enterprise knowledge management systems. With proper tagging and search strategies, you can build a searchable repository of all your analytical work.