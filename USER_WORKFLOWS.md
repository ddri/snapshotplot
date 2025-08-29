# SnapshotPlot User Workflows

SnapshotPlot is designed around four distinct user workflows, each building on the previous one. You can start simple and add features as your needs grow.

## 🔬 Workflow 1: Solo Researcher (Core Only)

**Who:** Individual researchers, data scientists, or analysts working on personal projects.

**Goal:** Quick documentation of analysis code and plots for future reference.

### Installation
```bash
pip install snapshotplot
```

### Usage
```python
from snapshotplot import snapshot
import matplotlib.pyplot as plt
import numpy as np

@snapshot()
def my_analysis():
    """Simple analysis with automatic documentation."""
    x = np.linspace(0, 10, 100)
    y = x**2
    plt.plot(x, y)
    plt.title("Quadratic Function")
    plt.show()

# Or as context manager
with snapshot():
    plt.scatter(data_x, data_y)
    plt.title("My Research Data")
    plt.show()
```

### Output
Creates timestamped folders with:
- `{timestamp}_code.py` - Your source code
- `{timestamp}_plot.png` - Generated plot  
- `{timestamp}_snapshot.html` - Beautiful documentation

### When to Use
- Personal research notebooks
- Quick exploratory analysis
- Prototyping and experimentation
- "I just want to save this plot with the code"

---

## 👥 Workflow 2: Data Science Team (Core + Jupyter)

**Who:** Data science teams using Jupyter notebooks for collaborative analysis.

**Goal:** Seamless documentation within existing Jupyter workflows with team metadata.

### Installation
```bash
pip install snapshotplot[jupyter]
```

### Usage
```python
# Load extension once per notebook
%load_ext snapshotplot

# Cell magic for comprehensive capture
%%snapshot -t "Customer Segmentation" -a "Analytics Team" --tags ml clustering
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Perform analysis
kmeans = KMeans(n_clusters=3)
clusters = kmeans.fit_predict(customer_data)

# Visualize results
plt.figure(figsize=(10, 6))
plt.scatter(customer_data[:, 0], customer_data[:, 1], c=clusters, cmap='viridis')
plt.title('Customer Segments')
plt.colorbar(label='Cluster')
plt.show()

# Line magic for retroactive capture
plt.plot(time_series)
plt.show()

%snapshot -t "Time Series Analysis" -a "Data Team" --description "Key trend identified"
```

### Team Features
- **Author tracking**: Know who created each analysis
- **Tagging system**: Organize analyses across notebooks
- **Retroactive capture**: Document important plots after creation
- **Metadata**: Rich context for team collaboration

### When to Use
- Team data science projects
- Jupyter-based workflows
- Analysis that needs author attribution
- Collaborative research environments

---

## 🌐 Workflow 3: Research Organization (Core + Site)

**Who:** Research labs, academic institutions, or companies publishing analysis results.

**Goal:** Professional documentation websites with automated publication workflows.

### Installation
```bash
pip install snapshotplot[site]
```

### Usage
```python
from snapshotplot import snapshot

# Automatic site integration
with snapshot(
    title="Quarterly Performance Analysis",
    author="Research Lab",
    site="../research-website",
    collection="quarterly-reports",
    auto_build=True
):
    # Perform complex analysis
    analyze_quarterly_data()
    plt.figure(figsize=(12, 8))
    plot_performance_metrics()
    plt.show()

# Or in Jupyter with site integration
%%snapshot -t "Breakthrough Results" \
           --site "../lab-website" \
           --collection "publications" \
           --auto-commit \
           --auto-build
           
# Your research code
perform_breakthrough_analysis()
plt.show()
```

### Site Features
- **Static site generation**: Beautiful Jekyll/Hugo-style websites
- **Collections**: Organize research by topic/project
- **Auto-deployment**: GitHub Pages integration
- **Professional themes**: Publication-ready styling
- **Git integration**: Automatic commits and builds

### When to Use
- Public research publication
- Lab websites and documentation
- Professional analysis presentation
- Long-term archival with discoverability

---

## ⚙️ Workflow 4: DevOps/Automation (CLI Tools)

**Who:** DevOps teams, automation engineers, or organizations with CI/CD pipelines.

**Goal:** Automated documentation generation and deployment as part of development workflows.

### Installation
```bash
pip install snapshotplot[cli]
# OR for everything:
pip install snapshotplot[all]
```

### Usage
```bash
# Initialize a new plot site
snapshotplot init my-research-site --author "Research Team"

# Create collections for organizing plots
snapshotplot collection create experiments --title "ML Experiments"

# Build the static site
snapshotplot build --output docs

# Deploy to GitHub Pages
snapshotplot deploy --push

# List all captured plots
snapshotplot list --collection experiments

# Serve locally for development
snapshotplot serve --port 8000
```

### CI/CD Integration
```yaml
# .github/workflows/build-plots.yml (auto-generated)
- name: Build site
  run: snapshotplot build
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs
```

### When to Use
- Automated documentation pipelines
- Large-scale analysis processing
- Enterprise deployment workflows
- Integration with existing DevOps tools

---

## 🚀 Progressive Adoption Path

### Start Simple → Scale Up

1. **Begin with Core** (`pip install snapshotplot`)
   - Try the basic decorator/context manager
   - Get comfortable with automatic documentation

2. **Add Jupyter** (`pip install snapshotplot[jupyter]`)
   - Load the magic commands in your notebooks
   - Start using team metadata (author, tags)

3. **Enable Site Generation** (`pip install snapshotplot[site]`)
   - Create a research website
   - Set up auto-building workflows

4. **Automate Everything** (`pip install snapshotplot[cli]`)
   - Integrate with CI/CD
   - Scale to organizational level

### Migration Between Workflows

Moving between workflows is seamless - all snapshots use the same file format:

```python
# Workflow 1: Basic snapshot
with snapshot():
    plt.plot(data)
    plt.show()

# Workflow 2: Add Jupyter metadata (same files!)
%%snapshot -t "Analysis" -a "Team"
plt.plot(data)  # Same plotting code
plt.show()

# Workflow 3: Publish to site (same snapshots!)
with snapshot(site="../website", auto_build=True):
    plt.plot(data)  # Same plotting code  
    plt.show()
```

## 📦 Installation Quick Reference

| Workflow | Installation | Features |
|----------|-------------|----------|
| Solo Researcher | `pip install snapshotplot` | Basic capture, HTML docs |
| Data Science Team | `pip install snapshotplot[jupyter]` | + Magic commands, metadata |
| Research Organization | `pip install snapshotplot[site]` | + Site generation, deployment |
| DevOps/Automation | `pip install snapshotplot[cli]` | + Command line tools |
| Everything | `pip install snapshotplot[all]` | All features |

## 🎯 Choosing Your Workflow

**Start here if you:**
- **Just want to save plots with code** → Workflow 1 (Core)
- **Work in Jupyter notebooks** → Workflow 2 (Jupyter)  
- **Need a research website** → Workflow 3 (Site)
- **Have automation needs** → Workflow 4 (CLI)

Each workflow builds naturally on the previous one, so you can evolve your usage as your needs grow.