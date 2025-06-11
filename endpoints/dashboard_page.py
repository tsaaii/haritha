# endpoints/dashboard_page.py - SYNTAX FIXED VERSION
"""
Clean Dashboard Page with Only Filter Container - All Syntax Fixed
"""

from flask import session, redirect, jsonify, request
from datetime import datetime, timedelta
import logging
from config.themes import THEMES
from utils.page_builder import create_themed_page

logger = logging.getLogger(__name__)

def get_current_theme():
    """Get current theme from session or default"""
    return session.get('current_theme', 'dark')

def create_dashboard_filter_content(theme_name="dark"):
    """Create dashboard content with only filter container"""
    
    # Get theme from THEMES dict
    theme = THEMES.get(theme_name, THEMES.get('dark', {
        'primary_bg': '#0D1B2A',
        'card_bg': '#1B263B', 
        'accent_bg': '#415A77',
        'text_primary': '#F8F9FA',
        'text_secondary': '#ADB5BD',
        'brand_primary': '#3182CE',
        'border_light': '#495057'
    }))
    
    # Get border color safely
    border_color = theme.get('border_light', theme['accent_bg'])
    
    # Calculate default dates
    start_date_default = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date_default = datetime.now().strftime('%Y-%m-%d')
    
    # Build HTML string safely
    filter_html = '<div id="dashboard-filter-container" style="'
    filter_html += 'background-color: ' + theme['card_bg'] + ';'
    filter_html += 'border: 2px solid ' + border_color + ';'
    filter_html += 'border-radius: 12px;'
    filter_html += 'padding: 1.5rem;'
    filter_html += 'box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);'
    filter_html += '">'
    
    # Header section
    filter_html += '<div style="'
    filter_html += 'margin-bottom: 1.5rem;'
    filter_html += 'text-align: center;'
    filter_html += 'border-bottom: 2px solid ' + theme['accent_bg'] + ';'
    filter_html += 'padding-bottom: 1rem;'
    filter_html += '">'
    filter_html += '<h3 style="'
    filter_html += 'color: ' + theme['text_primary'] + ';'
    filter_html += 'font-size: 1.5rem;'
    filter_html += 'font-weight: 700;'
    filter_html += 'margin: 0 0 0.5rem 0;'
    filter_html += '<p style="'
    filter_html += 'color: ' + theme['text_secondary'] + ';'
    filter_html += 'font-size: 0.9rem;'
    filter_html += 'margin: 0;'
    filter_html += 'line-height: 1.4;'
    filter_html += '">Filter waste collection data by agency, location, and time period</p>'
    filter_html += '</div>'
    
    # Filter grid
    filter_html += '<div style="'
    filter_html += 'display: grid;'
    filter_html += 'grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));'
    filter_html += 'gap: 1.5rem;'
    filter_html += 'margin-bottom: 1.5rem;'
    filter_html += '">'
    
    # Agency filter
    filter_html += '<div>'
    filter_html += '<label style="'
    filter_html += 'color: ' + theme['text_primary'] + ';'
    filter_html += 'font-size: 0.9rem;'
    filter_html += 'font-weight: 600;'
    filter_html += 'margin-bottom: 0.5rem;'
    filter_html += 'display: block;'
    filter_html += '">🏢 Agency</label>'
    filter_html += '<select id="agency-filter" style="'
    filter_html += 'width: 100%;'
    filter_html += 'padding: 0.75rem;'
    filter_html += 'border: 2px solid ' + border_color + ';'
    filter_html += 'border-radius: 8px;'
    filter_html += 'background-color: ' + theme['card_bg'] + ';'
    filter_html += 'color: ' + theme['text_primary'] + ';'
    filter_html += 'font-size: 0.9rem;'
    filter_html += 'cursor: pointer;'
    filter_html += '">'
    filter_html += '<option value="all">All Agencies</option>'
    filter_html += '<option value="zigma">Zigma</option>'
    filter_html += '<option value="green_clean">Green Clean Solutions</option>'
    filter_html += '<option value="ecoserve">EcoServe India</option>'
    filter_html += '<option value="urban_waste">Urban Waste Management</option>'
    filter_html += '<option value="clean_city">Clean City Services</option>'
    filter_html += '</select>'
    filter_html += '</div>'
    
    # Cluster filter
    filter_html += '<div>'
    filter_html += '<label style="'
    filter_html += 'color: ' + theme['text_primary'] + ';'
    filter_html += 'font-size: 0.9rem;'
    filter_html += 'font-weight: 600;'
    filter_html += 'margin-bottom: 0.5rem;'
    filter_html += 'display: block;'
    filter_html += '">🗺️ Cluster</label>'
    filter_html += '<select id="cluster-filter" style="'
    filter_html += 'width: 100%;'
    filter_html += 'padding: 0.75rem;'
    filter_html += 'border: 2px solid ' + border_color + ';'
    filter_html += 'border-radius: 8px;'
    filter_html += 'background-color: ' + theme['card_bg'] + ';'
    filter_html += 'color: ' + theme['text_primary'] + ';'
    filter_html += 'font-size: 0.9rem;'
    filter_html += 'cursor: pointer;'
    filter_html += '">'
    filter_html += '<option value="all">All Clusters</option>'
    filter_html += '<option value="nellore">Nellore Municipal Corporation</option>'
    filter_html += '<option value="chittor">Chittor District</option>'
    filter_html += '<option value="tirupathi">Tirupathi Urban</option>'
    filter_html += '<option value="gvmc">GVMC (Greater Visakhapatnam)</option>'
    filter_html += '<option value="kurnool">Kurnool Municipal</option>'
    filter_html += '<option value="vijayawada">Vijayawada Corporation</option>'
    filter_html += '<option value="guntur">Guntur Municipal</option>'
    filter_html += '</select>'
    filter_html += '</div>'
    
    # Site filter
    filter_html += '<div>'
    filter_html += '<label style="'
    filter_html += 'color: ' + theme['text_primary'] + ';'
    filter_html += 'font-size: 0.9rem;'
    filter_html += 'font-weight: 600;'
    filter_html += 'margin-bottom: 0.5rem;'
    filter_html += 'display: block;'
    filter_html += '">📍 Site</label>'
    filter_html += '<select id="site-filter" style="'
    filter_html += 'width: 100%;'
    filter_html += 'padding: 0.75rem;'
    filter_html += 'border: 2px solid ' + border_color + ';'
    filter_html += 'border-radius: 8px;'
    filter_html += 'background-color: ' + theme['card_bg'] + ';'
    filter_html += 'color: ' + theme['text_primary'] + ';'
    filter_html += 'font-size: 0.9rem;'
    filter_html += 'cursor: pointer;'
    filter_html += '">'
    filter_html += '<option value="all">All Sites</option>'
    filter_html += '<option value="allipuram">Allipuram Collection Point</option>'
    filter_html += '<option value="donthalli">Donthalli Processing Center</option>'
    filter_html += '<option value="kuppam">Kuppam Municipal Yard</option>'
    filter_html += '<option value="palamaner">Palamaner Collection Hub</option>'
    filter_html += '<option value="madanapalle">Madanapalle Transfer Station</option>'
    filter_html += '<option value="tpty">TPTY Central Facility</option>'
    filter_html += '<option value="vizagsac">Vizagsac Processing Plant</option>'
    filter_html += '<option value="anantapur">Anantapur Collection Center</option>'
    filter_html += '</select>'
    filter_html += '</div>'
    
    # Date range filter
    filter_html += '<div>'
    filter_html += '<label style="'
    filter_html += 'color: ' + theme['text_primary'] + ';'
    filter_html += 'font-size: 0.9rem;'
    filter_html += 'font-weight: 600;'
    filter_html += 'margin-bottom: 0.5rem;'
    filter_html += 'display: block;'
    filter_html += '">📅 Date Range</label>'
    filter_html += '<div style="display: flex; gap: 0.5rem;">'
    filter_html += '<input type="date" id="start-date" style="'
    filter_html += 'flex: 1;'
    filter_html += 'padding: 0.75rem;'
    filter_html += 'border: 2px solid ' + border_color + ';'
    filter_html += 'border-radius: 8px;'
    filter_html += 'background-color: ' + theme['card_bg'] + ';'
    filter_html += 'color: ' + theme['text_primary'] + ';'
    filter_html += 'font-size: 0.9rem;'
    filter_html += '" value="' + start_date_default + '">'
    filter_html += '<input type="date" id="end-date" style="'
    filter_html += 'flex: 1;'
    filter_html += 'padding: 0.75rem;'
    filter_html += 'border: 2px solid ' + border_color + ';'
    filter_html += 'border-radius: 8px;'
    filter_html += 'background-color: ' + theme['card_bg'] + ';'
    filter_html += 'color: ' + theme['text_primary'] + ';'
    filter_html += 'font-size: 0.9rem;'
    filter_html += '" value="' + end_date_default + '">'
    filter_html += '</div>'
    filter_html += '</div>'
    
    # Close filter grid
    filter_html += '</div>'
    
    # Action buttons
    filter_html += '<div style="'
    filter_html += 'display: flex;'
    filter_html += 'flex-wrap: wrap;'
    filter_html += 'gap: 1rem;'
    filter_html += 'justify-content: center;'
    filter_html += 'align-items: center;'
    filter_html += 'border-top: 1px solid ' + theme['accent_bg'] + ';'
    filter_html += 'padding-top: 1.5rem;'
    filter_html += '">'
    
    # Apply button
    filter_html += '<button id="apply-filters" style="'
    filter_html += 'background-color: ' + theme['brand_primary'] + ';'
    filter_html += 'color: white;'
    filter_html += 'border: none;'
    filter_html += 'padding: 0.75rem 1.5rem;'
    filter_html += 'border-radius: 8px;'
    filter_html += 'font-size: 0.9rem;'
    filter_html += 'font-weight: 600;'
    filter_html += 'cursor: pointer;'
    filter_html += 'transition: all 0.2s ease;'
    filter_html += 'box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);'
    filter_html += 'min-width: 140px;'
    filter_html += '">🔍 Apply Filters</button>'
    
    # Reset button
    filter_html += '<button id="reset-filters" style="'
    filter_html += 'background-color: ' + theme['accent_bg'] + ';'
    filter_html += 'color: ' + theme['text_primary'] + ';'
    filter_html += 'border: 2px solid ' + border_color + ';'
    filter_html += 'padding: 0.75rem 1.5rem;'
    filter_html += 'border-radius: 8px;'
    filter_html += 'font-size: 0.9rem;'
    filter_html += 'font-weight: 600;'
    filter_html += 'cursor: pointer;'
    filter_html += 'transition: all 0.2s ease;'
    filter_html += 'min-width: 120px;'
    filter_html += '">🔄 Reset</button>'
    
    # Export button
    filter_html += '<button id="export-data" style="'
    filter_html += 'background-color: #38A169;'
    filter_html += 'color: white;'
    filter_html += 'border: none;'
    filter_html += 'padding: 0.75rem 1.5rem;'
    filter_html += 'border-radius: 8px;'
    filter_html += 'font-size: 0.9rem;'
    filter_html += 'font-weight: 600;'
    filter_html += 'cursor: pointer;'
    filter_html += 'transition: all 0.2s ease;'
    filter_html += 'min-width: 140px;'
    filter_html += '">📊 Export Data</button>'
    
    # Close buttons div
    filter_html += '</div>'
    
    # Status div
    filter_html += '<div id="filter-status" style="'
    filter_html += 'margin-top: 1rem;'
    filter_html += 'padding: 0.75rem;'
    filter_html += 'background-color: ' + theme['accent_bg'] + ';'
    filter_html += 'border-radius: 8px;'
    filter_html += 'text-align: center;'
    filter_html += 'font-size: 0.85rem;'
    filter_html += 'color: ' + theme['text_secondary'] + ';'
    filter_html += 'display: none;'
    filter_html += '">Ready to filter dashboard data</div>'
    
    # Results div
    filter_html += '<div id="filter-results" style="'
    filter_html += 'margin-top: 1.5rem;'
    filter_html += 'padding: 1.5rem;'
    filter_html += 'background-color: ' + theme['accent_bg'] + ';'
    filter_html += 'border-radius: 8px;'
    filter_html += 'border: 2px dashed ' + border_color + ';'
    filter_html += 'text-align: center;'
    filter_html += 'display: none;'
    filter_html += '">'
    filter_html += '<h4 style="'
    filter_html += 'color: ' + theme['text_primary'] + ';'
    filter_html += 'margin-bottom: 1rem;'
    filter_html += 'font-size: 1.2rem;'
    filter_html += '">📊 Filter Results</h4>'
    filter_html += '<div id="filter-data" style="'
    filter_html += 'color: ' + theme['text_secondary'] + ';'
    filter_html += 'font-size: 0.9rem;'
    filter_html += '">No filters applied yet</div>'
    filter_html += '</div>'
    
    # Close main container
    filter_html += '</div>'
    
    # Add JavaScript
    filter_html += '''
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var applyBtn = document.getElementById('apply-filters');
        var resetBtn = document.getElementById('reset-filters');
        var exportBtn = document.getElementById('export-data');
        var statusDiv = document.getElementById('filter-status');
        var resultsDiv = document.getElementById('filter-results');
        var filterDataDiv = document.getElementById('filter-data');
        
        if (applyBtn) {
            applyBtn.addEventListener('click', function() {
                var agency = document.getElementById('agency-filter').value;
                var cluster = document.getElementById('cluster-filter').value;
                var site = document.getElementById('site-filter').value;
                var startDate = document.getElementById('start-date').value;
                var endDate = document.getElementById('end-date').value;
                
                statusDiv.style.display = 'block';
                statusDiv.innerHTML = '✅ Filters applied: ' + agency + ' → ' + cluster + ' → ' + site + ' (' + startDate + ' to ' + endDate + ')';
                
                resultsDiv.style.display = 'block';
                filterDataDiv.innerHTML = 
                    '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1rem;">' +
                        '<div><strong>Agency:</strong> ' + agency + '</div>' +
                        '<div><strong>Cluster:</strong> ' + cluster + '</div>' +
                        '<div><strong>Site:</strong> ' + site + '</div>' +
                        '<div><strong>Date Range:</strong> ' + startDate + ' to ' + endDate + '</div>' +
                    '</div>' +
                    '<div style="margin-top: 1rem; padding: 1rem; background-color: rgba(56, 161, 105, 0.1); border-radius: 6px;">' +
                        '<strong>Filter Data Available:</strong><br>' +
                        '• Agency Filter: ' + agency + '<br>' +
                        '• Cluster Filter: ' + cluster + '<br>' +
                        '• Site Filter: ' + site + '<br>' +
                        '• Start Date: ' + startDate + '<br>' +
                        '• End Date: ' + endDate +
                    '</div>';
                
                console.log('Filter Data:', {
                    agency: agency,
                    cluster: cluster,
                    site: site,
                    startDate: startDate,
                    endDate: endDate
                });
            });
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                document.getElementById('agency-filter').value = 'all';
                document.getElementById('cluster-filter').value = 'all';
                document.getElementById('site-filter').value = 'all';
                document.getElementById('start-date').value = ''' + '"' + start_date_default + '"' + ''';
                document.getElementById('end-date').value = ''' + '"' + end_date_default + '"' + ''';
                
                statusDiv.style.display = 'none';
                resultsDiv.style.display = 'none';
                
                console.log('Filters reset to defaults');
            });
        }
        
        if (exportBtn) {
            exportBtn.addEventListener('click', function() {
                var agency = document.getElementById('agency-filter').value;
                var cluster = document.getElementById('cluster-filter').value;
                var site = document.getElementById('site-filter').value;
                var startDate = document.getElementById('start-date').value;
                var endDate = document.getElementById('end-date').value;
                
                var exportData = {
                    agency: agency,
                    cluster: cluster,
                    site: site,
                    startDate: startDate,
                    endDate: endDate,
                    timestamp: new Date().toISOString()
                };
                
                console.log('Export Data:', exportData);
                alert('Filter data logged to console. Check browser console for details.');
            });
        }
    });
    </script>
    
    <style>
    @media (max-width: 768px) {
        #dashboard-filter-container {
            padding: 1rem !important;
        }
        
        #dashboard-filter-container > div:nth-child(2) {
            grid-template-columns: 1fr !important;
            gap: 1rem !important;
        }
        
        #dashboard-filter-container > div:nth-child(3) {
            flex-direction: column !important;
            gap: 0.75rem !important;
        }
        
        #dashboard-filter-container button {
            width: 100% !important;
            min-width: unset !important;
        }
    }
    
    @media (min-width: 769px) and (max-width: 1024px) {
        #dashboard-filter-container > div:nth-child(2) {
            grid-template-columns: repeat(2, 1fr) !important;
        }
    }
    </style>
    '''
    
    # Return content structure expected by page_builder.py
    return {
        "features": [
            {
                "icon": "🔍",
                "title": "Data Filtering",
                "description": "Filter waste collection data by multiple parameters"
            }
        ],
        "metrics": {
            "total_collections": "0",
            "active_vehicles": "0", 
            "efficiency_score": "0%",
            "waste_processed": "0 tonnes",
            "citizen_satisfaction": "0/5",
            "cost_savings": "₹0"
        },
        "description": filter_html,
        "capabilities": [
            "Filter by Agency, Cluster, Site and Date Range",
            "Real-time filter application",
            "Export filtered data",
            "Reset filters to defaults"
        ]
    }

def register_dashboard_routes(server):
    """Register dashboard route with only filter container"""
    
    @server.route('/dashboard')
    def dashboard_page():
        """Dashboard Page with Only Filter Container"""
        # Check authentication
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme_name = get_current_theme()
        content = create_dashboard_filter_content(theme_name)
        
        return create_themed_page(
            title="Dashboard Filters",
            icon="🔍",
            theme_name=theme_name,
            content=content,
            page_type="dashboard"
        )
    
    @server.route('/dashboard/filter-data')
    def get_filter_data():
        """API endpoint to get current filter data"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        # Get filter parameters from request
        agency = request.args.get('agency', 'all')
        cluster = request.args.get('cluster', 'all')
        site = request.args.get('site', 'all')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        filter_data = {
            "agency": agency,
            "cluster": cluster,
            "site": site,
            "start_date": start_date,
            "end_date": end_date,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(filter_data)