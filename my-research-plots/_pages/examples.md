---
title: Examples and Use Cases
description: Real-world examples of using SnapshotPlot for data analysis documentation
layout: default
permalink: /examples/
---

# Examples and Use Cases

See how SnapshotPlot can be used across different data science workflows.

## Data Exploration

### Basic Statistical Analysis

```python
from snapshotplot import snapshot
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

@snapshot(
    title="Customer Demographics Analysis",
    tags=["demographics", "eda", "customers"],
    author="Data Science Team"
)
def analyze_demographics():
    # Generate sample customer data
    np.random.seed(42)
    ages = np.random.normal(35, 12, 1000)
    incomes = ages * 1200 + np.random.normal(0, 5000, 1000)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Age distribution
    ax1.hist(ages, bins=30, alpha=0.7, color='skyblue')
    ax1.set_title('Age Distribution')
    ax1.set_xlabel('Age')
    ax1.set_ylabel('Frequency')
    
    # Income vs Age scatter
    ax2.scatter(ages, incomes, alpha=0.6, color='coral')
    ax2.set_title('Income vs Age')
    ax2.set_xlabel('Age')
    ax2.set_ylabel('Annual Income ($)')
    
    plt.tight_layout()
    plt.show()

analyze_demographics()
```

## Machine Learning Workflows

### Model Performance Evaluation

```python
@snapshot(
    title="Classification Model Evaluation",
    tags=["ml", "classification", "evaluation"],
    export_formats=["html", "pdf"],
    enable_search=True
)
def evaluate_classifier():
    from sklearn.metrics import confusion_matrix, classification_report
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    import seaborn as sns
    
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=3, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Train model
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Create visualizations
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax1)
    ax1.set_title('Confusion Matrix')
    ax1.set_ylabel('Actual')
    ax1.set_xlabel('Predicted')
    
    # Feature Importance
    feature_importance = model.feature_importances_
    indices = np.argsort(feature_importance)[::-1][:10]
    
    ax2.bar(range(10), feature_importance[indices])
    ax2.set_title('Top 10 Feature Importances')
    ax2.set_xlabel('Feature Index')
    ax2.set_ylabel('Importance')
    
    plt.tight_layout()
    plt.show()
    
    # Print classification report
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

evaluate_classifier()
```

## Interactive Visualizations with Plotly

### Sales Dashboard

```python
@snapshot(
    title="Interactive Sales Dashboard",
    backend="plotly",
    tags=["sales", "dashboard", "interactive"],
    notes="Interactive visualization showing sales trends and regional performance"
)
def create_sales_dashboard():
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import pandas as pd
    
    # Sample sales data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    north_sales = [20, 25, 30, 35, 40, 45]
    south_sales = [15, 20, 25, 30, 35, 40]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Sales Trends', 'Regional Comparison', 'Growth Rate', 'Cumulative Sales'),
        specs=[[{"secondary_y": True}, {"type": "bar"}],
               [{"type": "scatter"}, {"type": "scatter"}]]
    )
    
    # Sales trends
    fig.add_trace(go.Scatter(x=months, y=north_sales, name='North Region', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=months, y=south_sales, name='South Region', line=dict(color='red')), row=1, col=1)
    
    # Regional comparison
    fig.add_trace(go.Bar(x=months, y=north_sales, name='North', marker_color='lightblue'), row=1, col=2)
    fig.add_trace(go.Bar(x=months, y=south_sales, name='South', marker_color='lightcoral'), row=1, col=2)
    
    # Growth rates
    north_growth = [0] + [((north_sales[i] - north_sales[i-1]) / north_sales[i-1]) * 100 for i in range(1, len(north_sales))]
    fig.add_trace(go.Scatter(x=months, y=north_growth, mode='markers+lines', name='North Growth %'), row=2, col=1)
    
    # Cumulative sales
    cumulative_north = np.cumsum(north_sales)
    cumulative_south = np.cumsum(south_sales)
    fig.add_trace(go.Scatter(x=months, y=cumulative_north, fill='tonexty', name='North Cumulative'), row=2, col=2)
    fig.add_trace(go.Scatter(x=months, y=cumulative_south, fill='tozeroy', name='South Cumulative'), row=2, col=2)
    
    fig.update_layout(height=600, showlegend=True, title_text="Sales Performance Dashboard")
    fig.show()

create_sales_dashboard()
```

