# callbacks/dashboard_callbacks.py
"""
Dashboard Route Callbacks for Aligned Navigation
Handles theme switching, tab navigation, and logout
"""

from dash import callback, Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate
from config.themes import THEMES, DEFAULT_THEME
import dash

def register_dashboard_callbacks(app):
    """Register all dashboard-specific callbacks"""
    
    # Theme switching callback
    @app.callback(
        [Output('current-theme', 'data'),
         Output('dashboard-route', 'data-theme')],  # Update data-theme attribute
        [Input('theme-dark', 'n_clicks'),
         Input('theme-light', 'n_clicks'),
         Input('theme-high_contrast', 'n_clicks'),
         Input('theme-swaccha_green', 'n_clicks')],
        [State('current-theme', 'data')],
        prevent_initial_call=True
    )
    def update_dashboard_theme(dark_clicks, light_clicks, contrast_clicks, green_clicks, current_theme):
        """Update theme for dashboard route"""
        if not ctx.triggered:
            raise PreventUpdate
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        theme_map = {
            'theme-dark': 'dark',
            'theme-light': 'light',
            'theme-high_contrast': 'high_contrast',
            'theme-swaccha_green': 'swaccha_green'
        }
        
        new_theme = theme_map.get(button_id, current_theme or DEFAULT_THEME)
        return new_theme, new_theme

    # Tab navigation callback
    @app.callback(
        [Output('active-tab', 'data'),
         Output('tab-content', 'children')],
        [Input('tab-dashboard', 'n_clicks'),
         Input('tab-analytics', 'n_clicks'),
         Input('tab-charts', 'n_clicks'),
         Input('tab-reports', 'n_clicks'),
         Input('tab-reviews', 'n_clicks'),
         Input('tab-forecasting', 'n_clicks'),
         Input('tab-upload', 'n_clicks')],
        [State('current-theme', 'data'),
         State('active-tab', 'data')],
        prevent_initial_call=True
    )
    def handle_tab_navigation(dash_clicks, analytics_clicks, charts_clicks, reports_clicks, 
                            reviews_clicks, forecast_clicks, upload_clicks, theme_name, current_tab):
        """Handle tab navigation and content updates"""
        if not ctx.triggered:
            raise PreventUpdate
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        tab_map = {
            'tab-dashboard': 'dashboard',
            'tab-analytics': 'analytics',
            'tab-charts': 'charts',
            'tab-reports': 'reports',
            'tab-reviews': 'reviews',
            'tab-forecasting': 'forecasting',
            'tab-upload': 'upload'
        }
        
        new_tab = tab_map.get(button_id, current_tab or 'dashboard')
        content = get_tab_content(new_tab, theme_name or DEFAULT_THEME)
        
        return new_tab, content

    # Logout callback
    @app.callback(
        [Output('user-authenticated', 'data'),
         Output('url', 'pathname')],
        Input('logout-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def handle_logout(n_clicks):
        """Handle user logout"""
        if n_clicks:
            return False, '/'  # Redirect to home page
        raise PreventUpdate

    # Update navigation button states based on active tab
    @app.callback(
        [Output('tab-dashboard', 'className'),
         Output('tab-analytics', 'className'),
         Output('tab-charts', 'className'),
         Output('tab-reports', 'className'),
         Output('tab-reviews', 'className'),
         Output('tab-forecasting', 'className'),
         Output('tab-upload', 'className')],
        Input('active-tab', 'data'),
        prevent_initial_call=True
    )
    def update_nav_button_states(active_tab):
        """Update navigation button active states"""
        tabs = ['dashboard', 'analytics', 'charts', 'reports', 'reviews', 'forecasting', 'upload']
        return [f"nav-tab {'active' if tab == active_tab else ''}" for tab in tabs]

    # Update theme button states
    @app.callback(
        [Output('theme-dark', 'className'),
         Output('theme-light', 'className'),
         Output('theme-high_contrast', 'className'),
         Output('theme-swaccha_green', 'className')],
        Input('current-theme', 'data'),
        prevent_initial_call=True
    )
    def update_theme_button_states(current_theme):
        """Update theme button active states"""
        themes = ['dark', 'light', 'high_contrast', 'swaccha_green']
        return [f"theme-btn {'active' if theme == current_theme else ''}" for theme in themes]

def get_tab_content(tab_name, theme_name):
    """
    Generate content for different tabs
    
    Args:
        tab_name (str): Name of the tab
        theme_name (str): Current theme
        
    Returns:
        html.Div: Tab content
    """
    theme = THEMES[theme_name]
    
    content_map = {
        'dashboard': {
            'title': '📊 Dashboard Overview',
            'description': 'Real-time monitoring of waste collection and management across Andhra Pradesh.',
            'features': ['Live vehicle tracking', 'Collection efficiency metrics', 'Route optimization data']
        },
        'analytics': {
            'title': '📈 Data Analytics',
            'description': 'Advanced analytics and insights from waste management data.',
            'features': ['Trend analysis', 'Predictive modeling', 'Performance metrics']
        },
        'charts': {
            'title': '📉 Charts & Visualizations',
            'description': 'Interactive charts and graphs for data visualization.',
            'features': ['Custom dashboards', 'Export capabilities', 'Real-time updates']
        },
        'reports': {
            'title': '📋 Reports',
            'description': 'Comprehensive reports and documentation.',
            'features': ['Automated reports', 'Custom filters', 'PDF exports']
        },
        'reviews': {
            'title': '⭐ Reviews & Feedback',
            'description': 'Public feedback and service reviews management.',
            'features': ['Customer ratings', 'Complaint tracking', 'Response management']
        },
        'forecasting': {
            'title': '🔮 Forecasting',
            'description': 'Predictive analytics for waste management planning.',
            'features': ['Demand forecasting', 'Resource planning', 'Capacity optimization']
        },
        'upload': {
            'title': '📤 Data Upload',
            'description': 'Upload and manage data files and documents.',
            'features': ['Bulk data import', 'File validation', 'Processing status']
        }
    }
    
    content = content_map.get(tab_name, content_map['dashboard'])
    
    return html.Div(
        style={
            "padding": "2rem",
            "backgroundColor": theme["accent_bg"],
            "border": f"2px solid {theme['card_bg']}",
            "borderRadius": "12px",
            "minHeight": "400px"
        },
        children=[
            html.H2(
                content['title'],
                style={"color": theme["text_primary"], "marginBottom": "1rem"}
            ),
            html.P(
                content['description'],
                style={"color": theme["text_secondary"], "marginBottom": "2rem", "fontSize": "1.1rem"}
            ),
            html.H3(
                "Features:",
                style={"color": theme["text_primary"], "marginBottom": "1rem"}
            ),
            html.Ul(
                children=[
                    html.Li(
                        feature,
                        style={"color": theme["text_secondary"], "marginBottom": "0.5rem"}
                    ) for feature in content['features']
                ],
                style={"paddingLeft": "1.5rem"}
            ),
            
            # Placeholder for future content
            html.Div(
                style={
                    "marginTop": "2rem",
                    "padding": "1.5rem",
                    "backgroundColor": theme["card_bg"],
                    "borderRadius": "8px",
                    "border": f"1px solid {theme['border_light']}"
                },
                children=[
                    html.P(
                        f"🚧 {content['title']} functionality is coming soon!",
                        style={
                            "color": theme["warning"],
                            "fontWeight": "600",
                            "textAlign": "center",
                            "margin": "0"
                        }
                    )
                ]
            )
        ]
    )