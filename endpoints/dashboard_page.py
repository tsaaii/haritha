# endpoints/dashboard_page.py
"""
Dashboard Page Endpoint
Handles /dashboard route with authentication and themed content
"""

from flask import session, redirect
from config.themes import THEMES, get_theme
from utils.page_builder import create_themed_page

def get_current_theme():
    """Get current theme from session or default"""
    return session.get('current_theme', 'dark')

def create_dashboard_content(theme_name="dark"):
    """Create dashboard-specific content"""
    theme = get_theme(theme_name)
    
    # Dashboard-specific features and metrics
    features = [
        {
            "icon": "📊",
            "title": "Real-time Analytics",
            "description": "Live monitoring of waste collection and processing"
        },
        {
            "icon": "🚛",
            "title": "Vehicle Tracking",
            "description": "GPS tracking of all collection vehicles"
        },
        {
            "icon": "📈",
            "title": "Performance Metrics",
            "description": "Efficiency and productivity analytics"
        },
        {
            "icon": "🗺️",
            "title": "Route Optimization",
            "description": "AI-powered route planning and optimization"
        },
        {
            "icon": "🏭",
            "title": "Processing Plants",
            "description": "Status and capacity monitoring"
        },
        {
            "icon": "📱",
            "title": "Citizen Reports",
            "description": "Public feedback and complaint management"
        }
    ]
    
    # Sample dashboard metrics
    metrics = {
        "total_collections": "2,347",
        "active_vehicles": "67",
        "efficiency_score": "94%",
        "waste_processed": "1,256 tonnes",
        "citizen_satisfaction": "4.8/5",
        "cost_savings": "₹12.4 lakhs"
    }
    
    return {
        "features": features,
        "metrics": metrics,
        "description": "Comprehensive waste management dashboard for Andhra Pradesh. Monitor real-time operations, track performance metrics, and optimize collection routes across all districts.",
        "capabilities": [
            "Real-time vehicle tracking and route optimization",
            "Waste processing plant monitoring and capacity management", 
            "Citizen feedback integration and complaint resolution",
            "Performance analytics and efficiency reporting",
            "Cost analysis and budget optimization",
            "Environmental impact assessment and reporting"
        ]
    }

def register_dashboard_routes(server):
    """Register dashboard-specific routes"""
    
    @server.route('/dashboard')
    def dashboard_page():
        """Main Dashboard Page"""
        # Check authentication
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme_name = get_current_theme()
        content = create_dashboard_content(theme_name)
        
        return create_themed_page(
            title="Dashboard",
            icon="📊",
            theme_name=theme_name,
            content=content,
            page_type="dashboard"
        )
    
    @server.route('/dashboard/metrics')
    def dashboard_metrics():
        """Dashboard metrics API endpoint"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        # Return real-time metrics (this would connect to actual data sources)
        import random
        from datetime import datetime
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "collections_today": random.randint(180, 250),
            "active_vehicles": random.randint(45, 75),
            "efficiency_score": random.randint(85, 98),
            "alerts": random.randint(0, 5),
            "citizen_reports": random.randint(12, 28),
            "processing_capacity": random.randint(75, 95)
        }
        
        return metrics