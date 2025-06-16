# layouts/enhanced_public_layout_with_csv.py
"""
Enhanced Public Landing Page Layout with CSV Data Integration
Displays Agency name, Cluster name, and charts from csv_outputs_data_viz.csv
"""

from dash import html, dcc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import logging
import os

from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner

logger = logging.getLogger(__name__)

def load_csv_visualization_data():
    """Load data from csv_outputs_data_viz.csv"""
    try:
        csv_path = 'data/csv_outputs_data_viz.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            logger.info(f"✅ Loaded {len(df)} records from CSV visualization data")
            
            # Convert date column to datetime if needed
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            return df
        else:
            logger.warning(f"CSV file not found at {csv_path}")
            return create_sample_csv_data()
    except Exception as e:
        logger.error(f"Error loading CSV data: {e}")
        return create_sample_csv_data()

def create_sample_csv_data():
    """Create sample data matching the CSV structure"""
    return pd.DataFrame({
        'Agency': ['Swaccha Andhra Corporation'] * 10,
        'Sub_contractor': ['Contractor A', 'Contractor B'] * 5,
        'Cluster': ['Nellore Municipal Corporation', 'Chittor', 'Tirupathi', 'GVMC', 'Kurnool'] * 2,
        'Site': ['Site A', 'Site B', 'Site C'] * 3 + ['Site D'],
        'Machines': ['Machine Type 1', 'Machine Type 2'] * 5,
        'Total_capacity_per_day': [100, 150, 200, 250, 300] * 2,
        'Total_waste_to_be_remediated': ['1000 tons', '1500 tons'] * 5,
        'date': [datetime.now().strftime('%Y-%m-%d')] * 10,
        'ticket_no': [f'TKT{i:03d}' for i in range(1, 11)],
        'net_weight_calculated': [50, 75, 100, 125, 150] * 2
    })

def create_agency_chart(df, theme):
    """Create a chart showing agency distribution"""
    if df.empty or 'Agency' not in df.columns:
        return html.Div("No agency data available", style={'color': theme['text_secondary']})
    
    agency_counts = df['Agency'].value_counts()
    
    fig = go.Figure(data=[
        go.Bar(
            x=agency_counts.values,
            y=agency_counts.index,
            orientation='h',
            marker_color=theme['brand_primary'],
            hovertemplate='<b>%{y}</b><br>Projects: %{x}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=theme['text_primary'], size=10),
        margin=dict(l=0, r=0, t=0, b=0),
        height=120,
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=9)
        )
    )
    
    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False},
        style={'height': '120px'}
    )

def create_cluster_chart(df, theme):
    """Create a chart showing cluster distribution"""
    if df.empty or 'Cluster' not in df.columns:
        return html.Div("No cluster data available", style={'color': theme['text_secondary']})
    
    cluster_counts = df['Cluster'].value_counts().head(5)  # Top 5 clusters
    
    fig = go.Figure(data=[
        go.Pie(
            labels=cluster_counts.index,
            values=cluster_counts.values,
            hole=0.4,
            marker_colors=px.colors.qualitative.Set3[:len(cluster_counts)],
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=theme['text_primary'], size=9),
        margin=dict(l=0, r=0, t=0, b=0),
        height=120,
        showlegend=False
    )
    
    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False},
        style={'height': '120px'}
    )

def create_weight_trend_chart(df, theme):
    """Create a chart showing weight trends"""
    if df.empty or 'net_weight_calculated' not in df.columns:
        return html.Div("No weight data available", style={'color': theme['text_secondary']})
    
    # Group by date if available, otherwise just show distribution
    if 'date' in df.columns and df['date'].notna().any():
        daily_weights = df.groupby('date')['net_weight_calculated'].sum().reset_index()
        daily_weights = daily_weights.sort_values('date').tail(7)  # Last 7 days
        
        fig = go.Figure(data=[
            go.Scatter(
                x=daily_weights['date'],
                y=daily_weights['net_weight_calculated'],
                mode='lines+markers',
                line=dict(color=theme['success'], width=2),
                marker=dict(color=theme['success'], size=6),
                hovertemplate='<b>%{x}</b><br>Weight: %{y} kg<extra></extra>'
            )
        ])
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=theme['text_primary'], size=9),
            margin=dict(l=0, r=0, t=0, b=0),
            height=100,
            showlegend=False,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
    else:
        # Show histogram of weights
        fig = go.Figure(data=[
            go.Histogram(
                x=df['net_weight_calculated'],
                nbinsx=10,
                marker_color=theme['success'],
                hovertemplate='Weight Range: %{x}<br>Count: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=theme['text_primary'], size=9),
            margin=dict(l=0, r=0, t=0, b=0),
            height=100,
            showlegend=False,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
    
    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False},
        style={'height': '100px'}
    )

def create_capacity_chart(df, theme):
    """Create a chart showing daily capacity"""
    if df.empty or 'Total_capacity_per_day' not in df.columns:
        return html.Div("No capacity data available", style={'color': theme['text_secondary']})
    
    capacity_data = df['Total_capacity_per_day'].value_counts().head(5)
    
    fig = go.Figure(data=[
        go.Bar(
            x=capacity_data.index,
            y=capacity_data.values,
            marker_color=theme['warning'],
            hovertemplate='Capacity: %{x}<br>Sites: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=theme['text_primary'], size=9),
        margin=dict(l=0, r=0, t=0, b=0),
        height=100,
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False)
    )
    
    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False},
        style={'height': '100px'}
    )

