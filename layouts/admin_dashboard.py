# layouts/admin_dashboard.py
"""
Admin Dashboard Layout
Protected dashboard for authenticated users
"""

from dash import html, dcc
from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner
from components.cards.stat_card import create_stat_card, create_metric_grid, create_trend_stat_card
from components.cards.status_indicators import create_status_grid, create_detailed_status_indicator

def create_admin_welcome_section(theme, user_data):
    """Create welcome section for authenticated user"""
    return html.Div(
        className="admin-welcome-section",
        style={
            "background": f"linear-gradient(135deg, {theme['secondary_bg']} 0%, {theme['brand_primary']}22 100%)",
            "borderRadius": "12px",
            "border": f"2px solid {theme['brand_primary']}",
            "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.3)",
            "padding": "2rem",
            "margin": "1rem 0",
            "position": "relative",
            "overflow": "hidden"
        },
        children=[
            # Background decoration
            html.Div(
                style={
                    "position": "absolute",
                    "top": "-50px",
                    "right": "-50px",
                    "width": "150px",
                    "height": "150px",
                    "background": f"radial-gradient(circle, {theme['brand_primary']}33 0%, transparent 70%)",
                    "borderRadius": "50%",
                    "pointerEvents": "none"
                }
            ),
            
            # Welcome content
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "1.5rem",
                    "flexWrap": "wrap"
                },
                children=[
                    # User avatar
                    html.Img(
                        src=user_data.get('picture', '/assets/img/default-avatar.png'),
                        alt=f"{user_data.get('name', 'User')} Avatar",
                        style={
                            "width": "80px",
                            "height": "80px",
                            "borderRadius": "50%",
                            "border": f"3px solid {theme['brand_primary']}",
                            "objectFit": "cover",
                            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.3)"
                        }
                    ),
                    
                    # Welcome text
                    html.Div([
                        html.H2(
                            f"Welcome back, {user_data.get('name', 'Administrator')}!",
                            style={
                                "color": theme["text_primary"],
                                "fontSize": "2rem",
                                "fontWeight": "800",
                                "margin": "0 0 0.5rem 0"
                            }
                        ),
                        html.P(
                            f"Role: {user_data.get('role', 'user').replace('_', ' ').title()}",
                            style={
                                "color": theme["brand_primary"],
                                "fontSize": "1.1rem",
                                "fontWeight": "600",
                                "margin": "0 0 0.5rem 0"
                            }
                        ),
                        html.P(
                            f"Last login: {user_data.get('created_at', 'Unknown')}",
                            style={
                                "color": theme["text_secondary"],
                                "fontSize": "0.9rem",
                                "margin": "0"
                            }
                        )
                    ]),
                    
                    # Quick actions
                    html.Div(
                        style={
                            "marginLeft": "auto",
                            "display": "flex",
                            "gap": "1rem",
                            "flexWrap": "wrap"
                        },
                        children=[
                            html.Button(
                                [html.Span("📊 "), "View Reports"],
                                id="quick-reports-btn",
                                style={
                                    "backgroundColor": theme["success"],
                                    "color": "white",
                                    "border": "none",
                                    "padding": "0.75rem 1.5rem",
                                    "borderRadius": "8px",
                                    "fontWeight": "600",
                                    "cursor": "pointer",
                                    "transition": "all 0.2s ease"
                                }
                            ),
                            html.Button(
                                [html.Span("⚙️ "), "Settings"],
                                id="quick-settings-btn",
                                style={
                                    "backgroundColor": theme["info"],
                                    "color": "white",
                                    "border": "none",
                                    "padding": "0.75rem 1.5rem",
                                    "borderRadius": "8px",
                                    "fontWeight": "600",
                                    "cursor": "pointer",
                                    "transition": "all 0.2s ease"
                                }
                            ),
                            html.Button(
                                [html.Span("🚪 "), "Logout"],
                                id="logout-btn",
                                style={
                                    "backgroundColor": theme["error"],
                                    "color": "white",
                                    "border": "none",
                                    "padding": "0.75rem 1.5rem",
                                    "borderRadius": "8px",
                                    "fontWeight": "600",
                                    "cursor": "pointer",
                                    "transition": "all 0.2s ease"
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )

def create_admin_metrics_section(theme_styles):
    """Create advanced metrics for admin dashboard"""
    admin_metrics = [
        {
            "icon": "🏘️",
            "title": "Total Districts",
            "value": "13",
            "unit": "Monitored",
            "size": "normal"
        },
        {
            "icon": "🚮",
            "title": "Waste Processed",
            "value": "2.4M",
            "unit": "Tons This Month",
            "size": "normal"
        },
        {
            "icon": "♻️",
            "title": "Recycling Rate",
            "value": "78.5%",
            "unit": "↗️ +5.2%",
            "size": "normal"
        },
        {
            "icon": "🌱",
            "title": "Cleanliness Score",
            "value": "94.2",
            "unit": "⭐ Excellent",
            "size": "normal"
        },
        {
            "icon": "👥",
            "title": "Active Users",
            "value": "1,247",
            "unit": "Online Now",
            "size": "normal"
        },
        {
            "icon": "📱",
            "title": "Mobile Reports",
            "value": "3,892",
            "unit": "This Week",
            "size": "normal"
        }
    ]
    
    return html.Div([
        html.H3(
            "📈 Performance Metrics",
            style={
                "color": theme_styles["theme"]["text_primary"],
                "fontSize": "1.8rem",
                "marginBottom": "1.5rem",
                "textAlign": "center"
            }
        ),
        create_metric_grid(admin_metrics, theme_styles, columns=3)
    ])

def create_system_status_section(theme):
    """Create detailed system status for admins"""
    status_data = [
        {
            "label": "Data Collection",
            "status": "active",
            "color_key": "success",
            "size": "normal"
        },
        {
            "label": "API Services",
            "status": "online",
            "color_key": "success",
            "size": "normal"
        },
        {
            "label": "Database",
            "status": "healthy",
            "color_key": "success",
            "size": "normal"
        },
        {
            "label": "Mobile Sync",
            "status": "connected",
            "color_key": "success",
            "size": "normal"
        },
        {
            "label": "Backup System",
            "status": "running",
            "color_key": "info",
            "size": "normal"
        },
        {
            "label": "Security",
            "status": "secured",
            "color_key": "success",
            "size": "normal"
        }
    ]
    
    return html.Div(
        className="system-status-section",
        style={
            "backgroundColor": theme["accent_bg"],
            "border": f"2px solid {theme['brand_primary']}",
            "borderRadius": "12px",
            "padding": "2rem",
            "margin": "2rem 0"
        },
        children=[
            html.H3(
                "🔧 System Health Monitor",
                style={
                    "color": theme["text_primary"],
                    "fontSize": "1.8rem",
                    "marginBottom": "1.5rem",
                    "textAlign": "center"
                }
            ),
            create_status_grid(status_data, theme, columns=3),
            
            # Detailed status cards
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))",
                    "gap": "1rem",
                    "marginTop": "2rem"
                },
                children=[
                    create_detailed_status_indicator(
                        label="Server Performance",
                        status="optimal",
                        color_key="success",
                        theme=theme,
                        details="CPU: 15%, Memory: 32%, Disk: 67%",
                        timestamp="2 minutes ago"
                    ),
                    create_detailed_status_indicator(
                        label="Data Synchronization",
                        status="active",
                        color_key="info",
                        theme=theme,
                        details="Last sync completed successfully. Next sync in 8 minutes.",
                        timestamp="5 minutes ago"
                    )
                ]
            )
        ]
    )

