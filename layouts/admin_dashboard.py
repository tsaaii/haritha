# layouts/admin_dashboard.py - UPDATED WITH MOVED FUNCTIONALITY FROM MAIN.PY
"""
Enhanced Admin Dashboard Layout for Swaccha Andhra - WITH ALL DASHBOARD FUNCTIONALITY MOVED FROM MAIN.PY
Now includes all the Flask routes and functions that were in main.py
"""

from dash import html, dcc
from datetime import datetime
import random
from flask import session, redirect, request
import os
from pathlib import Path

from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner
from components.data.filterable_container import create_filterable_container


def get_current_theme():
    """Get current theme from session or default"""
    return session.get('current_theme', 'dark')


def create_empty_themed_page(title, icon, theme_name="dark"):
    """Create an empty themed page template with user info moved to nav-tabs"""
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    user_info = session.get('user_data', {})
    user_name = user_info.get('name', 'Administrator')
    user_role = user_info.get('role', 'administrator').replace('_', ' ').title()
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Swaccha Andhra Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background-color: {theme["primary_bg"]};
                color: {theme["text_primary"]};
                line-height: 1.6;
                min-height: 100vh;
            }}
            
            .page-container {{
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }}
            
            /* Navigation Header */
            .navigation-header {{
                background: linear-gradient(135deg, {theme["secondary_bg"]} 0%, {theme["accent_bg"]} 100%);
                border-bottom: 3px solid {theme["brand_primary"]};
                padding: 1rem 2rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
                position: sticky;
                top: 0;
                z-index: 1000;
            }}
            
            .nav-content {{
                max-width: 1600px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 1rem;
            }}
            
            /* MODIFIED: Nav-tabs now contains both navigation and user info */
            .nav-tabs {{
                display: flex;
                align-items: center;
                gap: 1rem;
                flex-wrap: wrap;
                flex: 1;
                justify-content: space-between;
            }}
            
            /* Navigation buttons container */
            .nav-buttons {{
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
                align-items: center;
            }}
            
            .nav-tab {{
                background: {theme["accent_bg"]};
                color: {theme["text_primary"]};
                border: 2px solid {theme["card_bg"]};
                padding: 0.75rem 1.25rem;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                font-size: 0.9rem;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                white-space: nowrap;
                min-height: 44px;
            }}
            
            .nav-tab:hover {{
                background: {theme["brand_primary"]};
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }}
            
            .nav-tab.active {{
                background: {theme["brand_primary"]};
                color: white;
                border-color: {theme["brand_primary"]};
                box-shadow: 0 4px 12px rgba(49, 130, 206, 0.4);
            }}
            
            /* MOVED: User info is now inside nav-tabs */
            .user-info {{
                display: flex;
                align-items: center;
                gap: 1rem;
                background: {theme["card_bg"]};
                padding: 0.5rem 1rem;
                border-radius: 8px;
                border: 2px solid {theme["accent_bg"]};
                min-height: 44px;
                flex-shrink: 0;
            }}
            
            .user-avatar {{
                width: 32px;
                height: 32px;
                border-radius: 50%;
                border: 2px solid {theme["brand_primary"]};
                object-fit: cover;
            }}
            
            .user-details {{
                display: flex;
                flex-direction: column;
            }}
            
            .user-name {{
                font-weight: 600;
                font-size: 0.9rem;
                color: {theme["text_primary"]};
                line-height: 1.2;
            }}
            
            .user-role {{
                font-size: 0.75rem;
                color: {theme["text_secondary"]};
                line-height: 1.2;
            }}
            
            .logout-btn {{
                background: {theme["error"]};
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                font-size: 0.85rem;
                transition: all 0.2s ease;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 0.25rem;
                min-height: 36px;
            }}
            
            .logout-btn:hover {{
                background: #C53030;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(197, 48, 48, 0.4);
            }}
            
            /* Theme Switcher - moved to right side */
            .theme-switcher {{
                display: flex;
                align-items: center;
                gap: 0.25rem;
                background: {theme["card_bg"]};
                border: 2px solid {theme["accent_bg"]};
                border-radius: 8px;
                padding: 0.25rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
                min-height: 44px;
            }}
            
            .theme-btn {{
                background: transparent;
                border: 1px solid {theme["border_light"] if "border_light" in theme else theme["accent_bg"]};
                color: {theme["text_primary"]};
                padding: 0.25rem;
                border-radius: 4px;
                cursor: pointer;
                font-size: 1rem;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s ease;
            }}
            
            .theme-btn:hover {{
                background: {theme["brand_primary"]};
                color: white;
                transform: scale(1.1);
            }}
            
            .theme-btn.active {{
                background: {theme["brand_primary"]};
                color: white;
            }}
            
            /* Main Content */
            .main-content {{
                flex: 1;
                padding: 2rem;
                max-width: 1600px;
                margin: 0 auto;
                width: 100%;
            }}
            
            .page-hero {{
                background: linear-gradient(135deg, {theme["secondary_bg"]} 0%, {theme["accent_bg"]} 100%);
                border-radius: 12px;
                padding: 3rem 2rem;
                margin-bottom: 2rem;
                text-align: center;
                border: 2px solid {theme["card_bg"]};
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                position: relative;
                overflow: hidden;
            }}
            
            .page-hero::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(circle at 30% 70%, {theme["brand_primary"]}22 0%, transparent 50%);
                pointer-events: none;
            }}
            
            .page-hero-content {{
                position: relative;
                z-index: 2;
            }}
            
            .page-icon {{
                font-size: 4rem;
                margin-bottom: 1rem;
                filter: drop-shadow(2px 2px 8px rgba(0, 0, 0, 0.3));
                animation: float 3s ease-in-out infinite;
            }}
            
            @keyframes float {{
                0%, 100% {{ transform: translateY(0px); }}
                50% {{ transform: translateY(-10px); }}
            }}
            
            .page-title {{
                font-size: 3rem;
                font-weight: 900;
                color: {theme["text_primary"]};
                margin-bottom: 0.5rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                line-height: 1.1;
            }}
            
            .page-subtitle {{
                font-size: 1.2rem;
                color: {theme["text_secondary"]};
                line-height: 1.5;
                max-width: 600px;
                margin: 0 auto;
            }}
            
            .coming-soon {{
                background: {theme["card_bg"]};
                border-radius: 12px;
                border: 2px solid {theme["accent_bg"]};
                padding: 3rem 2rem;
                text-align: center;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
                margin: 2rem 0;
            }}
            
            .coming-soon-icon {{
                font-size: 3rem;
                margin-bottom: 1rem;
                opacity: 0.7;
            }}
            
            .coming-soon h2 {{
                color: {theme["text_primary"]};
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 1rem;
            }}
            
            .coming-soon p {{
                color: {theme["text_secondary"]};
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 2rem;
            }}
            
            .feature-preview {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1rem;
                margin-top: 2rem;
            }}
            
            .preview-item {{
                background: {theme["accent_bg"]};
                border: 1px solid {theme["card_bg"]};
                border-radius: 8px;
                padding: 1rem;
                text-align: center;
                transition: all 0.2s ease;
            }}
            
            .preview-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                border-color: {theme["brand_primary"]};
            }}
            
            .preview-item-icon {{
                font-size: 1.5rem;
                margin-bottom: 0.5rem;
            }}
            
            .preview-item h4 {{
                color: {theme["text_primary"]};
                font-size: 0.9rem;
                font-weight: 600;
                margin-bottom: 0.25rem;
            }}
            
            .preview-item p {{
                color: {theme["text_secondary"]};
                font-size: 0.8rem;
                line-height: 1.3;
            }}
            
            /* Footer */
            .footer {{
                background: {theme["secondary_bg"]};
                border-top: 2px solid {theme["card_bg"]};
                padding: 1rem 2rem;
                text-align: center;
                color: {theme["text_secondary"]};
                font-size: 0.9rem;
            }}
            
            /* Responsive Design */
            @media (max-width: 1200px) {{
                .nav-tabs {{
                    flex-direction: column;
                    gap: 1rem;
                    align-items: stretch;
                }}
                
                .nav-buttons {{
                    justify-content: center;
                    width: 100%;
                }}
                
                .user-info {{
                    justify-content: center;
                    width: 100%;
                }}
            }}
            
            @media (max-width: 768px) {{
                .nav-content {{
                    flex-direction: column;
                    gap: 1rem;
                }}
                
                .nav-tabs {{
                    width: 100%;
                }}
                
                .nav-buttons {{
                    width: 100%;
                    justify-content: center;
                    flex-wrap: wrap;
                }}
                
                .nav-tab {{
                    flex: 1;
                    justify-content: center;
                    min-width: auto;
                    padding: 0.5rem 0.75rem;
                    font-size: 0.8rem;
                }}
                
                .main-content {{
                    padding: 1rem;
                }}
                
                .page-title {{
                    font-size: 2rem;
                }}
                
                .page-hero {{
                    padding: 2rem 1rem;
                }}
                
                .theme-switcher {{
                    align-self: center;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="page-container">
            <!-- Navigation Header -->
            <nav class="navigation-header">
                <div class="nav-content">
                    <!-- MODIFIED: Nav-tabs now contains both navigation buttons and user info -->
                    <div class="nav-tabs">
                        <!-- Left: Navigation Buttons -->
                        <div class="nav-buttons">
                            <a href="/dashboard" class="nav-tab {'active' if 'dashboard' in title.lower() else ''}">
                                📊 Dashboard
                            </a>
                            <a href="/data-analytics" class="nav-tab {'active' if 'data analytics' in title.lower() else ''}">
                                🔍 Data Analytics
                            </a>
                            <a href="/charts" class="nav-tab {'active' if 'charts' in title.lower() else ''}">
                                📈 Charts
                            </a>
                            <a href="/reports" class="nav-tab {'active' if 'reports' in title.lower() else ''}">
                                📋 Reports
                            </a>
                            <a href="/reviews" class="nav-tab {'active' if 'reviews' in title.lower() else ''}">
                                ⭐ Reviews
                            </a>
                            <a href="/forecasting" class="nav-tab {'active' if 'forecasting' in title.lower() else ''}">
                                🔮 Forecasting
                            </a>
                            <a href="/upload" class="nav-tab {'active' if 'upload' in title.lower() else ''}">
                                📤 Upload
                            </a>
                        </div>
                        
                        <!-- Center/Right: User Info (now inside nav-tabs) -->
                        <div class="user-info">
                            <img src="/assets/img/default-avatar.png" alt="User Avatar" class="user-avatar">
                            <div class="user-details">
                                <div class="user-name">{user_name}</div>
                                <div class="user-role">{user_role}</div>
                            </div>
                            <a href="/?logout=true" class="logout-btn">
                                🚪 Logout
                            </a>
                        </div>
                    </div>
                    
                    <!-- Right: Theme Switcher -->
                    <div class="theme-switcher">
                        <button class="theme-btn {'active' if theme_name == 'dark' else ''}" onclick="changeTheme('dark')" title="Dark Mode">🌙</button>
                        <button class="theme-btn {'active' if theme_name == 'light' else ''}" onclick="changeTheme('light')" title="Light Mode">☀️</button>
                        <button class="theme-btn {'active' if theme_name == 'high_contrast' else ''}" onclick="changeTheme('high_contrast')" title="High Contrast">🔳</button>
                        <button class="theme-btn {'active' if theme_name == 'swaccha_green' else ''}" onclick="changeTheme('swaccha_green')" title="Swaccha Green">🌿</button>
                    </div>
                </div>
            </nav>
            
            <!-- Main Content -->
            <main class="main-content">
                <div class="page-hero">
                </div>
                
                <div class="coming-soon">
                    <div class="coming-soon-icon">🚧</div>
                    <h2>Coming Soon</h2>
                    <p>
                        We're working hard to bring you amazing features for this section. 
                        Check back soon for updates and new functionality!
                    </p>
                    
                    <div class="feature-preview">
                        <div class="preview-item">
                            <div class="preview-item-icon">⚡</div>
                            <h4>Fast & Efficient</h4>
                            <p>Optimized for performance</p>
                        </div>
                        <div class="preview-item">
                            <div class="preview-item-icon">🎨</div>
                            <h4>Beautiful Design</h4>
                            <p>Modern and intuitive interface</p>
                        </div>
                        <div class="preview-item">
                            <div class="preview-item-icon">📱</div>
                            <h4>Mobile Ready</h4>
                            <p>Works on all devices</p>
                        </div>
                        <div class="preview-item">
                            <div class="preview-item-icon">🔒</div>
                            <h4>Secure</h4>
                            <p>Enterprise-level security</p>
                        </div>
                    </div>
                </div>
            </main>
            
            <!-- Footer -->
            <footer class="footer">
                <p>© 2025 Swaccha Andhra Corporation • {title} Section • <span id="current-time"></span></p>
            </footer>
        </div>
        
        <script>
            // Update current time
            function updateTime() {{
                const now = new Date();
                document.getElementById('current-time').textContent = now.toLocaleString();
            }}
            updateTime();
            setInterval(updateTime, 1000);
            
            // Theme switching
            function changeTheme(themeName) {{
                // Store theme preference
                fetch('/api/set-theme', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ theme: themeName }})
                }}).then(() => {{
                    // Reload page with new theme
                    window.location.reload();
                }});
            }}
            
            // Add smooth scroll behavior
            document.documentElement.style.scrollBehavior = 'smooth';
        </script>
    </body>
    </html>
    '''


def register_dashboard_flask_routes(server):
    """
    Register all Flask routes that were in main.py for dashboard functionality
    MOVED FROM MAIN.PY TO ADMIN_DASHBOARD.PY
    """
    
    @server.route('/dashboard')
    def admin_dashboard():
        """Main Dashboard Page - Empty for now"""
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme = get_current_theme()
        return create_empty_themed_page("Dashboard", "📊", theme)

    @server.route('/data-analytics')
    def admin_data_analytics():
        """Data Analytics Page - Empty for now"""
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme = get_current_theme()
        return create_empty_themed_page("Data Analytics", "🔍", theme)

    @server.route('/charts')
    def admin_charts():
        """Charts Page - Empty for now"""
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme = get_current_theme()
        return create_empty_themed_page("Charts", "📈", theme)

    @server.route('/reports')
    def admin_reports():
        """Reports Page - Empty for now"""
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme = get_current_theme()
        return create_empty_themed_page("Reports", "📋", theme)

    @server.route('/reviews')
    def admin_reviews():
        """Reviews Page - Empty for now"""
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme = get_current_theme()
        return create_empty_themed_page("Reviews", "⭐", theme)

    @server.route('/forecasting')
    def admin_forecasting():
        """Forecasting Page - Empty for now"""
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme = get_current_theme()
        return create_empty_themed_page("Forecasting", "🔮", theme)

    @server.route('/upload')
    def admin_upload():
        """Upload Page - Empty for now"""
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme = get_current_theme()
        return create_empty_themed_page("Upload", "📤", theme)

    # Theme switching API endpoint
    @server.route('/api/set-theme', methods=['POST'])
    def set_theme():
        """API endpoint to change theme"""
        data = request.get_json()
        theme_name = data.get('theme', 'dark')
        
        # Validate theme
        valid_themes = ['dark', 'light', 'high_contrast', 'swaccha_green']
        if theme_name in valid_themes:
            session['current_theme'] = theme_name
            return {'status': 'success', 'theme': theme_name}
        else:
            return {'status': 'error', 'message': 'Invalid theme'}, 400
    
    @server.route('/api/download/<file_id>')
    def download_file(file_id):
        """Serve uploaded files for download"""
        try:
            # Find file in uploads directory
            upload_dir = Path('uploads/dash_uploads')
            
            # Look for file with matching ID
            for file_path in upload_dir.glob(f"{file_id}.*"):
                if file_path.exists():
                    from flask import send_file
                    return send_file(
                        file_path,
                        as_attachment=True,
                        download_name=f"download.{file_path.suffix[1:]}"  # Remove the dot
                    )
            
            return "File not found", 404
            
        except Exception as e:
            print(f"Download error: {e}")
            return "Download failed", 500


def ensure_upload_directory(server):
    """Create upload directory if it doesn't exist - MOVED FROM MAIN.PY"""
    upload_path = server.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_path):
        os.makedirs(upload_path, exist_ok=True)
    print(f"✅ Upload directory ensured: {os.path.abspath(upload_path)}")
    return upload_path


def configure_upload_settings(server):
    """Configure upload settings - MOVED FROM MAIN.PY"""
    server.config.update({
        'UPLOAD_FOLDER': 'uploads',  # Relative to project root
        'MAX_CONTENT_LENGTH': 50 * 1024 * 1024,  # 50MB max file size
        'UPLOAD_EXTENSIONS': {'.pdf', '.csv', '.xlsx', '.xls'},
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-' + str(hash(os.getcwd())))
    })


def validate_file_type(file):
    """Validate file type by extension and MIME type - MOVED FROM MAIN.PY"""
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'text/csv',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
    }
    
    if not file or not file.filename:
        return False
    
    # Check file extension
    extension = '.' + file.filename.rsplit('.', 1)[1].lower()
    server_config = {'UPLOAD_EXTENSIONS': {'.pdf', '.csv', '.xlsx', '.xls'}}
    if extension not in server_config['UPLOAD_EXTENSIONS']:
        return False
    
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False
    
    return True


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
    """Create content based on active tab - WITH FILTER CONTAINER"""
    theme = theme_styles["theme"]
    
    if active_tab == "tab-analytics":
        from components.filters.filter_container import create_filter_container
        
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
                    "Filter and analyze waste management data with advanced controls.",
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
            
            # Filter container
            create_filter_container(theme, "analytics-filter-container"),
            
            # Filtered data display area
            html.Div(
                id="filtered-data-display",
                children=[
                    html.Div(
                        "📊 Select filters above and click 'Apply Filters' to view data",
                        style={
                            "textAlign": "center",
                            "padding": "3rem",
                            "color": theme["text_secondary"],
                            "fontSize": "1.1rem",
                            "backgroundColor": theme["card_bg"],
                            "borderRadius": "12px",
                            "border": f"2px dashed {theme['accent_bg']}"
                        }
                    )
                ]
            )
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
__all__ = [
    'build_enhanced_dashboard', 
    'create_tab_content', 
    'generate_sample_data',
    'register_dashboard_flask_routes',
    'get_current_theme',
    'create_empty_themed_page',
    'ensure_upload_directory',
    'configure_upload_settings',
    'validate_file_type'
]