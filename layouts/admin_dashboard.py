# layouts/admin_dashboard.py - UPDATED WITH FILTERABLE CONTAINER
"""
Enhanced Admin Dashboard Layout for Swaccha Andhra - WITH FILTERABLE CONTAINER
Now includes a new "Data Analytics" tab with advanced filtering capabilities
"""

from dash import html, dcc
from datetime import datetime
import random

from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner
from components.data.filterable_container import create_filterable_container


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
    """OPTIMIZED: Navigation tabs with uniform sizing and no user info"""
    
    tabs = [
        {"href": "/admin/dashboard", "label": "Dashboard", "icon": "📊"},
        {"href": "/admin/data-analytics", "label": "Data Analytics", "icon": "🔍"},
        {"href": "/admin/charts", "label": "Charts", "icon": "📈"},
        {"href": "/admin/reports", "label": "Reports", "icon": "📋"},
        {"href": "/admin/reviews", "label": "Reviews", "icon": "⭐"},
        {"href": "/admin/forecasting", "label": "Forecasting", "icon": "🔮"},
        {"href": "/admin/upload", "label": "Upload", "icon": "📤"}
    ]
    
    return html.Div(
        className="navigation-tabs",
        style={
            "backgroundColor": theme["card_bg"],
            "borderRadius": "8px",  # Reduced from 12px
            "border": f"2px solid {theme['accent_bg']}",
            "padding": "0.75rem 1.5rem",  # Reduced padding for less height
            "margin": "0.75rem 0",  # Reduced margin
            "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.2)"
        },
        children=[
            # Single centered container for navigation tabs only
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "center",  # Center the tabs
                    "alignItems": "center",
                    "gap": "0.75rem",  # Consistent gap between buttons
                    "flexWrap": "wrap"
                },
                children=[
                    html.A(
                        [
                            html.Span(tab["icon"], style={"marginRight": "0.5rem", "fontSize": "1rem"}),
                            html.Span(tab["label"], style={"fontSize": "0.9rem", "fontWeight": "600"})
                        ],
                        href=tab["href"],
                        style={
                            # UNIFORM SIZING FOR ALL BUTTONS
                            "backgroundColor": theme["accent_bg"],
                            "color": theme["text_primary"],
                            "border": f"2px solid {theme['card_bg']}",
                            "borderRadius": "8px",
                            "padding": "1rem 1.5rem",  # Bigger padding for larger buttons
                            "fontSize": "0.9rem",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "textDecoration": "none",
                            "whiteSpace": "nowrap",  # Prevent text wrapping
                            
                            # UNIFORM SIZE CONSTRAINTS
                            "minWidth": "140px",  # Consistent minimum width
                            "maxWidth": "160px",  # Consistent maximum width
                            "height": "48px",     # Fixed height for uniformity
                            "flex": "0 0 auto",   # Don't grow or shrink
                            
                            # HOVER EFFECTS
                            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)"
                        }
                    ) for tab in tabs
                ]
            )
        ]
    )


def create_tab_content(active_tab, theme_styles, user_data, data=None):
    """Create content based on active tab - UPDATED WITH FILTERABLE CONTAINER"""
    theme = theme_styles["theme"]
    
    # Handle the new Data Analytics tab
    if active_tab == "tab-data-analytics":
        return html.Div([
            # Tab header
            html.Div([
                html.H2(
                    "🔍 Advanced Data Analytics",
                    style={
                        "color": theme["text_primary"],
                        "fontSize": "2.5rem",
                        "fontWeight": "800",
                        "marginBottom": "1rem",
                        "textAlign": "center"
                    }
                ),
                html.P(
                    "Comprehensive data filtering, analysis, and visualization tools for waste management operations.",
                    style={
                        "color": theme["text_secondary"],
                        "fontSize": "1.2rem",
                        "textAlign": "center",
                        "marginBottom": "2rem",
                        "lineHeight": "1.5"
                    }
                )
            ], style={
                "padding": "2rem 0",
                "backgroundColor": theme["accent_bg"],
                "borderRadius": "12px",
                "marginBottom": "2rem",
                "border": f"2px solid {theme['card_bg']}"
            }),
            
            # Filterable container
            create_filterable_container(theme, "admin-filterable-container")
        ])
    
    # Simple content for other tabs
    elif active_tab == "tab-dashboard":
        return create_minimal_dashboard_content(theme_styles, user_data)
    elif active_tab == "tab-analytics":
        return create_simple_tab_content("📈 Charts & Analytics", "Interactive charts and analytics will be available here soon.", theme_styles)
    elif active_tab == "tab-reports":
        return create_simple_tab_content("📋 Reports", "Report generation and management will be available here.", theme_styles)
    elif active_tab == "tab-reviews":
        return create_simple_tab_content("⭐ Reviews", "Customer reviews and feedback will be displayed here.", theme_styles)
    elif active_tab == "tab-forecasting":
        return create_simple_tab_content("🔮 Forecasting", "Predictive analytics and waste management forecasting will be available here.", theme_styles)
    elif active_tab == "tab-upload":
        return create_simple_tab_content("📤 Upload", "File upload and data management tools will be available here.", theme_styles)
    else:
        return create_minimal_dashboard_content(theme_styles, user_data)