def create_quick_actions_panel(theme):
    """Create quick actions panel for admins"""
    return html.Div(
        className="quick-actions-panel",
        style={
            "backgroundColor": theme["card_bg"],
            "border": f"2px solid {theme['accent_bg']}",
            "borderRadius": "12px",
            "padding": "2rem",
            "margin": "2rem 0"
        },
        children=[
            html.H3(
                "⚡ Quick Actions",
                style={
                    "color": theme["text_primary"],
                    "fontSize": "1.6rem",
                    "marginBottom": "1.5rem",
                    "textAlign": "center"
                }
            ),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                    "gap": "1rem"
                },
                children=[
                    create_action_card("📊", "Generate Report", "Create detailed analytics report", theme),
                    create_action_card("👥", "Manage Users", "Add or remove user access", theme),
                    create_action_card("🔄", "Sync Data", "Force data synchronization", theme),
                    create_action_card("📤", "Export Data", "Download system data", theme),
                    create_action_card("⚙️", "System Settings", "Configure system parameters", theme),
                    create_action_card("📋", "View Logs", "Check system activity logs", theme)
                ]
            )
        ]
    )

def create_action_card(icon, title, description, theme):
    """Create individual action card"""
    return html.Div(
        style={
            "backgroundColor": theme["accent_bg"],
            "border": f"1px solid {theme['border_light']}",
            "borderRadius": "8px",
            "padding": "1.5rem",
            "textAlign": "center",
            "cursor": "pointer",
            "transition": "all 0.2s ease",
            "hover": {
                "transform": "translateY(-2px)",
                "boxShadow": "0 8px 24px rgba(0, 0, 0, 0.2)"
            }
        },
        children=[
            html.Div(icon, style={"fontSize": "2.5rem", "marginBottom": "1rem"}),
            html.H4(
                title,
                style={
                    "color": theme["text_primary"],
                    "fontSize": "1.1rem",
                    "fontWeight": "600",
                    "marginBottom": "0.5rem"
                }
            ),
            html.P(
                description,
                style={
                    "color": theme["text_secondary"],
                    "fontSize": "0.9rem",
                    "margin": "0",
                    "lineHeight": "1.4"
                }
            )
        ]
    )

