# main.py
"""
Enhanced Main Application with Complete Authentication System
Supports Google OAuth, session management, and protected routes
"""

import dash
from dash import html, dcc, callback, Input, Output, State, ctx, clientside_callback, ClientsideFunction
from dash.exceptions import PreventUpdate
import flask
from flask import request, redirect, session
import urllib.parse
import secrets

from config.themes import THEMES, DEFAULT_THEME
from config.auth import load_google_oauth_config
from utils.theme_utils import get_hover_overlay_css
from layouts.public_layout import build_public_layout
from layouts.login_layout import build_login_layout
from layouts.admin_dashboard import build_admin_dashboard
from services.auth_service import auth_service, session_manager, get_login_redirect_url

# Initialize Dash app with Flask server
server = flask.Flask(__name__)
server.secret_key = 'your-secret-key-change-this-in-production'  # Change this!

app = dash.Dash(
    __name__, 
    server=server,
    suppress_callback_exceptions=True, 
    title="स्वच्छ आंध्र प्रदेश - Swaccha Andhra Dashboard",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap"
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0, user-scalable=no, maximum-scale=1.0"},
        {"name": "theme-color", "content": "#0D1B2A"},
        {"name": "apple-mobile-web-app-capable", "content": "yes"},
        {"name": "apple-mobile-web-app-status-bar-style", "content": "black-translucent"},
        {"name": "apple-mobile-web-app-title", "content": "Swaccha Andhra"},
        {"name": "description", "content": "स्वच्छ आंध्र प्रदेश - Real-time cleanliness monitoring dashboard for Andhra Pradesh"}
    ]
)

# Enhanced PWA configuration with authentication
app.index_string = f'''
<!DOCTYPE html>
<html lang="en">
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <link rel="manifest" href="/assets/manifest.json">
        <style>
            {get_hover_overlay_css()}
            
            /* Enhanced loading screen */
            .pwa-loading {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(135deg, #0D1B2A 0%, #1A1F2E 100%);
                display: flex; justify-content: center; align-items: center; 
                z-index: 9999; opacity: 1; transition: opacity 0.8s ease;
            }}
            .pwa-loading.hidden {{ opacity: 0; pointer-events: none; }}
            
            .loading-content {{
                text-align: center; color: white; animation: fadeInUp 0.8s ease;
            }}
            
            .loading-icon {{
                font-size: 4rem; margin-bottom: 1.5rem; 
                animation: bounce 2s infinite;
            }}
            
            .loading-title {{
                font-size: 2rem; font-weight: 900; margin-bottom: 0.5rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            }}
            
            .loading-subtitle {{
                font-size: 1.2rem; margin-bottom: 2rem; color: #A0AEC0;
            }}
            
            .loading-progress {{
                width: 200px; height: 4px; background: #2D3748;
                border-radius: 2px; margin: 0 auto; overflow: hidden;
            }}
            
            .progress-bar {{
                height: 100%; background: linear-gradient(90deg, #3182CE, #38A169);
                border-radius: 2px; animation: loadProgress 2s ease-in-out;
            }}
            
            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            @keyframes bounce {{
                0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
                40% {{ transform: translateY(-10px); }}
                60% {{ transform: translateY(-5px); }}
            }}
            
            @keyframes loadProgress {{
                from {{ width: 0%; }}
                to {{ width: 100%; }}
            }}
            
            /* Google OAuth button hover effects */
            #google-login-btn:hover {{
                background-color: #f8f9fa !important;
                border-color: #4285f4 !important;
                box-shadow: 0 4px 16px rgba(66, 133, 244, 0.3) !important;
                transform: translateY(-2px) !important;
            }}
            
            /* Login form styling */
            .login-form-container {{
                animation: slideInUp 0.6s ease-out;
            }}
            
            @keyframes slideInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(40px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
        </style>
    </head>
    <body>
        <!-- Enhanced Loading Screen -->
        <div id="pwa-loading" class="pwa-loading">
            <div class="loading-content">
                <div class="loading-icon">🌱</div>
                <div class="loading-title">स्वच्छ आंध्र प्रदेश</div>
                <div class="loading-subtitle">Loading Dashboard...</div>
                <div class="loading-progress">
                    <div class="progress-bar"></div>
                </div>
            </div>
        </div>
        
        {{%app_entry%}}
        {{%config%}}
        {{%scripts%}}
        {{%renderer%}}
        
        <script>
            // Enhanced loading sequence
            window.addEventListener('load', function() {{
                setTimeout(() => {{
                    document.getElementById('pwa-loading').classList.add('hidden');
                }}, 1500);
            }});
            
            // Service Worker Registration
            if ('serviceWorker' in navigator) {{
                window.addEventListener('load', () => {{
                    navigator.serviceWorker.register('/assets/sw.js')
                        .then((registration) => {{
                            console.log('SW registered: ', registration);
                        }})
                        .catch((registrationError) => {{
                            console.log('SW registration failed: ', registrationError);
                        }});
                }});
            }}
        </script>
    </body>
</html>
'''

