---
title: Static Site Generation
description: Build beautiful, searchable websites from your SnapshotPlot analyses
layout: default
permalink: /static-sites/
---

# Static Site Generation

SnapshotPlot can automatically generate beautiful, searchable static websites from your analysis snapshots. Perfect for research teams, documentation, and sharing insights with stakeholders.

## Quick Start

### Basic Site Generation

```python
from snapshotplot.site.site_generator import SiteGenerator

# Generate a site from your snapshots
generator = SiteGenerator('.')
generator.build('docs', verbose=True)
```

### Automatic Site Integration

```python
# Configure snapshots to automatically update your site
@snapshot(
    title="Sales Analysis Q4",
    author="Data Team",
    tags=["sales", "quarterly"],
    site="./my-research-site",
    collection="quarterly-reports",
    auto_build=True
)
def quarterly_analysis():
    # Your analysis code
    plt.bar(['Q1', 'Q2', 'Q3', 'Q4'], [100, 120, 115, 140])
    plt.title('Quarterly Sales Growth')
    plt.show()
```

## Site Structure

SnapshotPlot generates organized static sites with this structure:

```
docs/                          # Generated site
├── index.html                 # Homepage with plot gallery
├── collections/
│   ├── experiments/          # Collection pages
│   │   ├── index.html        # Collection overview
│   │   └── plot-name/
│   │       └── index.html    # Individual plot page
│   └── visualizations/
├── assets/
│   ├── css/                  # Responsive styling
│   ├── js/                   # Search functionality
│   └── images/               # Plot images and thumbnails
└── search.html               # Dedicated search page
```

## Features

### 🔍 Client-Side Search
- **Instant Results**: No server required, works offline
- **Smart Scoring**: Relevance-based ranking with keyword highlighting
- **Multiple Fields**: Search titles, descriptions, tags, and content
- **Mobile Optimized**: Touch-friendly interface

### 🎨 Modern Design
- **GitHub-Inspired**: Clean, professional appearance
- **Responsive Layout**: Works on all devices
- **Dark Mode Ready**: Easy on the eyes
- **Fast Loading**: Optimized assets and lazy loading

### 📁 Smart Organization
- **Collections**: Group related analyses together
- **Automatic Tagging**: Visual tag system with colors
- **Chronological Sorting**: Latest analyses first
- **Metadata Rich**: Author, date, description display

## Configuration

### Site Generator Options

```python
from snapshotplot.site.site_generator import SiteGenerator

generator = SiteGenerator(
    snapshot_dir='.',           # Directory containing snapshots
    site_title='Research Lab',  # Site title
    site_description='Our latest research findings',
    author='Research Team',
    base_url='https://research.example.com'
)

generator.build(
    output_dir='docs',          # Output directory
    verbose=True,               # Show build progress
    clean=True                  # Clean output dir first
)
```

### Snapshot Integration

```python
@snapshot(
    # Site configuration
    site="./my-site",                    # Site directory
    collection="experiments",           # Collection name
    auto_build=True,                    # Rebuild site after snapshot
    
    # Content metadata
    title="Customer Segmentation",
    author="ML Team",
    tags=["clustering", "customers"],
    description="K-means clustering analysis of customer behavior",
    
    # Export options
    export_formats=["html", "markdown"], # Include markdown for site
    enable_search=True                   # Add to search index
)
def customer_analysis():
    # Your analysis code
    pass
```

## Collections

Collections help organize related analyses. Common patterns:

### Research Collections
```python
# Experiments collection
@snapshot(collection="experiments", tags=["research", "ml"])
def experiment_1():
    pass

# Visualizations collection  
@snapshot(collection="visualizations", tags=["eda", "plots"])
def data_exploration():
    pass

# Reports collection
@snapshot(collection="reports", tags=["business", "quarterly"])
def quarterly_report():
    pass
```

### Team Collections
```python
# By team
@snapshot(collection="data-science", author="DS Team")
def ml_analysis():
    pass

@snapshot(collection="product", author="Product Team")  
def feature_analysis():
    pass

# By project
@snapshot(collection="project-alpha", tags=["alpha", "prototype"])
def alpha_metrics():
    pass
```

## Search Functionality

### Search Index Generation

The site generator automatically creates a search index:

```javascript
// Generated search-index.json
[
  {
    "id": "analysis-id",
    "title": "Customer Segmentation",
    "description": "K-means clustering analysis",
    "author": "Data Team",
    "tags": ["clustering", "ml"],
    "collection": "experiments",
    "date": "2024-07-18",
    "url": "/experiments/customer-segmentation/",
    "keywords": ["customer", "segments", "clusters"]
  }
]
```

