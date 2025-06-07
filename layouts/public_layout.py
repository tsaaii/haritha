# layouts/public_layout.py
"""
Public Layout - Main dashboard visible without login
Features hover overlay for admin access
"""

from dash import html
from header import render_header
from footer import render_footer
from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner
from components.cards.stat_card import create_stat_card, create_metric_grid
from components.cards.status_indicators import create_status_indicator, create_status_grid

def create_hero_section(theme):
    """Create hero section for public dashboard"""
    return html.Div(
        className="hero-section",
        style={
            "background": f"linear-gradient(135deg, {theme['secondary_bg']} 0%, {theme['accent_bg']} 100%)",
            "borderRadius": "12px",
            "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.3)",
            "textAlign": "center",
            "padding": "2rem 0",
            "margin": "1rem 0"
        },
        children=[
            html.H1(
                "स्वच्छ आंध्र प्रदेश",
                style={
                    "fontSize": "3rem",
                    "fontWeight": "800",
                    "marginBottom": "0.5rem",
                    "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.5)",
                    "color": theme["text_primary"]
                }
            ),
            html.P(
                "Clean Andhra Pradesh • Real-time Analytics Dashboard",
                style={
                    "fontSize": "1.25rem",
                    "fontWeight": "500",
                    "margin": "0",
                    "color": theme["text_secondary"]
                }
            ),
            html.P(
                "🖱️ Hover at the top of your screen for navigation options",
                style={
                    "fontSize": "0.95rem",
                    "fontWeight": "400",
                    "margin": "1rem 0 0 0",
                    "color": theme["brand_primary"],
                    "fontStyle": "italic",
                    "padding": "0.5rem 1rem",
                    "backgroundColor": f"{theme['accent_bg']}80",
                    "borderRadius": "8px",
                    "border": f"1px solid {theme['brand_primary']}40"
                }
            )
        ]
    )

def create_welcome_section(theme):
    """Create welcome section with mission info"""
    return html.Div(
        className="welcome-section",
        style={
            "backgroundColor": theme["accent_bg"],
            "border": f"2px solid {theme['card_bg']}",
            "borderRadius": "12px",
            "padding": "2rem",
            "margin": "2rem 0",
            "textAlign": "center"
        },
        children=[
            html.H2(
                "🌟 Welcome to Swaccha Andhra Pradesh",
                style={
                    "color": theme["brand_primary"],
                    "fontSize": "2rem",
                    "marginBottom": "1rem"
                }
            ),
            html.P(
                "Transforming Andhra Pradesh into a cleaner, greener state through innovative waste management and community participation. Track our progress in real-time.",
                style={
                    "fontSize": "1.1rem",
                    "color": theme["text_secondary"],
                    "marginBottom": "2rem",
                    "lineHeight": "1.8"
                }
            ),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                    "gap": "1rem",
                    "marginTop": "2rem"
                },
                children=[
                    html.Div([
                        html.Div("🎯", style={"fontSize": "2rem", "marginBottom": "0.5rem"}),
                        html.H4("Our Mission", style={"color": theme["text_primary"], "marginBottom": "0.5rem"}),
                        html.P("Creating a sustainable and clean environment for future generations", 
                               style={"fontSize": "0.9rem", "color": theme["text_secondary"]})
                    ], style={"padding": "1rem", "backgroundColor": theme["card_bg"], "borderRadius": "8px"}),
                    
                    html.Div([
                        html.Div("🌱", style={"fontSize": "2rem", "marginBottom": "0.5rem"}),
                        html.H4("Impact", style={"color": theme["text_primary"], "marginBottom": "0.5rem"}),
                        html.P("Reducing waste, increasing recycling, and promoting eco-friendly practices", 
                               style={"fontSize": "0.9rem", "color": theme["text_secondary"]})
                    ], style={"padding": "1rem", "backgroundColor": theme["card_bg"], "borderRadius": "8px"}),
                    
                    html.Div([
                        html.Div("🤝", style={"fontSize": "2rem", "marginBottom": "0.5rem"}),
                        html.H4("Community", style={"color": theme["text_primary"], "marginBottom": "0.5rem"}),
                        html.P("Engaging citizens and organizations in our cleanliness mission", 
                               style={"fontSize": "0.9rem", "color": theme["text_secondary"]})
                    ], style={"padding": "1rem", "backgroundColor": theme["card_bg"], "borderRadius": "8px"})
                ]
            )
        ]
    )

