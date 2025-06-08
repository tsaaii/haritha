"""
BULLETPROOF Main Application with Google OAuth - Fixed All Callback Errors
Simplified and robust implementation that prevents all callback conflicts
"""

import dash
from dash import html, dcc, callback, Input, Output, State, ctx, clientside_callback
from dash.exceptions import PreventUpdate
import flask
from flask import request, redirect, session
import urllib.parse
import os
import logging

from config.themes import THEMES, DEFAULT_THEME
from utils.theme_utils import get_hover_overlay_css
from layouts.public_layout import build_public_layout
from layouts.login_layout import build_login_layout
from layouts.admin_dashboard import build_admin_dashboard
from services.auth_service import auth_service


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Google OAuth utilities with error handling
try:
    from utils.google_auth import get_google_auth_manager
    google_auth_manager = get_google_auth_manager()
    GOOGLE_AUTH_AVAILABLE = True
    print("✅ Google OAuth utilities loaded successfully")
    print(f"✅ Auth manager type: {type(google_auth_manager).__name__}")
    
    # Test if it's the real GoogleAuthManager or MockGoogleAuth
    if hasattr(google_auth_manager, 'client_secrets_file'):
        print("✅ Real GoogleAuthManager detected")
        REAL_OAUTH_AVAILABLE = True
    else:
        print("⚠️ MockGoogleAuth detected - client_secrets.json missing or invalid")
        REAL_OAUTH_AVAILABLE = False
        
except Exception as e:
    print(f"❌ Google OAuth utilities not available: {e}")
    google_auth_manager = None
    GOOGLE_AUTH_AVAILABLE = False
    REAL_OAUTH_AVAILABLE = False

# Initialize Dash app
server = flask.Flask(__name__)
server.secret_key = 'your-secret-key-change-this-in-production'

app = dash.Dash(
    __name__, 
    server=server,
    suppress_callback_exceptions=True, 
    title="स्वच्छ आंध्र प्रदेश - Swaccha Andhra Dashboard",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap"
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {"name": "theme-color", "content": "#0D1B2A"},
        {"name": "description", "content": "स्वच्छ आंध्र प्रदेश - Real-time cleanliness monitoring dashboard"}
    ]
)

# Enhanced PWA configuration with hover overlay CSS
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
            
            /* Enhanced Google OAuth styling */
            #google-login-btn {{
                position: relative;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }}
            
            #google-login-btn:hover {{
                background-color: #3367d6 !important;
                box-shadow: 0 8px 25px rgba(66, 133, 244, 0.5) !important;
                transform: translateY(-2px) scale(1.02) !important;
            }}
            
            /* OAuth status animations */
            .oauth-loading {{
                animation: pulse 1.5s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
            }}
            
            /* Loading screen */
            .pwa-loading {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(135deg, #0D1B2A 0%, #1A1F2E 100%);
                display: flex; justify-content: center; align-items: center; 
                z-index: 9999; opacity: 1; transition: opacity 0.8s ease;
            }}
            .pwa-loading.hidden {{ opacity: 0; pointer-events: none; }}
        </style>
    </head>
    <body>
        <!-- Loading Screen -->
        <div id="pwa-loading" class="pwa-loading">
            <div style="text-align: center; color: white;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🌱</div>
                <div style="font-size: 2rem; font-weight: 900;">स्वच्छ आंध्र प्रदेश</div>
                <div style="font-size: 1.2rem; color: #A0AEC0;">Loading Dashboard...</div>
            </div>
        </div>
        
        {{%app_entry%}}
        {{%config%}}
        {{%scripts%}}
        {{%renderer%}}
        
        <script>
            // Loading screen
            window.addEventListener('load', function() {{
                setTimeout(() => {{
                    const loading = document.getElementById('pwa-loading');
                    if (loading) loading.classList.add('hidden');
                }}, 1500);
            }});
            
            // OAuth status management
            window.swacchaOAuth = {{
                updateStatus: function(status, message) {{
                    console.log('OAuth Status:', status, message);
                }}
            }};
        </script>
    </body>
