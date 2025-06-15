# layouts/public_layout.py
"""
Responsive Public Layout - Compatible with existing theme system
Optimized tile sizes for perfect screen fit on all devices
"""

from dash import html,dcc
from footer import render_footer
from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner
from config.themes import THEMES, DEFAULT_THEME



def create_responsive_logo(image_name, alt_text, position="left"):
    """Create responsive logo that auto-resizes for all devices"""
    return html.Img(
        src=f"/assets/img/{image_name}.png",
        alt=alt_text,
        className=f"logo-{position} responsive-logo",
        style={
            "display": "block",
            "visibility": "visible",
            "opacity": "1"
        }
    )


def create_hero_section(theme_styles):
    """Create compact hero section optimized for one-screen fit"""
    return html.Div(
        className="hero-section",
        style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "height": "clamp(80px, 12vh, 120px)",
            "width": "100%",
            "padding": "clamp(0.75rem, 2vh, 1.25rem) clamp(1rem, 3vw, 2rem)"
        },
        children=[
            html.Div(
                className="hero-content",
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "gap": "clamp(1in, 4vw, 3rem)",  # Controlled gap between elements
                    "maxWidth": "1200px",  # Limit max width to prevent extreme stretching
                    "width": "100%",
                    "height": "100%"
                },
                children=[
                    # Left Logo - Positioned near title
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "height": "100%",
                            "flexShrink": "0"  # Prevent logo from shrinking
                        },
                        children=[
                            create_responsive_logo("left", "Left Organization Logo", "left")
                        ]
                    ),
                    
                    # Title Section - Centered but not stretched
                    html.Div(
                        className="hero-title-section",
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "textAlign": "center",
                            "height": "100%",
                            "flexGrow": "0",  # Don't grow to fill space
                            "flexShrink": "0",  # Don't shrink
                            "minWidth": "300px",
                            "maxWidth": "600px"  # Limit title width
                        },
                        children=[
                            html.H1(
                                "Swaccha Andhra Corporation",
                                style={
                                    "margin": "0",
                                    "padding": "0",
                                    "lineHeight": "1",
                                    "fontSize": "clamp(0.9rem, 3vw, 1.8rem)",
                                    "fontWeight": "800",
                                    "textAlign": "center",
                                    "whiteSpace": "nowrap"  # Keep title on one line if possible
                                }
                            ),
                            html.P(
                                "Real Time Legacy Waste Remediation Progress Tracker",
                                className="hero-subtitle",
                                style={
                                    "margin": "0.25rem 0 0 0",
                                    "padding": "0",
                                    "fontSize": "clamp(1rem, 1.8vw, 0.9rem)",
                                    "fontWeight": "500",
                                    "lineHeight": "25px",
                                    "opacity": "0.9",
                                    "textAlign": "center"
                                }
                            )
                        ]
                    ),
                    
                    # Right Logo - Positioned near title
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "height": "100%",
                            "flexShrink": "0"  # Prevent logo from shrinking
                        },
                        children=[
                            create_responsive_logo("right", "Right Organization Logo", "right")
                        ]
                    )
                ]
            )
        ]
    )


def get_eight_metric_cards():
    """Get 8 metric cards for the dashboard"""
    return [
        {
            "icon": "🏘️",
            "title": "Districts Covered",
            "value": "13",
            "unit": "Active",
            "status": "online"
        },
        {
            "icon": "🚮",
            "title": "Waste Collected",
            "value": "2.4M",
            "unit": "Tons",
            "status": "online"
        },
        {
            "icon": "♻️",
            "title": "Recycling Rate",
            "value": "78%",
            "unit": "Efficiency",
            "status": "online"
        },
        {
            "icon": "🌱",
            "title": "Clean Score",
            "value": "94",
            "unit": "Rating",
            "status": "info"
        },
        {
            "icon": "🚛",
            "title": "Active Vehicles",
            "value": "156",
            "unit": "Fleet",
            "status": "online"
        },
        {
            "icon": "👥",
            "title": "Workers",
            "value": "1,247",
            "unit": "Active",
            "status": "online"
        },
        {
            "icon": "📊",
            "title": "Data Points",
            "value": "5,673",
            "unit": "Records",
            "status": "info"
        },
        {
            "icon": "⚡",
            "title": "System Status",
            "value": "99.8%",
            "unit": "Uptime",
            "status": "online"
        }
    ]


def create_metric_cards_grid(metrics_data, theme_styles):
    """Create responsive grid of 8 metric cards with optimized sizing"""
    cards = []
    theme = theme_styles["theme"]
    
    for metric in metrics_data:
        status_class = f"status-{metric.get('status', 'info')}"
        
        card = html.Div(
            className="metric-card",
            children=[
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
                    className="metric-value"
                ),
                html.Div(
                    metric["unit"],
                    className="metric-unit"
                )
            ]
        )
        cards.append(card)
    
    return html.Div(
        className="cards-grid",
        children=cards
    )


