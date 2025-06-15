# layouts/admin_dashboard.py - FIXED VERSION WITH MATCHING HTML AND JAVASCRIPT
"""
Enhanced Admin Dashboard Layout for Swaccha Andhra - FIXED ERROR HANDLING
Now properly matches HTML filter elements with JavaScript code
"""

from dash import html, dcc
from datetime import datetime
import random
from flask import session, redirect, request
import os
from pathlib import Path
import pandas as pd
import json
from file_watcher import get_latest_data, get_data_timestamp
from utils.theme_utils import get_theme_styles
from components.navigation.hover_overlay import create_hover_overlay_banner
from components.data.filterable_container import create_filterable_container
from flask import jsonify

def get_current_theme():
    """Get current theme from session or default"""
    return session.get('current_theme', 'dark')





def get_filter_options_from_embedded_data():
    """Extract unique filter options from real CSV data using pandas"""
    try:
        # Load CSV data using pandas
        csv_data = get_embedded_csv_data()
        
        if not csv_data:
            return {
                'agencies': ['No data available'],
                'clusters': ['No data available'], 
                'sites': ['No data available'],
                'suppliers': ['No data available'],
                'materials': ['No data available'],
                'vehicles': ['No data available']
            }
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(csv_data)
        
        # Extract unique values for each filter, handling various column name possibilities
        def get_unique_values(df, possible_columns, default_name):
            """Get unique values from DataFrame for given possible column names"""
            for col in possible_columns:
                if col in df.columns:
                    unique_vals = df[col].dropna().astype(str).str.strip()
                    unique_vals = unique_vals[unique_vals != ''].unique()
                    return sorted(list(unique_vals))
            return [f'No {default_name} data']
        
        # Define possible column names for each filter
        agency_columns = ['agency', 'Agency', 'AGENCY']
        cluster_columns = ['cluster', 'Cluster', 'CLUSTER', 'zone', 'Zone']
        site_columns = ['site', 'Site', 'SITE', 'location', 'Location', 'source_location']
        supplier_columns = ['Supplier Name', 'supplier', 'Supplier', 'SUPPLIER']
        material_columns = ['Material Name', 'material', 'Material', 'MATERIAL']
        vehicle_columns = ['Vehicle No', 'vehicle', 'Vehicle', 'VEHICLE', 'vehicle_no']
        
        # Extract unique values
        agencies = get_unique_values(df, agency_columns, 'agency')
        clusters = get_unique_values(df, cluster_columns, 'cluster')
        sites = get_unique_values(df, site_columns, 'site')
        suppliers = get_unique_values(df, supplier_columns, 'supplier')
        materials = get_unique_values(df, material_columns, 'material')
        vehicles = get_unique_values(df, vehicle_columns, 'vehicle')
        
        options = {
            'agencies': agencies,
            'clusters': clusters,
            'sites': sites,
            'suppliers': suppliers,
            'materials': materials,
            'vehicles': vehicles
        }
        
        print(f"✅ Filter options extracted from {len(csv_data)} CSV records:")
        for key, values in options.items():
            print(f"   {key}: {len(values)} options")
            if len(values) <= 10:
                print(f"      Values: {values}")
            else:
                print(f"      Sample: {values[:5]}... (+{len(values)-5} more)")
        
        return options
        
    except Exception as e:
        print(f"❌ Error extracting filter options: {str(e)}")
        return {
            'agencies': ['Error loading data'],
            'clusters': ['Error loading data'], 
            'sites': ['Error loading data'],
            'suppliers': ['Error loading data'],
            'materials': ['Error loading data'],
            'vehicles': ['Error loading data']
        }

def register_enhanced_csv_routes(server):
    """Register enhanced CSV data routes with full pandas integration"""
    
    @server.route('/api/csv-data-enhanced')
    def get_enhanced_csv_data():
        """Enhanced API endpoint to get CSV data with comprehensive filtering"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        try:
            # Load CSV data using pandas
            csv_data = get_embedded_csv_data()
            
            if not csv_data:
                return flask.jsonify({
                    'error': 'No CSV data available',
                    'message': 'CSV file not found or empty'
                })
            
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(csv_data)
            
            # Get filter parameters
            agency = request.args.get('agency', 'all')
            cluster = request.args.get('cluster', 'all')
            site = request.args.get('site', 'all')
            material = request.args.get('material', 'all')
            vehicle = request.args.get('vehicle', 'all')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            # Apply filters using pandas
            filtered_df = df.copy()
            
            # Agency filter
            if agency != 'all' and 'agency' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['agency'] == agency]
            
            # Cluster filter
            if cluster != 'all' and 'cluster' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['cluster'] == cluster]
            
            # Site filter
            if site != 'all':
                site_cols = ['site', 'Site', 'source_location']
                for col in site_cols:
                    if col in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df[col] == site]
                        break
            
            # Material filter
            if material != 'all':
                material_cols = ['Material Name', 'material', 'Material']
                for col in material_cols:
                    if col in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df[col] == material]
                        break
            
            # Vehicle filter
            if vehicle != 'all':
                vehicle_cols = ['Vehicle No', 'vehicle', 'Vehicle']
                for col in vehicle_cols:
                    if col in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df[col] == vehicle]
                        break
            
            # Date filters
            if start_date or end_date:
                date_cols = ['Date', 'date', 'DATE']
                date_col = None
                for col in date_cols:
                    if col in filtered_df.columns:
                        date_col = col
                        break
                
                if date_col:
                    try:
                        filtered_df[date_col] = pd.to_datetime(filtered_df[date_col])
                        
                        if start_date:
                            start_dt = pd.to_datetime(start_date)
                            filtered_df = filtered_df[filtered_df[date_col] >= start_dt]
                        
                        if end_date:
                            end_dt = pd.to_datetime(end_date)
                            filtered_df = filtered_df[filtered_df[date_col] <= end_dt]
                            
                    except Exception as e:
                        print(f"⚠️ Date filtering error: {e}")
            
            # Calculate statistics
            total_records = len(filtered_df)
            
            # Calculate total weight (try different column names)
            total_weight = 0
            weight_cols = ['Net Weight', 'net_weight', 'weight', 'Weight']
            for col in weight_cols:
                if col in filtered_df.columns:
                    try:
                        total_weight = filtered_df[col].fillna(0).astype(float).sum()
                        break
                    except:
                        continue
            
            # Count unique vehicles
            unique_vehicles = 0
            vehicle_cols = ['Vehicle No', 'vehicle', 'Vehicle']
            for col in vehicle_cols:
                if col in filtered_df.columns:
                    unique_vehicles = filtered_df[col].dropna().nunique()
                    break
            
            # Count unique materials
            unique_materials = 0
            material_cols = ['Material Name', 'material', 'Material']
            for col in material_cols:
                if col in filtered_df.columns:
                    unique_materials = filtered_df[col].dropna().nunique()
                    break
            
            # Convert filtered DataFrame back to records
            filtered_records = filtered_df.to_dict('records')
            
            response_data = {
                'success': True,
                'total_records': total_records,
                'total_weight': f"{total_weight:,.0f} kg",
                'unique_vehicles': unique_vehicles,
                'unique_materials': unique_materials,
                'records': filtered_records[:1000],  # Limit to 1000 records for performance
                'total_available': len(csv_data),
                'filters_applied': {
                    'agency': agency,
                    'cluster': cluster,
                    'site': site,
                    'material': material,
                    'vehicle': vehicle,
                    'start_date': start_date,
                    'end_date': end_date
                },
                'columns_detected': {
                    'date_column': next((col for col in ['Date', 'date', 'DATE'] if col in df.columns), None),
                    'weight_column': next((col for col in weight_cols if col in df.columns), None),
                    'vehicle_column': next((col for col in vehicle_cols if col in df.columns), None),
                    'material_column': next((col for col in material_cols if col in df.columns), None)
                }
            }
            
            print(f"✅ Enhanced CSV API: {total_records} records filtered from {len(csv_data)} total")
            
            return flask.jsonify(response_data)
            
        except Exception as e:
            print(f"❌ Error in enhanced CSV API: {e}")
            return flask.jsonify({
                'error': 'Error processing CSV data',
                'message': str(e)
            }), 500
    
    @server.route('/api/csv-summary')
    def get_csv_summary():
        """Get comprehensive CSV data summary"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        try:
            csv_data = get_embedded_csv_data()
            
            if not csv_data:
                return flask.jsonify({
                    'error': 'No CSV data available'
                })
            
            df = pd.DataFrame(csv_data)
            
            # Basic info
            summary = {
                'total_records': len(df),
                'columns': list(df.columns),
                'column_count': len(df.columns),
                'data_types': df.dtypes.astype(str).to_dict(),
                'null_counts': df.isnull().sum().to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'date_range': {},
                'numeric_columns': []
            }
            
            # Detect date columns and get range
            date_cols = ['Date', 'date', 'DATE']
            for col in date_cols:
                if col in df.columns:
                    try:
                        date_series = pd.to_datetime(df[col], errors='coerce')
                        valid_dates = date_series.dropna()
                        if len(valid_dates) > 0:
                            summary['date_range'] = {
                                'column': col,
                                'min_date': valid_dates.min().isoformat(),
                                'max_date': valid_dates.max().isoformat(),
                                'valid_dates': len(valid_dates),
                                'invalid_dates': len(date_series) - len(valid_dates)
                            }
                            break
                    except:
                        continue
            
            # Detect numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            for col in numeric_cols:
                col_stats = {
                    'column': col,
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'sum': float(df[col].sum()),
                    'count': int(df[col].count())
                }
                summary['numeric_columns'].append(col_stats)
            
            # Sample records
            summary['sample_records'] = df.head(3).to_dict('records')
            
            return flask.jsonify(summary)
            
        except Exception as e:
            print(f"❌ Error getting CSV summary: {e}")
            return flask.jsonify({
                'error': 'Error processing CSV summary',
                'message': str(e)
            }), 500

# Additional utility functions for CSV processing

