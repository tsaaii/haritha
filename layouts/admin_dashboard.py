# layouts/dashboard_layout.py
"""
Enhanced Dashboard Layout for Swaccha Andhra
Comprehensive dashboard with real-time data, charts, and interactive components
"""

from dash import html, dcc, dash_table
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random

from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner
from components.cards.stat_card import create_stat_card, create_trend_stat_card, create_compact_stat_card
from components.cards.status_indicators import create_status_indicator, create_detailed_status_indicator


def generate_sample_data():
    """Generate realistic sample data for the dashboard"""
    
    # Districts data
    districts = [
        "Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", 
        "Rajahmundry", "Tirupati", "Kakinada", "Anantapur", "Kadapa",
        "Eluru", "Ongole", "Chittoor"
    ]
    
    # Generate time series data for charts
    dates = pd.date_range(start='2024-01-01', end='2025-06-08', freq='D')
    
    # Waste collection trends
    waste_data = []
    base_collection = 2000
    for i, date in enumerate(dates):
        daily_collection = base_collection + (i * 2) + random.randint(-200, 300)
        waste_data.append({
            'date': date,
            'waste_collected': daily_collection,
            'recycled': daily_collection * 0.78 + random.randint(-50, 50),
            'composted': daily_collection * 0.15 + random.randint(-20, 30),
            'landfill': daily_collection * 0.07 + random.randint(-10, 20)
        })
    
    # District performance data
    district_data = []
    for district in districts:
        district_data.append({
            'district': district,
            'cleanliness_score': random.randint(85, 98),
            'waste_processed': random.randint(800, 2500),
            'recycling_rate': random.randint(70, 85),
            'population_covered': random.randint(85, 99),
            'complaints_resolved': random.randint(92, 99),
            'green_initiatives': random.randint(15, 45)
        })
    
    return {
        'waste_trends': pd.DataFrame(waste_data),
        'district_performance': pd.DataFrame(district_data),
        'last_updated': datetime.now()
    }


def create_kpi_section(theme_styles, user_data):
    """Create main KPI cards section"""
    theme = theme_styles["theme"]
    
    # Generate current metrics
    current_metrics = {
        'total_waste': f"{random.randint(240, 280)}K",
        'recycling_rate': f"{random.randint(76, 82)}%",
        'districts_covered': "13",
        'cleanliness_score': f"{random.randint(92, 96)}.{random.randint(1, 9)}",
        'active_users': f"{random.randint(1200, 1500):,}",
        'complaints_resolved': f"{random.randint(95, 99)}%"
    }
    
    # Trend indicators
    trends = ['up', 'up', 'neutral', 'up', 'up', 'up']
    trend_values = ['+5.2%', '+2.1%', '0%', '+1.8%', '+12%', '+3.5%']
    
    kpi_cards = [
        create_trend_stat_card("🗑️", "Total Waste Processed", current_metrics['total_waste'], 
                             "Tons This Month", trend_values[0], trends[0], theme_styles),
        create_trend_stat_card("♻️", "Recycling Rate", current_metrics['recycling_rate'], 
                             "Current Efficiency", trend_values[1], trends[1], theme_styles),
        create_trend_stat_card("🏘️", "Districts Monitored", current_metrics['districts_covered'], 
                             "Complete Coverage", trend_values[2], trends[2], theme_styles),
        create_trend_stat_card("🌟", "Cleanliness Score", current_metrics['cleanliness_score'], 
                             "State Average", trend_values[3], trends[3], theme_styles),
        create_trend_stat_card("👥", "Active Users", current_metrics['active_users'], 
                             "Citizens Engaged", trend_values[4], trends[4], theme_styles),
        create_trend_stat_card("✅", "Issues Resolved", current_metrics['complaints_resolved'], 
                             "Success Rate", trend_values[5], trends[5], theme_styles)
    ]
    
    return html.Div(
        className="kpi-section",
        style={
            "margin": "2rem 0",
            "padding": "1.5rem",
            "backgroundColor": theme["accent_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['brand_primary']}"
        },
        children=[
            html.H2(
                "📊 Key Performance Indicators",
                style={
                    "color": theme["text_primary"],
                    "textAlign": "center",
                    "marginBottom": "2rem",
                    "fontSize": "1.8rem"
                }
            ),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
                    "gap": "1.5rem"
                },
                children=kpi_cards
            )
        ]
    )


