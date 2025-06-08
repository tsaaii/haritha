# components/navigation/hover_overlay.py
"""
Hover Overlay Navigation Component
Creates the hoverable banner for admin access
"""

from dash import html
from config.themes import THEMES
from components.navigation.theme_switcher import create_theme_switcher

def create_hover_trigger():
    """Create invisible hover trigger area at top of screen"""
    return html.Div(
        id="hover-trigger-area",
        style={
            "position": "fixed",
            "top": "0",
            "left": "0", 
            "right": "0",
            "height": "30px",
            "zIndex": "10002",
            "backgroundColor": "transparent",
            "cursor": "pointer"
        }
    )

def create_admin_login_button(theme):
    """Create admin login button"""
    return html.Button(
        [html.Span(style={"marginRight": "0.5rem"}), "User Login"],
        id="admin-login-btn",
        style={
            "background": f"linear-gradient(135deg, {theme['success']} 0%, {theme['info']} 100%)",
            "border": "none",
            "color": "white",
            "fontSize": "1rem",
            "fontWeight": "700",
            "padding": "0.8rem 1.5rem",
            "borderRadius": "10px",
            "cursor": "pointer",
            "transition": "all 0.2s ease",
            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.3)",
            "textTransform": "uppercase",
            "letterSpacing": "0.5px"
        }
    )

def create_divider(theme):
    """Create visual divider"""
    return html.Div(
        style={
            "width": "2px",
            "height": "50px",
            "backgroundColor": theme["border_light"],
            "margin": "0 1rem"
        }
    )

def create_hover_overlay_banner(current_theme="dark"):
    """
    Create complete hover overlay banner with navigation, theme switcher and login
    
    Args:
        current_theme (str): Currently active theme
        
    Returns:
        html.Div: Complete hover overlay component
    """
    theme = THEMES[current_theme]
    
    return html.Div([
        # Invisible hover trigger area
        create_hover_trigger(),
        
        # The actual overlay banner - with full navigation
        html.Div(
            id="overlay-banner",
            className="overlay-banner",
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "right": "0",
                "zIndex": "10001",
                "backgroundColor": f"{theme['secondary_bg']}ee",  # Semi-transparent
                "backdropFilter": "blur(10px)",
                "border": f"3px solid {theme['brand_primary']}",
                "borderTop": "none",
                "borderRadius": "0 0 12px 12px",
                "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.5)",
                "transform": "translateY(-100%)",
                "transition": "transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                "padding": "1rem 2rem 1.5rem 2rem",
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "opacity": "0",
                "pointerEvents": "none"
            },
            children=[
                # Left - Navigation buttons
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "1rem",
                        "alignItems": "center"
                    },
                    children=[
                        html.Button(
                            [html.Span("🏠 "), "Overview"],
                            id="nav-overview",
                            style={
                                "backgroundColor": "transparent",
                                "border": f"2px solid {theme['border_light']}",
                                "color": theme["text_primary"],
                                "padding": "0.6rem 1.2rem",
                                "borderRadius": "8px",
                                "cursor": "pointer",
                                "fontSize": "0.9rem",
                                "fontWeight": "600",
                                "transition": "all 0.2s ease"
                            }
                        ),
                        html.Button(
                            [html.Span("📈 "), "Analytics"],
                            id="nav-analytics",
                            style={
                                "backgroundColor": "transparent",
                                "border": f"2px solid {theme['border_light']}",
                                "color": theme["text_primary"],
                                "padding": "0.6rem 1.2rem",
                                "borderRadius": "8px",
                                "cursor": "pointer",
                                "fontSize": "0.9rem",
                                "fontWeight": "600",
                                "transition": "all 0.2s ease"
                            }
                        ),
                        html.Button(
                            [html.Span("📋 "), "Reports"],
                            id="nav-reports",
                            style={
                                "backgroundColor": "transparent",
                                "border": f"2px solid {theme['border_light']}",
                                "color": theme["text_primary"],
                                "padding": "0.6rem 1.2rem",
                                "borderRadius": "8px",
                                "cursor": "pointer",
                                "fontSize": "0.9rem",
                                "fontWeight": "600",
                                "transition": "all 0.2s ease"
                            }
                        )
                    ]
                ),
                
                # Center - Theme switcher
                create_theme_switcher(current_theme),
                
                # Right - Admin login
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "1rem",
                        "alignItems": "center"
                    },
                    children=[
                        create_divider(theme),
                        create_admin_login_button(theme)
                    ]
                )
            ]
        )
    ])

def create_simple_hover_overlay_banner(current_theme="dark"):
    """
    Create simplified hover overlay banner with only theme switcher and login
    Alternative version without navigation buttons
    
    Args:
        current_theme (str): Currently active theme
        
    Returns:
        html.Div: Simplified hover overlay component
    """
    theme = THEMES[current_theme]
    
    return html.Div([
        # Invisible hover trigger area
        create_hover_trigger(),
        
        # The actual overlay banner - simplified
        html.Div(
            id="overlay-banner",
            className="overlay-banner",
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "right": "0",
                "zIndex": "10001",
                "backgroundColor": f"{theme['secondary_bg']}ee",  # Semi-transparent
                "backdropFilter": "blur(10px)",
                "border": f"3px solid {theme['brand_primary']}",
                "borderTop": "none",
                "borderRadius": "0 0 12px 12px",
                "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.5)",
                "transform": "translateY(-100%)",
                "transition": "transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                "padding": "1rem 2rem 1.5rem 2rem",
                "display": "flex",
                "justifyContent": "center",  # Center the content
                "alignItems": "center",
                "opacity": "0",
                "pointerEvents": "none"
            },
            children=[
                # Centered content - Only theme switcher and login
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "1rem",
                        "alignItems": "center",
                        "justifyContent": "center"
                    },
                    children=[
                        create_theme_switcher(current_theme),
                        create_divider(theme),
                        create_admin_login_button(theme)
                    ]
                )
            ]
        )
    ])

def create_compact_hover_overlay(current_theme="dark"):
    """
    Create a more compact version of the hover overlay
    Useful for smaller screens or simpler layouts
    """
    theme = THEMES[current_theme]
    
    return html.Div([
        create_hover_trigger(),
        html.Div(
            id="compact-overlay-banner",
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "right": "0",
                "zIndex": "10001",
                "backgroundColor": f"{theme['secondary_bg']}dd",
                "border": f"2px solid {theme['brand_primary']}",
                "borderTop": "none",
                "transform": "translateY(-100%)",
                "transition": "transform 0.3s ease",
                "padding": "1rem",
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "gap": "1rem",
                "opacity": "0",
                "pointerEvents": "none"
            },
            children=[
                create_theme_switcher(current_theme),
                create_admin_login_button(theme)
            ]
        )
    ])