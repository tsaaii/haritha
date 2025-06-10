# layouts/enhanced_public_landing.py
"""
Enhanced Public Landing Page Layout for Swaccha Andhra
Displays real dashboard data with visualizations for Zigma Agency
"""

from dash import html, dcc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging

from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner

logger = logging.getLogger(__name__)

# Cluster mapping for waste management
WASTE_CLUSTER_MAPPING = {
    'Nellore Municipal Corporation': ['allipuram', 'donthalli'],
    'Chittor': ['kuppam', 'palamaner', 'madanapalle'],
    'Tirupathi': ['tpty'],
    'GVMC': ['vizagsac']
}

def load_dashboard_data():
    """Load waste management data from CSV for dashboard display - LAST 7 DAYS ONLY"""
    try:
        df = pd.read_csv('waste_management_data_20250606_004558.csv')
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Net Weight'] = pd.to_numeric(df['Net Weight'], errors='coerce')
        df['Loaded Weight'] = pd.to_numeric(df['Loaded Weight'], errors='coerce')
        df['Empty Weight'] = pd.to_numeric(df['Empty Weight'], errors='coerce')
        df = df.dropna(subset=['Date', 'source_location'])
        
        # FILTER FOR LAST 7 DAYS ONLY
        one_week_ago = datetime.now() - timedelta(days=7)
        df = df[df['Date'] >= one_week_ago]
        
        # Add cluster info using the mapping
        def get_cluster(site):
            for cluster, sites in WASTE_CLUSTER_MAPPING.items():
                if site in sites:
                    return cluster
            return 'Unknown'
        
        df['Cluster'] = df['source_location'].apply(get_cluster)
        df['Agency'] = 'Zigma'
        
        # Add time-based columns for analysis
        df['Hour'] = df['Date'].dt.hour
        df['DayOfWeek'] = df['Date'].dt.day_name()
        df['Week'] = df['Date'].dt.isocalendar().week
        df['WeekStart'] = df['Date'] - pd.to_timedelta(df['Date'].dt.dayofweek, unit='d')
        
        logger.info(f"Loaded {len(df)} dashboard records for public landing (last 7 days)")
        return df
    except FileNotFoundError:
        logger.warning("Dashboard data CSV not found, creating sample data")
        return create_sample_dashboard_data()
    except Exception as e:
        logger.error(f"Error loading dashboard data: {e}")
        return create_sample_dashboard_data()

def create_sample_dashboard_data():
    """Create sample dashboard data if CSV is not available - LAST 7 DAYS ONLY"""
    import random
    from datetime import datetime, timedelta
    
    sites = ['allipuram', 'donthalli', 'kuppam', 'palamaner', 'madanapalle', 'tpty', 'vizagsac']
    materials = ['Mixed Waste', 'Plastic', 'Paper', 'Organic', 'Metal', 'Glass']
    vehicles = ['AP01AB1234', 'AP02CD5678', 'AP03EF9012', 'AP04GH3456']
    
    data = []
    # Only generate data for the last 7 days
    start_date = datetime.now() - timedelta(days=7)
    
    for i in range(200):  # Reduced from 500 since we only have 1 week
        date = start_date + timedelta(
            days=random.randint(0, 7),
            hours=random.randint(6, 18),
            minutes=random.randint(0, 59)
        )
        site = random.choice(sites)
        
        # Get cluster for site
        cluster = 'Unknown'
        for cluster_name, cluster_sites in WASTE_CLUSTER_MAPPING.items():
            if site in cluster_sites:
                cluster = cluster_name
                break
        
        data.append({
            'Date': date,
            'source_location': site,
            'Cluster': cluster,
            'Agency': 'Zigma',
            'Material Name': random.choice(materials),
            'Net Weight': random.randint(500, 5000),
            'Loaded Weight': random.randint(5500, 10000),
            'Empty Weight': random.randint(2000, 3000),
            'Vehicle No': random.choice(vehicles),
            'Hour': date.hour,
            'DayOfWeek': date.strftime('%A'),
            'Week': date.isocalendar()[1],
            'WeekStart': date - timedelta(days=date.weekday())
        })
    
    df = pd.DataFrame(data)
    logger.info(f"Created {len(df)} sample dashboard records (last 7 days)")
    return df