def create_charts_section(theme_styles, data):
    """Create interactive charts section"""
    theme = theme_styles["theme"]
    
    # Waste trends chart
    waste_trends_fig = create_waste_trends_chart(data['waste_trends'], theme)
    
    # District performance chart
    district_performance_fig = create_district_performance_chart(data['district_performance'], theme)
    
    # Recycling breakdown pie chart
    recycling_breakdown_fig = create_recycling_breakdown_chart(theme)
    
    # Monthly progress chart
    monthly_progress_fig = create_monthly_progress_chart(theme)
    
    return html.Div(
        className="charts-section",
        style={
            "margin": "2rem 0",
            "display": "grid",
            "gridTemplateColumns": "2fr 1fr",
            "gap": "2rem"
        },
        children=[
            # Left column - main charts
            html.Div([
                # Waste trends chart
                html.Div(
                    style={
                        "backgroundColor": theme["card_bg"],
                        "borderRadius": "12px",
                        "border": f"2px solid {theme['accent_bg']}",
                        "padding": "1.5rem",
                        "marginBottom": "2rem"
                    },
                    children=[
                        html.H3(
                            "📈 Waste Collection Trends",
                            style={"color": theme["text_primary"], "marginBottom": "1rem"}
                        ),
                        dcc.Graph(
                            id="waste-trends-chart",
                            figure=waste_trends_fig,
                            config={'displayModeBar': False},
                            style={"height": "300px"}
                        )
                    ]
                ),
                
                # District performance chart
                html.Div(
                    style={
                        "backgroundColor": theme["card_bg"],
                        "borderRadius": "12px",
                        "border": f"2px solid {theme['accent_bg']}",
                        "padding": "1.5rem"
                    },
                    children=[
                        html.H3(
                            "🏆 District Performance Comparison",
                            style={"color": theme["text_primary"], "marginBottom": "1rem"}
                        ),
                        dcc.Graph(
                            id="district-performance-chart",
                            figure=district_performance_fig,
                            config={'displayModeBar': False},
                            style={"height": "350px"}
                        )
                    ]
                )
            ]),
            
            # Right column - smaller charts
            html.Div([
                # Recycling breakdown
                html.Div(
                    style={
                        "backgroundColor": theme["card_bg"],
                        "borderRadius": "12px",
                        "border": f"2px solid {theme['accent_bg']}",
                        "padding": "1.5rem",
                        "marginBottom": "2rem"
                    },
                    children=[
                        html.H3(
                            "♻️ Recycling Breakdown",
                            style={"color": theme["text_primary"], "marginBottom": "1rem"}
                        ),
                        dcc.Graph(
                            id="recycling-breakdown-chart",
                            figure=recycling_breakdown_fig,
                            config={'displayModeBar': False},
                            style={"height": "250px"}
                        )
                    ]
                ),
                
                # Monthly progress
                html.Div(
                    style={
                        "backgroundColor": theme["card_bg"],
                        "borderRadius": "12px",
                        "border": f"2px solid {theme['accent_bg']}",
                        "padding": "1.5rem"
                    },
                    children=[
                        html.H3(
                            "📅 Monthly Progress",
                            style={"color": theme["text_primary"], "marginBottom": "1rem"}
                        ),
                        dcc.Graph(
                            id="monthly-progress-chart",
                            figure=monthly_progress_fig,
                            config={'displayModeBar': False},
                            style={"height": "250px"}
                        )
                    ]
                )
            ])
        ]
    )