def get_sample_metrics():
    """Get sample metrics data for the dashboard"""
    return [
        {
            "icon": "🏘️",
            "title": "Districts",
            "value": "13",
            "unit": "Covered",
            "size": "normal"
        },
        {
            "icon": "🚮",
            "title": "Waste Collected",
            "value": "2.4M",
            "unit": "Tons",
            "size": "normal"
        },
        {
            "icon": "♻️",
            "title": "Recycling Rate",
            "value": "78%",
            "unit": "Efficiency",
            "size": "normal"
        },
        {
            "icon": "🌱",
            "title": "Clean Score",
            "value": "94",
            "unit": "Rating",
            "size": "normal"
        }
    ]

def get_sample_status():
    """Get sample status data for the dashboard"""
    return [
        {
            "label": "Data Collection",
            "status": "active",
            "color_key": "success",
            "size": "normal"
        },
        {
            "label": "API Services",
            "status": "online",
            "color_key": "info",
            "size": "normal"
        },
        {
            "label": "Mobile Sync",
            "status": "connected",
            "color_key": "success",
            "size": "normal"
        },
        {
            "label": "Public Access",
            "status": "available",
            "color_key": "success",
            "size": "normal"
        }
    ]

def create_status_section(theme):
    """Create system status section"""
    status_data = get_sample_status()
    
    return html.Div(
        className="status-section",
        style={
            "backgroundColor": theme["accent_bg"],
            "border": f"2px solid {theme['card_bg']}",
            "borderRadius": "8px",
            "padding": "1.5rem",
            "margin": "1rem 0"
        },
        children=[
            html.H3(
                "🔄 System Status",
                style={
                    "marginBottom": "1rem",
                    "color": theme["text_primary"],
                    "fontSize": "1.5rem"
                }
            ),
            create_status_grid(status_data, theme)
        ]
    )

def build_public_layout(theme_name="dark"):
    """
    Build the complete public layout
    
    Args:
        theme_name (str): Current theme name
        
    Returns:
        html.Div: Complete public layout
    """
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    metrics_data = get_sample_metrics()
    
    return html.Div(
        className="public-layout",
        style=theme_styles["container_style"],
        children=[
            # Hover overlay banner (admin access)
            create_hover_overlay_banner(theme_name),
            
            # Main header (always visible)
            render_header(),
            
            # Main content area
            html.Div(
                className="main-content",
                style=theme_styles["main_content_style"],
                children=[
                    # Hero section
                    create_hero_section(theme),
                    
                    # Welcome section
                    create_welcome_section(theme),
                    
                    # Metrics grid
                    create_metric_grid(metrics_data, theme_styles),
                    
                    # Status section
                    create_status_section(theme)
                ]
            ),
            
            # Footer
            render_footer()
        ]
    )

def create_mobile_public_layout(theme_name="dark"):
    """
    Create mobile-optimized version of public layout
    """
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    # Mobile-specific metrics (fewer items)
    mobile_metrics = get_sample_metrics()[:2]  # Only show first 2 metrics
    
    return html.Div(
        className="mobile-public-layout",
        style={
            **theme_styles["container_style"],
            "padding": "0.5rem"
        },
        children=[
            create_hover_overlay_banner(theme_name),
            render_header(),
            html.Div(
                style={
                    **theme_styles["main_content_style"],
                    "padding": "1rem"
                },
                children=[
                    create_hero_section(theme),
                    create_metric_grid(mobile_metrics, theme_styles, columns=1),
                    create_status_section(theme)
                ]
            ),
            render_footer()
        ]
    )