def get_enhanced_metric_cards_with_csv():
    """Get enhanced metric cards using CSV data"""
    # Load CSV data
    df = load_csv_visualization_data()
    
    # Get primary agency and cluster
    primary_agency = df['Agency'].mode().iloc[0] if not df.empty and 'Agency' in df.columns else "No Agency Data"
    primary_cluster = df['Cluster'].mode().iloc[0] if not df.empty and 'Cluster' in df.columns else "No Cluster Data"
    
    # Calculate metrics from CSV
    total_sites = df['Site'].nunique() if not df.empty and 'Site' in df.columns else 0
    total_weight = df['net_weight_calculated'].sum() if not df.empty and 'net_weight_calculated' in df.columns else 0
    total_capacity = df['Total_capacity_per_day'].sum() if not df.empty and 'Total_capacity_per_day' in df.columns else 0
    active_clusters = df['Cluster'].nunique() if not df.empty and 'Cluster' in df.columns else 0
    
    return [
        {
            "icon": "🏢",
            "title": "Agency Name",
            "value": primary_agency,
            "unit": "Primary",
            "status": "online",
            "chart_data": df,
            "chart_type": "agency"
        },
        {
            "icon": "🗺️",
            "title": "Cluster Name", 
            "value": primary_cluster,
            "unit": "Primary",
            "status": "online",
            "chart_data": df,
            "chart_type": "cluster"
        },
        {
            "icon": "📍",
            "title": "Total Sites",
            "value": str(total_sites),
            "unit": "Active",
            "status": "online",
            "chart_data": df,
            "chart_type": "sites"
        },
        {
            "icon": "⚖️",
            "title": "Total Weight",
            "value": f"{total_weight:,.0f}",
            "unit": "kg",
            "status": "online",
            "chart_data": df,
            "chart_type": "weight"
        },
        {
            "icon": "🏭",
            "title": "Daily Capacity",
            "value": f"{total_capacity:,.0f}",
            "unit": "Per Day",
            "status": "info",
            "chart_data": df,
            "chart_type": "capacity"
        },
        {
            "icon": "🌐",
            "title": "Active Clusters",
            "value": str(active_clusters),
            "unit": "Regions",
            "status": "online"
        },
        {
            "icon": "🎫",
            "title": "Total Tickets",
            "value": str(len(df)),
            "unit": "Records",
            "status": "info"
        },
        {
            "icon": "📊",
            "title": "Data Points",
            "value": f"{len(df) * len(df.columns) if not df.empty else 0:,}",
            "unit": "Records",
            "status": "info"
        }
    ]

def create_enhanced_metric_cards_grid(metrics_data, theme_styles):
    """Create enhanced metric cards grid with charts from CSV data"""
    cards = []
    theme = theme_styles["theme"]
    
    for i, metric in enumerate(metrics_data):
        status_class = f"status-{metric.get('status', 'info')}"
        
        # Create chart based on type
        chart_element = None
        if metric.get('chart_data') is not None and not metric['chart_data'].empty:
            chart_type = metric.get('chart_type')
            if chart_type == 'agency':
                chart_element = create_agency_chart(metric['chart_data'], theme)
            elif chart_type == 'cluster':
                chart_element = create_cluster_chart(metric['chart_data'], theme)
            elif chart_type == 'weight':
                chart_element = create_weight_trend_chart(metric['chart_data'], theme)
            elif chart_type == 'capacity':
                chart_element = create_capacity_chart(metric['chart_data'], theme)
        
        # Card content
        card_content = [
            html.Div(
                metric["icon"],
                className="metric-icon"
            ),
            html.Div(
                [
                    metric["title"],
                    html.Span(
                        className=f"status-indicator {status_class}",
                        title=f"Status: {metric.get('status', 'info')}"
                    ) if metric.get('status') else ""
                ],
                className="metric-title"
            ),
            html.Div(
                metric["value"],
                className="metric-value",
                style={'marginBottom': '0.5rem' if chart_element else '0'}
            ),
            html.Div(
                metric["unit"],
                className="metric-unit"
            )
        ]
        
        # Add chart if available
        if chart_element:
            card_content.append(html.Div(
                chart_element,
                style={'marginTop': '0.5rem'}
            ))
        
        card = html.Div(
            className="metric-card",
            children=card_content
        )
        cards.append(card)
    
    return html.Div(
        className="cards-grid",
        children=cards
    )