# Flask routes for OAuth handling
@server.route('/oauth/login')
def oauth_login():
    """Initiate Google OAuth login"""
    try:
        auth_url, state = auth_service.generate_oauth_url()
        flask.session['oauth_state'] = state
        return redirect(auth_url)
    except Exception as e:
        print(f"OAuth login error: {e}")
        return redirect('/login?error=oauth_config')

@server.route('/oauth/callback')
def oauth_callback():
    """Handle OAuth callback"""
    try:
        # Get authorization code and state
        code = request.args.get('code')
        state = request.args.get('state')
        stored_state = flask.session.get('oauth_state')
        
        # Verify state parameter (CSRF protection)
        if not state or state != stored_state:
            return redirect('/login?error=invalid_state')
        
        # Exchange code for token
        token_response = auth_service.exchange_code_for_token(code, state)
        if 'error' in token_response:
            return redirect(f'/login?error={token_response["error"]}')
        
        # Get user info
        access_token = token_response.get('access_token')
        user_info = auth_service.get_user_info(access_token)
        if 'error' in user_info:
            return redirect(f'/login?error={user_info["error"]}')
        
        # Authenticate user
        success, message, session_data = auth_service.authenticate_user(user_info)
        
        if success:
            # Store session in Flask session
            flask.session['swaccha_session_id'] = session_data['session_id']
            flask.session['user_data'] = session_data
            return redirect('/dashboard')
        else:
            return redirect(f'/login?error=unauthorized&message={urllib.parse.quote(message)}')
            
    except Exception as e:
        print(f"OAuth callback error: {e}")
        return redirect('/login?error=callback_failed')

@server.route('/auth/logout')
def logout():
    """Handle user logout - FIXED"""
    print("Logout route called")  # Debug
    
    # Clear session
    session_id = flask.session.get('swaccha_session_id')
    if session_id:
        auth_service.logout_user(session_id)
    
    # Clear Flask session completely
    flask.session.clear()
    
    # Redirect to home page (not just /)
    return redirect('/')

