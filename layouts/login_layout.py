# layouts/login_layout.py
"""
Login Page Layout - UPDATED
Themed login interface with Google OAuth integration and hardcoded credentials
"""

from dash import html, dcc
from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner


def create_login_hero(theme):
    """Create login page hero section"""
    return html.Div(
        className="login-hero",
        style={
            "background": f"linear-gradient(135deg, {theme['secondary_bg']} 0%, {theme['accent_bg']} 100%)",
            "borderRadius": "12px",
            "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.3)",
            "textAlign": "center",
            "padding": "3rem 2rem",
            "margin": "2rem 0",
            "position": "relative",
            "overflow": "hidden"
        },
        children=[
            # Decorative background pattern
            html.Div(
                style={
                    "position": "absolute",
                    "top": "0",
                    "left": "0",
                    "right": "0",
                    "bottom": "0",
                    "background": f"radial-gradient(circle at 20% 80%, {theme['brand_primary']}22 0%, transparent 50%)",
                    "pointerEvents": "none"
                }
            ),
            
            # Logo section
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "gap": "2rem",
                    "marginBottom": "2rem",
                    "flexWrap": "wrap"
                },
                children=[
                    html.Img(
                        src="/assets/img/left.png",
                        alt="Organization Logo",
                        style={
                            "height": "80px",
                            "width": "auto",
                            "objectFit": "contain",
                            "filter": "drop-shadow(2px 2px 8px rgba(0, 0, 0, 0.3))"
                        }
                    ),
                    html.Div([
                        html.H1(
                            "Swaccha Andhra",
                            style={
                                "color": theme["text_primary"],
                                "fontSize": "2.5rem",
                                "fontWeight": "900",
                                "margin": "0",
                                "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.5)"
                            }
                        ),
                        html.P(
                            "Admin Portal",
                            style={
                                "color": theme["text_secondary"],
                                "fontSize": "1.2rem",
                                "fontWeight": "600",
                                "margin": "0.5rem 0 0 0"
                            }
                        )
                    ]),
                    html.Img(
                        src="/assets/img/right.png",
                        alt="Government Logo", 
                        style={
                            "height": "80px",
                            "width": "auto",
                            "objectFit": "contain",
                            "filter": "drop-shadow(2px 2px 8px rgba(0, 0, 0, 0.3))"
                        }
                    )
                ]
            ),
            
            # Security message
            html.Div([
                html.Div("🔐", style={"fontSize": "2rem", "marginBottom": "1rem"}),
                html.H3(
                    "Secure Access Required",
                    style={
                        "color": theme["text_primary"],
                        "fontSize": "1.5rem",
                        "marginBottom": "0.5rem"
                    }
                ),
                html.P(
                    "This portal requires authorized access. Please authenticate with your authorized Google account or use development credentials.",
                    style={
                        "color": theme["text_secondary"],
                        "fontSize": "1rem",
                        "lineHeight": "1.6",
                        "maxWidth": "500px",
                        "margin": "0 auto"
                    }
                )
            ])
        ]
    )