def build_enhanced_public_layout(theme_name="dark", is_authenticated=False, user_data=None):
    """
    Build the enhanced public layout with CSV data integration
    """
    # Use existing theme system
    theme_styles = get_theme_styles(theme_name)
    metrics_data = get_enhanced_metric_cards_with_csv()
    
    return html.Div(
        className="public-layout",
        # Apply theme CSS variables for compatibility
        style={
            "--primary-bg": theme_styles["theme"]["primary_bg"],
            "--secondary-bg": theme_styles["theme"]["secondary_bg"],
            "--accent-bg": theme_styles["theme"]["accent_bg"],
            "--card-bg": theme_styles["theme"]["card_bg"],
            "--text-primary": theme_styles["theme"]["text_primary"],
            "--text-secondary": theme_styles["theme"]["text_secondary"],
            "--brand-primary": theme_styles["theme"]["brand_primary"],
            "--border-light": theme_styles["theme"].get("border_light", theme_styles["theme"]["accent_bg"]),
            "--success": theme_styles["theme"]["success"],
            "--warning": theme_styles["theme"]["warning"],
            "--error": theme_styles["theme"]["error"],
            "--info": theme_styles["theme"]["info"]
        },
        children=[
            # Hover overlay banner (admin access)
            create_hover_overlay_banner(theme_name),
            
            # Main content area
            html.Div(
                className="main-content",
                children=[
                    # Hero section with logos and title
                    html.Div(
                        className="hero-section",
                        children=[
                            html.Div(
                                className="hero-content",
                                children=[
                                    # Left Logo
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "center",
                                            "height": "100%",
                                            "flexShrink": "0"
                                        },
                                        children=[
                                            html.Img(
                                                src="/assets/img/left.png",
                                                alt="Left Organization Logo",
                                                className="responsive-logo",
                                                style={
                                                    "height": "clamp(40px, 8vh, 60px)",
                                                    "width": "auto",
                                                    "objectFit": "contain",
                                                    "filter": "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3))"
                                                }
                                            )
                                        ]
                                    ),
                                    
                                    # Title Section
                                    html.Div(
                                        className="hero-title-section",
                                        style={
                                            "textAlign": "center",
                                            "flex": "1",
                                            "padding": "0 clamp(1rem, 3vw, 2rem)",
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "justifyContent": "center",
                                            "alignItems": "center",
                                            "height": "100%"
                                        },
                                        children=[
                                            html.H1(
                                                "Swaccha Andhra Corporation",
                                                className="hero-title",
                                                style={
                                                    "margin": "0",
                                                    "padding": "0",
                                                    "fontSize": "clamp(1.5rem, 4vw, 2.5rem)",
                                                    "fontWeight": "800",
                                                    "lineHeight": "1.1",
                                                    "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.3)",
                                                    "letterSpacing": "-0.5px"
                                                }
                                            ),
                                            html.P(
                                                "Real Time Legacy Waste Remediation Progress Tracker",
                                                className="hero-subtitle",
                                                style={
                                                    "margin": "0.25rem 0 0 0",
                                                    "padding": "0",
                                                    "fontSize": "clamp(0.8rem, 1.8vw, 1rem)",
                                                    "fontWeight": "500",
                                                    "lineHeight": "1.3",
                                                    "opacity": "0.9",
                                                    "textAlign": "center"
                                                }
                                            )
                                        ]
                                    ),
                                    
                                    # Right Logo
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "center",
                                            "height": "100%",
                                            "flexShrink": "0"
                                        },
                                        children=[
                                            html.Img(
                                                src="/assets/img/right.png",
                                                alt="Right Organization Logo",
                                                className="responsive-logo",
                                                style={
                                                    "height": "clamp(40px, 8vh, 60px)",
                                                    "width": "auto",
                                                    "objectFit": "contain",
                                                    "filter": "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3))"
                                                }
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Enhanced metric cards grid with charts
                    create_enhanced_metric_cards_grid(metrics_data, theme_styles)
                ]
            )
        ]
    )

# Export the main function
__all__ = ['build_enhanced_public_layout', 'get_enhanced_metric_cards_with_csv']