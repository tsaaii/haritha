# layouts/admin_dashboard.py - ENHANCED MINIMAL VERSION
"""
Enhanced Admin Dashboard Layout for Swaccha Andhra - HEADER AND MENU ONLY
Removes all panels except header and navigation menu for clean interface
"""

from dash import html, dcc
from datetime import datetime
import random

from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner


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
                                    "fontSize": "clamp(1.2rem, 4vw, 2.5rem)",
                                    "fontWeight": "900",
                                    "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.3)",
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
    """Create navigation tabs with user info (logout moved to overlay)"""
    tabs = [
        {"id": "tab-dashboard", "label": "Dashboard", "icon": "📊"},
        {"id": "tab-analytics", "label": "Analytics", "icon": "📈"},
        {"id": "tab-reports", "label": "Reports", "icon": "📋"},
        {"id": "tab-reviews", "label": "Reviews", "icon": "⭐"},
        {"id": "tab-upload", "label": "Upload", "icon": "📤"}
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
                    # Tab buttons container
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
                                    html.Span(tab["icon"], style={"marginRight": "0.5rem"}),
                                    tab["label"]
                                ],
                                id=tab["id"],
                                style={
                                    "backgroundColor": theme["brand_primary"] if tab["id"] == "tab-dashboard" else theme["accent_bg"],
                                    "color": "white" if tab["id"] == "tab-dashboard" else theme["text_secondary"],
                                    "border": "none",
                                    "borderRadius": "8px",
                                    "padding": "0.75rem 1rem",
                                    "fontSize": "0.9rem",
                                    "fontWeight": "600",
                                    "cursor": "pointer",
                                    "transition": "all 0.2s ease",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "minWidth": "120px"
                                }
                            ) for tab in tabs
                        ]
                    ),
                    
                    # User info and logout section
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "1rem",
                            "flexWrap": "wrap"
                        },
                    )
                ]
            )
        ]
    )


def create_minimal_dashboard_content(theme_styles, user_data):
    """Create minimal dashboard content - ONLY welcome message"""
    theme = theme_styles["theme"]
    
    return html.Div(
        style={
            "textAlign": "center",
            "padding": "4rem 2rem",
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['accent_bg']}",
            "margin": "2rem 0",
            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.2)"
        },
        children=[
            html.Div(
                "🎯",
                style={
                    "fontSize": "4rem",
                    "marginBottom": "1rem",
                    "filter": "drop-shadow(0 4px 8px rgba(0,0,0,0.3))"
                }
            ),
            html.H2(
                f"Welcome, {user_data.get('name', 'Administrator')}!",
                style={
                    "color": theme["text_primary"],
                    "fontSize": "2rem",
                    "fontWeight": "700",
                    "marginBottom": "1rem",
                    "lineHeight": "1.2"
                }
            ),
            html.P(
                "Dashboard content has been simplified. Use the navigation menu above to access different sections.",
                style={
                    "color": theme["text_secondary"],
                    "fontSize": "1.1rem",
                    "maxWidth": "600px",
                    "margin": "0 auto",
                    "lineHeight": "1.5"
                }
            ),
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "gap": "1rem",
                    "marginTop": "2rem",
                    "flexWrap": "wrap"
                },
                children=[
                    html.Div(
                        children=[
                            html.Span("📊", style={"fontSize": "1.5rem", "marginRight": "0.5rem"}),
                            "Analytics Ready"
                        ],
                        style={
                            "backgroundColor": theme["accent_bg"],
                            "color": theme["text_primary"],
                            "padding": "0.75rem 1.5rem",
                            "borderRadius": "8px",
                            "fontSize": "1rem",
                            "fontWeight": "600"
                        }
                    ),
                    html.Div(
                        children=[
                            html.Span("⭐", style={"fontSize": "1.5rem", "marginRight": "0.5rem"}),
                            "Reviews Available"
                        ],
                        style={
                            "backgroundColor": theme["accent_bg"],
                            "color": theme["text_primary"],
                            "padding": "0.75rem 1.5rem",
                            "borderRadius": "8px",
                            "fontSize": "1rem",
                            "fontWeight": "600"
                        }
                    ),
                    html.Div(
                        children=[
                            html.Span("📋", style={"fontSize": "1.5rem", "marginRight": "0.5rem"}),
                            "Reports Ready"
                        ],
                        style={
                            "backgroundColor": theme["accent_bg"],
                            "color": theme["text_primary"],
                            "padding": "0.75rem 1.5rem",
                            "borderRadius": "8px",
                            "fontSize": "1rem",
                            "fontWeight": "600"
                        }
                    )
                ]
            )
        ]
    )


def create_tab_content(active_tab, theme_styles, user_data, data=None):
    """Create content based on active tab - MINIMAL VERSION"""
    theme = theme_styles["theme"]
    
    # Simple content for each tab
    if active_tab == "tab-dashboard":
        return create_minimal_dashboard_content(theme_styles, user_data)
    elif active_tab == "tab-analytics":
        return create_simple_tab_content("📈 Analytics", "Advanced analytics will be available here soon.", theme_styles)
    elif active_tab == "tab-reports":
        return create_simple_tab_content("📋 Reports", "Report generation and management will be available here.", theme_styles)
    elif active_tab == "tab-reviews":
        return create_simple_tab_content("⭐ Reviews", "Customer reviews and feedback will be displayed here.", theme_styles)
    elif active_tab == "tab-upload":
        return create_simple_tab_content("📤 Upload", "File upload and data management tools will be available here.", theme_styles)
    else:
        return create_minimal_dashboard_content(theme_styles, user_data)


def create_simple_tab_content(title, description, theme_styles):
    """Create simple placeholder content for tabs"""
    theme = theme_styles["theme"]
    
    return html.Div(
        style={
            "textAlign": "center",
            "padding": "4rem 2rem",
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['accent_bg']}",
            "margin": "2rem 0",
            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.2)"
        },
        children=[
            html.H2(
                title,
                style={
                    "color": theme["text_primary"],
                    "fontSize": "2rem",
                    "fontWeight": "700",
                    "marginBottom": "1rem"
                }
            ),
            html.P(
                description,
                style={
                    "color": theme["text_secondary"],
                    "fontSize": "1.1rem",
                    "maxWidth": "600px",
                    "margin": "0 auto",
                    "lineHeight": "1.5"
                }
            )
        ]
    )


def build_enhanced_dashboard(theme_name="dark", user_data=None, active_tab="tab-dashboard"):
    """
    Build the MINIMAL enhanced dashboard layout with tabs - HEADER AND MENU ONLY
    
    Args:
        theme_name (str): Current theme name
        user_data (dict): Authenticated user data
        active_tab (str): Currently active tab
        
    Returns:
        html.Div: Complete minimal dashboard layout
    """
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
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
            create_hover_overlay_banner(theme_name, is_authenticated=True, user_data=user_data),

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
                    
                    # Tab content container - MINIMAL CONTENT ONLY
                    html.Div(
                        id="tab-content",
                        children=[
                            create_tab_content(active_tab, theme_styles, user_data)
                        ]
                    ),
                    
                    # Simple footer status info
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
                                html.Span("⚡", style={"marginRight": "0.5rem"}),
                                "Dashboard ready for content • ",
                                html.Span("🎯", style={"marginLeft": "0.5rem", "marginRight": "0.5rem"}),
                                f"Simplified interface • Current time: {datetime.now().strftime('%H:%M:%S')}"
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
__all__ = ['build_enhanced_dashboard']