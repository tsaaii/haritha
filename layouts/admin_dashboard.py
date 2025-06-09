# layouts/admin_dashboard.py - COMPLETE ENHANCED VERSION
"""
Enhanced Admin Dashboard Layout for Swaccha Andhra
Same header as public landing + navigation tabs with logout + comprehensive dashboard content
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


def create_admin_hero_section(theme):
    """Create hero section identical to public landing"""
    return html.Div(
        className="hero-section",
        style={
            "background": f"linear-gradient(135deg, {theme['secondary_bg']} 0%, {theme['accent_bg']} 100%)",
            "borderRadius": "8px",
            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.3)",
            "textAlign": "center",
            "position": "relative",
            "overflow": "hidden"
        },
        children=[
            # Main content - logos and title only (same as public landing)
            html.Div(
                children=[
                    # Left Logo
                    html.Img(
                        src="/assets/img/left.png",
                        alt="Left Organization Logo",
                        className="logo-left responsive-logo"
                    ),
                    
                    # Title Section
                    html.Div(
                        className="hero-title-section",
                        children=[
                            # Main Title
                            html.H1(
                                "Swaccha Andhra Corporation",
                                style={
                                    "color": theme["text_primary"],
                                    "margin": "0 0 0.25rem 0",
                                    "lineHeight": "1.1"
                                }
                            ),
                            
                            # Subtitle
                            html.P(
                                "Admin Portal - Real Time Dashboard",
                                className="hero-subtitle",
                                style={
                                    "color": theme["text_secondary"],
                                    "fontSize": "clamp(0.8rem, 2vw, 1rem)",
                                    "fontWeight": "500",
                                    "margin": "0",
                                    "lineHeight": "1.2",
                                    "fontStyle": "Bold"
                                }
                            )
                        ]
                    ),
                    
                    # Right Logo
                    html.Img(
                        src="/assets/img/right.png",
                        alt="Right Organization Logo",
                        className="logo-right responsive-logo"
                    )
                ]
            )
        ]
    )


def create_navigation_tabs(theme, user_data):
    """Create navigation tabs with logout button and user info"""
    tabs = [
        {"id": "tab-dashboard", "label": "📊 Dashboard", "icon": "📊"},
        {"id": "tab-analytics", "label": "📈 Analytics", "icon": "📈"},
        {"id": "tab-reports", "label": "📋 Reports", "icon": "📋"},
        {"id": "tab-reviews", "label": "⭐ Reviews", "icon": "⭐"},
        {"id": "tab-upload", "label": "📤 Upload", "icon": "📤"}
    ]
    
    return html.Div(
        className="navigation-tabs",
        style={
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['accent_bg']}",
            "padding": "1rem",
            "margin": "1rem 0",
            "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.2)"
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "flexWrap": "wrap",
                    "gap": "1rem"
                },
                children=[
                    # Left side - Navigation tabs
                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "0.5rem",
                            "flexWrap": "wrap",
                            "alignItems": "center"
                        },
                        children=[
                            html.Button(
                                [
                                    html.Span(tab["icon"], style={"marginRight": "0.5rem", "fontSize": "1.1rem"}),
                                    tab["label"].split(" ", 1)[1]  # Remove emoji from label text
                                ],
                                id=tab["id"],
                                style={
                                    "backgroundColor": theme["brand_primary"] if tab["id"] == "tab-dashboard" else theme["accent_bg"],
                                    "color": "white" if tab["id"] == "tab-dashboard" else theme["text_primary"],
                                    "border": f"2px solid {theme['brand_primary']}" if tab["id"] == "tab-dashboard" else f"1px solid {theme.get('border_light', theme['accent_bg'])}",
                                    "padding": "0.75rem 1.5rem",
                                    "borderRadius": "8px",
                                    "fontSize": "0.95rem",
                                    "fontWeight": "600",
                                    "cursor": "pointer",
                                    "transition": "all 0.2s ease",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "gap": "0.5rem",
                                    "minWidth": "120px",
                                    "justifyContent": "center"
                                }
                            ) for tab in tabs
                        ]
                    ),
                    
                    # Right side - User info and logout
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "1rem"
                        },
                        children=[
                            # User info
                            html.Div(
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "gap": "0.75rem",
                                    "padding": "0.5rem 1rem",
                                    "backgroundColor": theme["accent_bg"],
                                    "borderRadius": "8px",
                                    "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}"
                                },
                                children=[
                                    # User avatar
                                    html.Img(
                                        src=user_data.get('picture', '/assets/img/default-avatar.png'),
                                        alt=f"{user_data.get('name', 'User')} Avatar",
                                        style={
                                            "width": "32px",
                                            "height": "32px",
                                            "borderRadius": "50%",
                                            "border": f"2px solid {theme['brand_primary']}",
                                            "objectFit": "cover"
                                        }
                                    ),
                                    # User name and role
                                    html.Div([
                                        html.Div(
                                            user_data.get('name', 'Administrator'),
                                            style={
                                                "fontSize": "0.9rem",
                                                "fontWeight": "600",
                                                "color": theme["text_primary"],
                                                "lineHeight": "1.2"
                                            }
                                        ),
                                        html.Div(
                                            user_data.get('role', 'admin').replace('_', ' ').title(),
                                            style={
                                                "fontSize": "0.75rem",
                                                "color": theme["text_secondary"],
                                                "lineHeight": "1.2"
                                            }
                                        )
                                    ])
                                ]
                            ),
                            
                            # Logout button
                            html.Button(
                                [
                                    html.Span("🚪", style={"marginRight": "0.5rem"}),
                                    "Logout"
                                ],
                                id="logout-btn",
                                style={
                                    "background": f"linear-gradient(135deg, {theme['error']} 0%, #C53030 100%)",
                                    "color": "white",
                                    "border": "none",
                                    "padding": "0.75rem 1.5rem",
                                    "borderRadius": "8px",
                                    "fontSize": "0.95rem",
                                    "fontWeight": "600",
                                    "cursor": "pointer",
                                    "transition": "all 0.2s ease",
                                    "boxShadow": f"0 4px 12px {theme['error']}44",
                                    "textTransform": "uppercase",
                                    "letterSpacing": "0.5px"
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )


def create_tab_content(active_tab, theme_styles, user_data, data):
    """Create content based on active tab"""
    theme = theme_styles["theme"]
    
    if active_tab == "tab-dashboard":
        return create_dashboard_content(theme_styles, user_data, data)
    elif active_tab == "tab-analytics":
        return create_analytics_content(theme_styles, data)
    elif active_tab == "tab-reports":
        return create_reports_content(theme_styles, data)
    elif active_tab == "tab-reviews":
        return create_reviews_content(theme_styles)
    elif active_tab == "tab-upload":
        return create_upload_content(theme_styles)
    else:
        return create_dashboard_content(theme_styles, user_data, data)


def create_dashboard_content(theme_styles, user_data, data):
    """Create main dashboard content"""
    theme = theme_styles["theme"]
    
    return html.Div([
        # Quick stats
        create_kpi_section(theme_styles, user_data),
        
        # Charts section
        create_charts_section(theme_styles, data),
        
        # Status and alerts
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "2rem",
                "margin": "2rem 0"
            },
            children=[
                create_alerts_section(theme_styles),
                create_quick_actions_section(theme_styles)
            ]
        )
    ])


def create_analytics_content(theme_styles, data):
    """Create analytics tab content"""
    theme = theme_styles["theme"]
    
    return html.Div([
        html.H2("📈 Advanced Analytics", 
               style={"color": theme["text_primary"], "textAlign": "center", "marginBottom": "2rem"}),
        
        # Analytics charts
        create_charts_section(theme_styles, data),
        
        # Data table
        create_data_table_section(theme_styles, data)
    ])


def create_reports_content(theme_styles, data):
    """Create reports tab content"""
    theme = theme_styles["theme"]
    
    return html.Div([
        html.H2("📋 Reports & Documentation", 
               style={"color": theme["text_primary"], "textAlign": "center", "marginBottom": "2rem"}),
        
        # Report generation section
        html.Div(
            style={
                "backgroundColor": theme["card_bg"],
                "borderRadius": "12px",
                "border": f"2px solid {theme['accent_bg']}",
                "padding": "2rem",
                "margin": "1rem 0"
            },
            children=[
                html.H3("Generate Reports", style={"color": theme["text_primary"], "marginBottom": "1rem"}),
                
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                        "gap": "1rem"
                    },
                    children=[
                        create_report_card("📊 Daily Summary", "Generate daily performance report", theme),
                        create_report_card("📈 Weekly Analytics", "Comprehensive weekly analysis", theme),
                        create_report_card("📋 Monthly Report", "Detailed monthly overview", theme),
                        create_report_card("🔍 Custom Report", "Create custom date range report", theme)
                    ]
                )
            ]
        ),
        
        # Recent reports
        html.Div(
            style={
                "backgroundColor": theme["card_bg"],
                "borderRadius": "12px",
                "border": f"2px solid {theme['accent_bg']}",
                "padding": "2rem",
                "margin": "1rem 0"
            },
            children=[
                html.H3("Recent Reports", style={"color": theme["text_primary"], "marginBottom": "1rem"}),
                html.P("Recent reports will be displayed here.", 
                      style={"color": theme["text_secondary"], "textAlign": "center"})
            ]
        )
    ])


def create_reviews_content(theme_styles):
    """Create reviews tab content"""
    theme = theme_styles["theme"]
    
    # Sample review data
    reviews = [
        {"name": "Ramesh Kumar", "location": "Visakhapatnam", "rating": 5, "comment": "Excellent waste management system! Very satisfied.", "date": "2025-06-07"},
        {"name": "Priya Sharma", "location": "Vijayawada", "rating": 4, "comment": "Good service, could improve pickup timing.", "date": "2025-06-06"},
        {"name": "Suresh Reddy", "location": "Guntur", "rating": 5, "comment": "Amazing cleanliness improvements in our area.", "date": "2025-06-05"},
        {"name": "Lakshmi Devi", "location": "Tirupati", "rating": 4, "comment": "Happy with the recycling program.", "date": "2025-06-04"}
    ]
    
    return html.Div([
        html.H2("⭐ Customer Reviews & Feedback", 
               style={"color": theme["text_primary"], "textAlign": "center", "marginBottom": "2rem"}),
        
        # Review stats
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                "gap": "1rem",
                "margin": "2rem 0"
            },
            children=[
                create_compact_stat_card("⭐", "Average Rating", "4.7", theme_styles),
                create_compact_stat_card("📝", "Total Reviews", "1,247", theme_styles),
                create_compact_stat_card("👍", "Positive Reviews", "92%", theme_styles),
                create_compact_stat_card("📈", "This Month", "+15%", theme_styles)
            ]
        ),
        
        # Reviews list
        html.Div(
            style={
                "backgroundColor": theme["card_bg"],
                "borderRadius": "12px",
                "border": f"2px solid {theme['accent_bg']}",
                "padding": "2rem",
                "margin": "1rem 0"
            },
            children=[
                html.H3("Recent Reviews", style={"color": theme["text_primary"], "marginBottom": "1.5rem"}),
                
                html.Div([
                    create_review_card(review, theme) for review in reviews
                ])
            ]
        )
    ])


def create_upload_content(theme_styles):
    """Create upload tab content"""
    theme = theme_styles["theme"]
    
    return html.Div([
        html.H2("📤 Data Upload & Management", 
               style={"color": theme["text_primary"], "textAlign": "center", "marginBottom": "2rem"}),
        
        # Upload section
        html.Div(
            style={
                "backgroundColor": theme["card_bg"],
                "borderRadius": "12px",
                "border": f"2px solid {theme['accent_bg']}",
                "padding": "2rem",
                "margin": "1rem 0"
            },
            children=[
                html.H3("Upload Data Files", style={"color": theme["text_primary"], "marginBottom": "1.5rem"}),
                
                # Upload area
                html.Div(
                    className="upload-area",
                    style={
                        "border": f"2px dashed {theme['brand_primary']}",
                        "borderRadius": "12px",
                        "padding": "3rem",
                        "textAlign": "center",
                        "backgroundColor": theme["accent_bg"],
                        "cursor": "pointer",
                        "transition": "all 0.2s ease"
                    },
                    children=[
                        html.Div("📁", style={"fontSize": "3rem", "marginBottom": "1rem"}),
                        html.H4("Drag & Drop Files Here", 
                               style={"color": theme["text_primary"], "marginBottom": "0.5rem"}),
                        html.P("Or click to browse files", 
                              style={"color": theme["text_secondary"], "marginBottom": "1rem"}),
                        html.P("Supported formats: CSV, Excel, JSON", 
                              style={"color": theme.get("text_muted", theme["text_secondary"]), "fontSize": "0.9rem"})
                    ]
                ),
                
                # Upload actions
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "1rem",
                        "justifyContent": "center",
                        "marginTop": "2rem"
                    },
                    children=[
                        html.Button("Choose Files", 
                                   style={"backgroundColor": theme["brand_primary"], "color": "white", 
                                         "border": "none", "padding": "0.75rem 1.5rem", 
                                         "borderRadius": "8px", "cursor": "pointer"}),
                        html.Button("Upload", 
                                   style={"backgroundColor": theme["success"], "color": "white", 
                                         "border": "none", "padding": "0.75rem 1.5rem", 
                                         "borderRadius": "8px", "cursor": "pointer"})
                    ]
                )
            ]
        ),
        
        # Recent uploads
        html.Div(
            style={
                "backgroundColor": theme["card_bg"],
                "borderRadius": "12px",
                "border": f"2px solid {theme['accent_bg']}",
                "padding": "2rem",
                "margin": "1rem 0"
            },
            children=[
                html.H3("Recent Uploads", style={"color": theme["text_primary"], "marginBottom": "1rem"}),
                html.P("Upload history will be displayed here.", 
                      style={"color": theme["text_secondary"], "textAlign": "center"})
            ]
        )
    ])


def create_report_card(title, description, theme):
    """Create report generation card"""
    return html.Div(
        className="report-card",
        style={
            "backgroundColor": theme["accent_bg"],
            "borderRadius": "8px",
            "padding": "1.5rem",
            "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}",
            "cursor": "pointer",
            "transition": "all 0.2s ease",
            "textAlign": "center"
        },
        children=[
            html.H4(title, style={"color": theme["text_primary"], "marginBottom": "0.5rem"}),
            html.P(description, style={"color": theme["text_secondary"], "marginBottom": "1rem", "fontSize": "0.9rem"}),
            html.Button("Generate", 
                       style={"backgroundColor": theme["brand_primary"], "color": "white", 
                             "border": "none", "padding": "0.5rem 1rem", 
                             "borderRadius": "6px", "cursor": "pointer"})
        ]
    )


def create_review_card(review, theme):
    """Create individual review card"""
    stars = "⭐" * review["rating"] + "☆" * (5 - review["rating"])
    
    return html.Div(
        className="review-card",
        style={
            "backgroundColor": theme["accent_bg"],
            "borderRadius": "8px",
            "padding": "1.5rem",
            "margin": "1rem 0",
            "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}"
        },
        children=[
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start", "marginBottom": "1rem"},
                children=[
                    html.Div([
                        html.H4(review["name"], style={"color": theme["text_primary"], "margin": "0", "fontSize": "1.1rem"}),
                        html.P(f"📍 {review['location']}", style={"color": theme["text_secondary"], "margin": "0.25rem 0", "fontSize": "0.9rem"})
                    ]),
                    html.Div([
                        html.P(stars, style={"fontSize": "1.2rem", "margin": "0"}),
                        html.P(review["date"], style={"color": theme.get("text_muted", theme["text_secondary"]), "fontSize": "0.8rem", "margin": "0"})
                    ], style={"textAlign": "right"})
                ]
            ),
            html.P(review["comment"], 
                  style={"color": theme["text_secondary"], "lineHeight": "1.5", "margin": "0", "fontStyle": "italic"})
        ]
    )


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
            gridcolor=theme.get("border_light", theme["accent_bg"]),
            showgrid=True
        ),
        yaxis=dict(
            gridcolor=theme.get("border_light", theme["accent_bg"]),
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
                                    "color": theme.get("text_muted", theme["text_secondary"]),
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
        {"icon": "⚙️", "title": "System Settings", "description": "Configure dashboard parameters"}
    ]
    
    return html.Div(
        className="quick-actions-section",
        style={
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
                    "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
                    "gap": "1rem"
                },
                children=[
                    html.Div(
                        className="action-card",
                        style={
                            "backgroundColor": theme["accent_bg"],
                            "borderRadius": "8px",
                            "padding": "1.5rem",
                            "textAlign": "center",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease",
                            "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}"
                        },
                        children=[
                            html.Div(
                                action["icon"],
                                style={
                                    "fontSize": "2rem",
                                    "marginBottom": "0.5rem"
                                }
                            ),
                            html.H4(
                                action["title"],
                                style={
                                    "color": theme["text_primary"],
                                    "fontSize": "1rem",
                                    "fontWeight": "600",
                                    "marginBottom": "0.5rem"
                                }
                            ),
                            html.P(
                                action["description"],
                                style={
                                    "color": theme["text_secondary"],
                                    "fontSize": "0.8rem",
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


def build_enhanced_dashboard(theme_name="dark", user_data=None, active_tab="tab-dashboard"):
    """
    Build the complete enhanced dashboard layout with tabs
    
    Args:
        theme_name (str): Current theme name
        user_data (dict): Authenticated user data
        active_tab (str): Currently active tab
        
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
            # Hover overlay banner for theme switching
            create_hover_overlay_banner(theme_name),
            
            # Main dashboard content
            html.Div(
                className="dashboard-main-content",
                style={
                    **theme_styles["main_content_style"],
                    "paddingTop": "1rem"
                },
                children=[
                    # Hero header (same as public landing)
                    create_admin_hero_section(theme),
                    
                    # Navigation tabs with user info and logout
                    create_navigation_tabs(theme, user_data),
                    
                    # Tab content container
                    html.Div(
                        id="tab-content",
                        children=[
                            create_tab_content(active_tab, theme_styles, user_data, data)
                        ]
                    ),
                    
                    # Footer status info
                    html.Div(
                        style={
                            "textAlign": "center",
                            "marginTop": "3rem",
                            "padding": "1rem",
                            "backgroundColor": theme["accent_bg"],
                            "borderRadius": "8px",
                            "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}"
                        },
                        children=[
                            html.P([
                                html.Span("🔄", style={"marginRight": "0.5rem"}),
                                "Dashboard auto-refreshes every 30 seconds • ",
                                html.Span("⚡", style={"marginLeft": "0.5rem", "marginRight": "0.5rem"}),
                                f"Real-time data • Last updated: {data['last_updated'].strftime('%H:%M:%S')}"
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