@server.route('/debug/oauth')
def debug_oauth():
    """Debug route to check OAuth configuration"""
    config_info = auth_service.debug_oauth_config()
    
    html_response = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth Debug Information</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .status {{ padding: 10px; margin: 10px 0; border-radius: 4px; }}
            .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
            .error {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }}
            .info {{ background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }}
            pre {{ background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }}
            .fix-section {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 15px 0; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 OAuth Configuration Debug</h1>
            
            <div class="status {'success' if config_info['config_loaded'] else 'error'}">
                <strong>Configuration Status:</strong> {'✅ Loaded' if config_info['config_loaded'] else '❌ Not Loaded'}
            </div>
            
            <h3>📋 Configuration Details:</h3>
            <pre>{config_info}</pre>
            
            <div class="fix-section">
                <h3>🛠️ How to Fix redirect_uri_mismatch:</h3>
                <ol>
                    <li><strong>Go to Google Cloud Console:</strong><br>
                        <a href="https://console.cloud.google.com/apis/credentials" target="_blank">
                        https://console.cloud.google.com/apis/credentials</a>
                    </li>
                    <li><strong>Find your OAuth 2.0 Client ID</strong></li>
                    <li><strong>Click Edit (pencil icon)</strong></li>
                    <li><strong>In "Authorized redirect URIs", add:</strong><br>
                        <code>http://localhost:8050/oauth/callback</code>
                    </li>
                    <li><strong>Click Save</strong></li>
                    <li><strong>Download the updated credentials</strong></li>
                    <li><strong>Replace your client_secrets.json file</strong></li>
                </ol>
            </div>
            
            <div class="info">
                <strong>Current Redirect URIs in your config:</strong><br>
                {config_info.get('redirect_uris', 'None found')}
            </div>
            
            <div class="fix-section">
                <h3>✅ Quick Test:</h3>
                <p>After fixing the redirect URI, test the OAuth flow:</p>
                <a href="/oauth/login" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                    🔄 Test OAuth Login
                </a>
            </div>
            
            <p><a href="/">← Back to Dashboard</a></p>
        </div>
    </body>
    </html>
    """
    
    return html_response

# App layout with enhanced routing
app.layout = html.Div(
    id="app-container",
    children=[
        dcc.Store(id='current-theme', data=DEFAULT_THEME),
        dcc.Store(id='user-authenticated', data=False),
        dcc.Store(id='current-page', data='public_landing'),
        dcc.Store(id='user-session-data', data={}),
        dcc.Store(id='auth-error-message', data=''),
        dcc.Location(id='url', refresh=False),
        dcc.Location(id='redirect', refresh=True),  # Add redirect location for OAuth
        dcc.Interval(id='session-check-interval', interval=30*1000, n_intervals=0),
        html.Div(id="main-layout")
    ]
)

# Page routing callback with authentication check
@callback(
    [Output('current-page', 'data'),
     Output('user-authenticated', 'data'),
     Output('user-session-data', 'data'),
     Output('auth-error-message', 'data')],
    [Input('url', 'pathname'),
     Input('url', 'search')],
    prevent_initial_call=False
)
def update_current_page_and_auth(pathname, search):
    """Determine current page and check authentication status"""
    print(f"DEBUG: Routing - pathname: {pathname}, search: {search}")  # Debug
    
    # Parse URL parameters
    params = {}
    if search:
        params = dict(urllib.parse.parse_qsl(search.lstrip('?')))
    
    # Get session from Flask session
    session_id = flask.session.get('swaccha_session_id')
    user_data = flask.session.get('user_data', {})
    
    # Validate session
    is_authenticated = False
    if session_id:
        is_valid, session_data = auth_service.validate_session(session_id)
        if is_valid:
            is_authenticated = True
            user_data = session_data
            # Update Flask session with latest data
            flask.session['user_data'] = session_data
        else:
            # Session expired, clear Flask session
            flask.session.clear()
            user_data = {}
    
    print(f"DEBUG: is_authenticated: {is_authenticated}")  # Debug
    
    # Handle different routes
    if pathname is None or pathname == '/' or pathname == '':
        return 'public_landing', is_authenticated, user_data, ''
    
    elif pathname == '/login':
        error_message = params.get('error', '')
        if error_message:
            error_messages = {
                'oauth_config': 'OAuth configuration error. Please contact administrator.',
                'invalid_state': 'Security error. Please try again.',
                'unauthorized': params.get('message', 'You are not authorized to access this system.'),
                'callback_failed': 'Authentication failed. Please try again.'
            }
            return 'login', False, {}, error_messages.get(error_message, error_message)
        return 'login', False, {}, ''
    
    elif pathname == '/dashboard':
        if is_authenticated:
            return 'admin_dashboard', True, user_data, ''
        else:
            # Redirect to login if not authenticated - but don't change URL
            return 'login', False, {}, 'Please log in to access the dashboard.'
    
    elif pathname == '/analytics':
        if is_authenticated:
            return 'analytics_page', True, user_data, ''
        else:
            return 'login', False, {}, 'Please log in to access analytics.'
    
    elif pathname == '/reports':
        if is_authenticated:
            return 'reports_page', True, user_data, ''
        else:
            return 'login', False, {}, 'Please log in to access reports.'
    
    else:
        return 'public_landing', is_authenticated, user_data, ''

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

# Main layout callback
@callback(
    Output('main-layout', 'children'),
    [
        Input('current-theme', 'data'),
        Input('user-authenticated', 'data'),
        Input('current-page', 'data'),
        Input('user-session-data', 'data'),
        Input('auth-error-message', 'data')
    ]
)
def update_main_layout(theme_name, is_authenticated, current_page, user_data, error_message):
    """Update main layout based on current page and authentication status"""
    print(f"DEBUG: Layout - current_page: {current_page}, is_authenticated: {is_authenticated}")  # Debug
    
    if current_page == 'login':
        return build_login_layout(theme_name, error_message)
    
    elif current_page == 'admin_dashboard' and is_authenticated:
        return build_admin_dashboard(theme_name, user_data)
    
    elif current_page in ['analytics_page', 'reports_page'] and is_authenticated:
        # Placeholder layouts for these pages
        return build_placeholder_layout(current_page, theme_name, user_data)
    
    else:
        # Default to public landing
        return build_public_layout(theme_name)

# FIXED - Main navigation callback with proper debug and button handling
@callback(
    Output('url', 'pathname'),
    [
        Input('admin-login-btn', 'n_clicks'),
        Input('overlay-nav-overview', 'n_clicks'),
        Input('overlay-nav-analytics', 'n_clicks'),
        Input('overlay-nav-reports', 'n_clicks')
    ],
    prevent_initial_call=True
)
def handle_main_navigation(admin_login, nav_overview, nav_analytics, nav_reports):
    """Handle main navigation actions available on all pages"""
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    trigger_value = ctx.triggered[0]['value']
    
    print(f"DEBUG: Navigation - button: {button_id}, value: {trigger_value}")  # Debug
    
    # Only process if the button was actually clicked (value > 0)
    if trigger_value is None or trigger_value == 0:
        raise PreventUpdate
    
    if button_id == 'admin-login-btn':
        print("DEBUG: Navigating to /login")  # Debug
        return '/login'
    elif button_id == 'overlay-nav-overview':
        print("DEBUG: Navigating to /")  # Debug
        return '/'
    elif button_id == 'overlay-nav-analytics':
        print("DEBUG: Navigating to /analytics")  # Debug
        return '/analytics'
    elif button_id == 'overlay-nav-reports':
        print("DEBUG: Navigating to /reports")  # Debug
        return '/reports'
    
    raise PreventUpdate

# FIXED Login page callback - Using clientside callback for OAuth redirect
clientside_callback(
    """
    function(google_clicks, google_alt_clicks, back_clicks, manual_clicks, manual_email, current_page) {
        const triggered = window.dash_clientside.callback_context.triggered;
        if (!triggered || triggered.length === 0) {
            return window.dash_clientside.no_update;
        }
        
        // Only process if we're actually on the login page
        if (current_page !== 'login') {
            return window.dash_clientside.no_update;
        }
        
        const button_id = triggered[0].prop_id.split('.')[0];
        const button_value = triggered[0].value;
        
        // Only process if button was actually clicked
        if (!button_value || button_value === 0) {
            return window.dash_clientside.no_update;
        }
        
        console.log('Login callback triggered:', button_id);
        
        if (button_id === 'google-login-btn' || button_id === 'google-login-btn-alt') {
            // Redirect to OAuth endpoint using browser navigation
            console.log('Redirecting to OAuth...');
            window.location.href = '/oauth/login';
            return window.dash_clientside.no_update;
        } else if (button_id === 'back-to-public-btn') {
            return '/';
        } else if (button_id === 'manual-login-btn') {
            if (manual_email) {
                return '/login?error=manual_login_not_implemented';
            } else {
                return '/login?error=email_required';
            }
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('redirect', 'pathname'),
    [
        Input('google-login-btn', 'n_clicks'),
        Input('google-login-btn-alt', 'n_clicks'),
        Input('back-to-public-btn', 'n_clicks'),
        Input('manual-login-btn', 'n_clicks')
    ],
    [State('manual-email', 'value'),
     State('current-page', 'data')],  # Add current page as state
    prevent_initial_call=True
)

# FIXED - Admin dashboard callback with proper logout handling
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [
        Input('logout-btn', 'n_clicks'),
        Input('quick-reports-btn', 'n_clicks'),
        Input('quick-settings-btn', 'n_clicks')
    ],
    [State('current-page', 'data')],
    prevent_initial_call=True
)
def handle_admin_actions(logout, quick_reports, quick_settings, current_page):
    """Handle admin dashboard specific actions"""
    # Only process if we're on an admin page
    if current_page not in ['admin_dashboard', 'analytics_page', 'reports_page']:
        raise PreventUpdate
    
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    print(f"DEBUG: Admin action - button: {button_id}")  # Debug
    
    if button_id == 'logout-btn':
        print("DEBUG: Logout button clicked")  # Debug
        # Use clientside redirect to Flask route
        return '/auth/logout'
    elif button_id == 'quick-reports-btn':
        return '/reports'
    elif button_id == 'quick-settings-btn':
        return '/settings'  # Future implementation
    
    raise PreventUpdate

# Session validation callback
@callback(
    [Output('user-authenticated', 'data', allow_duplicate=True),
     Output('user-session-data', 'data', allow_duplicate=True)],
    [Input('session-check-interval', 'n_intervals')],
    prevent_initial_call=True
)
def validate_session_periodically(n_intervals):
    """Periodically validate user session"""
    session_id = flask.session.get('swaccha_session_id')
    if session_id:
        is_valid, session_data = auth_service.validate_session(session_id)
        if not is_valid:
            flask.session.clear()
            return False, {}
        else:
            # Update Flask session with latest data
            flask.session['user_data'] = session_data
            return True, session_data
    return False, {}

# Placeholder layout function
def build_placeholder_layout(page_type, theme_name, user_data):
    """Build placeholder layouts for analytics and reports pages"""
    from utils.theme_utils import get_theme_styles
    from components.navigation.hover_overlay import create_hover_overlay_banner
    
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    page_titles = {
        'analytics_page': '📈 Advanced Analytics',
        'reports_page': '📋 Reports & Documentation'
    }
    
    return html.Div(
        style=theme_styles["container_style"],
        children=[
            create_hover_overlay_banner(theme_name),
            html.Div(
                style=theme_styles["main_content_style"],
                children=[
                    html.H1(
                        page_titles.get(page_type, '📊 Dashboard'),
                        style={"color": theme["text_primary"], "textAlign": "center"}
                    ),
                    html.P(
                        f"Welcome {user_data.get('name', 'User')}! This section is under development.",
                        style={"color": theme["text_secondary"], "textAlign": "center", "fontSize": "1.2rem"}
                    ),
                    html.Div(
                        style={
                            "textAlign": "center",
                            "marginTop": "2rem"
                        },
                        children=[
                            html.Button(
                                "← Back to Dashboard",
                                id="back-to-dashboard-btn",
                                style={
                                    "backgroundColor": theme["brand_primary"],
                                    "color": "white",
                                    "border": "none",
                                    "padding": "1rem 2rem",
                                    "borderRadius": "8px",
                                    "fontSize": "1rem",
                                    "cursor": "pointer"
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )

# Handle back to dashboard navigation
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('back-to-dashboard-btn', 'n_clicks')],
    prevent_initial_call=True
)
def back_to_dashboard(n_clicks):
    """Navigate back to main dashboard"""
    if n_clicks:
        return '/dashboard'
    raise PreventUpdate

if __name__ == "__main__":
    # Clean up expired sessions on startup
    auth_service.cleanup_expired_sessions()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=8050)

# Export for production deployment
__all__ = ['app', 'server']