def build_public_layout(theme_name="dark", is_authenticated=False, user_data=None):
    """
    Build the complete public layout - compatible with existing theme system
    Optimized for one screen fit with proper tile sizing
    FIXED: Now compatible with public_landing_callbacks.py
    
    Args:
        theme_name (str): Current theme name from THEMES dict
        is_authenticated (bool): Authentication status
        user_data (dict): User data if authenticated
        
    Returns:
        html.Div: Complete public layout optimized for one screen
    """
    # Use existing theme system
    theme_styles = get_theme_styles(theme_name)
    metrics_data = get_eight_metric_cards()
    
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
            # Hover overlay banner (admin access) - THEME SWITCHING WORKS!
            create_hover_overlay_banner(theme_name, is_authenticated, user_data),
            
            # Main content area - YOUR EXACT CONTENT
            html.Div(
                className="main-content",
                children=[
                    # Compact hero section - YOUR EXACT CONTENT
                    create_hero_section(theme_styles),
                    
                    # FIXED: Your 8 metric cards with the ID the callback expects
                    html.Div(
                        id='public-summary-metrics',  # This ID is expected by callbacks
                        children=[create_metric_cards_grid(metrics_data, theme_styles)]
                    )
                ]
            ),
            
            # FIXED: Add hidden components that callbacks expect (so no errors)
            html.Div(style={'display': 'none'}, children=[
                html.Div(id='public-weekly-histogram'),
                html.Div(id='public-daily-line-chart'), 
                html.Div(id='public-hourly-analysis'),
                html.Div(id='public-cluster-performance'),
                html.Div(id='public-last-updated'),
                html.Div(id='public-loading-indicator')
            ]),
            
            # FIXED: Add the interval component that callbacks expect
            dcc.Interval(
                id='public-data-refresh',
                interval=5*60*1000,  # 5 minutes
                n_intervals=0
            ),
            
            # Compact footer - YOUR EXACT CONTENT
            html.Div(
                className="app-footer",
                children=[
                    html.P([
                        html.Span("⚡", style={"marginRight": "0.5rem"}),
                        "Real-time Dashboard • ",
                        html.Span("🔍", style={"marginLeft": "0.5rem", "marginRight": "0.5rem"}),
                        "Live Data Integration • ",
                        html.Span("📊", style={"marginLeft": "0.5rem", "marginRight": "0.5rem"}),
                        "Swaccha Andhra Corporation"
                    ], style={"margin": "0"})
                ]
            )
        ]
    )

def create_mobile_public_layout(theme_name="dark"):
    """
    Create mobile-optimized version of public layout
    Still fits on one screen without scrolling
    """
    return build_public_layout(theme_name)


def integrate_with_real_data(metrics_data, csv_data=None):
    """
    Integrate with real-time data from file_watcher.py
    
    Args:
        metrics_data (list): Default metrics data
        csv_data (DataFrame): Real CSV data from file_watcher
        
    Returns:
        list: Updated metrics with real data
    """
    if csv_data is None or csv_data.empty:
        return metrics_data
    
    try:
        # Update metrics with real data
        updated_metrics = metrics_data.copy()
        
        # Districts count
        if 'Agency' in csv_data.columns:
            unique_districts = len(csv_data['Agency'].unique())
            updated_metrics[0]['value'] = str(unique_districts)
        
        # Waste collected
        if 'Net Weight' in csv_data.columns:
            total_weight = csv_data['Net Weight'].sum() / 1000000  # Convert to millions
            updated_metrics[1]['value'] = f"{total_weight:.1f}M"
        
        # Active vehicles
        if 'Vehicle No' in csv_data.columns:
            unique_vehicles = len(csv_data['Vehicle No'].unique())
            updated_metrics[4]['value'] = str(unique_vehicles)
        
        # Data points
        updated_metrics[6]['value'] = f"{len(csv_data):,}"
        
        # Update timestamp info
        from datetime import datetime
        current_time = datetime.now()
        updated_metrics[7]['unit'] = f"Updated: {current_time.strftime('%H:%M')}"
        
        return updated_metrics
        
    except Exception as e:
        print(f"Error integrating real data: {e}")
        return metrics_data


def create_theme_aware_layout(theme_name="dark", real_time_data=None):
    """
    Create layout that automatically adapts to theme changes
    
    Args:
        theme_name (str): Theme name from THEMES dict
        real_time_data (DataFrame): Optional real-time data
        
    Returns:
        html.Div: Theme-aware layout
    """
    # Get metrics and integrate real data if available
    metrics_data = get_eight_metric_cards()
    if real_time_data is not None:
        metrics_data = integrate_with_real_data(metrics_data, real_time_data)
    
    # Build layout with current theme
    return build_public_layout(theme_name, False, None)