def validate_csv_structure(csv_path):
    """Validate CSV file structure and return diagnostic info"""
    try:
        # Read first few rows to check structure
        df_sample = pd.read_csv(csv_path, nrows=5)
        
        diagnostics = {
            'file_exists': True,
            'readable': True,
            'columns': list(df_sample.columns),
            'column_count': len(df_sample.columns),
            'sample_row_count': len(df_sample),
            'has_data': len(df_sample) > 0,
            'potential_issues': []
        }
        
        # Check for common issues
        if df_sample.empty:
            diagnostics['potential_issues'].append('File appears to be empty')
        
        if len(df_sample.columns) == 1:
            diagnostics['potential_issues'].append('Only one column detected - check delimiter')
        
        # Check for unnamed columns
        unnamed_cols = [col for col in df_sample.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            diagnostics['potential_issues'].append(f'Unnamed columns detected: {unnamed_cols}')
        
        # Check column names for expected waste management fields
        expected_fields = ['date', 'agency', 'weight', 'vehicle', 'site', 'material']
        detected_fields = []
        
        for expected in expected_fields:
            for col in df_sample.columns:
                if expected.lower() in col.lower():
                    detected_fields.append(col)
                    break
        
        diagnostics['detected_waste_fields'] = detected_fields
        diagnostics['missing_common_fields'] = [
            field for field in expected_fields 
            if not any(field.lower() in col.lower() for col in df_sample.columns)
        ]
        
        return diagnostics
        
    except FileNotFoundError:
        return {
            'file_exists': False,
            'readable': False,
            'error': 'CSV file not found'
        }
    except Exception as e:
        return {
            'file_exists': True,
            'readable': False,
            'error': f'Error reading CSV: {str(e)}'
        }

def optimize_csv_loading(csv_path, max_records=None):
    """Optimized CSV loading with memory management"""
    try:
        # Get file size for memory estimation
        file_size = os.path.getsize(csv_path)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"📁 CSV file size: {file_size_mb:.2f} MB")
        
        # Determine chunk size based on file size
        if file_size_mb > 100:
            chunk_size = 10000
            print(f"⚡ Large file detected - using chunked loading (chunk size: {chunk_size})")
        else:
            chunk_size = None
        
        # Load CSV with optimizations
        load_params = {
            'low_memory': False,
            'na_values': ['', 'NULL', 'null', 'N/A', 'n/a', 'NaN'],
            'keep_default_na': True
        }
        
        if max_records:
            load_params['nrows'] = max_records
            print(f"📊 Limiting to {max_records} records")
        
        if chunk_size:
            # Load in chunks for large files
            chunks = []
            for chunk in pd.read_csv(csv_path, chunksize=chunk_size, **load_params):
                chunks.append(chunk)
                if max_records and sum(len(c) for c in chunks) >= max_records:
                    break
            
            df = pd.concat(chunks, ignore_index=True)
            if max_records:
                df = df.head(max_records)
        else:
            # Load entire file
            df = pd.read_csv(csv_path, **load_params)
        
        # Memory optimization
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to category for memory savings
                if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique values
                    df[col] = df[col].astype('category')
        
        print(f"✅ Optimized loading complete: {len(df)} records, {len(df.columns)} columns")
        print(f"💾 Memory usage: {df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB")
        
        return df.to_dict('records')
        
    except Exception as e:
        print(f"❌ Error in optimized CSV loading: {e}")
        return []


def get_embedded_csv_data():
    """Load CSV data from the data folder using pandas"""
    try:
        # Get the absolute path to the data directory
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        csv_path = os.path.join(data_dir, 'waste_management_data_updated.csv')
        
        print(f"📁 Loading CSV from: {csv_path}")
        
        # Check if file exists
        if not os.path.exists(csv_path):
            print(f"❌ CSV file not found at: {csv_path}")
            return []
        
        # Read the CSV file using pandas
        df = pd.read_csv(csv_path)
        
        print(f"✅ Loaded {len(df)} records from CSV")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Convert DataFrame to dictionary format for JavaScript
        csv_data = df.to_dict('records')
        
        # Print sample record for debugging
        if csv_data:
            print(f"📊 Sample record: {list(csv_data[0].keys())}")
        
        return csv_data
        
    except Exception as e:
        print(f"❌ Error loading CSV data: {str(e)}")
        return []

def csv_to_javascript_string(csv_data):
    """Convert CSV data to JavaScript string format"""
    if not csv_data:
        return ""
    
    # Get headers from first record
    headers = list(csv_data[0].keys())
    
    # Create CSV string
    csv_lines = [','.join(headers)]
    
    for record in csv_data:
        row_values = []
        for header in headers:
            value = record.get(header, '')
            # Handle potential commas in values by wrapping in quotes
            if ',' in str(value):
                row_values.append(f'"{value}"')
            else:
                row_values.append(str(value))
        csv_lines.append(','.join(row_values))
    
    return '\n'.join(csv_lines)


# def create_empty_themed_page(title, icon, theme_name="dark"):
#     """Create an empty themed page template with ROLE-BASED TAB FILTERING"""
#     theme_styles = get_theme_styles(theme_name)
#     theme = theme_styles["theme"]
    
#     user_info = session.get('user_data', {})
#     user_name = user_info.get('name', 'Administrator')
#     user_role = user_info.get('role', 'administrator').replace('_', ' ').title()
    
#     # ✅ GET USER ROLE AND APPLY ACCESS CONTROL
#     user_role_raw = user_info.get('role', 'viewer')
    
#     # ✅ APPLY SAME ACCESS CONTROL AS create_navigation_tabs
#     try:
#         from config.auth import get_tab_permissions
#         allowed_tabs = get_tab_permissions(user_role_raw)
#     except ImportError:
#         # RESTRICTIVE fallback
#         restrictive_permissions = {
#             'viewer': ['dashboard', 'analytics', 'reports'],  # ONLY these 3 tabs
#             'administrator': ['dashboard', 'analytics', 'reports', 'reviews', 'upload'],
#             'super_admin': ['dashboard', 'analytics', 'reports', 'reviews', 'upload', 'forecasting']
#         }
#         allowed_tabs = restrictive_permissions.get(user_role_raw, ['dashboard'])
    
#     # ✅ ALL POSSIBLE TABS
#     all_tabs = [
#         {"id": "dashboard", "href": "/dashboard", "label": "📊 Dashboard", "icon": "📊"},
#         {"id": "analytics", "href": "/data-analytics", "label": "🔍 Data Analytics", "icon": "🔍"},
#         {"id": "reports", "href": "/reports", "label": "📋 Reports", "icon": "📋"},
#         {"id": "reviews", "href": "/reviews", "label": "⭐ Reviews", "icon": "⭐"},
#         {"id": "upload", "href": "/upload", "label": "📤 Upload", "icon": "📤"},
#         {"id": "forecasting", "href": "/forecasting", "label": "🔮 Forecasting", "icon": "🔮"}
#     ]
    
#     # ✅ FILTER TABS BASED ON USER PERMISSIONS
#     visible_tabs = [tab for tab in all_tabs if tab["id"] in allowed_tabs]
    
#     print(f"🔒 HTML PAGE - USER ROLE: {user_role_raw}")
#     print(f"🔒 HTML PAGE - ALLOWED TABS: {allowed_tabs}")
#     print(f"🔒 HTML PAGE - VISIBLE TABS: {[t['id'] for t in visible_tabs]}")
    
#     # ✅ BUILD NAVIGATION BUTTONS ONLY FOR VISIBLE TABS
#     nav_buttons_html = ""
#     for tab in visible_tabs:
#         active_class = "active" if tab["id"].lower() in title.lower() else ""
#         nav_buttons_html += f'''
#             <a href="{tab["href"]}" class="nav-tab {active_class}">
#                 {tab["label"]}
#             </a>
#         '''
    
#     # Load CSV data and get filter options (existing code)
#     csv_data = get_embedded_csv_data()
#     embedded_csv_string = csv_to_javascript_string(csv_data)
#     filter_options = get_filter_options_from_embedded_data()
    
#     return f'''
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <!-- ... existing head content ... -->
#     </head>
#     <body>
#         <div class="page-container">
#             <!-- Navigation Header -->
#             <nav class="navigation-header">
#                 <div class="nav-content">
#                     <div class="nav-tabs">
#                         <div class="nav-buttons">
#                             {nav_buttons_html}
#                         </div>
                        
#                         <div class="user-info">
#                             <img src="/assets/img/default-avatar.png" alt="User Avatar" class="user-avatar">
#                             <div class="user-details">
#                                 <div class="user-name">{user_name}</div>
#                                 <div class="user-role">{user_role}</div>
#                             </div>
#                             <a href="/?logout=true" class="logout-btn">
#                                 🚪 Logout
#                             </a>
#                         </div>
#                     </div>
                    
#                     <div class="theme-switcher">
#                         <!-- ... existing theme switcher ... -->
#                     </div>
#                 </div>
#             </nav>
            
#             <!-- ... rest of the HTML remains the same ... -->
#         </div>
#     </body>
#     </html>
#     '''