def create_minimal_dashboard_content(theme_styles, user_data):
    """Create minimal dashboard content - welcome message and quick stats"""
    theme = theme_styles["theme"]
    
    return html.Div([
        # Welcome section
        html.Div([
            html.H2(
                f"👋 Welcome back, {user_data.get('name', 'Administrator')}!",
                style={
                    "color": theme["text_primary"],
                    "fontSize": "2rem",
                    "fontWeight": "700",
                    "marginBottom": "1rem",
                    "textAlign": "center"
                }
            ),
            html.P(
                "Your dashboard is ready. Use the tabs above to navigate to different sections.",
                style={
                    "color": theme["text_secondary"],
                    "fontSize": "1.1rem",
                    "textAlign": "center",
                    "marginBottom": "2rem",
                    "lineHeight": "1.5"
                }
            )
        ], style={
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "border": f"2px solid {theme['accent_bg']}",
            "padding": "2rem",
            "margin": "2rem 0",
            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.2)"
        }),
        
        # Quick access cards
        html.Div([
            html.H3(
                "🚀 Quick Access",
                style={
                    "color": theme["text_primary"],
                    "fontSize": "1.5rem",
                    "fontWeight": "700",
                    "marginBottom": "1.5rem",
                    "textAlign": "center"
                }
            ),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                    "gap": "1.5rem"
                },
                children=[
                    create_quick_access_card(
                        "🔍", "Data Analytics", 
                        "Filter and analyze waste management data with advanced tools",
                        "tab-data-analytics", theme
                    ),
                    create_quick_access_card(
                        "📈", "Charts & Visualizations", 
                        "View interactive charts and data visualizations",
                        "tab-analytics", theme
                    ),
                    create_quick_access_card(
                        "📋", "Generate Reports", 
                        "Create and export detailed operational reports",
                        "tab-reports", theme
                    ),
                    create_quick_access_card(
                        "📤", "Upload Data", 
                        "Upload new data files and manage existing datasets",
                        "tab-upload", theme
                    )
                ]
            )
        ], style={
            "backgroundColor": theme["accent_bg"],
            "borderRadius": "12px",
            "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}",
            "padding": "2rem",
            "margin": "2rem 0"
        })
    ])


def create_quick_access_card(icon, title, description, tab_id, theme):
    """Create quick access cards for dashboard"""
    return html.Div([
        html.Div(
            icon,
            style={
                "fontSize": "2.5rem",
                "marginBottom": "1rem",
                "textAlign": "center"
            }
        ),
        html.H4(
            title,
            style={
                "color": theme["text_primary"],
                "fontSize": "1.2rem",
                "fontWeight": "700",
                "marginBottom": "0.5rem",
                "textAlign": "center"
            }
        ),
        html.P(
            description,
            style={
                "color": theme["text_secondary"],
                "fontSize": "0.9rem",
                "lineHeight": "1.4",
                "textAlign": "center",
                "marginBottom": "1rem"
            }
        ),
        html.Button(
            "Open",
            id=f"quick-access-{tab_id}",
            style={
                "backgroundColor": theme["brand_primary"],
                "color": "white",
                "border": "none",
                "borderRadius": "6px",
                "padding": "0.5rem 1rem",
                "fontSize": "0.9rem",
                "fontWeight": "600",
                "cursor": "pointer",
                "width": "100%",
                "transition": "all 0.2s ease"
            }
        )
    ], style={
        "backgroundColor": theme["card_bg"],
        "borderRadius": "8px",
        "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}",
        "padding": "1.5rem",
        "textAlign": "center",
        "transition": "transform 0.2s ease, box-shadow 0.2s ease",
        "cursor": "pointer"
    })


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


def generate_sample_data():
    """Generate sample data for dashboard components"""
    return {
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "total_collections": random.randint(1500, 2500),
        "efficiency_score": random.randint(85, 98),
        "active_vehicles": random.randint(45, 75)
    }


def build_enhanced_dashboard(theme_name="dark", user_data=None, active_tab="tab-dashboard"):
    """
    Build the ENHANCED dashboard layout with filterable container
    
    Args:
        theme_name (str): Current theme name
        user_data (dict): Authenticated user data
        active_tab (str): Currently active tab
        
    Returns:
        html.Div: Complete enhanced dashboard layout
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
                    
                    # Tab content container - NOW INCLUDES FILTERABLE CONTAINER
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
                                "Dashboard with Advanced Analytics ready • ",
                                html.Span("🔍", style={"marginLeft": "0.5rem", "marginRight": "0.5rem"}),
                                f"Data Analytics tab added • Current time: {datetime.now().strftime('%H:%M:%S')}"
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
__all__ = ['build_enhanced_dashboard', 'create_tab_content', 'generate_sample_data']