def create_login_form(theme):
    """Create the main login form - STABLE with multiple reliable methods"""
    return html.Div(
        className="login-form-container",
        style={
            "maxWidth": "400px",
            "margin": "0 auto",
            "backgroundColor": theme["card_bg"],
            "borderRadius": "16px",
            "border": f"2px solid {theme['accent_bg']}",
            "boxShadow": "0 12px 40px rgba(0, 0, 0, 0.3)",
            "padding": "2.5rem",
            "textAlign": "center"
        },
        children=[
            # Form header
            html.Div([
                html.H2(
                    "Administrator Login",
                    style={
                        "color": theme["text_primary"],
                        "fontSize": "1.8rem",
                        "fontWeight": "700",
                        "marginBottom": "0.5rem"
                    }
                ),
                html.P(
                    "Choose your authentication method",
                    style={
                        "color": theme["text_secondary"],
                        "fontSize": "1rem",
                        "marginBottom": "2rem"
                    }
                )
            ]),
            
            # STABLE METHOD 1: Quick Demo Login - One Click
            html.Button(
                [
                    html.Span("🚀", style={"marginRight": "12px", "fontSize": "1.2rem"}),
                    html.Span("Quick Demo Login", style={"fontSize": "1rem", "fontWeight": "600"})
                ],
                id="demo-login-btn",
                style={
                    "width": "100%",
                    "padding": "16px 24px",
                    "backgroundColor": theme["success"],
                    "color": "white",
                    "border": "none",
                    "borderRadius": "8px",
                    "fontSize": "1rem",
                    "fontWeight": "600",
                    "cursor": "pointer",
                    "transition": "all 0.2s ease",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "marginBottom": "1rem",
                    "boxShadow": "0 4px 12px rgba(56, 161, 105, 0.3)"
                }
            ),
            
            # Info for demo login
            html.P(
                "Instant access - no credentials needed",
                style={
                    "color": theme["text_secondary"],
                    "fontSize": "0.85rem",
                    "margin": "0 0 1.5rem 0",
                    "fontStyle": "italic"
                }
            ),
            
            # Divider
            html.Div([
                html.Div(style={"height": "1px", "backgroundColor": theme["border_light"], "flex": "1"}),
                html.Span("OR", style={"color": theme["text_secondary"], "fontSize": "0.9rem", "padding": "0 1rem", "backgroundColor": theme["card_bg"]}),
                html.Div(style={"height": "1px", "backgroundColor": theme["border_light"], "flex": "1"})
            ], style={"display": "flex", "alignItems": "center", "margin": "1.5rem 0"}),
            
            # STABLE METHOD 2: Multiple Preset Accounts
            html.Div([
                html.P(
                    "Select Admin Account:",
                    style={
                        "color": theme["text_secondary"],
                        "fontSize": "0.9rem",
                        "marginBottom": "1rem",
                        "fontWeight": "600"
                    }
                ),
                
                # Admin account buttons
                html.Div([
                    html.Button(
                        "👨‍💼 Administrator",
                        id="admin-account-btn",
                        style={
                            "width": "100%",
                            "padding": "12px 16px",
                            "backgroundColor": theme["brand_primary"],
                            "color": "white",
                            "border": "none",
                            "borderRadius": "6px",
                            "fontSize": "0.9rem",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "marginBottom": "0.5rem",
                            "transition": "all 0.2s ease"
                        }
                    ),
                    html.Button(
                        "👨‍💻 Developer",
                        id="dev-account-btn",
                        style={
                            "width": "100%",
                            "padding": "12px 16px",
                            "backgroundColor": theme["info"],
                            "color": "white",
                            "border": "none",
                            "borderRadius": "6px",
                            "fontSize": "0.9rem",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "marginBottom": "0.5rem",
                            "transition": "all 0.2s ease"
                        }
                    ),
                    html.Button(
                        "👁️ Viewer",
                        id="viewer-account-btn",
                        style={
                            "width": "100%",
                            "padding": "12px 16px",
                            "backgroundColor": theme["warning"],
                            "color": "white",
                            "border": "none",
                            "borderRadius": "6px",
                            "fontSize": "0.9rem",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "marginBottom": "1rem",
                            "transition": "all 0.2s ease"
                        }
                    )
                ])
            ]),
            
            # Divider
            html.Div([
                html.Div(style={"height": "1px", "backgroundColor": theme["border_light"], "flex": "1"}),
                html.Span("OR", style={"color": theme["text_secondary"], "fontSize": "0.9rem", "padding": "0 1rem", "backgroundColor": theme["card_bg"]}),
                html.Div(style={"height": "1px", "backgroundColor": theme["border_light"], "flex": "1"})
            ], style={"display": "flex", "alignItems": "center", "margin": "1.5rem 0"}),
            
            # STABLE METHOD 3: PIN Code Access
            html.Div([
                html.P(
                    "Access PIN:",
                    style={
                        "color": theme["text_secondary"],
                        "fontSize": "0.9rem",
                        "marginBottom": "1rem",
                        "fontWeight": "600"
                    }
                ),
                
                html.Div([
                    dcc.Input(
                        id="access-pin",
                        type="password",
                        placeholder="Enter 4-digit PIN",
                        maxLength=4,
                        style={
                            "width": "60%",
                            "padding": "12px 16px",
                            "backgroundColor": theme["accent_bg"],
                            "border": f"2px solid {theme['border_light']}",
                            "borderRadius": "8px 0 0 8px",
                            "color": theme["text_primary"],
                            "fontSize": "1.2rem",
                            "textAlign": "center",
                            "outline": "none",
                            "fontFamily": "monospace",
                            "letterSpacing": "0.5rem"
                        }
                    ),
                    html.Button(
                        "Enter",
                        id="pin-login-btn",
                        style={
                            "width": "40%",
                            "padding": "12px 16px",
                            "backgroundColor": theme["brand_primary"],
                            "color": "white",
                            "border": "none",
                            "borderRadius": "0 8px 8px 0",
                            "fontSize": "1rem",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease"
                        }
                    )
                ], style={"display": "flex", "marginBottom": "1rem"})
            ]),
            
            # PIN hints
            html.Div([
                html.P(
                    "💡 Valid PINs:",
                    style={
                        "color": theme["info"],
                        "fontSize": "0.85rem",
                        "marginBottom": "0.5rem",
                        "fontWeight": "600"
                    }
                ),
                html.Div([
                    html.Span("1234", style={"backgroundColor": theme["accent_bg"], "padding": "0.25rem 0.5rem", "borderRadius": "4px", "fontFamily": "monospace", "margin": "0.25rem", "fontSize": "0.8rem"}),
                    html.Span(" Admin • "),
                    html.Span("5678", style={"backgroundColor": theme["accent_bg"], "padding": "0.25rem 0.5rem", "borderRadius": "4px", "fontFamily": "monospace", "margin": "0.25rem", "fontSize": "0.8rem"}),
                    html.Span(" Dev • "),
                    html.Span("9999", style={"backgroundColor": theme["accent_bg"], "padding": "0.25rem 0.5rem", "borderRadius": "4px", "fontFamily": "monospace", "margin": "0.25rem", "fontSize": "0.8rem"}),
                    html.Span(" Demo")
                ], style={"color": theme["text_secondary"], "fontSize": "0.8rem", "lineHeight": "2"})
            ], style={
                "backgroundColor": f"{theme['info']}22",
                "border": f"1px solid {theme['info']}",
                "borderRadius": "8px",
                "padding": "1rem",
                "marginBottom": "1.5rem"
            }),
            
            # Optional: Google OAuth (if available)
            html.Details([
                html.Summary(
                    "Advanced: Google OAuth",
                    style={
                        "color": theme["text_secondary"],
                        "fontSize": "0.9rem",
                        "cursor": "pointer",
                        "marginBottom": "1rem"
                    }
                ),
                html.Button(
                    [
                        html.Span("🔵", style={"marginRight": "8px"}),
                        "Continue with Google"
                    ],
                    id="google-login-btn",
                    style={
                        "width": "100%",
                        "padding": "12px 16px",
                        "backgroundColor": "#4285f4",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "8px",
                        "fontSize": "0.9rem",
                        "fontWeight": "600",
                        "cursor": "pointer",
                        "transition": "all 0.2s ease"
                    }
                ),
                html.P(
                    "Note: Google OAuth may be unreliable. Use methods above for guaranteed access.",
                    style={
                        "color": theme["warning"],
                        "fontSize": "0.75rem",
                        "marginTop": "0.5rem",
                        "fontStyle": "italic"
                    }
                )
            ], style={"marginBottom": "1.5rem"}),
            
            # Help text
            html.Div([
                html.P(
                    "Need help? All methods above provide immediate access to the dashboard.",
                    style={
                        "color": theme["text_secondary"],
                        "fontSize": "0.85rem",
                        "margin": "0",
                        "lineHeight": "1.4"
                    }
                )
            ])
        ]
    )