def create_waste_trends_chart(waste_data, theme):
    """Create waste collection trends chart"""
    fig = go.Figure()
    
    # Add traces for different waste types
    fig.add_trace(go.Scatter(
        x=waste_data['date'],
        y=waste_data['waste_collected'],
        mode='lines+markers',
        name='Total Collected',
        line=dict(color='#3182CE', width=3),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=waste_data['date'],
        y=waste_data['recycled'],
        mode='lines',
        name='Recycled',
        line=dict(color='#38A169', width=2),
        fill='tonexty'
    ))
    
    fig.add_trace(go.Scatter(
        x=waste_data['date'],
        y=waste_data['composted'],
        mode='lines',
        name='Composted',
        line=dict(color='#DD6B20', width=2)
    ))
    
    fig.update_layout(
        plot_bgcolor=theme["accent_bg"],
        paper_bgcolor=theme["card_bg"],
        font=dict(color=theme["text_primary"], family="Inter"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(
            gridcolor=theme["border_light"],
            showgrid=True
        ),
        yaxis=dict(
            gridcolor=theme["border_light"],
            showgrid=True,
            title="Tons"
        )
    )
    
    return fig


def create_district_performance_chart(district_data, theme):
    """Create district performance comparison chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=district_data['district'],
        y=district_data['cleanliness_score'],
        name='Cleanliness Score',
        marker_color='#3182CE',
        text=district_data['cleanliness_score'],
        textposition='auto'
    ))
    
    fig.add_trace(go.Scatter(
        x=district_data['district'],
        y=district_data['recycling_rate'],
        mode='lines+markers',
        name='Recycling Rate %',
        yaxis='y2',
        line=dict(color='#38A169', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        plot_bgcolor=theme["accent_bg"],
        paper_bgcolor=theme["card_bg"],
        font=dict(color=theme["text_primary"], family="Inter"),
        xaxis=dict(
            title="Districts",
            tickangle=45
        ),
        yaxis=dict(
            title="Cleanliness Score",
            side="left"
        ),
        yaxis2=dict(
            title="Recycling Rate (%)",
            side="right",
            overlaying="y"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=40, b=80)
    )
    
    return fig


def create_recycling_breakdown_chart(theme):
    """Create recycling breakdown pie chart"""
    categories = ['Plastic', 'Paper', 'Organic', 'Metal', 'Glass', 'Other']
    values = [28, 25, 20, 12, 10, 5]
    colors = ['#3182CE', '#38A169', '#DD6B20', '#9F7AEA', '#E53E3E', '#319795']
    
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=values,
        hole=0.4,
        marker=dict(colors=colors, line=dict(color=theme["card_bg"], width=2))
    )])
    
    fig.update_layout(
        plot_bgcolor=theme["accent_bg"],
        paper_bgcolor=theme["card_bg"],
        font=dict(color=theme["text_primary"], family="Inter"),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return fig


def create_monthly_progress_chart(theme):
    """Create monthly progress gauge chart"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    targets = [100, 100, 100, 100, 100, 100]
    achieved = [95, 102, 98, 105, 99, 108]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=months,
        y=targets,
        name='Target',
        marker_color='rgba(49, 130, 206, 0.3)',
        text=[f'{v}%' for v in targets],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        x=months,
        y=achieved,
        name='Achieved',
        marker_color='#38A169',
        text=[f'{v}%' for v in achieved],
        textposition='auto'
    ))
    
    fig.update_layout(
        plot_bgcolor=theme["accent_bg"],
        paper_bgcolor=theme["card_bg"],
        font=dict(color=theme["text_primary"], family="Inter"),
        xaxis=dict(title="Month"),
        yaxis=dict(title="Progress %"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        barmode='group'
    )
    
    return fig


def create_data_table_section(theme_styles, data):
    """Create interactive data table section"""
    theme = theme_styles["theme"]
    
    return html.Div(
        className="data-table-section",
        style={
            "margin": "2rem 0",
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['accent_bg']}",
            "padding": "1.5rem"
        },
        children=[
            html.H3(
                "📋 District Performance Table",
                style={
                    "color": theme["text_primary"],
                    "marginBottom": "1.5rem"
                }
            ),
            dash_table.DataTable(
                id='district-performance-table',
                data=data['district_performance'].to_dict('records'),
                columns=[
                    {"name": "District", "id": "district", "type": "text"},
                    {"name": "Cleanliness Score", "id": "cleanliness_score", "type": "numeric", "format": {"specifier": ".0f"}},
                    {"name": "Waste Processed (Tons)", "id": "waste_processed", "type": "numeric", "format": {"specifier": ","}},
                    {"name": "Recycling Rate (%)", "id": "recycling_rate", "type": "numeric", "format": {"specifier": ".0f"}},
                    {"name": "Population Coverage (%)", "id": "population_covered", "type": "numeric", "format": {"specifier": ".0f"}},
                    {"name": "Complaints Resolved (%)", "id": "complaints_resolved", "type": "numeric", "format": {"specifier": ".0f"}},
                    {"name": "Green Initiatives", "id": "green_initiatives", "type": "numeric"}
                ],
                style_cell={
                    'backgroundColor': theme["accent_bg"],
                    'color': theme["text_primary"],
                    'textAlign': 'center',
                    'fontFamily': 'Inter',
                    'fontSize': '14px',
                    'padding': '12px'
                },
                style_header={
                    'backgroundColor': theme["brand_primary"],
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': theme["secondary_bg"]
                    },
                    {
                        'if': {
                            'filter_query': '{cleanliness_score} > 95',
                            'column_id': 'cleanliness_score'
                        },
                        'backgroundColor': '#2D5A31',
                        'color': 'white',
                    },
                    {
                        'if': {
                            'filter_query': '{recycling_rate} > 80',
                            'column_id': 'recycling_rate'
                        },
                        'backgroundColor': '#2D5A31',
                        'color': 'white',
                    }
                ],
                sort_action="native",
                filter_action="native",
                page_action="native",
                page_current=0,
                page_size=10,
                style_as_list_view=True
            )
        ]
    )