## Time Series Analysis

### Stock Price Analysis

```python
@snapshot(
    title="Stock Price Technical Analysis",
    tags=["finance", "time-series", "technical-analysis"],
    export_formats=["html", "markdown"],
    author="Quantitative Analysis Team"
)
def analyze_stock_prices():
    # Generate sample stock data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=252, freq='D')
    price = 100
    prices = []
    
    for _ in range(252):
        price += np.random.normal(0, 2)
        prices.append(max(price, 10))  # Prevent negative prices
    
    df = pd.DataFrame({'Date': dates, 'Price': prices})
    df['MA_20'] = df['Price'].rolling(window=20).mean()
    df['MA_50'] = df['Price'].rolling(window=50).mean()
    
    # Create technical analysis chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[3, 1])
    
    # Price and moving averages
    ax1.plot(df['Date'], df['Price'], label='Price', linewidth=1, color='black')
    ax1.plot(df['Date'], df['MA_20'], label='20-day MA', color='blue', alpha=0.7)
    ax1.plot(df['Date'], df['MA_50'], label='50-day MA', color='red', alpha=0.7)
    ax1.set_title('Stock Price with Moving Averages')
    ax1.set_ylabel('Price ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Volume (simulated)
    volume = np.random.normal(1000000, 200000, 252)
    ax2.bar(df['Date'], volume, alpha=0.6, color='gray')
    ax2.set_title('Trading Volume')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Volume')
    
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print(f"Price Statistics:")
    print(f"Mean: ${df['Price'].mean():.2f}")
    print(f"Std Dev: ${df['Price'].std():.2f}")
    print(f"Min: ${df['Price'].min():.2f}")
    print(f"Max: ${df['Price'].max():.2f}")

analyze_stock_prices()
```

## Scientific Computing

### Physics Simulation

```python
@snapshot(
    title="Pendulum Motion Simulation",
    tags=["physics", "simulation", "differential-equations"],
    notes="Numerical solution of a damped pendulum using Runge-Kutta method"
)
def simulate_pendulum():
    from scipy.integrate import odeint
    
    def pendulum_eq(state, t, b, c):
        """Damped pendulum differential equation"""
        theta, theta_dot = state
        dydt = [theta_dot, -b*theta_dot - c*np.sin(theta)]
        return dydt
    
    # Parameters
    b = 0.25  # damping coefficient
    c = 5.0   # gravitational term
    
    # Initial conditions
    theta0 = np.pi - 0.1  # initial angle (near inverted)
    theta_dot0 = 0.0      # initial angular velocity
    state0 = [theta0, theta_dot0]
    
    # Time points
    t = np.linspace(0, 10, 1000)
    
    # Solve ODE
    solution = odeint(pendulum_eq, state0, t, args=(b, c))
    
    # Create visualization
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    
    # Angle vs time
    ax1.plot(t, solution[:, 0], 'b-', linewidth=2)
    ax1.set_ylabel('Angle (rad)')
    ax1.set_title('Damped Pendulum Motion')
    ax1.grid(True, alpha=0.3)
    
    # Angular velocity vs time
    ax2.plot(t, solution[:, 1], 'r-', linewidth=2)
    ax2.set_ylabel('Angular Velocity (rad/s)')
    ax2.grid(True, alpha=0.3)
    
    # Phase space plot
    ax3.plot(solution[:, 0], solution[:, 1], 'g-', linewidth=2)
    ax3.set_xlabel('Angle (rad)')
    ax3.set_ylabel('Angular Velocity (rad/s)')
    ax3.set_title('Phase Space')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

simulate_pendulum()
```

## Business Intelligence

### KPI Dashboard