def create_weekly_trips_histogram(data, theme):
    """Create histogram of trips in current week"""
    if data.empty:
        return create_empty_chart("No trip data available", theme)
    
    # Count trips by day for the last 7 days
    daily_trips = data.groupby('DayOfWeek').size().reset_index(name='Trip_Count')
    
    # Ensure all days are present
    all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_trips = daily_trips.set_index('DayOfWeek').reindex(all_days, fill_value=0).reset_index()
    
    fig = go.Figure(data=[
        go.Bar(
            x=daily_trips['DayOfWeek'],
            y=daily_trips['Trip_Count'],
            marker_color=theme['brand_primary'],
            text=daily_trips['Trip_Count'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Trips: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': '🚛 Weekly Trips Distribution (Last 7 Days)',
            'x': 0.5,
            'font': {'color': theme['text_primary'], 'size': 18}
        },
        xaxis={'title': 'Day of Week', 'color': theme['text_secondary']},
        yaxis={'title': 'Number of Trips', 'color': theme['text_secondary']},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': theme['text_primary']},
        margin=dict(l=50, r=50, t=60, b=50),
        height=400  # LANDSCAPE MODE - fixed height
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_daily_waste_line_chart(data, theme):
    """Create line graph of sum of trash picked by each day (Last 7 days)"""
    if data.empty:
        return create_empty_chart("No waste data available", theme)
    
    # Group by date and sum net weight for last 7 days
    daily_waste = data.groupby(data['Date'].dt.date)['Net Weight'].sum().reset_index()
    daily_waste['Date'] = pd.to_datetime(daily_waste['Date'])
    daily_waste = daily_waste.sort_values('Date')
    
    # Convert to tons for better readability
    daily_waste['Net Weight (Tons)'] = daily_waste['Net Weight'] / 1000
    
    fig = go.Figure(data=[
        go.Scatter(
            x=daily_waste['Date'],
            y=daily_waste['Net Weight (Tons)'],
            mode='lines+markers',
            line=dict(color=theme['brand_primary'], width=4),
            marker=dict(size=8, color=theme['brand_primary']),
            fill='tonexty',
            fillcolor=f"rgba{tuple(list(px.colors.hex_to_rgb(theme['brand_primary'])) + [0.2])}",
            hovertemplate='<b>%{x}</b><br>Waste: %{y:.2f} tons<extra></extra>',
            name='Daily Waste Collection'
        )
    ])
    
    fig.update_layout(
        title={
            'text': '📈 Daily Waste Collection Trend (Last 7 Days)',
            'x': 0.5,
            'font': {'color': theme['text_primary'], 'size': 18}
        },
        xaxis={'title': 'Date', 'color': theme['text_secondary']},
        yaxis={'title': 'Waste Collected (Tons)', 'color': theme['text_secondary']},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': theme['text_primary']},
        margin=dict(l=50, r=50, t=60, b=50),
        height=400,  # LANDSCAPE MODE - fixed height
        showlegend=False
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_hourly_analysis_charts(data, theme):
    """Create hourly trip and net weight graphs (Last 7 days)"""
    if data.empty:
        return html.Div("No hourly data available", style={'color': theme['text_secondary']})
    
    # Group by hour for last 7 days
    hourly_stats = data.groupby('Hour').agg({
        'Net Weight': 'sum',
        'source_location': 'count'  # Count trips
    }).reset_index()
    
    hourly_stats.columns = ['Hour', 'Total_Weight', 'Trip_Count']
    hourly_stats['Total_Weight_Tons'] = hourly_stats['Total_Weight'] / 1000
    
    # Create subplots
    fig = go.Figure()
    
    # Add trips trace
    fig.add_trace(go.Scatter(
        x=hourly_stats['Hour'],
        y=hourly_stats['Trip_Count'],
        mode='lines+markers',
        name='Trips',
        line=dict(color=theme['brand_primary'], width=3),
        marker=dict(size=8),
        yaxis='y',
        hovertemplate='<b>Hour %{x}:00</b><br>Trips: %{y}<extra></extra>'
    ))
    
    # Add weight trace (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=hourly_stats['Hour'],
        y=hourly_stats['Total_Weight_Tons'],
        mode='lines+markers',
        name='Weight (Tons)',
        line=dict(color=theme['warning'], width=3),
        marker=dict(size=8),
        yaxis='y2',
        hovertemplate='<b>Hour %{x}:00</b><br>Weight: %{y:.2f} tons<extra></extra>'
    ))
    
    # Update layout with secondary y-axis
    fig.update_layout(
        title={
            'text': '⏰ Hourly Operations Analysis (Last 7 Days)',
            'x': 0.5,
            'font': {'color': theme['text_primary'], 'size': 18}
        },
        xaxis={'title': 'Hour of Day', 'color': theme['text_secondary']},
        yaxis={
            'title': 'Number of Trips',
            'color': theme['text_secondary'],
            'side': 'left'
        },
        yaxis2={
            'title': 'Weight (Tons)',
            'color': theme['text_secondary'],
            'side': 'right',
            'overlaying': 'y'
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': theme['text_primary']},
        legend=dict(x=0.02, y=0.98),
        margin=dict(l=50, r=70, t=60, b=50),
        height=400  # LANDSCAPE MODE - fixed height
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_cluster_performance_chart(data, theme):
    """Create cluster-wise performance visualization (Last 7 days)"""
    if data.empty:
        return create_empty_chart("No cluster data available", theme)
    
    # Group by cluster for last 7 days
    cluster_stats = data.groupby('Cluster').agg({
        'Net Weight': ['sum', 'mean', 'count'],
        'source_location': 'nunique'
    }).round(2)
    
    # Flatten column names
    cluster_stats.columns = ['Total_Weight', 'Avg_Weight', 'Trip_Count', 'Site_Count']
    cluster_stats = cluster_stats.reset_index()
    cluster_stats['Total_Weight_Tons'] = cluster_stats['Total_Weight'] / 1000
    cluster_stats['Avg_Weight_Tons'] = cluster_stats['Avg_Weight'] / 1000
    
    # Create horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(
            y=cluster_stats['Cluster'],
            x=cluster_stats['Total_Weight_Tons'],
            orientation='h',
            marker_color=theme['brand_primary'],
            text=[f"{weight:.1f}T ({trips} trips)" for weight, trips in 
                  zip(cluster_stats['Total_Weight_Tons'], cluster_stats['Trip_Count'])],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Total: %{x:.2f} tons<br>Trips: %{customdata}<br>Sites: %{customdata[1]}<extra></extra>',
            customdata=list(zip(cluster_stats['Trip_Count'], cluster_stats['Site_Count']))
        )
    ])
    
    fig.update_layout(
        title={
            'text': '🌐 Cluster-wise Performance (Last 7 Days)',
            'x': 0.5,
            'font': {'color': theme['text_primary'], 'size': 18}
        },
        xaxis={'title': 'Total Waste Collected (Tons)', 'color': theme['text_secondary']},
        yaxis={'title': 'Cluster', 'color': theme['text_secondary']},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': theme['text_primary']},
        margin=dict(l=200, r=50, t=60, b=50),
        height=400  # LANDSCAPE MODE - fixed height
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_empty_chart(message, theme):
    """Create empty chart with message"""
    return html.Div(
        message,
        style={
            'textAlign': 'center',
            'color': theme['text_secondary'],
            'padding': '2rem',
            'fontSize': '1.1rem',
            'backgroundColor': theme['card_bg'],
            'borderRadius': '8px',
            'border': f"1px solid {theme['accent_bg']}"
        }
    )

def create_hero_section(theme):
    """Create hero section for public landing - MATCH ORIGINAL SPACING"""
    return html.Div(
        className="hero-section",
        style={
            "background": f"linear-gradient(135deg, {theme['secondary_bg']} 0%, {theme['accent_bg']} 100%)",
            "borderRadius": "8px",  # Match original
            "padding": "1rem clamp(1rem, 3vw, 2rem)",  # Match original padding
            "marginBottom": "1rem",  # Reduced margin to match original
            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.3)",
            "textAlign": "center",
            "position": "relative",
            "overflow": "hidden",
            # MATCH ORIGINAL HEIGHT CONSTRAINTS
            "height": "clamp(80px, 7.5vh, 144px)",
            "minHeight": "80px",
            "maxHeight": "144px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center"
        },
        children=[
            html.Div(
                className="hero-content",
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",  # Changed from space-between to center
                    "gap": "clamp(0.75rem, 3vw, 2rem)",  # Match original responsive gap
                    "height": "100%"
                },
                children=[
                    # Left Logo - MATCH ORIGINAL RESPONSIVE SIZING
                    html.Img(
                        src="/assets/img/left.png",
                        alt="Left Organization Logo",
                        className="logo-left responsive-logo",
                        style={
                            "height": "clamp(52px, 5vh, 82px)",  # Match original responsive sizing
                            "width": "auto",
                            "objectFit": "contain",
                            "filter": "drop-shadow(1px 1px 4px rgba(0, 0, 0, 0.3))",
                            "transition": "all 0.3s ease",
                            "flexShrink": "0"
                        }
                    ),
                    
                    # Title Section - PROPER RESPONSIVE TEXT
                    html.Div(
                        className="hero-title-section",
                        style={
                            "flex": "1 1 auto", 
                            "textAlign": "center",
                            "padding": "0 1rem"  # Add padding to prevent text crowding
                        },
                        children=[
                            html.H1(
                                "Zigma Agency - Last 7 Days Analytics",
                                style={
                                    "color": theme["text_primary"],
                                    "fontSize": "clamp(1rem, 2.5vw, 1.75rem)",  # Smaller responsive text to fit height
                                    "fontWeight": "900",
                                    "margin": "0 0 0.25rem 0",
                                    "lineHeight": "1.1"
                                }
                            ),
                            html.P(
                                "Real-time Dashboard Data • Live Operations • Last 7 Days",
                                style={
                                    "color": theme["text_secondary"],
                                    "fontSize": "clamp(0.7rem, 1.5vw, 0.9rem)",  # Smaller subtitle
                                    "fontWeight": "500",
                                    "margin": "0",
                                    "lineHeight": "1.2"
                                }
                            )
                        ]
                    ),
                    
                    # Right Logo - MATCH ORIGINAL RESPONSIVE SIZING
                    html.Img(
                        src="/assets/img/right.png",
                        alt="Right Organization Logo",
                        className="logo-right responsive-logo",
                        style={
                            "height": "clamp(52px, 5vh, 82px)",  # Match original responsive sizing
                            "width": "auto",
                            "objectFit": "contain",
                            "filter": "drop-shadow(1px 1px 4px rgba(0, 0, 0, 0.3))",
                            "transition": "all 0.3s ease",
                            "flexShrink": "0"
                        }
                    )
                ]
            )
        ]
    )