def create_alerts_section(theme_styles):
    """Create alerts and notifications section"""
    theme = theme_styles["theme"]
    
    alerts = [
        {
            "type": "success",
            "icon": "✅",
            "title": "Target Achieved",
            "message": "Visakhapatnam district exceeded recycling target by 5%",
            "time": "2 hours ago"
        },
        {
            "type": "warning", 
            "icon": "⚠️",
            "title": "Maintenance Required",
            "message": "Processing facility in Guntur requires scheduled maintenance",
            "time": "4 hours ago"
        },
        {
            "type": "info",
            "icon": "ℹ️",
            "title": "New Initiative",
            "message": "Green waste composting program launched in 3 districts",
            "time": "1 day ago"
        }
    ]
    
    alert_colors = {
        "success": theme["success"],
        "warning": theme["warning"],
        "error": theme["error"],
        "info": theme["info"]
    }
    
    return html.Div(
        className="alerts-section",
        style={
            "margin": "2rem 0",
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['accent_bg']}",
            "padding": "1.5rem"
        },
        children=[
            html.H3(
                "🔔 Recent Alerts & Updates",
                style={
                    "color": theme["text_primary"],
                    "marginBottom": "1.5rem"
                }
            ),
            html.Div([
                html.Div(
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "1rem",
                        "padding": "1rem",
                        "marginBottom": "1rem",
                        "backgroundColor": theme["accent_bg"],
                        "borderRadius": "8px",
                        "borderLeft": f"4px solid {alert_colors[alert['type']]}"
                    },
                    children=[
                        html.Div(
                            alert["icon"],
                            style={
                                "fontSize": "1.5rem",
                                "color": alert_colors[alert["type"]]
                            }
                        ),
                        html.Div([
                            html.H4(
                                alert["title"],
                                style={
                                    "color": theme["text_primary"],
                                    "margin": "0 0 0.25rem 0",
                                    "fontSize": "1rem"
                                }
                            ),
                            html.P(
                                alert["message"],
                                style={
                                    "color": theme["text_secondary"],
                                    "margin": "0 0 0.25rem 0",
                                    "fontSize": "0.9rem"
                                }
                            ),
                            html.P(
                                alert["time"],
                                style={
                                    "color": theme["text_muted"] if "text_muted" in theme else theme["text_secondary"],
                                    "margin": "0",
                                    "fontSize": "0.8rem",
                                    "fontStyle": "italic"
                                }
                            )
                        ], style={"flex": "1"})
                    ]
                ) for alert in alerts
            ])
        ]
    )