### Search Features

- **Fuzzy Matching**: Finds results even with typos
- **Tag Filtering**: Click tags to filter results
- **Keyboard Navigation**: Arrow keys and Enter
- **URL Integration**: Shareable search URLs
- **Result Highlighting**: Matched terms highlighted

## Deployment

### GitHub Pages

```yaml
# .github/workflows/deploy.yml
name: Deploy Site
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
        
    - name: Install dependencies
      run: |
        pip install snapshotplot[site]
        
    - name: Build site
      run: |
        python -c "
        from snapshotplot.site.site_generator import SiteGenerator
        gen = SiteGenerator('.')
        gen.build('docs', verbose=True)
        "
        
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs
```

### Netlify

```toml
# netlify.toml
[build]
  command = "pip install snapshotplot[site] && python build_site.py"
  publish = "docs"

[build.environment]
  PYTHON_VERSION = "3.9"
```

```python
# build_site.py
from snapshotplot.site.site_generator import SiteGenerator

generator = SiteGenerator('.')
generator.build('docs', verbose=True)
```

### Custom Domain

```python
# Configure custom domain
generator = SiteGenerator(
    '.',
    base_url='https://research.yourcompany.com',
    site_title='Company Research Lab'
)
```

## Customization

### Custom Templates

Override default templates by creating `_layouts/` directory:

```html
<!-- _layouts/default.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ site.title }} - {{ page.title }}</title>
    <!-- Your custom CSS -->
</head>
<body>
    <!-- Your custom header -->
    {{ content }}
    <!-- Your custom footer -->
</body>
</html>
```

### Custom Styling

```css
/* assets/css/custom.css */
:root {
    --primary-color: #your-brand-color;
    --background-color: #your-bg-color;
}

.plot-card {
    border: 2px solid var(--primary-color);
}
```

### Custom Collections

```python
# Define custom collection templates
collections = {
    'experiments': {
        'title': 'Research Experiments',
        'description': 'Our latest research findings',
        'icon': '🔬'
    },
    'reports': {
        'title': 'Business Reports', 
        'description': 'Quarterly and annual reports',
        'icon': '📊'
    }
}

generator = SiteGenerator('.', collections=collections)
```

## Performance Optimization

### Image Optimization

```python
@snapshot(
    dpi=150,                    # Reasonable resolution
    format='webp',              # Modern image format
    optimize_images=True        # Enable compression
)
def analysis():
    pass
```

### Build Optimization

```python
# Incremental builds - only rebuild changed plots
generator.build(
    'docs',
    incremental=True,           # Only update changed files
    parallel=True,              # Use multiple cores
    compress_assets=True        # Minify CSS/JS
)
```

## Analytics Integration

### Google Analytics

```html
<!-- _layouts/default.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Custom Analytics

```javascript
// Track search usage
document.addEventListener('search', function(e) {
    // Your analytics code
    analytics.track('site_search', {
        query: e.detail.query,
        results: e.detail.results.length
    });
});
```

## Best Practices

### Content Organization
- **Consistent Collections**: Use standardized collection names
- **Descriptive Titles**: Make titles searchable and clear
- **Rich Metadata**: Include author, tags, and descriptions
- **Regular Builds**: Set up automated rebuilds

### SEO Optimization
- **Meta Tags**: Include descriptions and keywords
- **Semantic HTML**: Use proper heading structure
- **Sitemap**: Auto-generated for search engines
- **Fast Loading**: Optimized images and assets

### Team Workflow
- **Naming Conventions**: Agree on collection and tag standards
- **Review Process**: Use site for team reviews
- **Documentation**: Keep analysis context in descriptions
- **Version Control**: Include generated sites in git

## Troubleshooting

### Build Failures
```bash
# Check for missing dependencies
pip install snapshotplot[site]

# Verify file permissions
chmod -R 755 docs/

# Clean build
rm -rf docs/ && python build_site.py
```

### Search Not Working
```bash
# Verify search index exists
ls docs/assets/js/search-index.json

# Check JavaScript console for errors
# Ensure valid JSON in search index
```

### Deployment Issues
```bash
# Test local server
cd docs && python -m http.server 8000

# Check base URL configuration
# Verify asset paths are relative
```

Static site generation makes your research accessible, searchable, and professional. It's perfect for sharing insights with stakeholders, maintaining team documentation, and building a knowledge base of your analytical work.