def create_summary_metrics(data, theme):
    """Create summary metrics cards"""
    if data.empty:
        metrics = {
            'total_trips': 0,
            'total_waste': 0,
            'active_clusters': 0,
            'efficiency_score': 0
        }
    else:
        metrics = {
            'total_trips': len(data),
            'total_waste': data['Net Weight'].sum() / 1000,  # Convert to tons
            'active_clusters': data['Cluster'].nunique(),
            'efficiency_score': min(100, int((data['Net Weight'].mean() / 1000) * 20))  # Sample calculation
        }
    
    return html.Div(
        className="summary-metrics",
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
            "gap": "1.5rem",
            "margin": "2rem 0"
        },
        children=[
            create_metric_card("🚛", "Total Trips", f"{metrics['total_trips']:,}", "Collections", theme),
            create_metric_card("⚖️", "Total Waste", f"{metrics['total_waste']:.1f}", "Tons", theme),
            create_metric_card("🌐", "Active Clusters", f"{metrics['active_clusters']}", "Regions", theme),
            create_metric_card("📊", "Efficiency", f"{metrics['efficiency_score']}%", "Score", theme)
        ]
    )

def create_metric_card(icon, title, value, unit, theme):
    """Create individual metric card"""
    return html.Div(
        className="metric-card",
        style={
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['accent_bg']}",
            "padding": "1.5rem",
            "textAlign": "center",
            "transition": "all 0.3s ease",
            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.2)",
            "position": "relative",
            "overflow": "hidden"
        },
        children=[
            html.Div(
                icon,
                style={
                    "fontSize": "2.5rem",
                    "marginBottom": "1rem",
                    "filter": "drop-shadow(0 2px 4px rgba(0,0,0,0.3))"
                }
            ),
            html.H3(
                value,
                style={
                    "fontSize": "2rem",
                    "fontWeight": "800",
                    "color": theme["brand_primary"],
                    "margin": "0.5rem 0",
                    "lineHeight": "1"
                }
            ),
            html.P(
                title,
                style={
                    "fontSize": "1rem",
                    "color": theme["text_secondary"],
                    "fontWeight": "600",
                    "margin": "0.25rem 0"
                }
            ),
            html.P(
                unit,
                style={
                    "fontSize": "0.9rem",
                    "color": theme["success"],
                    "fontWeight": "500",
                    "margin": "0"
                }
            )
        ]
    )