def create_quick_actions_section(theme_styles):
    """Create quick actions panel"""
    theme = theme_styles["theme"]
    
    actions = [
        {"icon": "📊", "title": "Generate Report", "description": "Create detailed analytics report"},
        {"icon": "📤", "title": "Export Data", "description": "Download system data as CSV/Excel"},
        {"icon": "👥", "title": "Manage Users", "description": "Add or modify user permissions"},
        {"icon": "⚙️", "title": "System Settings", "description": "Configure dashboard parameters"},
        {"icon": "🔄", "title": "Sync Data", "description": "Force data synchronization"},
        {"icon": "📱", "title": "Mobile App", "description": "Download mobile companion app"}
    ]
    
    return html.Div(
        className="quick-actions-section",
        style={
            "margin": "2rem 0",
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['accent_bg']}",
            "padding": "1.5rem"
        },
        children=[
            html.H3(
                "⚡ Quick Actions",
                style={
                    "color": theme["text_primary"],
                    "marginBottom": "1.5rem"
                }
            ),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                    "gap": "1rem"
                },
                children=[
                    html.Div(
                        style={
                            "backgroundColor": theme["accent_bg"],
                            "borderRadius": "8px",
                            "padding": "1.5rem",
                            "textAlign": "center",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease",
                            "border": f"1px solid {theme['border_light']}"
                        },
                        children=[
                            html.Div(
                                action["icon"],
                                style={
                                    "fontSize": "2.5rem",
                                    "marginBottom": "1rem"
                                }
                            ),
                            html.H4(
                                action["title"],
                                style={
                                    "color": theme["text_primary"],
                                    "fontSize": "1.1rem",
                                    "fontWeight": "600",
                                    "marginBottom": "0.5rem"
                                }
                            ),
                            html.P(
                                action["description"],
                                style={
                                    "color": theme["text_secondary"],
                                    "fontSize": "0.9rem",
                                    "margin": "0",
                                    "lineHeight": "1.4"
                                }
                            )
                        ]
                    ) for action in actions
                ]
            )
        ]
    )