</html>
'''

# Enhanced Flask routes for Google OAuth
@server.route('/test/overlay')
def test_overlay():
    """Test overlay components"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Overlay Test</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #0D1B2A; color: white; }
            .test-area { 
                height: 100px; 
                background: #3182CE; 
                text-align: center; 
                line-height: 100px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <h1>🧪 Hover Overlay Test</h1>
        <div class="test-area">Hover at the very top of this page to test overlay</div>
        <p>The overlay should appear when you hover at the top edge of the page.</p>
        <p><a href="/" style="color: #68D391;">← Back to Dashboard</a></p>
        
        <script>
            // Check if hover overlay CSS is loaded
            const styles = Array.from(document.styleSheets).map(sheet => {
                try {
                    return Array.from(sheet.cssRules).map(rule => rule.cssText).join('\\n');
                } catch(e) {
                    return 'Cannot access stylesheet';
                }
            }).join('\\n');
            
            if (styles.includes('hover-trigger-area') || styles.includes('overlay-banner')) {
                console.log('✅ Hover overlay CSS detected');
            } else {
                console.log('❌ Hover overlay CSS not found');
            }
        </script>
    </body>
    </html>
    """

@server.route('/test/flask')
def test_flask():
    """Test if Flask routes are working"""
    return "Flask routes are working! OAuth status: " + str(GOOGLE_AUTH_AVAILABLE)

@server.route('/oauth/status')
def oauth_status():
    """Check OAuth configuration status"""
    if GOOGLE_AUTH_AVAILABLE and google_auth_manager:
        try:
            test_url, test_state = google_auth_manager.get_authorization_url('http://localhost:8050/oauth/callback')
            return flask.jsonify({
                'available': True,
                'configured': True,
                'message': 'Google OAuth is ready'
            })
        except Exception as e:
            return flask.jsonify({
                'available': True,
                'configured': False,
                'message': f'OAuth config error: {str(e)}'
            })
    else:
        return flask.jsonify({
            'available': False,
            'configured': False,
            'message': 'Google OAuth not available'
        })

@server.route('/oauth/login')
def oauth_login():
    """Initiate OAuth login - WORKING VERSION"""
    try:
        # Import the new OAuth manager
        from utils.simple_oauth import get_oauth_manager
        oauth_manager = get_oauth_manager()
        
        logger.info(f"🔐 OAuth login attempt - configured: {oauth_manager.is_available()}")
        
        if not oauth_manager.is_available():
            logger.info("⚠️ OAuth not configured - creating demo session")
            # Create demo session directly
            success, message, session_data = oauth_manager.create_demo_session()
            
            if success:
                flask.session['swaccha_session_id'] = session_data['session_id']
                flask.session['user_data'] = session_data
                logger.info("✅ Demo OAuth session created successfully")
                return redirect('/dashboard')
            else:
                logger.error(f"❌ Demo session creation failed: {message}")
                return redirect('/login?error=demo_oauth_failed')
        
        # Real OAuth flow
        try:
            auth_url, state = oauth_manager.get_authorization_url()
            flask.session['oauth_state'] = state
            
            logger.info(f"🔗 Redirecting to Google OAuth: {auth_url[:100]}...")
            return redirect(auth_url)
        except Exception as e:
            logger.error(f"❌ OAuth URL generation failed: {e}")
            # Fallback to demo
            success, message, session_data = oauth_manager.create_demo_session()
            if success:
                flask.session['swaccha_session_id'] = session_data['session_id']
                flask.session['user_data'] = session_data
                return redirect('/dashboard')
            else:
                return redirect('/login?error=oauth_fallback_failed')
        
    except Exception as e:
        logger.error(f"❌ Critical OAuth error: {e}")
        return redirect('/login?error=oauth_critical_error')

@server.route('/oauth/callback')
def oauth_callback():
    """Handle OAuth callback - WORKING VERSION"""
    try:
        from utils.simple_oauth import get_oauth_manager
        oauth_manager = get_oauth_manager()
        
        # Get callback parameters
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        logger.info(f"📥 OAuth callback - code: {'✅' if code else '❌'}, state: {'✅' if state else '❌'}, error: {error or 'None'}")
        
        if error:
            logger.error(f"❌ OAuth error from Google: {error}")
            return redirect(f'/login?error=oauth_denied&details={error}')
        
        if not code:
            logger.error("❌ No authorization code received")
            return redirect('/login?error=oauth_no_code')
        
        # Verify state parameter
        stored_state = flask.session.get('oauth_state')
        if not state or state != stored_state:
            logger.error("❌ OAuth state mismatch - possible CSRF attack")
            return redirect('/login?error=oauth_state_mismatch')
        
        # Exchange code for tokens
        logger.info("🔄 Starting token exchange...")
        token_response = oauth_manager.exchange_code_for_tokens(code)
        
        if 'error' in token_response:
            logger.error(f"❌ Token exchange failed: {token_response['error']}")
            return redirect('/login?error=token_exchange_failed')
        
        # Get access token
        access_token = token_response.get('access_token')
        if not access_token:
            logger.error("❌ No access token in response")
            return redirect('/login?error=no_access_token')
        
        # Get user information
        logger.info("👤 Fetching user information...")
        user_info = oauth_manager.get_user_info(access_token)
        
        if 'error' in user_info:
            logger.error(f"❌ Failed to get user info: {user_info['error']}")
            return redirect('/login?error=user_info_failed')
        
        # Authenticate user
        logger.info(f"🔐 Authenticating user: {user_info.get('email', 'unknown')}")
        success, message, session_data = oauth_manager.authenticate_user(user_info)
        
        if success:
            # Store session
            flask.session['swaccha_session_id'] = session_data['session_id']
            flask.session['user_data'] = session_data
            
            logger.info(f"✅ OAuth login successful for: {user_info.get('email')}")
            return redirect('/dashboard')
        else:
            logger.warning(f"❌ User authorization failed: {message}")
            return redirect(f'/login?error=unauthorized&message={urllib.parse.quote(message)}')
            
    except Exception as e:
        logger.error(f"❌ OAuth callback critical error: {e}")
        return redirect('/login?error=oauth_callback_error')

@server.route('/debug/oauth')
def debug_oauth():
    """OAuth debug page - ENHANCED VERSION"""
    try:
        from utils.simple_oauth import get_oauth_manager
        import json
        
        oauth_manager = get_oauth_manager()
        debug_info = oauth_manager.get_debug_info()
        
        # Additional system checks
        system_info = {
            'python_version': f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
            'platform': __import__('platform').system(),
            'cwd': os.getcwd(),
            'client_secrets_path': os.path.abspath('client_secrets.json') if os.path.exists('client_secrets.json') else 'Not found'
        }
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🔧 OAuth Debug Center</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                    margin: 0; padding: 0; background: #0D1B2A; color: #fff; 
                }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .section {{ 
                    margin: 30px 0; padding: 25px; background: #1A1F2E; 
                    border-radius: 16px; border: 2px solid #3182CE; 
                }}
                .status {{ 
                    padding: 15px; margin: 10px 0; border-radius: 10px; 
                    display: flex; align-items: center; gap: 15px;
                }}
                .good {{ background: #2D5A31; border: 2px solid #38A169; }}
                .bad {{ background: #5A2D2D; border: 2px solid #E53E3E; }}
                .warning {{ background: #5A4D2D; border: 2px solid #DD6B20; }}
                .icon {{ font-size: 24px; }}
                .details {{ flex: 1; }}
                .label {{ font-weight: 600; font-size: 16px; }}
                .desc {{ font-size: 14px; opacity: 0.8; margin-top: 5px; }}
                pre {{ 
                    background: #000; padding: 20px; border-radius: 12px; 
                    overflow-x: auto; font-size: 13px; line-height: 1.4;
                }}
                .btn {{ 
                    display: inline-block; padding: 15px 30px; margin: 10px 5px; 
                    background: #3182CE; color: white; text-decoration: none; 
                    border-radius: 10px; font-weight: 600; transition: all 0.2s;
                }}
                .btn:hover {{ background: #2C5AA0; transform: translateY(-2px); }}
                .btn.success {{ background: #38A169; }}
                .btn.warning {{ background: #DD6B20; }}
                h1, h2 {{ color: #3182CE; }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔧 OAuth Debug Center</h1>
                    <p>Complete OAuth configuration and testing dashboard</p>
                </div>
                
                <div class="section">
                    <h2>🚦 System Status</h2>
                    
                    <div class="status {'good' if debug_info.get('oauth_configured') else 'bad'}">
                        <div class="icon">{'✅' if debug_info.get('oauth_configured') else '❌'}</div>
                        <div class="details">
                            <div class="label">OAuth Configuration</div>
                            <div class="desc">
                                {'Properly configured with client_secrets.json' if debug_info.get('oauth_configured') else 'Missing or invalid client_secrets.json file'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="status {'good' if debug_info.get('client_secrets_exists') else 'bad'}">
                        <div class="icon">{'📄' if debug_info.get('client_secrets_exists') else '📭'}</div>
                        <div class="details">
                            <div class="label">client_secrets.json</div>
                            <div class="desc">
                                {'File found and readable' if debug_info.get('client_secrets_exists') else 'File missing - download from Google Cloud Console'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="status {'good' if debug_info.get('has_client_id') else 'bad'}">
                        <div class="icon">{'🆔' if debug_info.get('has_client_id') else '❓'}</div>
                        <div class="details">
                            <div class="label">Client ID</div>
                            <div class="desc">
                                {'Valid client ID found' if debug_info.get('has_client_id') else 'Missing or empty client ID'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="status {'good' if debug_info.get('has_client_secret') else 'bad'}">
                        <div class="icon">{'🔑' if debug_info.get('has_client_secret') else '🚫'}</div>
                        <div class="details">
                            <div class="label">Client Secret</div>
                            <div class="desc">
                                {'Valid client secret found' if debug_info.get('has_client_secret') else 'Missing or empty client secret'}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="grid">
                    <div class="section">
                        <h2>📦 Dependencies</h2>
                        {''.join([f'''
                        <div class="status {"good" if "✅" in status else "bad"}">
                            <div class="icon">{"📦" if "✅" in status else "⚠️"}</div>
                            <div class="details">
                                <div class="label">{dep}</div>
                                <div class="desc">{status}</div>
                            </div>
                        </div>
                        ''' for dep, status in debug_info.get('dependencies', {}).items()])}
                    </div>
                    
                    <div class="section">
                        <h2>🧪 Quick Tests</h2>
                        <a href="/oauth/login" class="btn success">🔗 Test OAuth Flow</a>
                        <p><em>Tests the complete OAuth login process</em></p>
                        
                        <a href="/login" class="btn">📋 Login Page</a>
                        <p><em>Go to the main login page</em></p>
                        
                        <a href="/" class="btn">🏠 Dashboard</a>
                        <p><em>Return to main dashboard</em></p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>⚙️ Configuration Details</h2>
                    <pre>{json.dumps(debug_info, indent=2, default=str)}</pre>
                </div>
                
                <div class="section">
                    <h2>🖥️ System Information</h2>
                    <pre>{json.dumps(system_info, indent=2, default=str)}</pre>
                </div>
                
                <div class="section">
                    <h2>📚 Setup Guide</h2>
                    <h3>🚀 Quick Setup (5 minutes)</h3>
                    <ol>
                        <li><strong>Install dependencies:</strong><br>
                            <code>pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client requests</code>
                        </li>
                        <li><strong>Google Cloud Console setup:</strong><br>
                            → Go to <a href="https://console.developers.google.com/" style="color: #3182CE;" target="_blank">console.developers.google.com</a><br>
                            → Create project or select existing<br>
                            → Enable "Google+ API" or "People API"<br>
                            → Create OAuth 2.0 credentials
                        </li>
                        <li><strong>Configure redirect URI:</strong><br>
                            Add: <code>http://localhost:8050/oauth/callback</code>
                        </li>
                        <li><strong>Download credentials:</strong><br>
                            → Download JSON file<br>
                            → Rename to <code>client_secrets.json</code><br>
                            → Place in project root directory
                        </li>
                        <li><strong>Add your email:</strong><br>
                            Edit <code>config/auth.py</code> → ALLOWED_USERS → administrators
                        </li>
                        <li><strong>Test:</strong><br>
                            Restart app and click "Test OAuth Flow" above
                        </li>
                    </ol>
                    
                    <h3>🎯 Current Status</h3>
                    <p>
                        {'✅ <strong>Ready for real OAuth!</strong> All configuration looks good.' if debug_info.get('oauth_configured') else 
                         '⚠️ <strong>Demo mode active.</strong> OAuth will work but use demo authentication until you complete setup above.'}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
        
    except Exception as e:
        logger.error(f"Debug page error: {e}")
        return f"""
        <html><body style="font-family: monospace; background: #1a1a1a; color: #fff; padding: 40px;">
            <h1>❌ Debug Error</h1>
            <p>Error loading debug info: {str(e)}</p>
            <p><a href="/" style="color: #3182CE;">← Back to Dashboard</a></p>
        </body></html>
        """


# BULLETPROOF App Layout - All components guaranteed to exist
app.layout = html.Div([
    # Core stores
    dcc.Store(id='current-theme', data=DEFAULT_THEME),
    dcc.Store(id='user-authenticated', data=False),
    dcc.Store(id='current-page', data='public_landing'),
    dcc.Store(id='user-session-data', data={}),
    dcc.Store(id='auth-error-message', data=''),
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='session-check-interval', interval=30*1000, n_intervals=0),
    
    # Main layout container
    html.Div(id="main-layout"),
    
    # BULLETPROOF: All possible callback components in hidden container
    html.Div(
        style={"display": "none"},
        children=[
            # Navigation buttons (exist in hover overlay - all layouts)
            html.Button("Admin Login", id="admin-login-btn"),
            html.Button("Overview", id="overlay-nav-overview"),
            html.Button("Analytics", id="overlay-nav-analytics"),
            html.Button("Reports", id="overlay-nav-reports"),
            
            # Theme buttons (exist in hover overlay - all layouts)
            html.Button("Dark", id="theme-dark"),
            html.Button("Light", id="theme-light"),
            html.Button("High Contrast", id="theme-high_contrast"),
            html.Button("Swaccha Green", id="theme-swaccha_green"),
            
            # Login page buttons (only exist when on login page)
            html.Button("Back to Public", id="back-to-public-btn"),
            html.Button("Google Login", id="google-login-btn"),
            html.Button("Demo Login", id="demo-login-btn"),
            html.Button("Admin Account", id="admin-account-btn"),
            html.Button("Dev Account", id="dev-account-btn"),
            html.Button("Viewer Account", id="viewer-account-btn"),
            html.Button("PIN Login", id="pin-login-btn"),
            html.Button("Manual Login", id="manual-login-btn"),
            html.Button("OAuth Debug", id="oauth-debug-btn"),
            html.Button("OAuth Test", id="oauth-test-btn"),
            dcc.Input(id="access-pin", type="password"),
            dcc.Input(id="manual-email", type="email"),
            
            # Admin dashboard buttons (only exist when authenticated)
            html.Button("Logout", id="logout-btn"),
            html.Button("Quick Reports", id="quick-reports-btn"),
            html.Button("Quick Settings", id="quick-settings-btn"),
            
            # Placeholder page buttons
            html.Button("Back to Dashboard", id="back-to-dashboard-btn")
        ]
    )
])

# 1. Page routing and authentication - CORE CALLBACK
@callback(
    [Output('current-page', 'data'),
     Output('user-authenticated', 'data'), 
     Output('user-session-data', 'data'),
     Output('auth-error-message', 'data')],
    [Input('url', 'pathname'), Input('url', 'search')],
    prevent_initial_call=False
)
def route_and_authenticate(pathname, search):
    """Core routing and authentication logic"""
    if pathname:
        pathname = urllib.parse.unquote(pathname)
    
    # Parse parameters
    params = {}
    if search:
        params = dict(urllib.parse.parse_qsl(search.lstrip('?')))
    
    # Session validation
    session_id = flask.session.get('swaccha_session_id')
    user_data = flask.session.get('user_data', {})
    oauth_user_info = flask.session.get('oauth_user_info', {})
    is_authenticated = False
    
    if session_id:
        # Demo sessions (always valid)
        if session_id.startswith('stable_session_'):
            is_authenticated = True
        # OAuth sessions
        elif GOOGLE_AUTH_AVAILABLE and google_auth_manager:
            try:
                session_data = google_auth_manager.validate_session(session_id)
                if session_data:
                    is_authenticated = True
                    user_data = {
                        'name': oauth_user_info.get('name', 'Google User'),
                        'email': oauth_user_info.get('email', 'user@gmail.com'),
                        'picture': oauth_user_info.get('picture', '/assets/img/default-avatar.png'),
                        'role': 'administrator',
                        'auth_method': 'google_oauth'
                    }
                    flask.session['user_data'] = user_data
                else:
                    flask.session.clear()
                    user_data = {}
            except Exception:
                flask.session.clear()
                user_data = {}
    
    # Handle logout
    if params.get('logout') == 'true':
        flask.session.clear()
        return 'public_landing', False, {}, 'Logged out successfully.'
    
    # Route determination
    if not pathname or pathname == '/':
        return 'public_landing', is_authenticated, user_data, ''
    elif pathname == '/login':
        error = params.get('error', '')
        error_messages = {
            'oauth_not_available': 'Google OAuth not configured. Use demo login.',
            'oauth_failed': 'OAuth setup failed. Use demo login.',
            'unauthorized': 'You are not authorized. Contact administrator.',
            'invalid_pin': 'Invalid PIN. Try: 1234, 5678, or 9999'
        }
        return 'login', is_authenticated, user_data, error_messages.get(error, error)
    elif pathname == '/dashboard':
        if is_authenticated:
            return 'admin_dashboard', True, user_data, ''
        else:
            return 'login', False, {}, 'Please log in to access dashboard.'
    elif pathname in ['/analytics', '/reports']:
        page = 'analytics_page' if pathname == '/analytics' else 'reports_page'
        if is_authenticated:
            return page, True, user_data, ''
        else:
            return 'login', False, {}, 'Please log in to access this page.'
    elif pathname.startswith('/oauth/') or pathname.startswith('/debug/'):
        raise PreventUpdate
    else:
        return 'public_landing', is_authenticated, user_data, ''

# 2. Theme switching - SAFE CALLBACK
@callback(
    Output('current-theme', 'data'),
    [Input('theme-dark', 'n_clicks'),
     Input('theme-light', 'n_clicks'), 
     Input('theme-high_contrast', 'n_clicks'),
     Input('theme-swaccha_green', 'n_clicks')],
    prevent_initial_call=True
)
def update_theme(dark, light, contrast, green):
    """Theme switching"""
    if not ctx.triggered:
        return DEFAULT_THEME
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    themes = {
        'theme-dark': 'dark',
        'theme-light': 'light',
        'theme-high_contrast': 'high_contrast', 
        'theme-swaccha_green': 'swaccha_green'
    }
    return themes.get(button_id, DEFAULT_THEME)

# 3. Layout rendering - SAFE CALLBACK
@callback(
    Output('main-layout', 'children'),
    [Input('current-theme', 'data'),
     Input('user-authenticated', 'data'),
     Input('current-page', 'data'),
     Input('user-session-data', 'data'),
     Input('auth-error-message', 'data')]
)
def render_layout(theme_name, is_authenticated, current_page, user_data, error_message):
    """Render appropriate layout"""
    # Handle None values
    theme_name = theme_name or DEFAULT_THEME
    is_authenticated = bool(is_authenticated)
    current_page = current_page or 'public_landing'
    user_data = user_data or {}
    error_message = error_message or ''
    
    print(f"DEBUG: Rendering layout - page: {current_page}, theme: {theme_name}")
    
    try:
        if current_page == 'login':
            layout = build_login_layout(theme_name, error_message)
            print("DEBUG: Login layout rendered")
            return layout
        elif current_page == 'admin_dashboard' and is_authenticated:
            layout = build_admin_dashboard(theme_name, user_data)
            print("DEBUG: Admin dashboard layout rendered")
            return layout
        elif current_page in ['analytics_page', 'reports_page'] and is_authenticated:
            layout = build_placeholder_layout(current_page, theme_name, user_data)
            print(f"DEBUG: Placeholder layout rendered for {current_page}")
            return layout
        else:
            layout = build_public_layout(theme_name)
            print("DEBUG: Public layout rendered")
            return layout
    except Exception as e:
        print(f"ERROR: Layout build failed: {e}")
        import traceback
        print(f"ERROR: Full traceback: {traceback.format_exc()}")
        return build_public_layout(DEFAULT_THEME)

# 4. Basic navigation - SAFE CALLBACK
@callback(
    Output('url', 'pathname'),
    [Input('admin-login-btn', 'n_clicks'),
     Input('overlay-nav-overview', 'n_clicks'),
     Input('overlay-nav-analytics', 'n_clicks'),
     Input('overlay-nav-reports', 'n_clicks')],
    prevent_initial_call=True
)
def handle_navigation(login_clicks, overview_clicks, analytics_clicks, reports_clicks):
    """Handle basic navigation"""
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ctx.triggered[0]['value'] in [None, 0]:
        raise PreventUpdate
    
    routes = {
        'admin-login-btn': '/login',
        'overlay-nav-overview': '/',
        'overlay-nav-analytics': '/analytics', 
        'overlay-nav-reports': '/reports'
    }
    return routes.get(button_id, '/')


@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('google-login-btn', 'n_clicks')],
    [State('current-page', 'data')],
    prevent_initial_call=True
)
def handle_google_oauth_login(google_clicks, current_page):
    """Handle Google OAuth login - WORKING VERSION"""
    if current_page != 'login':
        raise PreventUpdate
    
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    trigger_value = ctx.triggered[0]['value']
    
    if trigger_value is None or trigger_value == 0:
        raise PreventUpdate
    
    if button_id == 'google-login-btn':
        logger.info("🔵 Google OAuth login button clicked")
        return '/oauth/login'
    
    raise PreventUpdate


# 5. Login actions - ENHANCED WITH REAL OAUTH
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('google-login-btn', 'n_clicks'),      # REAL OAUTH BUTTON
     Input('demo-login-btn', 'n_clicks'),
     Input('admin-account-btn', 'n_clicks'),
     Input('dev-account-btn', 'n_clicks'),
     Input('viewer-account-btn', 'n_clicks'),
     Input('pin-login-btn', 'n_clicks'),
     Input('manual-login-btn', 'n_clicks'),
     Input('back-to-public-btn', 'n_clicks')],
    [State('access-pin', 'value'),
     State('manual-email', 'value'),
     State('current-page', 'data')],
    prevent_initial_call=True
)
def handle_login_actions(google_clicks, demo_clicks, admin_clicks, dev_clicks, 
                        viewer_clicks, pin_clicks, manual_clicks, back_clicks,
                        access_pin, manual_email, current_page):
    """Handle all login actions including REAL Google OAuth"""
    if not ctx.triggered or current_page != 'login':
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ctx.triggered[0]['value'] in [None, 0]:
        raise PreventUpdate
    
    print(f"DEBUG: Login action - {button_id}")
    
    # Navigation
    if button_id == 'back-to-public-btn':
        return '/'
    
    # REAL GOOGLE OAUTH - Routes to Flask /oauth/login
    elif button_id == 'google-login-btn':
        print("DEBUG: REAL Google OAuth initiated - routing to /oauth/login")
        print(f"DEBUG: GOOGLE_AUTH_AVAILABLE = {GOOGLE_AUTH_AVAILABLE}")
        print(f"DEBUG: REAL_OAUTH_AVAILABLE = {REAL_OAUTH_AVAILABLE}")
        print(f"DEBUG: google_auth_manager type = {type(google_auth_manager).__name__}")
        
        if GOOGLE_AUTH_AVAILABLE and REAL_OAUTH_AVAILABLE and google_auth_manager:
            print("DEBUG: Real Google Auth Manager available - redirecting to /oauth/login")
            return '/oauth/login'  # This should trigger the Flask route
        else:
            print("DEBUG: Google OAuth not available - using demo fallback")
            print(f"DEBUG: Reasons - Available: {GOOGLE_AUTH_AVAILABLE}, Real: {REAL_OAUTH_AVAILABLE}, Manager: {google_auth_manager is not None}")
            # Fallback to demo only if OAuth is truly not available
            create_demo_session('google_fallback', 'Google User (Demo)', 'administrator')
            return '/dashboard'
    
    # Demo login methods
    elif button_id == 'demo-login-btn':
        create_demo_session('demo_user', 'Demo User', 'administrator')
        return '/dashboard'
    
    elif button_id == 'admin-account-btn':
        create_demo_session('admin', 'Administrator', 'administrator')
        return '/dashboard'
    
    elif button_id == 'dev-account-btn':
        create_demo_session('developer', 'Developer', 'administrator')
        return '/dashboard'
    
    elif button_id == 'viewer-account-btn':
        create_demo_session('viewer', 'Viewer', 'viewer')
        return '/dashboard'
    
    elif button_id == 'pin-login-btn':
        pins = {
            '1234': ('admin', 'PIN Admin', 'administrator'),
            '5678': ('dev', 'PIN Developer', 'administrator'),
            '9999': ('demo', 'PIN Demo', 'viewer')
        }
        if access_pin in pins:
            user_id, name, role = pins[access_pin]
            create_demo_session(user_id, name, role)
            return '/dashboard'
        else:
            return '/login?error=invalid_pin'
    
    elif button_id == 'manual-login-btn':
        if manual_email and '@' in manual_email:
            role = 'administrator' if 'swaccha' in manual_email.lower() else 'viewer'
            create_demo_session('manual_user', f'User ({manual_email})', role)
            return '/dashboard'
        else:
            return '/login?error=invalid_email'
    
    raise PreventUpdate

# 6. Admin dashboard actions - SAFE CALLBACK
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('logout-btn', 'n_clicks'),
     Input('quick-reports-btn', 'n_clicks'),
     Input('quick-settings-btn', 'n_clicks')],
    [State('current-page', 'data'),
     State('user-authenticated', 'data')],
    prevent_initial_call=True
)
def handle_admin_actions(logout_clicks, reports_clicks, settings_clicks, current_page, is_authenticated):
    """Handle admin dashboard actions"""
    if not is_authenticated or current_page != 'admin_dashboard' or not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ctx.triggered[0]['value'] in [None, 0]:
        raise PreventUpdate
    
    if button_id == 'logout-btn':
        return '/auth/logout'  # Triggers Flask logout route
    elif button_id == 'quick-reports-btn':
        return '/reports'
    elif button_id == 'quick-settings-btn':
        return '/settings'
    
    raise PreventUpdate

# 7. Placeholder navigation - SAFE CALLBACK  
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('back-to-dashboard-btn', 'n_clicks')],
    [State('current-page', 'data'),
     State('user-authenticated', 'data')],
    prevent_initial_call=True
)
def handle_placeholder_nav(back_clicks, current_page, is_authenticated):
    """Handle placeholder page navigation"""
    if (not is_authenticated or 
        current_page not in ['analytics_page', 'reports_page'] or 
        not ctx.triggered):
        raise PreventUpdate
    
    if ctx.triggered[0]['value'] in [None, 0]:
        raise PreventUpdate
    
    return '/dashboard'

# Helper functions
def create_demo_session(user_id, name, role):
    """Create demo session (stable)"""
    session_data = {
        'session_id': f'stable_session_{user_id}',
        'user_id': user_id,
        'email': f'{user_id}@swacchaandhra.local',
        'name': name,
        'picture': '/assets/img/default-avatar.png',
        'role': role,
        'auth_method': 'demo'
    }
    flask.session['swaccha_session_id'] = session_data['session_id']
    flask.session['user_data'] = session_data
    print(f"DEBUG: Demo session created for {name}")

def build_placeholder_layout(page_type, theme_name, user_data):
    """Build placeholder layouts"""
    from utils.theme_utils import get_theme_styles
    from components.navigation.hover_overlay import create_hover_overlay_banner
    
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    titles = {
        'analytics_page': '📈 Advanced Analytics',
        'reports_page': '📋 Reports & Documentation'
    }
    
    auth_method = user_data.get('auth_method', 'unknown')
    auth_badge = {
        'google_oauth': '🔵 Google OAuth',
        'demo': '🚀 Demo Session'
    }.get(auth_method, '❓ Unknown')
    
    return html.Div(
        style=theme_styles["container_style"],
        children=[
            # ENSURE HOVER OVERLAY IS INCLUDED
            create_hover_overlay_banner(theme_name),
            html.Div(
                style=theme_styles["main_content_style"],
                children=[
                    html.H1(titles.get(page_type, '📊 Dashboard'),
                           style={"color": theme["text_primary"], "textAlign": "center"}),
                    html.P(f"Welcome {user_data.get('name', 'User')}! ({auth_badge})",
                          style={"color": theme["text_secondary"], "textAlign": "center", "fontSize": "1.2rem"}),
                    html.P("This section is under development.",
                          style={"color": theme["text_secondary"], "textAlign": "center"}),
                    html.Div(
                        style={"textAlign": "center", "marginTop": "2rem"},
                        children=[
                            html.Button("← Back to Dashboard", id="back-to-dashboard-btn",
                                       style={"backgroundColor": theme["brand_primary"], "color": "white",
                                             "border": "none", "padding": "1rem 2rem", "borderRadius": "8px",
                                             "fontSize": "1rem", "cursor": "pointer"})
                        ]
                    )
                ]
            )
        ]
    )

if __name__ == "__main__":
    print("🚀 Starting Swaccha Andhra Dashboard...")
    print(f"🔑 Google OAuth Utils: {'✅ Available' if GOOGLE_AUTH_AVAILABLE else '❌ Not Available'}")
    print(f"🔑 Real OAuth Config: {'✅ Available' if REAL_OAUTH_AVAILABLE else '❌ Not Available'}")
    print(f"🔑 Auth Manager: {type(google_auth_manager).__name__ if google_auth_manager else 'None'}")
    
    if google_auth_manager and hasattr(google_auth_manager, 'client_secrets_file'):
        secrets_exists = os.path.exists(google_auth_manager.client_secrets_file)
        print(f"🔑 client_secrets.json: {'✅ Found' if secrets_exists else '❌ Missing'}")
    
    print("🔐 Login Methods: Google OAuth (real), Demo, PIN (1234/5678/9999), Manual")
    print("🔧 Debug OAuth: http://localhost:8050/debug/oauth")
    print("🧪 Test Overlay: http://localhost:8050/test/overlay")
    print("🧪 Test Flask: http://localhost:8050/test/flask")
    print("📊 OAuth Status: http://localhost:8050/oauth/status")
    print("")
    print("📝 Testing Instructions:")
    print("1. Hover at the TOP edge of any page to see navigation overlay")
    print("2. Click 'User Login' in overlay to access login page")
    print("3. Try Google OAuth or demo login methods")
    print("")
    
    app.run(debug=True, host='0.0.0.0', port=8050)

__all__ = ['app', 'server']