def create_auth_status_card(theme, message_type="info", title="", message=""):
    """Create authentication status card for feedback"""
    color_map = {
        "success": theme["success"],
        "error": theme["error"],
        "warning": theme["warning"],
        "info": theme["info"]
    }
    
    icon_map = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    color = color_map.get(message_type, theme["info"])
    icon = icon_map.get(message_type, "ℹ️")
    
    return html.Div(
        id="auth-status-card",
        style={
            "maxWidth": "400px",
            "margin": "1rem auto",
            "backgroundColor": theme["card_bg"],
            "border": f"2px solid {color}",
            "borderRadius": "12px",
            "padding": "1.5rem",
            "textAlign": "center",
            "display": "none"  # Hidden by default
        },
        children=[
            html.Div(icon, style={"fontSize": "2rem", "marginBottom": "1rem"}),
            html.H3(
                title,
                style={
                    "color": color,
                    "fontSize": "1.2rem",
                    "fontWeight": "700",
                    "marginBottom": "0.5rem"
                }
            ),
            html.P(
                message,
                style={
                    "color": theme["text_secondary"],
                    "fontSize": "1rem",
                    "lineHeight": "1.5",
                    "margin": "0"
                }
            )
        ]
    )


def build_login_layout(theme_name="dark", error_message=""):
    """
    Build the complete login page layout
    
    Args:
        theme_name (str): Current theme name
        error_message (str): Error message to display
        
    Returns:
        html.Div: Complete login layout
    """
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    # Determine error display
    show_error = bool(error_message)
    error_card_style = {"display": "block" if show_error else "none"}
    
    return html.Div(
        className="login-layout",
        style=theme_styles["container_style"],
        children=[
            # Hover overlay for theme switching
            create_hover_overlay_banner(theme_name),
            
            # Main login content
            html.Div(
                className="login-content",
                style={
                    **theme_styles["main_content_style"],
                    "maxWidth": "800px",
                    "margin": "0 auto",
                    "paddingTop": "2rem"
                },
                children=[
                    # Back to public button
                    html.Div(
                        style={
                            "textAlign": "left",
                            "marginBottom": "2rem"
                        },
                        children=[
                            html.Button(
                                [html.Span("← "), "Back to Public Dashboard"],
                                id="back-to-public-btn",
                                style={
                                    "backgroundColor": "transparent",
                                    "border": f"2px solid {theme['border_light']}",
                                    "color": theme["text_secondary"],
                                    "padding": "0.5rem 1rem",
                                    "borderRadius": "8px",
                                    "cursor": "pointer",
                                    "fontSize": "0.9rem",
                                    "transition": "all 0.2s ease"
                                }
                            )
                        ]
                    ),
                    
                    # Login hero section
                    create_login_hero(theme),
                    
                    # Error message card (conditionally displayed)
                    html.Div(
                        id="auth-status-card",
                        style={
                            "maxWidth": "400px",
                            "margin": "1rem auto",
                            "backgroundColor": theme["card_bg"],
                            "border": f"2px solid {theme['error']}",
                            "borderRadius": "12px",
                            "padding": "1.5rem",
                            "textAlign": "center",
                            **error_card_style
                        },
                        children=[
                            html.Div("❌", style={"fontSize": "2rem", "marginBottom": "1rem"}),
                            html.H3(
                                "Authentication Error",
                                style={
                                    "color": theme["error"],
                                    "fontSize": "1.2rem",
                                    "fontWeight": "700",
                                    "marginBottom": "0.5rem"
                                }
                            ),
                            html.P(
                                error_message or "",
                                style={
                                    "color": theme["text_secondary"],
                                    "fontSize": "1rem",
                                    "lineHeight": "1.5",
                                    "margin": "0"
                                }
                            )
                        ]
                    ) if show_error else html.Div(),
                    
                    # Login form
                    create_login_form(theme)
                ]
            )
        ]
    )


def create_mobile_login_layout(theme_name="dark"):
    """Create mobile-optimized login layout"""
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    return html.Div(
        className="mobile-login-layout",
        style={
            **theme_styles["container_style"],
            "padding": "1rem"
        },
        children=[
            create_hover_overlay_banner(theme_name),
            html.Div(
                style={
                    **theme_styles["main_content_style"],
                    "padding": "1rem"
                },
                children=[
                    # Compact hero for mobile
                    html.Div(
                        style={
                            "textAlign": "center",
                            "marginBottom": "2rem"
                        },
                        children=[
                            html.H1(
                                "Admin Login",
                                style={
                                    "color": theme["text_primary"],
                                    "fontSize": "1.8rem",
                                    "marginBottom": "0.5rem"
                                }
                            ),
                            html.P(
                                "Secure access required",
                                style={
                                    "color": theme["text_secondary"],
                                    "fontSize": "1rem"
                                }
                            )
                        ]
                    ),
                    
                    # Mobile-optimized form
                    create_login_form(theme)
                ]
            )
        ]
    )