def create_empty_themed_page(title, icon, theme_name="dark"):
    """Create an empty themed page template with ROLE-BASED ACCESS CONTROL"""
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    user_info = session.get('user_data', {})
    user_name = user_info.get('name', 'Administrator')
    user_role_display = user_info.get('role', 'administrator').replace('_', ' ').title()
    
    # ✅ GET USER ROLE AND APPLY ACCESS CONTROL
    user_role_raw = user_info.get('role', 'viewer')
    
    # ✅ APPLY ROLE-BASED ACCESS CONTROL
    try:
        from config.auth import get_tab_permissions
        allowed_tabs = get_tab_permissions(user_role_raw)
    except ImportError:
        # RESTRICTIVE fallback
        restrictive_permissions = {
            'viewer': ['dashboard', 'analytics', 'reports'],  # ONLY these 3 tabs
            'administrator': ['dashboard', 'analytics', 'reports', 'reviews', 'upload'],
            'super_admin': ['dashboard', 'analytics', 'reports', 'reviews', 'upload', 'forecasting']
        }
        allowed_tabs = restrictive_permissions.get(user_role_raw, ['dashboard'])
    
    # ✅ ALL POSSIBLE TABS
    all_tabs = [
        {"id": "dashboard", "href": "/dashboard", "label": "📊 Dashboard", "active_check": "dashboard"},
        {"id": "analytics", "href": "/data-analytics", "label": "🔍 Data Analytics", "active_check": "data analytics"},
        {"id": "reports", "href": "/reports", "label": "📋 Reports", "active_check": "reports"},
        {"id": "reviews", "href": "/reviews", "label": "⭐ Reviews", "active_check": "reviews"},
        {"id": "upload", "href": "/upload", "label": "📤 Upload", "active_check": "upload"},
        {"id": "forecasting", "href": "/forecasting", "label": "🔮 Forecasting", "active_check": "forecasting"}
    ]
    
    # ✅ FILTER TABS BASED ON USER PERMISSIONS
    visible_tabs = [tab for tab in all_tabs if tab["id"] in allowed_tabs]
    
    print(f"🔒 HTML PAGE - USER ROLE: {user_role_raw}")
    print(f"🔒 HTML PAGE - ALLOWED TABS: {allowed_tabs}")
    print(f"🔒 HTML PAGE - VISIBLE TABS: {[t['id'] for t in visible_tabs]}")
    
    # ✅ BUILD NAVIGATION BUTTONS ONLY FOR VISIBLE TABS
    nav_buttons_html = ""
    for tab in visible_tabs:
        active_class = "active" if tab["active_check"] in title.lower() else ""
        nav_buttons_html += f'''
            <a href="{tab["href"]}" class="nav-tab {active_class}">
                {tab["label"]}
            </a>
        '''
    
    # ✅ LOAD REAL CSV DATA USING PANDAS
    csv_data = get_embedded_csv_data()
    
    # ✅ CONVERT TO JAVASCRIPT STRING
    embedded_csv_string = csv_to_javascript_string(csv_data)
    
    # Get real filter options from actual CSV data
    filter_options = get_filter_options_from_embedded_data()
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Swaccha Andhra Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary-bg: {theme["primary_bg"]};
                --secondary-bg: {theme["secondary_bg"]};
                --accent-bg: {theme["accent_bg"]};
                --card-bg: {theme["card_bg"]};
                --text-primary: {theme["text_primary"]};
                --text-secondary: {theme["text_secondary"]};
                --brand-primary: {theme["brand_primary"]};
                --border-light: {theme.get("border_light", theme["accent_bg"])};
                --error: {theme.get("error", "#E53E3E")};
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background-color: var(--primary-bg);
                color: var(--text-primary);
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
                background: linear-gradient(135deg, var(--secondary-bg) 0%, var(--accent-bg) 100%);
                border-bottom: 3px solid var(--brand-primary);
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
            
            .nav-tabs {{
                display: flex;
                align-items: center;
                gap: 1rem;
                flex-wrap: wrap;
                flex: 1;
                justify-content: space-between;
            }}
            
            .nav-buttons {{
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
                align-items: center;
            }}
            
            .nav-tab {{
                background: var(--accent-bg);
                color: var(--text-primary);
                border: 2px solid var(--card-bg);
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
                background: var(--brand-primary);
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }}
            
            .nav-tab.active {{
                background: var(--brand-primary);
                color: white;
                border-color: var(--brand-primary);
                box-shadow: 0 4px 12px rgba(49, 130, 206, 0.4);
            }}
            
            .user-info {{
                display: flex;
                align-items: center;
                gap: 1rem;
                background: var(--card-bg);
                padding: 0.5rem 1rem;
                border-radius: 8px;
                border: 2px solid var(--accent-bg);
                min-height: 44px;
                flex-shrink: 0;
            }}
            
            .user-avatar {{
                width: 32px;
                height: 32px;
                border-radius: 50%;
                border: 2px solid var(--brand-primary);
                object-fit: cover;
            }}
            
            .user-details {{
                display: flex;
                flex-direction: column;
            }}
            
            .user-name {{
                font-weight: 600;
                font-size: 0.9rem;
                color: var(--text-primary);
                line-height: 1.2;
            }}
            
            .user-role {{
                font-size: 0.75rem;
                color: var(--text-secondary);
                line-height: 1.2;
            }}
            
            .logout-btn {{
                background: var(--error);
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
            
            .theme-switcher {{
                display: flex;
                align-items: center;
                gap: 0.25rem;
                background: var(--card-bg);
                border: 2px solid var(--accent-bg);
                border-radius: 8px;
                padding: 0.25rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
                min-height: 44px;
            }}
            
            .theme-btn {{
                background: transparent;
                border: 1px solid var(--border-light);
                color: var(--text-primary);
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
                background: var(--brand-primary);
                color: white;
                transform: scale(1.1);
            }}
            
            .theme-btn.active {{
                background: var(--brand-primary);
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
                color: var(--text-primary);
                margin-bottom: 0.5rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                line-height: 1.1;
            }}
            
            .page-subtitle {{
                font-size: 1.2rem;
                color: var(--text-secondary);
                line-height: 1.5;
                max-width: 600px;
                margin: 0 auto;
            }}
            
            /* Enhanced Filter Container */
            .filter-container {{
                background-color: var(--card-bg);
                border-radius: 16px;
                padding: 2rem;
                margin: 0;
                width: 100%;
                max-width: 100%;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                border: 1px solid var(--border-light);
            }}
            
            .filter-header {{
                margin-bottom: 2rem;
                text-align: center;
                border-bottom: 2px solid var(--accent-bg);
                padding-bottom: 1.5rem;
            }}
            
            .filter-header h3 {{
                color: var(--text-primary);
                font-size: 2rem;
                font-weight: 700;
                margin: 0 0 1rem 0;
                letter-spacing: -0.5px;
            }}
            
            .filter-header p {{
                color: var(--text-secondary);
                font-size: 1.1rem;
                margin: 0;
                line-height: 1.5;
                max-width: 800px;
                margin: 0 auto;
            }}
            
            .filter-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 1.5rem;
                margin-bottom: 2rem;
                width: 100%;
            }}
            
            .filter-item {{
                width: 100%;
            }}
            
            .filter-item label {{
                color: var(--text-primary);
                font-size: 1.1rem;
                font-weight: 600;
                margin-bottom: 0.75rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            
            .filter-item select, 
            .filter-item input {{
                width: 100%;
                padding: 1rem;
                border: 2px solid var(--border-light);
                border-radius: 12px;
                background-color: var(--card-bg);
                color: var(--text-primary);
                font-size: 1.1rem;
                font-weight: 500;
                outline: none;
                transition: all 0.2s ease;
                cursor: pointer;
            }}
            
            .filter-item select:hover,
            .filter-item input:hover {{
                border-color: var(--brand-primary);
                box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
            }}
            
            .filter-item select:focus,
            .filter-item input:focus {{
                border-color: var(--brand-primary);
                box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.2);
            }}
            
            .date-range {{
                display: flex;
                gap: 1rem;
            }}
            
            .date-range input {{
                flex: 1;
            }}
            
            .filter-actions {{
                display: flex;
                justify-content: center;
                gap: 1.5rem;
                border-top: 2px solid var(--accent-bg);
                padding-top: 2rem;
                flex-wrap: wrap;
            }}
            
            .filter-btn {{
                border: none;
                padding: 1rem 2rem;
                border-radius: 12px;
                font-size: 1.2rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                min-width: 200px;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
            
            .filter-btn.primary {{
                background-color: var(--brand-primary);
                color: white;
            }}
            
            .filter-btn.primary:hover {{
                background-color: #2C5AA0;
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(49, 130, 206, 0.3);
            }}
            
            .filter-btn.secondary {{
                background-color: var(--accent-bg);
                color: var(--text-primary);
                border: 2px solid var(--border-light);
            }}
            
            .filter-btn.secondary:hover {{
                background-color: var(--brand-primary);
                color: white;
                transform: translateY(-2px);
            }}
            
            /* Data Display */
            .data-display {{
                margin-top: 2rem;
                background-color: var(--card-bg);
                border-radius: 16px;
                padding: 2rem;
                width: 100%;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                border: 1px solid var(--border-light);
            }}
            
            .data-header {{
                margin-bottom: 2rem;
                text-align: center;
                border-bottom: 2px solid var(--accent-bg);
                padding-bottom: 1.5rem;
            }}
            
            .data-header h3 {{
                color: var(--text-primary);
                font-size: 2rem;
                font-weight: 700;
                margin: 0 0 1rem 0;
                letter-spacing: -0.5px;
            }}
            
            .data-header p {{
                color: var(--text-secondary);
                font-size: 1.1rem;
                margin: 0;
                line-height: 1.5;
            }}
            
            .data-stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }}
            
            .stat-card {{
                background: var(--accent-bg);
                border-radius: 16px;
                padding: 2rem 1.5rem;
                text-align: center;
                border: 2px solid transparent;
                cursor: pointer;
                position: relative;
                overflow: hidden;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                transform: translateY(0);
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            }}
            
            .stat-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
                transition: left 0.6s;
            }}
            
            .stat-card:hover {{
                transform: translateY(-8px) scale(1.02);
                border-color: var(--brand-primary);
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2), 0 0 0 1px var(--brand-primary);
                background: linear-gradient(135deg, var(--accent-bg) 0%, var(--card-bg) 100%);
            }}
            
            .stat-card:hover::before {{
                left: 100%;
            }}
            
            .stat-card:active {{
                transform: translateY(-4px) scale(1.01);
                transition: all 0.1s ease;
            }}
            
            .stat-card .icon {{
                font-size: 2.5rem;
                margin-bottom: 1rem;
                display: block;
                transition: all 0.3s ease;
                filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
            }}
            
            .stat-card:hover .icon {{
                font-size: 3rem;
                transform: rotateY(360deg);
                filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
            }}
            
            .stat-card .label {{
                font-size: 0.9rem;
                color: var(--text-secondary);
                margin-bottom: 0.75rem;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                transition: color 0.3s ease;
            }}
            
            .stat-card:hover .label {{
                color: var(--brand-primary);
            }}
            
            .stat-card .value {{
                font-size: 2rem;
                font-weight: 900;
                color: var(--brand-primary);
                transition: all 0.3s ease;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                position: relative;
            }}
            
            .stat-card:hover .value {{
                font-size: 2.2rem;
                text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                color: var(--text-primary);
            }}
            
            /* Data Table Styles */
            .data-table-container {{
                overflow-x: auto;
                margin-top: 1rem;
                border-radius: 12px;
                border: 1px solid var(--border-light);
            }}
            
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 0.95rem;
            }}
            
            .data-table thead {{
                background-color: var(--accent-bg);
                color: var(--text-primary);
            }}
            
            .data-table th,
            .data-table td {{
                padding: 1rem;
                text-align: left;
                border-bottom: 1px solid var(--border-light);
            }}
            
            .data-table th {{
                font-weight: 600;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .data-table tbody tr:hover {{
                background-color: var(--accent-bg);
            }}
            
            .loading-state {{
                text-align: center;
                padding: 3rem;
                color: var(--text-secondary);
                font-size: 1.1rem;
            }}
            
            .loading-state .spinner {{
                display: inline-block;
                width: 40px;
                height: 40px;
                border: 3px solid var(--accent-bg);
                border-radius: 50%;
                border-top-color: var(--brand-primary);
                animation: spin 1s ease-in-out infinite;
                margin-bottom: 1rem;
            }}
            
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            .no-data {{
                text-align: center;
                padding: 3rem;
                color: var(--text-secondary);
                font-size: 1.1rem;
            }}
            
            .error-state {{
                text-align: center;
                padding: 3rem;
                color: var(--error);
                font-size: 1.1rem;
                background: rgba(229, 62, 62, 0.1);
                border-radius: 12px;
                border: 1px solid var(--error);
            }}
            
            /* Footer */
            .footer {{
                background: var(--secondary-bg);
                border-top: 2px solid var(--card-bg);
                padding: 1rem 2rem;
                text-align: center;
                color: var(--text-secondary);
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
                
                .filter-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .filter-actions {{
                    flex-direction: column;
                    align-items: center;
                }}
                
                .filter-btn {{
                    width: 100%;
                    max-width: 300px;
                }}
                
                .date-range {{
                    flex-direction: column;
                    gap: 1rem;
                }}
                
                .data-stats {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="page-container">
            <!-- Navigation Header -->
            <nav class="navigation-header">
                <div class="nav-content">
                    <div class="nav-tabs">
                        <div class="nav-buttons">
                            {nav_buttons_html}
                        </div>
                        
                        <div class="user-info">
                            <img src="/assets/img/default-avatar.png" alt="User Avatar" class="user-avatar">
                            <div class="user-details">
                                <div class="user-name">{user_name}</div>
                                <div class="user-role">{user_role_display}</div>
                            </div>
                            <a href="/?logout=true" class="logout-btn">
                                🚪 Logout
                            </a>
                        </div>
                    </div>
                    
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
                <!-- Filter Container -->
                <div class="filter-container">
                    <div class="filter-header">
                        <h3>🔍 Advanced Data Filters</h3>
                    </div>

                    <div class="filter-grid">
                        <!-- Agency Filter -->
                        <div class="filter-item">
                            <label><span>🏢</span> Agency</label>
                            <select id="agency-filter">
                                <option value="all">All Agencies</option>
                                {"".join([f'<option value="{agency}">{agency}</option>' for agency in filter_options['agencies']])}
                            </select>
                        </div>

                        <!-- Cluster Filter -->
                        <div class="filter-item">
                            <label><span>🗺️</span> Cluster</label>
                            <select id="cluster-filter">
                                <option value="all">All Clusters</option>
                                {"".join([f'<option value="{cluster}">{cluster}</option>' for cluster in filter_options['clusters']])}
                            </select>
                        </div>

                        <!-- Site Filter -->
                        <div class="filter-item">
                            <label><span>📍</span> Site</label>
                            <select id="site-filter">
                                <option value="all">All Sites</option>
                                {"".join([f'<option value="{site}">{site}</option>' for site in filter_options['sites']])}
                            </select>
                        </div>

                        <!-- Date Range Filter -->
                        <div class="filter-item">
                            <label><span>📅</span> Date Range</label>
                            <div class="date-range">
                                <input type="date" id="start-date" placeholder="Start Date">
                                <input type="date" id="end-date" placeholder="End Date">
                            </div>
                        </div>
                    </div>

                    <!-- Filter Actions -->
                    <div class="filter-actions">
                        <button id="apply-filters" class="filter-btn primary">
                            <span>🔍</span>
                            Apply Filters
                        </button>
                        <button id="reset-filters" class="filter-btn secondary">
                            <span>🔄</span>
                            Reset Filters
                        </button>
                        <button id="export-data" class="filter-btn secondary">
                            <span>📊</span>
                            Export Data
                        </button>
                    </div>
                </div>
                
                <!-- Filtered Data Display -->
                <div id="filtered-data" class="data-display">
                    <div class="data-header">
                        <h3>📊 Filtered Results</h3>
                    </div>

                    <!-- Interactive Data Statistics -->
                    <div id="data-stats" class="data-stats">
                        <div class="stat-card records-card" onclick="showRecordsDetail()">
                            <span class="icon">📊</span>
                            <div class="label">Total Records</div>
                            <div class="value" id="total-records">-</div>
                        </div>
                        <div class="stat-card weight-card" onclick="showWeightDetail()">
                            <span class="icon">⚖️</span>
                            <div class="label">Total Weight</div>
                            <div class="value" id="total-weight">-</div>
                        </div>
                        <div class="stat-card vehicles-card" onclick="showVehiclesDetail()">
                            <span class="icon">🚛</span>
                            <div class="label">Unique Vehicles</div>
                            <div class="value" id="unique-vehicles">-</div>
                        </div>
                        <div class="stat-card materials-card" onclick="showMaterialsDetail()">
                            <span class="icon">♻️</span>
                            <div class="label">Material Types</div>
                            <div class="value" id="material-types">-</div>
                        </div>
                    </div>

                    <!-- Data Table -->
                    <div id="data-table-container" class="data-table-container">
                        <table id="data-table" class="data-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Agency</th>
                                    <th>Cluster</th>
                                    <th>Site</th>
                                    <th>Vehicle No</th>
                                    <th>Material</th>
                                    <th>Net Weight (kg)</th>
                                    <th>Supplier</th>
                                    <th>Ticket No</th>
                                </tr>
                            </thead>
                            <tbody id="data-table-body">
                                <tr>
                                    <td colspan="9" class="loading-state">
                                        <div class="spinner"></div>
                                        <div>Loading {len(csv_data)} records from CSV...</div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <script>
                    // ✅ REAL CSV DATA FROM PANDAS DATAFRAME
                    const embeddedCSVData = `{embedded_csv_string}`;
                    
                    console.log('📊 Real CSV Data loaded:', embeddedCSVData.split('\\n').length - 1, 'records');

                    // Global variables
                    let wasteData = null;
                    let filteredData = null;
                    
                    // Safe element access function
                    function safeGetElement(id) {{
                        const element = document.getElementById(id);
                        if (!element) {{
                            console.warn(`⚠️ Element not found: ${{id}}`);
                        }}
                        return element;
                    }}
                    
                    // Safe get value function
                    function safeGetValue(id, defaultValue = 'all') {{
                        const element = safeGetElement(id);
                        return element ? element.value : defaultValue;
                    }}
                    
                    // Load CSV data using Papa Parse
                    function loadWasteData() {{
                        try {{
                            console.log('🔄 Loading real CSV waste management data...');
                            
                            // Parse CSV using Papa Parse
                            const results = Papa.parse(embeddedCSVData, {{
                                header: true,
                                skipEmptyLines: true,
                                dynamicTyping: true,
                                transformHeader: (header) => header.trim(),
                                transform: (value, field) => {{
                                    if (typeof value === 'string') {{
                                        return value.trim();
                                    }}
                                    return value;
                                }}
                            }});
                            
                            if (results.errors.length > 0) {{
                                console.warn('⚠️ CSV parsing warnings:', results.errors);
                            }}
                            
                            wasteData = results.data.filter(row => {{
                                // Filter out completely empty rows
                                return Object.values(row).some(value => 
                                    value !== null && value !== undefined && value !== ''
                                );
                            }});
                            
                            console.log(`✅ Loaded ${{wasteData.length}} records from real CSV data`);
                            console.log('📋 Sample record:', wasteData[0]);
                            console.log('📋 Available columns:', Object.keys(wasteData[0] || {{}}));
                            
                            // Initialize filters and display
                            populateFilterOptions();
                            applyFilters();
                            
                        }} catch (error) {{
                            console.error('❌ Error loading CSV data:', error);
                            showError(`Error loading data: ${{error.message}}`);
                        }}
                    }}

                    // Populate filter options from real CSV data
                    function populateFilterOptions() {{
                        if (!wasteData || wasteData.length === 0) {{
                            console.warn('⚠️ No data available for filters');
                            return;
                        }}

                        console.log('🔧 Populating filter options from real CSV data...');
                        
                        // Agency filter
                        updateFilterOptions('agency-filter', wasteData, 'agency');
                        
                        // Cluster filter
                        updateFilterOptions('cluster-filter', wasteData, 'cluster');
                        
                        // Site filter
                        updateFilterOptions('site-filter', wasteData, 'site');
                        
                        console.log('✅ Filter options populated from real CSV data');
                    }}

                    // Helper function to update filter options
                    function updateFilterOptions(selectId, data, column, limit = null) {{
                        const select = safeGetElement(selectId);
                        if (!select || !data || !column) {{
                            console.warn(`⚠️ Cannot update filter options for ${{selectId}}`);
                            return;
                        }}
                        
                        // Get unique values, filtering out nulls and empty strings
                        const uniqueValues = [...new Set(
                            data.map(row => row[column])
                                .filter(value => value !== null && value !== undefined && value !== '')
                                .map(value => String(value).trim())
                        )].sort();
                        
                        // Apply limit if specified
                        const valuesToShow = limit ? uniqueValues.slice(0, limit) : uniqueValues;
                        
                        // Keep the "All" option and add new options
                        const allOption = select.querySelector('option[value="all"]');
                        select.innerHTML = '';
                        if (allOption) {{
                            select.appendChild(allOption);
                        }} else {{
                            // Create "All" option if it doesn't exist
                            const newAllOption = document.createElement('option');
                            newAllOption.value = 'all';
                            newAllOption.textContent = `All ${{column}}s`;
                            select.appendChild(newAllOption);
                        }}
                        
                        valuesToShow.forEach(value => {{
                            const option = document.createElement('option');
                            option.value = value;
                            option.textContent = value;
                            select.appendChild(option);
                        }});
                        
                        console.log(`📋 ${{selectId}}: ${{valuesToShow.length}} options - ${{valuesToShow.slice(0, 5).join(', ')}}${{valuesToShow.length > 5 ? '...' : ''}}`);
                    }}

                    // Apply filters to real CSV data
                    function applyFilters() {{
                        if (!wasteData || wasteData.length === 0) {{
                            showError('No CSV data available to filter');
                            return;
                        }}

                        console.log('🔍 Applying filters to real CSV data...');
                        
                        // Get filter values
                        const filters = {{
                            agency: safeGetValue('agency-filter'),
                            cluster: safeGetValue('cluster-filter'),
                            site: safeGetValue('site-filter'),
                            startDate: safeGetValue('start-date', ''),
                            endDate: safeGetValue('end-date', '')
                        }};
                        
                        console.log('🔧 Filter values:', filters);
                        
                        // Apply filters using exact column names from CSV data
                        filteredData = wasteData.filter(row => {{
                            // Agency filter
                            if (filters.agency !== 'all' && row.agency !== filters.agency) {{
                                return false;
                            }}
                            
                            // Cluster filter
                            if (filters.cluster !== 'all' && row.cluster !== filters.cluster) {{
                                return false;
                            }}
                            
                            // Site filter
                            if (filters.site !== 'all' && row.site !== filters.site) {{
                                return false;
                            }}
                            
                            // Date filters
                            if (filters.startDate || filters.endDate) {{
                                const rowDate = new Date(row.Date);
                                if (isNaN(rowDate.getTime())) {{
                                    return false; // Skip invalid dates
                                }}
                                
                                if (filters.startDate && rowDate < new Date(filters.startDate)) {{
                                    return false;
                                }}
                                
                                if (filters.endDate && rowDate > new Date(filters.endDate)) {{
                                    return false;
                                }}
                            }}
                            
                            return true;
                        }});
                        
                        console.log(`✅ Filtered: ${{filteredData.length}} records from ${{wasteData.length}} total CSV records`);
                        
                        // Update display
                        updateDataDisplay();
                    }}

                    // Update the data display with filtered results
                    function updateDataDisplay() {{
                        if (!filteredData) {{
                            showError('No filtered data to display');
                            return;
                        }}
                        
                        // Update statistics
                        updateStatistics();
                        
                        // Update data table
                        updateDataTable();
                    }}

                    // Update statistics
                    function updateStatistics() {{
                        const totalRecords = filteredData.length;
                        
                        // Calculate total weight using 'Net Weight' column
                        const totalWeight = filteredData.reduce((sum, row) => {{
                            const weight = row['Net Weight'] || 0;
                            return sum + (parseFloat(weight) || 0);
                        }}, 0);
                        
                        // Count unique vehicles
                        const uniqueVehicles = new Set(
                            filteredData.map(row => row['Vehicle No'])
                                .filter(v => v !== null && v !== undefined && v !== '')
                        ).size;
                        
                        // Count unique materials
                        const uniqueMaterials = new Set(
                            filteredData.map(row => row['Material Name'])
                                .filter(m => m !== null && m !== undefined && m !== '')
                        ).size;
                        
                        // Update stat cards
                        const totalRecordsEl = safeGetElement('total-records');
                        const totalWeightEl = safeGetElement('total-weight');
                        const uniqueVehiclesEl = safeGetElement('unique-vehicles');
                        const materialTypesEl = safeGetElement('material-types');
                        
                        if (totalRecordsEl) totalRecordsEl.textContent = totalRecords.toLocaleString();
                        if (totalWeightEl) totalWeightEl.textContent = `${{totalWeight.toLocaleString()}} kg`;
                        if (uniqueVehiclesEl) uniqueVehiclesEl.textContent = uniqueVehicles;
                        if (materialTypesEl) materialTypesEl.textContent = uniqueMaterials;
                        
                        console.log('📊 Statistics updated:', {{ totalRecords, totalWeight, uniqueVehicles, uniqueMaterials }});
                    }}

                    // Update data table
                    function updateDataTable() {{
                        const tbody = safeGetElement('data-table-body');
                        if (!tbody) {{
                            console.error('❌ Cannot find data table body element');
                            return;
                        }}
                        
                        tbody.innerHTML = '';
                        
                        if (filteredData.length === 0) {{
                            tbody.innerHTML = `
                                <tr>
                                    <td colspan="9" class="no-data">
                                        <div>📭 No records match the selected filters</div>
                                        <div style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.7;">
                                            Available data from CSV: ${{wasteData.length}} total records
                                        </div>
                                    </td>
                                </tr>
                            `;
                            return;
                        }}
                        
                        // Display up to 100 records for performance
                        const recordsToShow = filteredData.slice(0, 100);
                        
                        recordsToShow.forEach((row, index) => {{
                            const tr = document.createElement('tr');
                            
                            // Format date
                            const date = row.Date ? new Date(row.Date).toLocaleDateString() : '-';
                            
                            tr.innerHTML = `
                                <td>${{date}}</td>
                                <td>${{row.agency || '-'}}</td>
                                <td>${{row.cluster || '-'}}</td>
                                <td>${{row.site || '-'}}</td>
                                <td>${{row['Vehicle No'] || '-'}}</td>
                                <td>${{row['Material Name'] || '-'}}</td>
                                <td>${{(row['Net Weight'] || 0).toLocaleString()}}</td>
                                <td>${{row['Supplier Name'] || '-'}}</td>
                                <td>${{row['Ticket No'] || '-'}}</td>
                            `;
                            
                            tbody.appendChild(tr);
                        }});
                        
                        // Add note if showing limited records
                        if (filteredData.length > 100) {{
                            const tr = document.createElement('tr');
                            tr.innerHTML = `
                                <td colspan="9" style="text-align: center; font-style: italic; color: var(--text-secondary); padding: 1rem;">
                                    Showing first 100 of ${{filteredData.length}} filtered records
                                </td>
                            `;
                            tbody.appendChild(tr);
                        }}
                        
                        console.log(`📋 Table updated with ${{recordsToShow.length}} records (from ${{filteredData.length}} filtered)`);
                    }}

                    // Reset filters
                    function resetFilters() {{
                        console.log('🔄 Resetting filters...');
                        
                        const agencyFilter = safeGetElement('agency-filter');
                        const clusterFilter = safeGetElement('cluster-filter');
                        const siteFilter = safeGetElement('site-filter');
                        const startDate = safeGetElement('start-date');
                        const endDate = safeGetElement('end-date');
                        
                        if (agencyFilter) agencyFilter.value = 'all';
                        if (clusterFilter) clusterFilter.value = 'all';
                        if (siteFilter) siteFilter.value = 'all';
                        if (startDate) startDate.value = '';
                        if (endDate) endDate.value = '';
                        
                        applyFilters();
                    }}

                    // Export filtered data
                    function exportData() {{
                        if (!filteredData || filteredData.length === 0) {{
                            alert('No data to export. Please apply filters first.');
                            return;
                        }}
                        
                        console.log('📊 Exporting filtered CSV data...');
                        
                        // Create CSV content using exact column names
                        const headers = ['Date', 'agency', 'cluster', 'site', 'Vehicle No', 'Material Name', 'Net Weight', 'Supplier Name', 'Ticket No'];
                        const csvContent = [
                            headers.join(','),
                            ...filteredData.map(row => [
                                row.Date || '',
                                row.agency || '',
                                row.cluster || '',
                                row.site || '',
                                row['Vehicle No'] || '',
                                row['Material Name'] || '',
                                row['Net Weight'] || '',
                                row['Supplier Name'] || '',
                                row['Ticket No'] || ''
                            ].map(field => `"${{String(field).replace(/"/g, '""')}}"`).join(','))
                        ].join('\\n');
                        
                        // Download file
                        const blob = new Blob([csvContent], {{ type: 'text/csv' }});
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.style.display = 'none';
                        a.href = url;
                        a.download = `filtered_waste_data_${{new Date().toISOString().split('T')[0]}}.csv`;
                        
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                        
                        console.log('✅ CSV data exported successfully');
                    }}

                    // Show error message
                    function showError(message) {{
                        const tbody = safeGetElement('data-table-body');
                        if (tbody) {{
                            tbody.innerHTML = `
                                <tr>
                                    <td colspan="9" class="error-state">
                                        <div>❌ Error: ${{message}}</div>
                                        <div style="font-size: 0.9rem; margin-top: 0.5rem;">
                                            Please check the console for more details
                                        </div>
                                    </td>
                                </tr>
                            `;
                        }}
                        
                        // Reset statistics
                        const totalRecordsEl = safeGetElement('total-records');
                        const totalWeightEl = safeGetElement('total-weight');
                        const uniqueVehiclesEl = safeGetElement('unique-vehicles');
                        const materialTypesEl = safeGetElement('material-types');
                        
                        if (totalRecordsEl) totalRecordsEl.textContent = '-';
                        if (totalWeightEl) totalWeightEl.textContent = '-';
                        if (uniqueVehiclesEl) uniqueVehiclesEl.textContent = '-';
                        if (materialTypesEl) materialTypesEl.textContent = '-';
                    }}

                    // Event Listeners
                    document.addEventListener('DOMContentLoaded', function() {{
                        console.log('🚀 Initializing dashboard with real CSV data...');
                        
                        // Load CSV data on page load
                        loadWasteData();
                        
                        // Filter event listeners
                        const applyBtn = safeGetElement('apply-filters');
                        const resetBtn = safeGetElement('reset-filters');
                        const exportBtn = safeGetElement('export-data');
                        
                        if (applyBtn) applyBtn.addEventListener('click', applyFilters);
                        if (resetBtn) resetBtn.addEventListener('click', resetFilters);
                        if (exportBtn) exportBtn.addEventListener('click', exportData);
                        
                        // Auto-apply filters when dropdowns change
                        const filterSelects = [
                            'agency-filter', 'cluster-filter', 'site-filter'
                        ];
                        
                        filterSelects.forEach(selectId => {{
                            const select = safeGetElement(selectId);
                            if (select) {{
                                select.addEventListener('change', applyFilters);
                            }}
                        }});
                        
                        // Auto-apply filters when date inputs change
                        const startDate = safeGetElement('start-date');
                        const endDate = safeGetElement('end-date');
                        
                        if (startDate) startDate.addEventListener('change', applyFilters);
                        if (endDate) endDate.addEventListener('change', applyFilters);
                        
                        console.log('✅ Event listeners registered for real CSV data');
                    }});

                    // Placeholder functions for stat card interactions
                    function showRecordsDetail() {{
                        console.log('📊 Records detail clicked');
                    }}
                    
                    function showWeightDetail() {{
                        console.log('⚖️ Weight detail clicked');
                    }}
                    
                    function showVehiclesDetail() {{
                        console.log('🚛 Vehicles detail clicked');
                    }}
                    
                    function showMaterialsDetail() {{
                        console.log('♻️ Materials detail clicked');
                    }}
                </script>
                
                <!-- Papa Parse Library for CSV parsing -->
                <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
            </main>
            
            <!-- Footer -->
            <footer class="footer">
                <p>© 2025 Swaccha Andhra Corporation • {title} Section • Connected to Real CSV Data ({len(csv_data)} records) • <span id="current-time"></span></p>
            </footer>
        </div>
        
        <script>
            // Update current time
            function updateTime() {{
                const now = new Date();
                const timeEl = document.getElementById('current-time');
                if (timeEl) {{
                    timeEl.textContent = now.toLocaleString();
                }}
            }}
            updateTime();
            setInterval(updateTime, 1000);
            
            // Theme switching
            function changeTheme(themeName) {{
                fetch('/api/set-theme', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ theme: themeName }})
                }}).then(() => {{
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
    Register ALL dashboard page routes with ROLE-BASED ACCESS CONTROL
    This replaces the individual endpoint files to avoid conflicts
    """
    
    def check_tab_access(required_tab):
        """Helper function to check if user can access a specific tab"""
        if not session.get('swaccha_session_id'):
            return False, redirect('/login')
        
        user_data = session.get('user_data', {})
        user_role = user_data.get('role', 'viewer')
        
        # Apply same access control as Dash callbacks
        try:
            from config.auth import can_user_access_tab
            if not can_user_access_tab(user_role, required_tab):
                return False, redirect('/dashboard')  # Redirect to dashboard if no access
        except ImportError:
            # RESTRICTIVE fallback
            restrictive_permissions = {
                'viewer': ['dashboard', 'analytics', 'reports'],
                'administrator': ['dashboard', 'analytics', 'reports', 'reviews', 'upload'],
                'super_admin': ['dashboard', 'analytics', 'reports', 'reviews', 'upload', 'forecasting']
            }
            allowed_tabs = restrictive_permissions.get(user_role, ['dashboard'])
            if required_tab not in allowed_tabs:
                return False, redirect('/dashboard')  # Redirect to dashboard if no access
        
        return True, None
    
    # Main dashboard (always accessible to authenticated users)
    @server.route('/dashboard')
    def admin_dashboard():
        """Main Dashboard Page - Always accessible to authenticated users"""
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme = get_current_theme()
        return create_empty_themed_page("Dashboard", "📊", theme)


# In layouts/admin_dashboard.py

    @server.route('/upload')
    def admin_upload():
        """Upload Page - Simple working version with persistent header"""
        has_access, redirect_response = check_tab_access('upload')
        if not has_access:
            return redirect_response
        
        theme_name = get_current_theme()
        
        # Get theme safely
        from utils.theme_utils import get_theme_styles
        theme_styles = get_theme_styles(theme_name)
        theme = theme_styles["theme"]  # This exists!
        
        # Get user info
        user_info = session.get('user_data', {})
        user_name = user_info.get('name', 'Administrator')
        user_role = user_info.get('role', 'administrator').replace('_', ' ').title()
        
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Upload - Swaccha Andhra Dashboard</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Inter', sans-serif; background: {theme['primary_bg']}; color: {theme['text_primary']}; min-height: 100vh; }}
                .upload-content {{ display: flex; justify-content: center; align-items: center; min-height: 80vh; padding: 2rem; }}
                .greeting-card {{ 
                    text-align: center; max-width: 600px; padding: 3rem 2rem; 
                    background: {theme['card_bg']}; border-radius: 20px; 
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); 
                    border: 2px solid {theme['brand_primary']};
                    animation: fadeInUp 0.8s ease-out;
                }}
                .greeting-icon {{ font-size: 5rem; margin-bottom: 1rem; animation: wave 2.5s ease-in-out infinite; }}
                .greeting-title {{ 
                    font-size: 3.5rem; font-weight: 900; color: {theme['text_primary']}; 
                    margin-bottom: 1rem; background: linear-gradient(45deg, {theme['brand_primary']}, {theme['brand_primary']});
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                }}
                @keyframes wave {{ 0%, 100% {{ transform: rotate(0deg); }} 25% {{ transform: rotate(-15deg); }} 75% {{ transform: rotate(15deg); }} }}
                @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            </style>
        </head>
        <body>
            <!-- Persistent Header -->
            <header style="background: linear-gradient(135deg, {theme['secondary_bg']} 0%, {theme['accent_bg']} 100%); border-bottom: 3px solid {theme['brand_primary']}; padding: 0.75rem 2rem; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3); position: sticky; top: 0; z-index: 1000;">
                <div style="max-width: 1600px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; gap: 2rem; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 2rem;">
                        <div style="font-size: 1.2rem; font-weight: 800; color: {theme['text_primary']};">🏢 Swaccha Andhra</div>
                        <nav style="display: flex; gap: 0.5rem;">
                            <a href="/dashboard" style="padding: 0.6rem 1.2rem; border-radius: 8px; text-decoration: none; font-weight: 600; background: rgba(255,255,255,0.1); color: {theme['text_primary']}; display: flex; align-items: center; gap: 0.4rem;">📊 Dashboard</a>
                            <a href="/upload" style="padding: 0.6rem 1.2rem; border-radius: 8px; text-decoration: none; font-weight: 600; background: {theme['brand_primary']}; color: white; display: flex; align-items: center; gap: 0.4rem;">📤 Upload</a>
                            <a href="/data-analytics" style="padding: 0.6rem 1.2rem; border-radius: 8px; text-decoration: none; font-weight: 600; background: rgba(255,255,255,0.1); color: {theme['text_primary']}; display: flex; align-items: center; gap: 0.4rem;">📈 Analytics</a>
                            <a href="/reports" style="padding: 0.6rem 1.2rem; border-radius: 8px; text-decoration: none; font-weight: 600; background: rgba(255,255,255,0.1); color: {theme['text_primary']}; display: flex; align-items: center; gap: 0.4rem;">📋 Reports</a>
                        </nav>
                    </div>
                    <div style="color: {theme['text_primary']};">Welcome, {user_name}! <a href="/?logout=true" style="color: #ff6b6b; text-decoration: none;">🚪</a></div>
                </div>
            </header>
            
            <!-- Upload Page Content -->
            <main class="upload-content">
                <div class="greeting-card">
                    <div class="greeting-icon">👋</div>
                    <h1 class="greeting-title">Hi Sai!</h1>
                    <p style="font-size: 1.3rem; color: {theme['text_secondary']}; margin-bottom: 2rem;">
                        Welcome to your personalized upload center!
                    </p>
                    <button style="padding: 1rem 2rem; background: {theme['brand_primary']}; color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer;" onclick="alert('Upload functionality coming soon! 🚀')">
                        📁 Start Uploading
                    </button>
                </div>
            </main>
        </body>
        </html>
        '''


    def create_persistent_header_html(theme_name, active_page):
        """Generate HTML for persistent header"""
        theme = get_theme_styles(theme_name)["theme"]
        user_info = session.get('user_data', {})
        user_name = user_info.get('name', 'Administrator')
        
        # Nav items based on user access
        nav_items = [
            {"id": "dashboard", "href": "/dashboard", "icon": "📊", "label": "Dashboard"},
            {"id": "upload", "href": "/upload", "icon": "📤", "label": "Upload"},
            {"id": "analytics", "href": "/data-analytics", "icon": "📈", "label": "Analytics"},
            {"id": "reports", "href": "/reports", "icon": "📋", "label": "Reports"},
            {"id": "reviews", "href": "/reviews", "icon": "⭐", "label": "Reviews"},
        ]
        
        nav_links = ""
        for item in nav_items:
            active_style = f"background: {theme['brand_primary']}; color: white;" if item['id'] == active_page else f"background: rgba(255,255,255,0.1); color: {theme['text_primary']};"
            nav_links += f'''
            <a href="{item['href']}" style="padding: 0.6rem 1.2rem; border-radius: 8px; text-decoration: none; font-weight: 600; {active_style} transition: all 0.3s ease; display: flex; align-items: center; gap: 0.4rem;">
                <span>{item['icon']}</span>
                <span>{item['label']}</span>
            </a>
            '''
        
        return f'''
        <header style="background: linear-gradient(135deg, {theme['secondary_bg']} 0%, {theme['accent_bg']} 100%); border-bottom: 3px solid {theme['brand_primary']}; padding: 0.75rem 2rem; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3); position: sticky; top: 0; z-index: 1000;">
            <div style="max-width: 1600px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; gap: 2rem;">
                <div style="display: flex; align-items: center; gap: 2rem;">
                    <div style="font-size: 1.2rem; font-weight: 800; color: {theme['text_primary']};">
                        🏢 Swaccha Andhra
                    </div>
                    <nav style="display: flex; gap: 0.5rem; align-items: center;">
                        {nav_links}
                    </nav>
                </div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="color: {theme['text_primary']};">{user_name}</span>
                    <a href="/?logout=true" style="padding: 0.4rem 0.8rem; background: rgba(220, 38, 38, 0.8); color: white; text-decoration: none; border-radius: 6px;">🚪</a>
                </div>
            </div>
        </header>
        '''

    @server.route('/data-analytics')
    def admin_data_analytics():
        """Analytics Page with dedicated layout"""
        has_access, redirect_response = check_tab_access('analytics')
        if not has_access:
            return redirect_response
        
        theme = get_current_theme()
        # Import and use the dedicated analytics layout
        from layouts.analytics_layout import create_analytics_layout
        return create_analytics_layout(theme)

    @server.route('/reports')
    def admin_reports():
        """Reports Page with dedicated layout"""
        has_access, redirect_response = check_tab_access('reports')
        if not has_access:
            return redirect_response
        
        theme = get_current_theme()
        # You can create reports_layout.py for this too
        return create_reports_layout(theme)

    # Charts page (with access control)
    @server.route('/charts')
    def admin_charts():
        """Charts Page - Check access control"""
        has_access, redirect_response = check_tab_access('charts')
        if not has_access:
            return redirect_response
        
        theme = get_current_theme()
        return create_empty_themed_page("Charts", "📈", theme)


    # Reviews page (with access control)
    @server.route('/reviews')
    def admin_reviews():
        """Reviews Page - Check access control"""
        has_access, redirect_response = check_tab_access('reviews')
        if not has_access:
            return redirect_response
        
        theme = get_current_theme()
        return create_empty_themed_page("Reviews", "⭐", theme)

    # Forecasting page (with access control)
    @server.route('/forecasting')
    def admin_forecasting():
        """Forecasting Page - Check access control"""
        has_access, redirect_response = check_tab_access('forecasting')
        if not has_access:
            return redirect_response
        
        theme = get_current_theme()
        return create_empty_themed_page("Forecasting", "🔮", theme)



    # All your existing API routes remain the same...
    @server.route('/api/csv-data')
    def get_csv_data():
        """API endpoint to get embedded CSV data with filtering"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        try:
            data = get_embedded_csv_data()
            
            if not data:
                return flask.jsonify({
                    'error': 'No embedded CSV data available',
                    'message': 'Embedded data is empty'
                })
            
            # Get filter parameters
            agency = request.args.get('agency', 'all')
            cluster = request.args.get('cluster', 'all')
            site = request.args.get('site', 'all')
            material = request.args.get('material', 'all')
            vehicle = request.args.get('vehicle', 'all')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            # Apply filters
            filtered_data = []
            for row in data:
                # Agency filter
                if agency != 'all' and row.get('agency') != agency:
                    continue
                
                # Cluster filter
                if cluster != 'all' and row.get('cluster') != cluster:
                    continue
                
                # Site filter
                if site != 'all' and row.get('site') != site:
                    continue
                
                # Material filter
                if material != 'all' and row.get('Material Name') != material:
                    continue
                
                # Vehicle filter
                if vehicle != 'all' and row.get('Vehicle No') != vehicle:
                    continue
                
                # Date filters
                if start_date or end_date:
                    try:
                        from datetime import datetime
                        row_date = datetime.strptime(row.get('Date', ''), '%Y-%m-%d')
                        if start_date and row_date < datetime.strptime(start_date, '%Y-%m-%d'):
                            continue
                        if end_date and row_date > datetime.strptime(end_date, '%Y-%m-%d'):
                            continue
                    except:
                        continue  # Skip invalid dates
                
                filtered_data.append(row)
            
            # Calculate statistics
            total_records = len(filtered_data)
            total_weight = sum(float(row.get('Net Weight', 0)) for row in filtered_data)
            unique_vehicles = len(set(row.get('Vehicle No', '') for row in filtered_data if row.get('Vehicle No')))
            unique_materials = len(set(row.get('Material Name', '') for row in filtered_data if row.get('Material Name')))
            
            return flask.jsonify({
                'success': True,
                'total_records': total_records,
                'total_weight': f"{total_weight:,.0f} kg",
                'unique_vehicles': unique_vehicles,
                'unique_materials': unique_materials,
                'records': filtered_data,
                'filters_applied': {
                    'agency': agency,
                    'cluster': cluster,
                    'site': site,
                    'material': material,
                    'vehicle': vehicle,
                    'start_date': start_date,
                    'end_date': end_date
                }
            })
            
        except Exception as e:
            print(f"❌ Error processing embedded CSV data: {e}")
            return flask.jsonify({
                'error': 'Error processing embedded CSV data',
                'message': str(e)
            }), 500
        
    @server.route('/api/data-status')
    def get_realtime_status():
        """Get real-time data status"""
        status = get_data_status()
        return jsonify(status)

    @server.route('/api/csv-metadata')
    def get_csv_metadata():
        """API endpoint to get embedded CSV metadata and filter options"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        try:
            data = get_embedded_csv_data()
            
            if not data:
                return flask.jsonify({
                    'error': 'No embedded CSV data available'
                })
            
            # Get metadata from embedded data
            sample_record = data[0] if data else {}
            columns = list(sample_record.keys()) if sample_record else []
            
            # Get date range
            dates = [row.get('Date', '') for row in data if row.get('Date')]
            min_date = min(dates) if dates else None
            max_date = max(dates) if dates else None
            
            metadata = {
                'total_records': len(data),
                'columns': columns,
                'filter_options': get_filter_options_from_embedded_data(),
                'date_range': {
                    'min_date': min_date,
                    'max_date': max_date
                },
                'sample_record': sample_record
            }
            
            return flask.jsonify(metadata)
            
        except Exception as e:
            print(f"❌ Error getting embedded CSV metadata: {e}")
            return flask.jsonify({
                'error': 'Error getting metadata',
                'message': str(e)
            }), 500

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

# Also update the register_custom_dashboard_routes function to only include API routes

def register_custom_dashboard_routes(server):
    """Register dashboard API routes without page conflicts"""
    
    @server.route('/dashboard/csv-relationships')
    def csv_relationships():
        """API endpoint to get CSV data relationships for cascading filters"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        try:
            from data_loader import get_cached_data
            df = get_cached_data()
            
            if df.empty:
                return flask.jsonify({
                    'agency_clusters': {},
                    'cluster_sites': {},
                    'message': 'No CSV data available'
                })
            
            # Build relationships from CSV data
            agency_clusters = {}
            cluster_sites = {}
            
            # Group by agency to get clusters
            if 'agency' in df.columns and 'cluster' in df.columns:
                grouped = df.groupby('agency')['cluster'].unique()
                for agency, clusters in grouped.items():
                    agency_clusters[agency] = list(clusters)
            
            # Group by cluster to get sites
            if 'cluster' in df.columns and 'site' in df.columns:
                grouped = df.groupby('cluster')['site'].unique()
                for cluster, sites in grouped.items():
                    cluster_sites[cluster] = list(sites)
            
            logger.info(f"✅ CSV relationships: {len(agency_clusters)} agencies, {len(cluster_sites)} clusters")
            
            return flask.jsonify({
                'agency_clusters': agency_clusters,
                'cluster_sites': cluster_sites,
                'total_records': len(df)
            })
            
        except Exception as e:
            logger.error(f"❌ Error getting CSV relationships: {e}")
            return flask.jsonify({
                'error': 'Error processing CSV data',
                'message': str(e)
            }), 500
    
    @server.route('/dashboard/filtered-csv-data')
    def filtered_csv_data():
        """API endpoint to get filtered CSV data - RENAMED TO AVOID CONFLICT"""
        if not session.get('swaccha_session_id'):
            return {'error': 'Authentication required'}, 401
        
        try:
            from data_loader import get_cached_data, filter_data
            
            # Get filter parameters from request
            agency = request.args.get('agency', 'all')
            cluster = request.args.get('cluster', 'all')
            site = request.args.get('site', 'all')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            # Load and filter CSV data
            df = get_cached_data()
            
            if df.empty:
                return flask.jsonify({
                    "error": "No CSV data available",
                    "message": "Please upload a CSV file"
                })
            
            # Apply filters
            filtered_df = filter_data(df, agency, cluster, site, start_date, end_date)
            
            # Calculate statistics using correct column names from your CSV
            record_count = len(filtered_df)
            
            # Use 'Net Weight' column (as per your CSV structure)
            total_weight = 0
            if 'Net Weight' in filtered_df.columns and not filtered_df.empty:
                total_weight = filtered_df['Net Weight'].sum()
            elif 'weight' in filtered_df.columns and not filtered_df.empty:
                total_weight = filtered_df['weight'].sum()
            
            # Use 'Vehicle No' column (as per your CSV structure)
            vehicle_count = 0
            if 'Vehicle No' in filtered_df.columns and not filtered_df.empty:
                vehicle_count = filtered_df['Vehicle No'].nunique()
            elif 'vehicle' in filtered_df.columns and not filtered_df.empty:
                vehicle_count = filtered_df['vehicle'].nunique()
            
            filter_response = {
                "agency": agency,
                "cluster": cluster,
                "site": site,
                "start_date": start_date,
                "end_date": end_date,
                "record_count": record_count,
                "total_weight": f"{total_weight:,.0f} kg",
                "vehicle_count": vehicle_count,
                "timestamp": time.time(),
                "source": "CSV Data with Cascading Filters",
                "total_records_available": len(df)
            }
            
            logger.info(f"✅ Filtered CSV data: {record_count} records from {len(df)} total")
            
            return flask.jsonify(filter_response)
            
        except Exception as e:
            logger.error(f"❌ Error filtering CSV data: {e}")
            return flask.jsonify({
                "error": "Error processing CSV data",
                "message": str(e)
            }), 500


# Keep all the other existing functions unchanged
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
    """
    ENHANCED: Navigation tabs with role-based access control
    Only shows tabs that the user has permission to access
    """
    
    # Get user role from session data
    user_role = user_data.get('role', 'viewer')
    
    # STRICT TAB PERMISSIONS
    try:
        from config.auth import get_tab_permissions
        allowed_tabs = get_tab_permissions(user_role)
    except ImportError:
        # RESTRICTIVE fallback if import fails
        restrictive_permissions = {
            'viewer': ['dashboard', 'analytics', 'reports'],  # ONLY these 3 tabs
            'administrator': ['dashboard', 'analytics', 'reports', 'reviews', 'upload'],
            'super_admin': ['dashboard', 'analytics', 'reports', 'reviews', 'upload', 'forecasting']
        }
        allowed_tabs = restrictive_permissions.get(user_role, ['dashboard'])
    
    # All possible tabs with their configuration
    all_tabs = [
        {"id": "dashboard", "tab_id": "tab-dashboard", "label": "📊 Dashboard", "icon": "📊"},
        {"id": "analytics", "tab_id": "tab-analytics", "label": "🔍 Data Analytics", "icon": "🔍"},
        {"id": "reports", "tab_id": "tab-reports", "label": "📋 Reports", "icon": "📋"},
        {"id": "reviews", "tab_id": "tab-reviews", "label": "⭐ Reviews", "icon": "⭐"},
        {"id": "upload", "tab_id": "tab-upload", "label": "📤 Upload", "icon": "📤"},
        {"id": "forecasting", "tab_id": "tab-forecasting", "label": "🔮 Forecasting", "icon": "🔮"}
    ]
    
    # FILTER TABS: Only show tabs the user has access to
    visible_tabs = [tab for tab in all_tabs if tab["id"] in allowed_tabs]
    
    print(f"🔒 USER ROLE: {user_role}")
    print(f"🔒 ALLOWED TABS: {allowed_tabs}")
    print(f"🔒 VISIBLE TABS: {[t['id'] for t in visible_tabs]}")
    
    # Create tab buttons - ONLY for allowed tabs
    tab_buttons = []
    for tab in visible_tabs:
        tab_button = html.Button(
            tab["label"],
            id=tab["tab_id"],
            n_clicks=0,
            className="nav-tab-button",
            style={
                "padding": "0.8rem 1.5rem",
                "margin": "0 0.5rem",
                "borderRadius": "8px",
                "border": f"2px solid {theme['card_bg']}",
                "backgroundColor": theme["accent_bg"],
                "color": theme["text_primary"],
                "fontSize": "0.9rem",
                "fontWeight": "600",
                "cursor": "pointer",
                "transition": "all 0.3s ease",
                "whiteSpace": "nowrap"
            }
        )
        tab_buttons.append(tab_button)
    
    # User info section
    user_avatar = html.Img(
        src=user_data.get('picture', '/assets/img/default-avatar.png'),
        alt="User Avatar",
        style={
            "width": "40px",
            "height": "40px",
            "borderRadius": "50%",
            "marginRight": "0.5rem",
            "border": f"2px solid {theme['primary']}"
        }
    )
    
    user_info = html.Div([
        user_avatar,
        html.Div([
            html.Div(
                user_data.get('name', 'User'),
                style={
                    "color": theme["text_primary"],
                    "fontSize": "0.9rem",
                    "fontWeight": "600",
                    "margin": "0"
                }
            ),
            html.Div(
                f"Role: {user_role.title()}",  # Show the role
                style={
                    "color": theme["text_secondary"],
                    "fontSize": "0.75rem",
                    "margin": "0"
                }
            )
        ])
    ], style={"display": "flex", "alignItems": "center"})
    
    # Logout button
    logout_button = html.Button(
        "🚪 Logout",
        id="logout-btn",
        n_clicks=0,
        style={
            "padding": "0.6rem 1.2rem",
            "borderRadius": "6px",
            "border": f"2px solid {theme['danger']}",
            "backgroundColor": "transparent",
            "color": theme["danger"],
            "fontSize": "0.8rem",
            "fontWeight": "600",
            "cursor": "pointer",
            "marginLeft": "1rem"
        }
    )
    
    # Return the complete navigation
    return html.Div(
        className="navigation-tabs",
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "padding": "1rem 2rem",
            "backgroundColor": theme["card_bg"],
            "borderBottom": f"1px solid {theme['border_light']}",
            "flexWrap": "wrap",
            "gap": "1rem"
        },
        children=[
            # Left: Tab buttons (only visible tabs)
            html.Div(
                style={"display": "flex", "alignItems": "center", "gap": "0.5rem"},
                children=tab_buttons
            ),
            # Right: User info and logout
            html.Div(
                style={"display": "flex", "alignItems": "center"},
                children=[user_info, logout_button]
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
    """Create minimal dashboard content - welcome message, quick stats AND FILTER CONTAINER"""
    theme = theme_styles["theme"]
    
    # Import filter container
    from components.filters.filter_container import create_filter_container
    
    return html.Div([
        # Welcome section
        html.Div([
            html.H2(
                f"👋 Welcome back, {user_data.get('name', 'Administrator')}!",
                style={
                    "color": theme["text_primary"],
                    "fontSize": "2.5rem",
                    "fontWeight": "800",
                    "marginBottom": "1rem",
                    "textAlign": "center"
                }
            ),
            html.P([
                html.Span("📊", style={"marginRight": "0.5rem"}),
                "Dashboard Analytics Ready • ",
                html.Span("🚀", style={"marginLeft": "0.5rem", "marginRight": "0.5rem"}),
                "Use filters below to analyze waste management data",
                html.Span(" • ⚡", style={"marginLeft": "0.5rem"}),
                f" Last updated: {datetime.now().strftime('%H:%M:%S')}"
            ], style={
                "color": theme["text_secondary"],
                "fontSize": "1.2rem",
                "textAlign": "center",
                "marginBottom": "2rem",
                "lineHeight": "1.5"
            })
        ], style={
            "padding": "2rem 0",
            "backgroundColor": theme["accent_bg"],
            "borderRadius": "12px",
            "marginBottom": "2rem",
            "border": f"2px solid {theme['card_bg']}"
        }),
        
        # ✅ ADD FILTER CONTAINER TO MAIN DASHBOARD
        create_filter_container(theme, "analytics-filter-container"),
        
        # Quick stats section (enhanced)
        html.Div([
            html.H3(
                "📈 Quick Stats Overview",
                style={
                    "color": theme["text_primary"],
                    "fontSize": "1.8rem",
                    "fontWeight": "700",
                    "marginBottom": "1.5rem",
                    "textAlign": "center"
                }
            ),
            html.Div([
                create_stat_card("🚛", "Active Vehicles", "67", "vehicles", theme),
                create_stat_card("⚖️", "Today's Collection", "1,234", "tonnes", theme),
                create_stat_card("📍", "Collection Points", "156", "sites", theme),
                create_stat_card("✅", "Efficiency Score", "94%", "performance", theme),
            ], style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                "gap": "1.5rem",
                "marginBottom": "2rem"
            })
        ], style={
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "padding": "2rem",
            "border": f"2px solid {theme['accent_bg']}",
            "marginBottom": "2rem"
        }),
        
        # ✅ ADD FILTERED DATA DISPLAY AREA
        html.Div(
            id="filtered-data-display",
            children=[
                html.Div([
                    html.H3(
                        "🔍 Filtered Data Results",
                        style={
                            "color": theme["text_primary"],
                            "fontSize": "1.5rem",
                            "fontWeight": "600",
                            "marginBottom": "1rem",
                            "textAlign": "center"
                        }
                    ),
                    html.P(
                        "📊 Apply filters above to view and analyze waste collection data",
                        style={
                            "textAlign": "center",
                            "color": theme["text_secondary"],
                            "fontSize": "1.1rem",
                            "margin": "0"
                        }
                    )
                ], style={
                    "textAlign": "center",
                    "padding": "3rem",
                    "backgroundColor": theme["card_bg"],
                    "borderRadius": "12px",
                    "border": f"2px dashed {theme['accent_bg']}"
                })
            ],
            style={"marginBottom": "2rem"}
        ),
        
        # Action buttons section
        html.Div([
            html.H3(
                "⚡ Quick Actions",
                style={
                    "color": theme["text_primary"],
                    "fontSize": "1.8rem",
                    "fontWeight": "700",
                    "marginBottom": "1.5rem",
                    "textAlign": "center"
                }
            ),
            html.Div([
                create_action_button("📊", "View Analytics", "Go to detailed analytics", theme),
                create_action_button("📋", "Generate Reports", "Create comprehensive reports", theme),
                create_action_button("⭐", "Check Reviews", "View customer feedback", theme),
                create_action_button("📤", "Upload Data", "Import new data files", theme),
            ], style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                "gap": "1.5rem"
            })
        ], style={
            "backgroundColor": theme["card_bg"],
            "borderRadius": "12px",
            "padding": "2rem",
            "border": f"2px solid {theme['accent_bg']}"
        })
    ])


def create_stat_card(icon, title, value, unit, theme):
    """Create a statistics card"""
    return html.Div([
        html.Div([
            html.Span(icon, style={
                "fontSize": "2.5rem",
                "marginBottom": "0.5rem",
                "display": "block"
            }),
            html.H4(title, style={
                "color": theme["text_primary"],
                "fontSize": "1rem",
                "fontWeight": "600",
                "marginBottom": "0.5rem"
            }),
            html.Div([
                html.Span(value, style={
                    "fontSize": "2rem",
                    "fontWeight": "800",
                    "color": theme["brand_primary"]
                }),
                html.Span(f" {unit}", style={
                    "fontSize": "0.9rem",
                    "color": theme["text_secondary"],
                    "marginLeft": "0.5rem"
                })
            ])
        ])
    ], style={
        "backgroundColor": theme["accent_bg"],
        "borderRadius": "8px",
        "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}",
        "padding": "1.5rem",
        "textAlign": "center",
        "transition": "transform 0.2s ease, box-shadow 0.2s ease",
        "cursor": "default",
        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)"
    })


def create_action_button(icon, title, description, theme):
    """Create an action button card"""
    return html.Div([
        html.Div(icon, style={
            "fontSize": "2rem",
            "marginBottom": "1rem",
            "color": theme["brand_primary"]
        }),
        html.H4(title, style={
            "color": theme["text_primary"],
            "fontSize": "1.1rem",
            "fontWeight": "600",
            "marginBottom": "0.5rem"
        }),
        html.P(description, style={
            "color": theme["text_secondary"],
            "fontSize": "0.9rem",
            "margin": "0"
        }),
        html.Button(
            f"Open {title}",
            style={
                "backgroundColor": theme["brand_primary"],
                "color": "white",
                "border": "none",
                "borderRadius": "6px",
                "padding": "0.5rem 1rem",
                "marginTop": "1rem",
                "fontSize": "0.9rem",
                "fontWeight": "600",
                "cursor": "pointer",
                "width": "100%",
                "transition": "all 0.2s ease"
            }
        )
    ], style={
        "backgroundColor": theme["accent_bg"],
        "borderRadius": "8px",
        "border": f"1px solid {theme.get('border_light', theme['accent_bg'])}",
        "padding": "1.5rem",
        "textAlign": "center",
        "transition": "transform 0.2s ease, box-shadow 0.2s ease",
        "cursor": "pointer",
        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)"
    })

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
                                "Dashboard with Real CSV Data Integration • ",
                                html.Span("🔍", style={"marginLeft": "0.5rem", "marginRight": "0.5rem"}),
                                f"Connected to waste_management_data_updated.csv • Current time: {datetime.now().strftime('%H:%M:%S')}"
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
    'validate_file_type',
    'get_embedded_csv_data',
    'get_filter_options_from_embedded_data'
]

def get_data_status():
    """Get current data status for dashboard"""
    timestamp = get_data_timestamp()
    data = get_latest_data()
    
    if timestamp and data is not None:
        return {
            'last_updated': timestamp.strftime('%H:%M:%S'),
            'record_count': len(data),
            'status': 'Connected'
        }
    else:
        return {
            'last_updated': 'Never',
            'record_count': 0,
            'status': 'Disconnected'
        }


def filter_data(df, filters):
    """Filter DataFrame based on selected filters"""
    try:
        # Create a copy of the DataFrame
        filtered_df = df.copy()
        
        # Apply agency filter
        if filters.get('agency') and filters['agency'] != 'all':
            filtered_df = filtered_df[filtered_df['agency'] == filters['agency']]
        
        # Apply cluster filter
        if filters.get('cluster') and filters['cluster'] != 'all':
            filtered_df = filtered_df[filtered_df['cluster'] == filters['cluster']]
        
        # Apply site filter
        if filters.get('site') and filters['site'] != 'all':
            filtered_df = filtered_df[filtered_df['site'] == filters['site']]
        
        # Apply date range filter
        if filters.get('start_date'):
            start_date = pd.to_datetime(filters['start_date'])
            filtered_df = filtered_df[filtered_df['date'] >= start_date]
        
        if filters.get('end_date'):
            end_date = pd.to_datetime(filters['end_date'])
            filtered_df = filtered_df[filtered_df['date'] <= end_date]
        
        return filtered_df
    except Exception as e:
        print(f"Error filtering data: {str(e)}")
        return pd.DataFrame()




def get_filter_options(df):
    """Get filter options from DataFrame"""
    try:
        # Get unique values for each filter
        agencies = sorted(df['agency'].unique().tolist())
        clusters = sorted(df['cluster'].unique().tolist())
        sites = sorted(df['site'].unique().tolist())
        
        # Get date range
        min_date = df['date'].min().strftime('%Y-%m-%d')
        max_date = df['date'].max().strftime('%Y-%m-%d')
        
        return {
            'agencies': agencies,
            'clusters': clusters,
            'sites': sites,
            'min_date': min_date,
            'max_date': max_date
        }
    except Exception as e:
        print(f"Error getting filter options: {str(e)}")
        return {
            'agencies': [],
            'clusters': [],
            'sites': [],
            'min_date': '',
            'max_date': ''
        }

def create_data_display(theme):
    """Create data display section with table and statistics"""
    # Load the data using pandas
    df = load_waste_data()
    
    # Calculate statistics
    total_records = len(df)
    total_waste = df['waste_collected'].sum()
    
    # Convert DataFrame to HTML table with custom styling
    table_html = df.to_html(
        classes='data-table',
        columns=['date', 'agency', 'cluster', 'site', 'waste_collected'],
        index=False,
        formatters={
            'date': lambda x: pd.to_datetime(x).strftime('%Y-%m-%d'),
            'waste_collected': lambda x: f"{float(x):,.0f} kg"
        }
    )
    
    return f'''
    <div class="data-display" style="
        background-color: var(--card-bg);
        border-radius: 16px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid var(--border-light);
    ">
        <div class="data-header" style="
            margin-bottom: 2rem;
            text-align: center;
            border-bottom: 2px solid var(--accent-bg);
            padding-bottom: 1.5rem;
        ">
            <h3 style="
                color: var(--text-primary);
                font-size: 2rem;
                font-weight: 700;
                margin: 0 0 1rem 0;
                letter-spacing: -0.5px;
            ">📊 Waste Collection Data</h3>
            <p style="
                color: var(--text-secondary);
                font-size: 1.1rem;
                margin: 0;
                line-height: 1.5;
                max-width: 800px;
                margin: 0 auto;
            ">View and analyze waste collection records</p>
        </div>

        <div class="stats-container" style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        ">
            <div class="stat-card" style="
                background-color: var(--card-bg);
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                border: 1px solid var(--border-light);
            ">
                <h4 style="
                    color: var(--text-secondary);
                    font-size: 1rem;
                    margin: 0 0 0.5rem 0;
                ">Total Records</h4>
                <p class="value" style="
                    color: var(--text-primary);
                    font-size: 2rem;
                    font-weight: 700;
                    margin: 0;
                ">{total_records:,}</p>
            </div>
            <div class="stat-card" style="
                background-color: var(--card-bg);
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                border: 1px solid var(--border-light);
            ">
                <h4 style="
                    color: var(--text-secondary);
                    font-size: 1rem;
                    margin: 0 0 0.5rem 0;
                ">Total Waste Collected</h4>
                <p class="value" style="
                    color: var(--text-primary);
                    font-size: 2rem;
                    font-weight: 700;
                    margin: 0;
                ">{total_waste:,.0f} kg</p>
            </div>
        </div>

        <div class="data-table-container" style="
            overflow-x: auto;
            margin-top: 2rem;
            background-color: var(--card-bg);
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-light);
        ">
            {table_html}
        </div>
    </div>

    <style>
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            background-color: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }}
        
        .data-table th {{
            padding: 1rem;
            text-align: left;
            background-color: var(--accent-bg);
            color: var(--text-primary);
            font-weight: 600;
            font-size: 1.1rem;
            border-bottom: 2px solid var(--border-light);
            white-space: nowrap;
        }}
        
        .data-table td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-light);
            color: var(--text-primary);
            font-size: 1rem;
        }}
        
        .data-table tr:hover {{
            background-color: var(--accent-bg);
        }}
        
        .data-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .data-table th:first-child,
        .data-table td:first-child {{
            padding-left: 1.5rem;
        }}
        
        .data-table th:last-child,
        .data-table td:last-child {{
            padding-right: 1.5rem;
        }}
        
        .data-table-container {{
            margin: 0;
            padding: 0;
        }}
        
        .data-table-container::-webkit-scrollbar {{
            height: 8px;
        }}
        
        .data-table-container::-webkit-scrollbar-track {{
            background: var(--accent-bg);
            border-radius: 4px;
        }}
        
        .data-table-container::-webkit-scrollbar-thumb {{
            background: var(--border-light);
            border-radius: 4px;
        }}
        
        .data-table-container::-webkit-scrollbar-thumb:hover {{
            background: var(--text-secondary);
        }}
    </style>
    '''