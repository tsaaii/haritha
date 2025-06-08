# main_modular.py
"""
Main Application - Modular Swaccha Andhra Dashboard
Clean, organized, and maintainable structure
"""

import dash
from dash import html, dcc, callback, Input, Output
from config.themes import THEMES, DEFAULT_THEME
from utils.theme_utils import get_hover_overlay_css
from layouts.public_layout import build_public_layout

# Initialize Dash app
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True, 
    title="Swaccha Andhra Dashboard",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0, user-scalable=no"},
        {"name": "theme-color", "content": "#0D1B2A"},
        {"name": "apple-mobile-web-app-capable", "content": "yes"},
        {"name": "apple-mobile-web-app-status-bar-style", "content": "black-translucent"},
        {"name": "apple-mobile-web-app-title", "content": "Swaccha Andhra"},
        {"name": "description", "content": "Swaccha Andhra Dashboard - Clean India Mission Analytics"}
    ]
)

server = app.server

# PWA Configuration with modular CSS
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
            {get_hover_overlay_css()}
            
            .pwa-loading {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: #0D1B2A; display: flex;
                justify-content: center; align-items: center; z-index: 9999;
                opacity: 1; transition: opacity 0.5s ease;
            }}
            .pwa-loading.hidden {{ opacity: 0; pointer-events: none; }}
        </style>
    </head>
    <body>
        <div id="pwa-loading" class="pwa-loading">
            <div style="text-align: center; color: white;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                <div style="font-size: 1.5rem; font-weight: bold;">Swaccha Andhra</div>
                <div style="font-size: 1rem; margin-top: 0.5rem;">Loading Dashboard...</div>
            </div>
        </div>
        {{%app_entry%}}
        {{%config%}}
        {{%scripts%}}
        {{%renderer%}}
        <script>
            window.addEventListener('load', function() {{
                setTimeout(() => document.getElementById('pwa-loading').classList.add('hidden'), 1000);
            }});
        </script>
    </body>
</html>
'''

# App layout - Simple and clean
app.layout = html.Div(
    id="app-container",
    children=[
        dcc.Store(id='current-theme', data=DEFAULT_THEME),
        dcc.Store(id='user-authenticated', data=False),
        html.Div(id="main-layout")
    ]
)

# Theme switching callback
@callback(
    Output('current-theme', 'data'),
    [
        Input('theme-dark', 'n_clicks'),
        Input('theme-light', 'n_clicks'),
        Input('theme-high_contrast', 'n_clicks'),
        Input('theme-swaccha_green', 'n_clicks')
    ],
    prevent_initial_call=True
)
def update_theme(dark_clicks, light_clicks, contrast_clicks, green_clicks):
    """Handle theme switching from overlay banner"""
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return DEFAULT_THEME
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    theme_map = {
        'theme-dark': 'dark',
        'theme-light': 'light', 
        'theme-high_contrast': 'high_contrast',
        'theme-swaccha_green': 'swaccha_green'
    }
    
    return theme_map.get(button_id, DEFAULT_THEME)

# Layout switching callback
@callback(
    Output('main-layout', 'children'),
    [
        Input('current-theme', 'data'),
        Input('user-authenticated', 'data')
    ]
)
def update_main_layout(theme_name, is_authenticated):
    """
    Update main layout based on theme and authentication status
    
    Args:
        theme_name (str): Current theme
        is_authenticated (bool): User authentication status
        
    Returns:
        html.Div: Appropriate layout
    """
    # For now, always show public layout
    # Later we can add admin layout when user is authenticated
    return build_public_layout(theme_name)

# Navigation callbacks (placeholder for future implementation)
# @callback(
#     Output('user-authenticated', 'data'),
#     [
#         Input('admin-login-btn', 'n_clicks'),
#         Input('nav-overview', 'n_clicks'),
#         Input('nav-analytics', 'n_clicks'),
#         Input('nav-reports', 'n_clicks')
#     ],
#     prevent_initial_call=True
# )
def handle_navigation(login_clicks, overview_clicks, analytics_clicks, reports_clicks):
    """
    Handle navigation and authentication
    This is a placeholder for future implementation
    """
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return False
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'admin-login-btn':
        # TODO: Implement actual authentication
        print("Admin login clicked - implement authentication")
        return False  # For now, keep as public
    
    elif button_id in ['nav-overview', 'nav-analytics', 'nav-reports']:
        # TODO: Implement page navigation
        print(f"Navigation clicked: {button_id}")
        return False
    
    return False

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8050)

# Export for testing
__all__ = ['app', 'server']