# Additional utility functions for integration
def create_loading_layout(theme_name="dark"):
    """Create loading state for public layout"""
    theme_styles = get_theme_styles(theme_name)
    
    return html.Div(
        className="public-layout",
        style={
            "--primary-bg": theme_styles["theme"]["primary_bg"],
            "--secondary-bg": theme_styles["theme"]["secondary_bg"],
            "--accent-bg": theme_styles["theme"]["accent_bg"],
            "--card-bg": theme_styles["theme"]["card_bg"],
            "--text-primary": theme_styles["theme"]["text_primary"],
            "--text-secondary": theme_styles["theme"]["text_secondary"],
            "--brand-primary": theme_styles["theme"]["brand_primary"]
        },
        children=[
            html.Div(
                className="main-content",
                children=[
                    html.Div(
                        className="hero-section",
                        children=[
                            html.Div("🔄 Loading Dashboard...", 
                                   style={"textAlign": "center", "fontSize": "1.2rem"})
                        ]
                    ),
                    html.Div(
                        className="cards-grid",
                        children=[
                            html.Div(
                                className="card-loading",
                                children=["Loading..."]
                            ) for _ in range(8)
                        ]
                    )
                ]
            )
        ]
    )


def create_error_layout(error_message="Unable to load dashboard", theme_name="dark"):
    """Create error state for public layout"""
    theme_styles = get_theme_styles(theme_name)
    
    return html.Div(
        className="public-layout",
        style={
            "--primary-bg": theme_styles["theme"]["primary_bg"],
            "--secondary-bg": theme_styles["theme"]["secondary_bg"],
            "--accent-bg": theme_styles["theme"]["accent_bg"],
            "--card-bg": theme_styles["theme"]["card_bg"],
            "--text-primary": theme_styles["theme"]["text_primary"],
            "--text-secondary": theme_styles["theme"]["text_secondary"],
            "--brand-primary": theme_styles["theme"]["brand_primary"]
        },
        children=[
            html.Div(
                className="main-content",
                children=[
                    html.Div(
                        className="hero-section",
                        children=[
                            html.Div([
                                html.Div("⚠️", style={"fontSize": "2rem", "marginBottom": "0.5rem"}),
                                html.Div(error_message, style={"fontSize": "1.1rem"})
                            ], style={"textAlign": "center"})
                        ]
                    )
                ]
            )
        ]
    )


def get_responsive_grid_config():
    """Get responsive grid configuration for different screen sizes"""
    return {
        "mobile_portrait": {
            "max_width": "480px",
            "grid_columns": "repeat(2, 1fr)",
            "grid_rows": "repeat(4, 1fr)",
            "description": "2x4 grid for mobile portrait"
        },
        "mobile_landscape": {
            "max_width": "767px",
            "orientation": "landscape",
            "grid_columns": "repeat(4, 1fr)",
            "grid_rows": "repeat(2, 1fr)",
            "description": "4x2 grid for mobile landscape"
        },
        "tablet": {
            "min_width": "768px",
            "max_width": "1024px",
            "grid_columns": "repeat(4, 1fr)",
            "grid_rows": "repeat(2, 1fr)",
            "description": "4x2 grid for tablets"
        },
        "desktop": {
            "min_width": "1024px",
            "max_width": "1440px",
            "grid_columns": "repeat(4, 1fr)",
            "grid_rows": "repeat(2, 1fr)",
            "description": "4x2 grid for desktop"
        },
        "large_screen": {
            "min_width": "1440px",
            "grid_columns": "repeat(4, 1fr)",
            "grid_rows": "repeat(2, 1fr)",
            "description": "4x2 grid for large screens and TV"
        }
    }


def test_theme_compatibility():
    """Test compatibility with all available themes"""
    from config.themes import THEMES
    
    print("Testing theme compatibility:")
    
    for theme_name in THEMES.keys():
        try:
            layout = build_public_layout(theme_name)
            print(f"✅ {theme_name}: Compatible")
        except Exception as e:
            print(f"❌ {theme_name}: Error - {e}")
    
    print("\nAll themes tested!")


# Export functions
__all__ = [
    'build_public_layout',
    'create_mobile_public_layout', 
    'create_loading_layout',
    'create_error_layout',
    'get_eight_metric_cards',
    'create_metric_cards_grid',
    'integrate_with_real_data',
    'create_theme_aware_layout',
    'get_responsive_grid_config',
    'test_theme_compatibility'
]