def create_recent_activity_section(theme):
    """Create recent activity timeline"""
    activities = [
        {"time": "2 min ago", "action": "Data sync completed", "user": "System", "type": "success"},
        {"time": "15 min ago", "action": "New mobile report received", "user": "Field Agent #47", "type": "info"},
        {"time": "1 hour ago", "action": "Backup completed successfully", "user": "System", "type": "success"},
        {"time": "2 hours ago", "action": "User login: admin@example.com", "user": "Administrator", "type": "info"},
        {"time": "3 hours ago", "action": "Weekly report generated", "user": "System", "type": "success"}
    ]
    
    return html.Div(
        className="recent-activity-section",
        style={
            "backgroundColor": theme["card_bg"],
            "border": f"2px solid {theme['accent_bg']}",
            "borderRadius": "12px",
            "padding": "2rem",
            "margin": "2rem 0"
        },
        children=[
            html.H3(
                "🕒 Recent Activity",
                style={
                    "color": theme["text_primary"],
                    "fontSize": "1.6rem",
                    "marginBottom": "1.5rem"
                }
            ),
            html.Div([
                create_activity_item(activity, theme) for activity in activities
            ])
        ]
    )

def create_activity_item(activity, theme):
    """Create individual activity item"""
    color_map = {
        "success": theme["success"],
        "info": theme["info"],
        "warning": theme["warning"],
        "error": theme["error"]
    }
    
    return html.Div(
        style={
            "display": "flex",
            "alignItems": "center",
            "gap": "1rem",
            "padding": "1rem",
            "borderBottom": f"1px solid {theme['border_light']}",
            "borderLeft": f"4px solid {color_map.get(activity['type'], theme['info'])}"
        },
        children=[
            html.Div(
                style={
                    "width": "8px",
                    "height": "8px",
                    "borderRadius": "50%",
                    "backgroundColor": color_map.get(activity['type'], theme['info']),
                    "flexShrink": "0"
                }
            ),
            html.Div([
                html.P(
                    activity['action'],
                    style={
                        "color": theme["text_primary"],
                        "fontSize": "1rem",
                        "fontWeight": "500",
                        "margin": "0 0 0.25rem 0"
                    }
                ),
                html.P(
                    f"{activity['user']} • {activity['time']}",
                    style={
                        "color": theme["text_secondary"],
                        "fontSize": "0.85rem",
                        "margin": "0"
                    }
                )
            ])
        ]
    )

def build_admin_dashboard(theme_name="dark", user_data=None):
    """
    Build the complete admin dashboard layout
    
    Args:
        theme_name (str): Current theme name
        user_data (dict): Authenticated user data
        
    Returns:
        html.Div: Complete admin dashboard layout
    """
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    if not user_data:
        user_data = {
            "name": "Administrator",
            "email": "admin@example.com",
            "role": "administrator",
            "picture": "/assets/img/default-avatar.png"
        }
    
    return html.Div(
        className="admin-dashboard-layout",
        style=theme_styles["container_style"],
        children=[
            # Hover overlay banner
            create_hover_overlay_banner(theme_name),
            
            # Main admin content
            html.Div(
                className="admin-main-content",
                style={
                    **theme_styles["main_content_style"],
                    "paddingTop": "1rem"
                },
                children=[
                    # Welcome section
                    create_admin_welcome_section(theme, user_data),
                    
                    # Metrics section
                    create_admin_metrics_section(theme_styles),
                    
                    # System status
                    create_system_status_section(theme),
                    
                    # Two-column layout for actions and activity
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "1fr 1fr",
                            "gap": "2rem",
                            "margin": "2rem 0"
                        },
                        children=[
                            create_quick_actions_panel(theme),
                            create_recent_activity_section(theme)
                        ]
                    )
                ]
            )
        ]
    )