```python
@snapshot(
    title="Monthly KPI Dashboard",
    tags=["business", "kpi", "dashboard"],
    export_formats=["html", "pdf"],
    enable_search=True,
    notes="Key performance indicators for monthly business review"
)
def create_kpi_dashboard():
    # Sample KPI data
    metrics = ['Revenue', 'New Customers', 'Retention Rate', 'CAC', 'LTV', 'Churn Rate']
    current = [150000, 245, 89.5, 120, 1250, 4.2]
    target = [140000, 200, 85.0, 100, 1200, 5.0]
    previous = [135000, 180, 87.2, 110, 1180, 4.8]
    
    # Create dashboard
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # KPI comparison bar chart
    x = np.arange(len(metrics))
    width = 0.25
    
    ax1.bar(x - width, current, width, label='Current', color='skyblue')
    ax1.bar(x, target, width, label='Target', color='lightgreen')
    ax1.bar(x + width, previous, width, label='Previous', color='lightcoral')
    
    ax1.set_ylabel('Value')
    ax1.set_title('KPI Performance Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, rotation=45)
    ax1.legend()
    
    # Revenue trend
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    revenue_trend = [120000, 125000, 130000, 135000, 145000, 150000]
    ax2.plot(months, revenue_trend, marker='o', linewidth=3, markersize=8, color='green')
    ax2.set_title('Revenue Trend')
    ax2.set_ylabel('Revenue ($)')
    ax2.grid(True, alpha=0.3)
    
    # Customer acquisition funnel
    funnel_stages = ['Visitors', 'Leads', 'Trials', 'Customers']
    funnel_values = [10000, 2500, 500, 245]
    colors = ['lightblue', 'blue', 'darkblue', 'navy']
    
    ax3.bar(funnel_stages, funnel_values, color=colors)
    ax3.set_title('Customer Acquisition Funnel')
    ax3.set_ylabel('Count')
    
    # Conversion rates
    conversion_rates = [25, 20, 49]  # Lead conversion, trial conversion, trial to customer
    stages = ['Visitor to Lead', 'Lead to Trial', 'Trial to Customer']
    
    ax4.pie(conversion_rates, labels=stages, autopct='%1.1f%%', startangle=90)
    ax4.set_title('Conversion Rates')
    
    plt.tight_layout()
    plt.show()
    
    # Print key insights
    print("Key Insights:")
    print(f"- Revenue exceeded target by ${current[0] - target[0]:,}")
    print(f"- Customer acquisition: {current[1]} vs target of {target[1]}")
    print(f"- Retention rate: {current[2]}% (target: {target[2]}%)")

create_kpi_dashboard()
```

## Best Practices

### Consistent Tagging and Organization

```python
# Use consistent tags across your analysis
TAGS = {
    'EXPLORATORY': ['eda', 'exploration', 'data-quality'],
    'MODELING': ['ml', 'modeling', 'prediction'],
    'EVALUATION': ['evaluation', 'metrics', 'performance'],
    'BUSINESS': ['business', 'kpi', 'insights'],
    'PRODUCTION': ['production', 'monitoring', 'deployment']
}

@snapshot(
    title="Customer Segmentation Analysis",
    tags=TAGS['MODELING'] + ['clustering', 'customers'],
    author="ML Team",
    enable_search=True
)
def customer_segmentation():
    # Your analysis code
    pass
```

### Progressive Analysis Documentation

```python
# Step 1: Exploration
@snapshot(title="Data Exploration", tags=TAGS['EXPLORATORY'])
def explore_data():
    # Initial data exploration
    pass

# Step 2: Feature Engineering  
@snapshot(title="Feature Engineering", tags=TAGS['EXPLORATORY'] + ['features'])
def engineer_features():
    # Feature creation and selection
    pass

# Step 3: Model Training
@snapshot(title="Model Training", tags=TAGS['MODELING'])
def train_model():
    # Model training and tuning
    pass

# Step 4: Evaluation
@snapshot(title="Model Evaluation", tags=TAGS['EVALUATION'], export_formats=['html', 'pdf'])
def evaluate_model():
    # Final model evaluation
    pass
```

These examples demonstrate the flexibility and power of SnapshotPlot across different domains and use cases. Each snapshot is automatically organized, searchable, and can be exported in multiple formats for different audiences.