def build_enhanced_dashboard(theme_name="dark", user_data=None):
    """
    Build the complete enhanced dashboard layout
    
    Args:
        theme_name (str): Current theme name
        user_data (dict): Authenticated user data
        
    Returns:
        html.Div: Complete enhanced dashboard layout
    """
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    # Generate sample data
    data = generate_sample_data()
    
    # Default user data if none provided
    if not user_data:
        user_data = {
            "name": "Administrator",
            "email": "admin@swacchaandhra.gov.in",
            "role": "administrator",
            "picture": "/assets/img/default-avatar.png",
            "auth_method": "demo"
        }
    
    return html.Div(
        className="enhanced-dashboard-layout",
        style=theme_styles["container_style"],
        children=[
            # Hover overlay banner for navigation
            create_hover_overlay_banner(theme_name),
            
            # Main dashboard content
            html.Div(
                className="dashboard-main-content",
                style={
                    **theme_styles["main_content_style"],
                    "paddingTop": "1rem"
                },
                children=[
                    # Welcome header with user info and logout
                    html.Div(
                        style={
                            "position": "relative",
                            "marginBottom": "2rem",
                            "padding": "2rem",
                            "background": f"linear-gradient(135deg, {theme['secondary_bg']} 0%, {theme['brand_primary']}22 100%)",
                            "borderRadius": "12px",
                            "border": f"2px solid {theme['brand_primary']}",
                            "overflow": "hidden"
                        },
                        children=[
                            # Background decoration
                            html.Div(
                                style={
                                    "position": "absolute",
                                    "top": "-30px",
                                    "right": "-30px",
                                    "width": "120px",
                                    "height": "120px",
                                    "background": f"radial-gradient(circle, {theme['brand_primary']}22 0%, transparent 70%)",
                                    "borderRadius": "50%",
                                    "pointerEvents": "none"
                                }
                            ),
                            
                            # Header content layout
                            html.Div(
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "flexWrap": "wrap",
                                    "gap": "1rem"
                                },
                                children=[
                                    # Left side - Main title and welcome
                                    html.Div([
                                        html.H1(
                                            "🌱 Swaccha Andhra Dashboard",
                                            style={
                                                "color": theme["text_primary"],
                                                "fontSize": "2.5rem",
                                                "fontWeight": "900",
                                                "marginBottom": "0.5rem",
                                                "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.3)"
                                            }
                                        ),
                                        html.P(
                                            f"Welcome back, {user_data.get('name', 'User')}! Real-time insights into Andhra Pradesh's cleanliness initiatives.",
                                            style={
                                                "color": theme["text_secondary"],
                                                "fontSize": "1.2rem",
                                                "marginBottom": "1rem",
                                                "lineHeight": "1.5"
                                            }
                                        )
                                    ], style={"flex": "1", "textAlign": "left"}),
                                    
                                    # Right side - User info and logout
                                    html.Div([
                                        # User avatar and info card
                                        html.Div(
                                            style={
                                                "backgroundColor": theme["card_bg"],
                                                "borderRadius": "12px",
                                                "border": f"2px solid {theme['accent_bg']}",
                                                "padding": "1.5rem",
                                                "textAlign": "center",
                                                "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.2)",
                                                "minWidth": "200px"
                                            },
                                            children=[
                                                # User avatar
                                                html.Img(
                                                    src=user_data.get('picture', '/assets/img/default-avatar.png'),
                                                    alt=f"{user_data.get('name', 'User')} Avatar",
                                                    style={
                                                        "width": "60px",
                                                        "height": "60px",
                                                        "borderRadius": "50%",
                                                        "border": f"3px solid {theme['brand_primary']}",
                                                        "objectFit": "cover",
                                                        "marginBottom": "1rem",
                                                        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.3)"
                                                    }
                                                ),
                                                
                                                # User name
                                                html.H3(
                                                    user_data.get('name', 'User'),
                                                    style={
                                                        "color": theme["text_primary"],
                                                        "fontSize": "1.1rem",
                                                        "fontWeight": "700",
                                                        "margin": "0 0 0.5rem 0"
                                                    }
                                                ),
                                                
                                                # User role badge
                                                html.Div(
                                                    user_data.get('role', 'user').replace('_', ' ').title(),
                                                    style={
                                                        "backgroundColor": theme["brand_primary"],
                                                        "color": "white",
                                                        "padding": "0.25rem 0.75rem",
                                                        "borderRadius": "12px",
                                                        "fontSize": "0.8rem",
                                                        "fontWeight": "600",
                                                        "marginBottom": "1rem",
                                                        "display": "inline-block"
                                                    }
                                                ),
                                                
                                                # Auth method indicator
                                                html.P(
                                                    f"🔐 {user_data.get('auth_method', 'unknown').replace('_', ' ').title()}",
                                                    style={
                                                        "color": theme["success"],
                                                        "fontSize": "0.8rem",
                                                        "margin": "0 0 1rem 0",
                                                        "fontWeight": "500"
                                                    }
                                                ),
                                                
                                                # Logout button - perfectly styled
                                                html.Button(
                                                    [
                                                        html.Span("🚪", style={"marginRight": "0.5rem", "fontSize": "1rem"}),
                                                        "Logout"
                                                    ],
                                                    id="logout-btn",
                                                    style={
                                                        "background": f"linear-gradient(135deg, {theme['error']} 0%, #C53030 100%)",
                                                        "color": "white",
                                                        "border": "none",
                                                        "padding": "0.75rem 1.5rem",
                                                        "borderRadius": "8px",
                                                        "fontSize": "0.9rem",
                                                        "fontWeight": "600",
                                                        "cursor": "pointer",
                                                        "transition": "all 0.2s ease",
                                                        "width": "100%",
                                                        "boxShadow": f"0 4px 12px {theme['error']}44",
                                                        "textTransform": "uppercase",
                                                        "letterSpacing": "0.5px"
                                                    }
                                                )
                                            ]
                                        )
                                    ], style={"display": "flex", "alignItems": "center"})
                                ]
                            ),
                            
                            # Bottom info bar
                            html.Div([
                                html.Span(
                                    f"📅 Last Updated: {data['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}",
                                    style={
                                        "color": theme["brand_primary"],
                                        "fontSize": "0.9rem",
                                        "fontWeight": "600"
                                    }
                                ),
                                html.Span(
                                    " • ",
                                    style={"color": theme["text_secondary"], "margin": "0 1rem"}
                                ),
                                html.Span(
                                    f"📊 Dashboard Status: Active",
                                    style={
                                        "color": theme["success"],
                                        "fontSize": "0.9rem",
                                        "fontWeight": "600"
                                    }
                                ),
                                html.Span(
                                    " • ",
                                    style={"color": theme["text_secondary"], "margin": "0 1rem"}
                                ),
                                html.Span(
                                    f"🔄 Auto-refresh: 30s",
                                    style={
                                        "color": theme["info"],
                                        "fontSize": "0.9rem",
                                        "fontWeight": "600"
                                    }
                                )
                            ], style={
                                "textAlign": "center",
                                "marginTop": "1.5rem",
                                "padding": "1rem",
                                "backgroundColor": theme["accent_bg"],
                                "borderRadius": "8px",
                                "border": f"1px solid {theme['border_light']}"
                            })
                        ]
                    ),
                    
                    # KPI Section
                    create_kpi_section(theme_styles, user_data),
                    
                    # Charts Section
                    create_charts_section(theme_styles, data),
                    
                    # Data Table Section
                    create_data_table_section(theme_styles, data),
                    
                    # Two-column layout for alerts and actions
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "2fr 1fr",
                            "gap": "2rem",
                            "margin": "2rem 0"
                        },
                        children=[
                            create_alerts_section(theme_styles),
                            create_quick_actions_section(theme_styles)
                        ]
                    ),
                    
                    # Auto-refresh indicator
                    html.Div(
                        style={
                            "textAlign": "center",
                            "marginTop": "2rem",
                            "padding": "1rem",
                            "backgroundColor": theme["accent_bg"],
                            "borderRadius": "8px",
                            "border": f"1px solid {theme['border_light']}"
                        },
                        children=[
                            html.P([
                                html.Span("🔄", style={"marginRight": "0.5rem"}),
                                "Dashboard auto-refreshes every 30 seconds • ",
                                html.Span("⚡", style={"marginLeft": "0.5rem", "marginRight": "0.5rem"}),
                                "Real-time data powered by Swaccha Andhra API"
                            ], style={
                                "color": theme["text_secondary"],
                                "fontSize": "0.9rem",
                                "margin": "0"
                            })
                        ]
                    )
                ]
            )
        ]
    )


# Export the main function
__all__ = ['build_enhanced_dashboard', 'generate_sample_data']