def build_enhanced_public_layout(theme_name="dark", is_authenticated=False, user_data=None):
    """
    Build the enhanced public layout with dashboard data visualizations
    NO HEADER - Only hover overlay for navigation
    
    Args:
        theme_name (str): Current theme name
        is_authenticated (bool): Authentication status
        user_data (dict): User data if authenticated
        
    Returns:
        html.Div: Complete enhanced public layout WITHOUT header
    """
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    # Load dashboard data
    dashboard_data = load_dashboard_data()
    
    return html.Div(
        className="enhanced-public-layout",
        style=theme_styles["container_style"],
        children=[
            # ONLY hover overlay banner - NO HEADER
            create_hover_overlay_banner(theme_name, is_authenticated, user_data),
            
            # Main content container - RESTORE ORIGINAL LAYOUT
            html.Div(
                className="main-content",
                style={
                    "maxWidth": "1600px",  # INCREASED tile size
                    "margin": "0 auto",
                    "padding": "1rem"
                },
                children=[
                    # Hero section - ORIGINAL DESIGN
                    create_hero_section(theme),
                    
                    # Summary metrics with ID for callbacks
                    html.Div(
                        id='public-summary-metrics',
                        children=[create_summary_metrics(dashboard_data, theme)]
                    ),
                    
                    # Data visualizations grid - LARGER TILES
                    html.Div(
                        className="visualizations-grid",
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(auto-fit, minmax(600px, 1fr))",  # INCREASED minimum size
                            "gap": "2rem",
                            "margin": "2rem 0"
                        },
                        children=[
                            # Weekly trips histogram
                            html.Div(
                                id='public-weekly-histogram',
                                className="chart-container",
                                style={
                                    "backgroundColor": theme["card_bg"],
                                    "borderRadius": "12px",
                                    "padding": "2rem",  # INCREASED padding
                                    "border": f"1px solid {theme['accent_bg']}",
                                    "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.1)",
                                    "minHeight": "450px"  # LARGER minimum height
                                },
                                children=[create_weekly_trips_histogram(dashboard_data, theme)]
                            ),
                            
                            # Daily waste line chart
                            html.Div(
                                id='public-daily-line-chart',
                                className="chart-container",
                                style={
                                    "backgroundColor": theme["card_bg"],
                                    "borderRadius": "12px",
                                    "padding": "2rem",  # INCREASED padding
                                    "border": f"1px solid {theme['accent_bg']}",
                                    "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.1)",
                                    "minHeight": "450px"  # LARGER minimum height
                                },
                                children=[create_daily_waste_line_chart(dashboard_data, theme)]
                            ),
                            
                            # Hourly analysis
                            html.Div(
                                id='public-hourly-analysis',
                                className="chart-container",
                                style={
                                    "backgroundColor": theme["card_bg"],
                                    "borderRadius": "12px",
                                    "padding": "2rem",  # INCREASED padding
                                    "border": f"1px solid {theme['accent_bg']}",
                                    "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.1)",
                                    "minHeight": "450px"  # LARGER minimum height
                                },
                                children=[create_hourly_analysis_charts(dashboard_data, theme)]
                            ),
                            
                            # Cluster performance
                            html.Div(
                                id='public-cluster-performance',
                                className="chart-container",
                                style={
                                    "backgroundColor": theme["card_bg"],
                                    "borderRadius": "12px",
                                    "padding": "2rem",  # INCREASED padding
                                    "border": f"1px solid {theme['accent_bg']}",
                                    "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.1)",
                                    "minHeight": "450px"  # LARGER minimum height
                                },
                                children=[create_cluster_performance_chart(dashboard_data, theme)]
                            )
                        ]
                    ),
                    
                    # Footer info
                    html.Div(
                        className="footer-info",
                        style={
                            "textAlign": "center",
                            "padding": "2rem",
                            "backgroundColor": theme["secondary_bg"],
                            "borderRadius": "8px",
                            "marginTop": "2rem",
                            "border": f"1px solid {theme['accent_bg']}"
                        },
                        children=[
                            html.P([
                                html.Span("📊", style={"marginRight": "0.5rem"}),
                                "Live dashboard data (Last 7 Days) automatically updates • ",
                                html.Span("🔄", style={"marginLeft": "0.5rem", "marginRight": "0.5rem"}),
                                html.Span(id='public-last-updated', children=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
                                " • ",
                                html.Span("🏢", style={"marginLeft": "0.5rem", "marginRight": "0.5rem"}),
                                "Zigma Agency Operations"
                            ], style={
                                "color": theme["text_secondary"],
                                "fontSize": "0.9rem",
                                "margin": "0"
                            })
                        ]
                    )
                ]
            ),
            
            # Data refresh interval and loading indicator
            dcc.Interval(
                id='public-data-refresh',
                interval=5*60*1000,  # 5 minutes
                n_intervals=0
            ),
            
            # Hidden loading indicator
            html.Div(
                id='public-loading-indicator',
                style={'display': 'none'}
            )
        ]
    )

# Export the main function
__all__ = ['build_enhanced_public_layout', 'load_dashboard_data']