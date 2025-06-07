# header.py
from dash import html, dcc
import datetime

def render_header():
    """
    Render responsive header following 6-foot rule and high contrast principles
    Optimized for TV, mobile, and web viewing
    """
    current_time = datetime.datetime.now()
    
    return html.Div(
        className="app-header",
        id="app-header",
        style={
            "backgroundColor": "#0D1B2A",  # Dark Navy Blue for high contrast
            "color": "#FFFFFF",
            "padding": "1rem 2rem",
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "fontSize": "1.5rem",
            "fontWeight": "bold",
            "position": "sticky",
            "top": "0",
            "zIndex": "1000",
            "boxShadow": "0 2px 10px rgba(0, 0, 0, 0.3)",
            "borderBottom": "3px solid #3182CE"
        },
        children=[
            # Left side - Logo and Title
            html.Div(
                className="header-left",
                id="header-left",
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "flex": "1"
                },
                children=[
                    html.Div(
                        "📊",
                        style={
                            "fontSize": "2rem",
                            "marginRight": "0.75rem",
                            "filter": "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.5))"
                        }
                    ),
                    html.Div(
                        id="header-title",
                        children=[
                            html.Div(
                                "Swaccha Andhra",
                                style={
                                    "fontSize": "1.5rem",
                                    "fontWeight": "800",
                                    "lineHeight": "1.2",
                                    "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.5)"
                                }
                            ),
                            html.Div(
                                "Dashboard",
                                style={
                                    "fontSize": "1rem",
                                    "fontWeight": "500",
                                    "color": "#A0AEC0",
                                    "lineHeight": "1"
                                }
                            )
                        ]
                    )
                ]
            ),
            
            # Center - Navigation (hidden on mobile)
            html.Div(
                className="header-nav",
                id="header-nav",
                style={
                    "display": "flex",
                    "gap": "2rem",
                    "flex": "1",
                    "justifyContent": "center"
                },
                children=[
                    create_nav_item("Overview", "/", True),
                    create_nav_item("Analytics", "/analytics", False),
                    create_nav_item("Reports", "/reports", False)
                ]
            ),
            
            # Right side - Time and Status
            html.Div(
                className="header-right",
                id="header-right",
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "flex-end",
                    "flex": "1"
                },
                children=[
                    html.Div(
                        id="live-time",
                        children=current_time.strftime("%H:%M:%S"),
                        style={
                            "fontSize": "1.2rem",
                            "fontWeight": "700",
                            "color": "#68D391",
                            "fontFamily": "monospace"
                        }
                    ),
                    html.Div(
                        current_time.strftime("%d %b %Y"),
                        style={
                            "fontSize": "0.9rem",
                            "fontWeight": "400",
                            "color": "#A0AEC0",
                            "marginTop": "0.25rem"
                        }
                    )
                ]
            ),
            
            # Mobile menu button (hidden on desktop)
            html.Div(
                className="mobile-menu-btn",
                id="mobile-menu-btn",
                style={
                    "display": "none",
                    "fontSize": "1.5rem",
                    "cursor": "pointer",
                    "padding": "0.5rem",
                    "borderRadius": "4px",
                    "backgroundColor": "#2D3748"
                },
                children="☰"
            )
        ]
    )

def create_nav_item(label, href, active=False):
    """Create navigation item with active state"""
    return html.A(
        label,
        href=href,
        style={
            "color": "#FFFFFF" if active else "#A0AEC0",
            "textDecoration": "none",
            "fontSize": "1rem",
            "fontWeight": "600" if active else "500",
            "padding": "0.5rem 1rem",
            "borderRadius": "6px",
            "backgroundColor": "#3182CE" if active else "transparent",
            "transition": "all 0.2s ease",
            "border": "2px solid transparent",
            "borderColor": "#3182CE" if active else "transparent"
        }
    )

def render_mobile_header():
    """
    Render mobile-optimized header
    """
    current_time = datetime.datetime.now()
    
    return html.Div(
        className="app-header mobile-header",
        style={
            "backgroundColor": "#0D1B2A",
            "color": "#FFFFFF",
            "padding": "0.75rem 1rem",
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "position": "sticky",
            "top": "0",
            "zIndex": "1000",
            "boxShadow": "0 2px 10px rgba(0, 0, 0, 0.3)",
            "borderBottom": "3px solid #3182CE"
        },
        children=[
            # Logo and compact title
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center"
                },
                children=[
                    html.Div("📊", style={"fontSize": "1.5rem", "marginRight": "0.5rem"}),
                    html.Div(
                        "Swaccha AP",
                        style={
                            "fontSize": "1.2rem",
                            "fontWeight": "800",
                            "textShadow": "1px 1px 2px rgba(0, 0, 0, 0.5)"
                        }
                    )
                ]
            ),
            
            # Compact time display
            html.Div(
                current_time.strftime("%H:%M"),
                style={
                    "fontSize": "1.1rem",
                    "fontWeight": "700",
                    "color": "#68D391",
                    "fontFamily": "monospace"
                }
            )
        ]
    )

def render_tv_header():
    """
    Render TV-optimized header with larger elements
    """
    current_time = datetime.datetime.now()
    
    return html.Div(
        className="app-header tv-header",
        style={
            "backgroundColor": "#0D1B2A",
            "color": "#FFFFFF",
            "padding": "2rem 3rem",
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "fontSize": "2rem",
            "fontWeight": "bold",
            "position": "sticky",
            "top": "0",
            "zIndex": "1000",
            "boxShadow": "0 4px 20px rgba(0, 0, 0, 0.4)",
            "borderBottom": "4px solid #3182CE"
        },
        children=[
            # Large logo and title for TV viewing
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center"
                },
                children=[
                    html.Div(
                        "📊",
                        style={
                            "fontSize": "3rem",
                            "marginRight": "1rem",
                            "filter": "drop-shadow(3px 3px 6px rgba(0, 0, 0, 0.5))"
                        }
                    ),
                    html.Div([
                        html.Div(
                            "स्वच्छ आंध्र प्रदेश",
                            style={
                                "fontSize": "2.5rem",
                                "fontWeight": "800",
                                "lineHeight": "1.2",
                                "textShadow": "3px 3px 6px rgba(0, 0, 0, 0.5)"
                            }
                        ),
                        html.Div(
                            "Real-time Analytics Dashboard",
                            style={
                                "fontSize": "1.2rem",
                                "fontWeight": "500",
                                "color": "#A0AEC0",
                                "lineHeight": "1"
                            }
                        )
                    ])
                ]
            ),
            
            # Large time display for TV
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "flex-end"
                },
                children=[
                    html.Div(
                        current_time.strftime("%H:%M:%S"),
                        style={
                            "fontSize": "2.5rem",
                            "fontWeight": "800",
                            "color": "#68D391",
                            "fontFamily": "monospace",
                            "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.5)"
                        }
                    ),
                    html.Div(
                        current_time.strftime("%A, %d %B %Y"),
                        style={
                            "fontSize": "1.2rem",
                            "fontWeight": "400",
                            "color": "#A0AEC0",
                            "marginTop": "0.5rem"
                        }
                    )
                ]
            )
        ]
    )