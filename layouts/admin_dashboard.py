# layouts/admin_dashboard.py - UPDATED FOR csv_outputs_data_viz.csv
"""
Enhanced Admin Dashboard Layout for Swaccha Andhra - UPDATED DATA SOURCE
Now uses data/csv_outputs_data_viz.csv with correct column mappings and DD-MM-YYYY date format
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
import flask
import traceback
import logging

logger = logging.getLogger(__name__)

def get_current_theme():
    """Get current theme from session or default"""
    return session.get('current_theme', 'dark')

def get_filter_options_from_embedded_data():
    """Extract unique filter options from csv_outputs_data_viz.csv using pandas"""
    try:
        # Load CSV data using pandas
        csv_data = get_embedded_csv_data()
        
        if not csv_data:
            return {
                'agencies': ['No data available'],
                'clusters': ['No data available'], 
                'sites': ['No data available'],
                'sub_contractors': ['No data available'],
                'machines': ['No data available']
            }
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(csv_data)
        
        # Extract unique values for each filter using actual CSV column names
        def get_unique_values(df, column_name, default_name):
            """Get unique values from DataFrame for given column name"""
            if column_name in df.columns:
                unique_vals = df[column_name].dropna().astype(str).str.strip()
                unique_vals = unique_vals[unique_vals != ''].unique()
                return sorted(list(unique_vals))
            return [f'No {default_name} data']
        
        # Extract unique values using actual CSV column names
        agencies = get_unique_values(df, 'Agency', 'agency')
        clusters = get_unique_values(df, 'Cluster', 'cluster')
        sites = get_unique_values(df, 'Site', 'site')
        sub_contractors = get_unique_values(df, 'Sub_contractor', 'sub_contractor')
        machines = get_unique_values(df, 'Machines', 'machine')
        
        options = {
            'agencies': agencies,
            'clusters': clusters,
            'sites': sites,
            'sub_contractors': sub_contractors,
            'machines': machines
        }
        
        logger.info(f"✅ Filter options extracted from {len(csv_data)} CSV records:")
        for key, values in options.items():
            logger.info(f"   {key}: {len(values)} options")
            if len(values) <= 10:
                logger.info(f"      Values: {values}")
            else:
                logger.info(f"      Sample: {values[:5]}... (+{len(values)-5} more)")
        
        return options
        
    except Exception as e:
        logger.error(f"❌ Error extracting filter options: {str(e)}")
        return {
            'agencies': ['Error loading data'],
            'clusters': ['Error loading data'], 
            'sites': ['Error loading data'],
            'sub_contractors': ['Error loading data'],
            'machines': ['Error loading data']
        }

def parse_dd_mm_yyyy_date(date_str):
    """Parse date string in DD-MM-YYYY format"""
    if not date_str or pd.isna(date_str):
        return None
    
    try:
        # Try DD-MM-YYYY format first
        return pd.to_datetime(date_str, format='%d-%m-%Y', errors='coerce')
    except:
        try:
            # Fallback to dayfirst=True
            return pd.to_datetime(date_str, dayfirst=True, errors='coerce')
        except:
            return None

def get_embedded_csv_data():
    """Load CSV data from data/csv_outputs_data_viz.csv using pandas"""
    try:
        # Updated path to use csv_outputs_data_viz.csv
        csv_path = 'data/csv_outputs_data_viz.csv'
        
        logger.info(f"📁 Loading CSV from: {csv_path}")
        
        # Check if file exists
        if not os.path.exists(csv_path):
            logger.error(f"❌ CSV file not found at: {csv_path}")
            return []
        
        # Read the CSV file using pandas with proper encoding
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(csv_path, encoding='latin-1')
            except:
                df = pd.read_csv(csv_path, encoding='cp1252')
        
        # Parse date column with DD-MM-YYYY format
        if 'date' in df.columns:
            df['date_parsed'] = df['date'].apply(parse_dd_mm_yyyy_date)
            # Keep original date string for display, add parsed for filtering
            logger.info(f"📅 Sample dates: {df['date'].head(3).tolist()}")
        
        logger.info(f"✅ Loaded {len(df)} records from CSV")
        logger.info(f"📋 Columns: {list(df.columns)}")
        
        # Convert DataFrame to dictionary format for JavaScript
        csv_data = df.to_dict('records')
        
        # Print sample record for debugging
        if csv_data:
            logger.info(f"📊 Sample record keys: {list(csv_data[0].keys())}")
        
        return csv_data
        
    except Exception as e:
        logger.error(f"❌ Error loading CSV data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
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

def register_enhanced_csv_routes(server):
    """Register enhanced CSV data routes with csv_outputs_data_viz.csv integration"""
    
    @server.route('/api/csv-data-enhanced')
    def get_enhanced_csv_data():
        """Enhanced API endpoint to get CSV data with comprehensive filtering using csv_outputs_data_viz.csv"""
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
            
            # Get filter parameters using actual CSV column names
            agency = request.args.get('agency', 'all')
            cluster = request.args.get('cluster', 'all')
            site = request.args.get('site', 'all')
            sub_contractor = request.args.get('sub_contractor', 'all')
            machine = request.args.get('machine', 'all')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            # Apply filters using pandas with actual column names
            filtered_df = df.copy()
            
            # Agency filter (using 'Agency' column)
            if agency != 'all' and 'Agency' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Agency'] == agency]
            
            # Cluster filter (using 'Cluster' column)
            if cluster != 'all' and 'Cluster' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Cluster'] == cluster]
            
            # Site filter (using 'Site' column)
            if site != 'all' and 'Site' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Site'] == site]
            
            # Sub-contractor filter (using 'Sub_contractor' column)
            if sub_contractor != 'all' and 'Sub_contractor' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Sub_contractor'] == sub_contractor]
            
            # Machine filter (using 'Machines' column)
            if machine != 'all' and 'Machines' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Machines'] == machine]
            
            # Date filters using DD-MM-YYYY format
            if start_date or end_date:
                if 'date_parsed' in filtered_df.columns:
                    try:
                        if start_date:
                            start_dt = pd.to_datetime(start_date, format='%Y-%m-%d')
                            filtered_df = filtered_df[filtered_df['date_parsed'] >= start_dt]
                        
                        if end_date:
                            end_dt = pd.to_datetime(end_date, format='%Y-%m-%d')
                            filtered_df = filtered_df[filtered_df['date_parsed'] <= end_dt]
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Date filtering error: {e}")
            
            # Calculate statistics using actual CSV columns
            total_records = len(filtered_df)
            
            # Calculate total weight using 'net_weight_calculated' column
            total_weight = 0
            if 'net_weight_calculated' in filtered_df.columns:
                try:
                    total_weight = filtered_df['net_weight_calculated'].fillna(0).astype(float).sum()
                except:
                    total_weight = 0
            
            # Count unique sub-contractors
            unique_sub_contractors = 0
            if 'Sub_contractor' in filtered_df.columns:
                unique_sub_contractors = filtered_df['Sub_contractor'].dropna().nunique()
            
            # Count unique machines
            unique_machines = 0
            if 'Machines' in filtered_df.columns:
                unique_machines = filtered_df['Machines'].dropna().nunique()
            
            # Get total capacity
            total_capacity = 0
            if 'Total_capacity_per_day' in filtered_df.columns:
                try:
                    total_capacity = filtered_df['Total_capacity_per_day'].fillna(0).astype(float).sum()
                except:
                    total_capacity = 0
            
            # Convert filtered DataFrame back to records (drop date_parsed for output)
            output_df = filtered_df.drop(columns=['date_parsed'], errors='ignore')
            filtered_records = output_df.to_dict('records')
            
            response_data = {
                'success': True,
                'total_records': total_records,
                'total_weight': f"{total_weight:,.0f} kg",
                'unique_sub_contractors': unique_sub_contractors,
                'unique_machines': unique_machines,
                'total_capacity': f"{total_capacity:,.0f}",
                'records': filtered_records[:1000],  # Limit to 1000 records for performance
                'total_available': len(csv_data),
                'filters_applied': {
                    'agency': agency,
                    'cluster': cluster,
                    'site': site,
                    'sub_contractor': sub_contractor,
                    'machine': machine,
                    'start_date': start_date,
                    'end_date': end_date
                },
                'columns_detected': {
                    'date_column': 'date',
                    'weight_column': 'net_weight_calculated',
                    'sub_contractor_column': 'Sub_contractor',
                    'machine_column': 'Machines',
                    'capacity_column': 'Total_capacity_per_day'
                }
            }
            
            logger.info(f"✅ Enhanced CSV API: {total_records} records filtered from {len(csv_data)} total")
            
            return flask.jsonify(response_data)
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced CSV API: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return flask.jsonify({
                'error': 'Error processing CSV data',
                'message': str(e)
            }), 500
    
    @server.route('/api/csv-summary')
    def get_csv_summary():
        """Get comprehensive CSV data summary for csv_outputs_data_viz.csv"""
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
            
            # Detect date column and get range
            if 'date' in df.columns:
                try:
                    # Parse dates with DD-MM-YYYY format
                    date_series = df['date'].apply(parse_dd_mm_yyyy_date)
                    valid_dates = date_series.dropna()
                    if len(valid_dates) > 0:
                        summary['date_range'] = {
                            'column': 'date',
                            'min_date': valid_dates.min().strftime('%d-%m-%Y'),
                            'max_date': valid_dates.max().strftime('%d-%m-%Y'),
                            'valid_dates': len(valid_dates),
                            'invalid_dates': len(date_series) - len(valid_dates)
                        }
                except Exception as e:
                    logger.warning(f"Error parsing dates: {e}")
            
            # Detect numeric columns
            numeric_cols = df.select_dtypes(include=[pd.np.number]).columns.tolist()
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
            logger.error(f"❌ Error getting CSV summary: {e}")
            return flask.jsonify({
                'error': 'Error processing CSV summary',
                'message': str(e)
            }), 500

def create_empty_themed_page(title, icon, theme_name="dark"):
    """Create an empty themed page template with csv_outputs_data_viz.csv integration"""
    theme_styles = get_theme_styles(theme_name)
    theme = theme_styles["theme"]
    
    user_info = session.get('user_data', {})
    user_name = user_info.get('name', 'Administrator')
    user_role_display = user_info.get('role', 'administrator').replace('_', ' ').title()
    
    # Get user role and apply access control
    user_role_raw = user_info.get('role', 'viewer')
    
    # Apply role-based access control
    try:
        from config.auth import get_tab_permissions
        allowed_tabs = get_tab_permissions(user_role_raw)
    except ImportError:
        # Restrictive fallback
        restrictive_permissions = {
            'viewer': ['dashboard', 'analytics', 'reports'],
            'administrator': ['dashboard', 'analytics', 'reports', 'reviews', 'upload'],
            'super_admin': ['dashboard', 'analytics', 'reports', 'reviews', 'upload', 'forecasting']
        }
        allowed_tabs = restrictive_permissions.get(user_role_raw, ['dashboard'])
    
    # All possible tabs
    all_tabs = [
        {"id": "dashboard", "href": "/dashboard", "label": "📊 Dashboard", "active_check": "dashboard"},
        {"id": "analytics", "href": "/data-analytics", "label": "🔍 Data Analytics", "active_check": "data analytics"},
        {"id": "reports", "href": "/reports", "label": "📋 Reports", "active_check": "reports"},
        {"id": "reviews", "href": "/reviews", "label": "⭐ Reviews", "active_check": "reviews"},
        {"id": "upload", "href": "/upload", "label": "📤 Upload", "active_check": "upload"},
        {"id": "forecasting", "href": "/forecasting", "label": "🔮 Forecasting", "active_check": "forecasting"}
    ]
    
    # Filter tabs based on user permissions
    visible_tabs = [tab for tab in all_tabs if tab["id"] in allowed_tabs]
    
    logger.info(f"🔒 HTML PAGE - USER ROLE: {user_role_raw}")
    logger.info(f"🔒 HTML PAGE - ALLOWED TABS: {allowed_tabs}")
    logger.info(f"🔒 HTML PAGE - VISIBLE TABS: {[t['id'] for t in visible_tabs]}")
    
    # Build navigation buttons only for visible tabs
    nav_buttons_html = ""
    for tab in visible_tabs:
        active_class = "active" if tab["active_check"] in title.lower() else ""
        nav_buttons_html += f'''
            <a href="{tab["href"]}" class="nav-tab {active_class}">
                {tab["label"]}
            </a>
        '''
    
    # Load real CSV data using pandas
    csv_data = get_embedded_csv_data()
    
    # Convert to JavaScript string
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
            
            /* Main Content */
            .main-content {{
                flex: 1;
                padding: 2rem;
                max-width: 1600px;
                margin: 0 auto;
                width: 100%;
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
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
                width: 100%;
                flex-wrap: nowrap;
            }}
            
            .date-range input {{
                flex: 1;
                min-width: 0;
                max-width: 50%;
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
                
                .date-range input {{
                    max-width: 100%;
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
                </div>
            </nav>
            
            <!-- Main Content -->
            <main class="main-content">
                <!-- Filter Container -->
                <div class="filter-container">
                    <div class="filter-header">
                        <h3>🔍 Advanced Data Filters</h3>
                        <p>Filter and analyze data from csv_outputs_data_viz.csv with {len(csv_data)} records • All records displayed in descending date order</p>
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
                                <input type="date" id="start-date" placeholder="Start Date" style="flex: 1; padding: 1rem; border: 2px solid var(--border-light); border-radius: 12px; background-color: var(--card-bg); color: var(--text-primary); font-size: 1.1rem;">
                                <input type="date" id="end-date" placeholder="End Date" style="flex: 1; padding: 1rem; border: 2px solid var(--border-light); border-radius: 12px; background-color: var(--card-bg); color: var(--text-primary); font-size: 1.1rem;">
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
                        <p>Data from csv_outputs_data_viz.csv</p>
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
                        <div class="stat-card contractors-card" onclick="showContractorsDetail()">
                            <span class="icon">👥</span>
                            <div class="label">Sub-contractors</div>
                            <div class="value" id="unique-contractors">-</div>
                        </div>
                        <div class="stat-card machines-card" onclick="showMachinesDetail()">
                            <span class="icon">🏭</span>
                            <div class="label">Machines</div>
                            <div class="value" id="unique-machines">-</div>
                        </div>
                        <div class="stat-card capacity-card" onclick="showCapacityDetail()">
                            <span class="icon">🔋</span>
                            <div class="label">Total Capacity</div>
                            <div class="value" id="total-capacity">-</div>
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
                                    <th>Sub-contractor</th>
                                    <th>Machine</th>
                                    <th>Net Weight (kg)</th>
                                    <th>Capacity/Day</th>
                                    <th>Ticket No</th>
                                </tr>
                            </thead>
                            <tbody id="data-table-body">
                                <tr>
                                    <td colspan="9" class="loading-state">
                                        <div class="spinner"></div>
                                        <div>Loading all {len(csv_data)} records from csv_outputs_data_viz.csv...</div>
                                        <div style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.7;">
                                            Records will be displayed in descending date order (newest first)
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <script>
                    // Real CSV Data from csv_outputs_data_viz.csv
                    const embeddedCSVData = `{embedded_csv_string}`;
                    
                    console.log('📊 Real CSV Data loaded from csv_outputs_data_viz.csv:', embeddedCSVData.split('\\n').length - 1, 'records');

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

                    // Parse DD-MM-YYYY date format
                    function parseDDMMYYYY(dateStr) {{
                        if (!dateStr) return null;
                        try {{
                            // Handle DD-MM-YYYY format
                            const parts = dateStr.split('-');
                            if (parts.length === 3) {{
                                const day = parseInt(parts[0]);
                                const month = parseInt(parts[1]) - 1; // Month is 0-indexed
                                const year = parseInt(parts[2]);
                                return new Date(year, month, day);
                            }}
                            return new Date(dateStr);
                        }} catch (e) {{
                            console.warn('Error parsing date:', dateStr, e);
                            return null;
                        }}
                    }}

                    // Format date as DD-MM-YYYY
                    function formatDDMMYYYY(date) {{
                        if (!date || isNaN(date.getTime())) return 'N/A';
                        const day = date.getDate().toString().padStart(2, '0');
                        const month = (date.getMonth() + 1).toString().padStart(2, '0');
                        const year = date.getFullYear();
                        return `${{day}}-${{month}}-${{year}}`;
                    }}
                    
                    // Load CSV data using Papa Parse
                    function loadWasteData() {{
                        try {{
                            console.log('🔄 Loading real CSV waste management data from csv_outputs_data_viz.csv...');
                            
                            // Parse CSV using Papa Parse
                            const results = Papa.parse(embeddedCSVData, {{
                                header: true,
                                skipEmptyLines: true,
                                dynamicTyping: false, // Keep as strings first
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

                            // Parse dates and convert numeric fields
                            wasteData.forEach(row => {{
                                // Parse date in DD-MM-YYYY format
                                if (row.date) {{
                                    row.date_parsed = parseDDMMYYYY(row.date);
                                }}
                                
                                // Convert numeric fields
                                if (row.net_weight_calculated) {{
                                    row.net_weight_calculated = parseFloat(row.net_weight_calculated) || 0;
                                }}
                                if (row.Total_capacity_per_day) {{
                                    row.Total_capacity_per_day = parseFloat(row.Total_capacity_per_day) || 0;
                                }}
                            }});
                            
                            console.log(`✅ Loaded ${{wasteData.length}} records from csv_outputs_data_viz.csv`);
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

                        console.log('🔧 Populating filter options from csv_outputs_data_viz.csv...');
                        
                        // Update filter options using actual CSV column names
                        updateFilterOptions('agency-filter', wasteData, 'Agency');
                        updateFilterOptions('cluster-filter', wasteData, 'Cluster');
                        updateFilterOptions('site-filter', wasteData, 'Site');
                        updateFilterOptions('sub-contractor-filter', wasteData, 'Sub_contractor');
                        updateFilterOptions('machine-filter', wasteData, 'Machines');
                        
                        console.log('✅ Filter options populated from csv_outputs_data_viz.csv');
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

                    // Apply filters to CSV data
                    function applyFilters() {{
                        if (!wasteData || wasteData.length === 0) {{
                            showError('No CSV data available to filter');
                            return;
                        }}

                        console.log('🔍 Applying filters to csv_outputs_data_viz.csv...');
                        
                        // Get filter values
                        const filters = {{
                            agency: safeGetValue('agency-filter'),
                            cluster: safeGetValue('cluster-filter'),
                            site: safeGetValue('site-filter'),
                            subContractor: safeGetValue('sub-contractor-filter'),
                            machine: safeGetValue('machine-filter'),
                            startDate: safeGetValue('start-date', ''),
                            endDate: safeGetValue('end-date', '')
                        }};
                        
                        console.log('🔧 Filter values:', filters);
                        
                        // Apply filters using exact column names from CSV
                        filteredData = wasteData.filter(row => {{
                            // Agency filter
                            if (filters.agency !== 'all' && row.Agency !== filters.agency) {{
                                return false;
                            }}
                            
                            // Cluster filter
                            if (filters.cluster !== 'all' && row.Cluster !== filters.cluster) {{
                                return false;
                            }}
                            
                            // Site filter
                            if (filters.site !== 'all' && row.Site !== filters.site) {{
                                return false;
                            }}
                            
                            // Sub-contractor filter
                            if (filters.subContractor !== 'all' && row.Sub_contractor !== filters.subContractor) {{
                                return false;
                            }}
                            
                            // Machine filter
                            if (filters.machine !== 'all' && row.Machines !== filters.machine) {{
                                return false;
                            }}
                            
                            // Date filters
                            if (filters.startDate || filters.endDate) {{
                                if (!row.date_parsed || isNaN(row.date_parsed.getTime())) {{
                                    return false; // Skip invalid dates
                                }}
                                
                                if (filters.startDate && row.date_parsed < new Date(filters.startDate)) {{
                                    return false;
                                }}
                                
                                if (filters.endDate && row.date_parsed > new Date(filters.endDate)) {{
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
                        
                        // Calculate total weight using 'net_weight_calculated' column
                        const totalWeight = filteredData.reduce((sum, row) => {{
                            const weight = row.net_weight_calculated || 0;
                            return sum + weight;
                        }}, 0);
                        
                        // Count unique sub-contractors
                        const uniqueContractors = new Set(
                            filteredData.map(row => row.Sub_contractor)
                                .filter(v => v !== null && v !== undefined && v !== '')
                        ).size;
                        
                        // Count unique machines
                        const uniqueMachines = new Set(
                            filteredData.map(row => row.Machines)
                                .filter(m => m !== null && m !== undefined && m !== '')
                        ).size;
                        
                        // Calculate total capacity
                        const totalCapacity = filteredData.reduce((sum, row) => {{
                            const capacity = row.Total_capacity_per_day || 0;
                            return sum + capacity;
                        }}, 0);
                        
                        // Update stat cards
                        const totalRecordsEl = safeGetElement('total-records');
                        const totalWeightEl = safeGetElement('total-weight');
                        const uniqueContractorsEl = safeGetElement('unique-contractors');
                        const uniqueMachinesEl = safeGetElement('unique-machines');
                        const totalCapacityEl = safeGetElement('total-capacity');
                        
                        if (totalRecordsEl) totalRecordsEl.textContent = totalRecords.toLocaleString();
                        if (totalWeightEl) totalWeightEl.textContent = `${{totalWeight.toLocaleString()}} kg`;
                        if (uniqueContractorsEl) uniqueContractorsEl.textContent = uniqueContractors;
                        if (uniqueMachinesEl) uniqueMachinesEl.textContent = uniqueMachines;
                        if (totalCapacityEl) totalCapacityEl.textContent = totalCapacity.toLocaleString();
                        
                        console.log('📊 Statistics updated:', {{ totalRecords, totalWeight, uniqueContractors, uniqueMachines, totalCapacity }});
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
                                            Available data from csv_outputs_data_viz.csv: ${{wasteData.length}} total records
                                        </div>
                                    </td>
                                </tr>
                            `;
                            return;
                        }}
                        
                        // Sort records by date in DESCENDING order (newest first)
                        const sortedData = [...filteredData].sort((a, b) => {{
                            const dateA = a.date_parsed || new Date(0);
                            const dateB = b.date_parsed || new Date(0);
                            return dateB - dateA; // Descending order (newest first)
                        }});
                        
                        console.log(`📋 Displaying ALL ${{sortedData.length}} records in descending date order`);
                        
                        // Display ALL records (no limit)
                        sortedData.forEach((row, index) => {{
                            const tr = document.createElement('tr');
                            
                            // Format date in DD-MM-YYYY
                            const date = row.date_parsed ? formatDDMMYYYY(row.date_parsed) : (row.date || '-');
                            
                            tr.innerHTML = `
                                <td>${{date}}</td>
                                <td>${{row.Agency || '-'}}</td>
                                <td>${{row.Cluster || '-'}}</td>
                                <td>${{row.Site || '-'}}</td>
                                <td>${{row.Sub_contractor || '-'}}</td>
                                <td>${{row.Machines || '-'}}</td>
                                <td>${{(row.net_weight_calculated || 0).toLocaleString()}}</td>
                                <td>${{(row.Total_capacity_per_day || 0).toLocaleString()}}</td>
                                <td>${{row.ticket_no || '-'}}</td>
                            `;
                            
                            tbody.appendChild(tr);
                        }});
                        
                        console.log(`📋 Table updated with ALL ${{sortedData.length}} records in descending date order`);
                    }}

                    // Reset filters
                    function resetFilters() {{
                        console.log('🔄 Resetting filters...');
                        
                        const agencyFilter = safeGetElement('agency-filter');
                        const clusterFilter = safeGetElement('cluster-filter');
                        const siteFilter = safeGetElement('site-filter');
                        const subContractorFilter = safeGetElement('sub-contractor-filter');
                        const machineFilter = safeGetElement('machine-filter');
                        const startDate = safeGetElement('start-date');
                        const endDate = safeGetElement('end-date');
                        
                        if (agencyFilter) agencyFilter.value = 'all';
                        if (clusterFilter) clusterFilter.value = 'all';
                        if (siteFilter) siteFilter.value = 'all';
                        if (subContractorFilter) subContractorFilter.value = 'all';
                        if (machineFilter) machineFilter.value = 'all';
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
                        const headers = ['Date', 'Agency', 'Cluster', 'Site', 'Sub_contractor', 'Machines', 'net_weight_calculated', 'Total_capacity_per_day', 'ticket_no'];
                        
                        // Sort data by date descending for export as well
                        const sortedDataForExport = [...filteredData].sort((a, b) => {{
                            const dateA = a.date_parsed || new Date(0);
                            const dateB = b.date_parsed || new Date(0);
                            return dateB - dateA; // Descending order (newest first)
                        }});
                        
                        const csvContent = [
                            headers.join(','),
                            ...sortedDataForExport.map(row => [
                                row.date_parsed ? formatDDMMYYYY(row.date_parsed) : (row.date || ''),
                                row.Agency || '',
                                row.Cluster || '',
                                row.Site || '',
                                row.Sub_contractor || '',
                                row.Machines || '',
                                row.net_weight_calculated || '',
                                row.Total_capacity_per_day || '',
                                row.ticket_no || ''
                            ].map(field => `"${{String(field).replace(/"/g, '""')}}"`).join(','))
                        ].join('\\n');
                        
                        // Download file
                        const blob = new Blob([csvContent], {{ type: 'text/csv' }});
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.style.display = 'none';
                        a.href = url;
                        a.download = `filtered_csv_outputs_data_viz_${{new Date().toISOString().split('T')[0]}}.csv`;
                        
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                        
                        console.log(`✅ CSV data exported successfully - ALL ${{filteredData.length}} records in descending date order`);
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
                        const uniqueContractorsEl = safeGetElement('unique-contractors');
                        const uniqueMachinesEl = safeGetElement('unique-machines');
                        const totalCapacityEl = safeGetElement('total-capacity');
                        
                        if (totalRecordsEl) totalRecordsEl.textContent = '-';
                        if (totalWeightEl) totalWeightEl.textContent = '-';
                        if (uniqueContractorsEl) uniqueContractorsEl.textContent = '-';
                        if (uniqueMachinesEl) uniqueMachinesEl.textContent = '-';
                        if (totalCapacityEl) totalCapacityEl.textContent = '-';
                    }}

                    // Event Listeners
                    document.addEventListener('DOMContentLoaded', function() {{
                        console.log('🚀 Initializing dashboard with csv_outputs_data_viz.csv...');
                        
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
                            'agency-filter', 'cluster-filter', 'site-filter', 'sub-contractor-filter', 'machine-filter'
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
                        
                        console.log('✅ Event listeners registered for csv_outputs_data_viz.csv');
                    }});

                    // Placeholder functions for stat card interactions
                    function showRecordsDetail() {{
                        console.log('📊 Records detail clicked');
                    }}
                    
                    function showWeightDetail() {{
                        console.log('⚖️ Weight detail clicked');
                    }}
                    
                    function showContractorsDetail() {{
                        console.log('👥 Sub-contractors detail clicked');
                    }}
                    
                    function showMachinesDetail() {{
                        console.log('🏭 Machines detail clicked');
                    }}

                    function showCapacityDetail() {{
                        console.log('🔋 Capacity detail clicked');
                    }}
                </script>
                
                <!-- Papa Parse Library for CSV parsing -->
                <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
            </main>
            
            <!-- Footer -->
            <footer class="footer">
                <p>© 2025 Swaccha Andhra Corporation • {title} Section • Connected to csv_outputs_data_viz.csv ({len(csv_data)} records) • Date Format: DD-MM-YYYY • All records shown in descending date order • <span id="current-time"></span></p>
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

# Continue with all the existing functions but keep them the same...
# I'll continue with the rest of the functions unchanged since they don't need modification for the data source change

def register_dashboard_flask_routes(server):
    """Register ALL dashboard page routes with csv_outputs_data_viz.csv integration"""
    
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
                return False, redirect('/dashboard')
        except ImportError:
            # RESTRICTIVE fallback
            restrictive_permissions = {
                'viewer': ['dashboard', 'analytics', 'reports'],
                'administrator': ['dashboard', 'analytics', 'reports', 'reviews', 'upload'],
                'super_admin': ['dashboard', 'analytics', 'reports', 'reviews', 'upload', 'forecasting']
            }
            allowed_tabs = restrictive_permissions.get(user_role, ['dashboard'])
            if required_tab not in allowed_tabs:
                return False, redirect('/dashboard')
        
        return True, None
    
    # Main dashboard (always accessible to authenticated users)
    @server.route('/dashboard')
    def admin_dashboard():
        """Main Dashboard Page using csv_outputs_data_viz.csv"""
        if not session.get('swaccha_session_id'):
            return redirect('/login')
        
        theme = get_current_theme()
        return create_empty_themed_page("Dashboard", "📊", theme)

    # Keep all other existing routes the same...
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
        theme = theme_styles["theme"]
        
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
        </head>
        <body style="font-family: 'Inter', sans-serif; background: {theme['primary_bg']}; color: {theme['text_primary']};">
            <div style="text-align: center; padding: 3rem;">
                <h1>📤 Upload Page</h1>
                <p>File upload functionality for csv_outputs_data_viz.csv management</p>
            </div>
        </body>
        </html>
        '''

    @server.route('/data-analytics')
    def admin_data_analytics():
        """Analytics Page using csv_outputs_data_viz.csv"""
        has_access, redirect_response = check_tab_access('analytics')
        if not has_access:
            return redirect_response
        
        theme_name = get_current_theme()
        return create_empty_themed_page("Data Analytics", "📈", theme_name)

    @server.route('/reports')
    def admin_reports():
        """Reports Page using csv_outputs_data_viz.csv"""
        has_access, redirect_response = check_tab_access('reports')
        if not has_access:
            return redirect_response
        
        theme_name = get_current_theme()
        return create_empty_themed_page("Reports", "📋", theme_name)

    @server.route('/reviews')
    def admin_reviews():
        """Reviews Page"""
        has_access, redirect_response = check_tab_access('reviews')
        if not has_access:
            return redirect_response
        
        theme_name = get_current_theme()
        return create_empty_themed_page("Reviews", "⭐", theme_name)

    @server.route('/forecasting')
    def admin_forecasting():
        """Forecasting Page"""
        has_access, redirect_response = check_tab_access('forecasting')
        if not has_access:
            return redirect_response
        
        theme_name = get_current_theme()
        return create_empty_themed_page("Forecasting", "🔮", theme_name)

# Keep all other existing functions unchanged - they don't need modification
def ensure_upload_directory(server):
    """Create upload directory if it doesn't exist"""
    upload_path = server.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_path):
        os.makedirs(upload_path, exist_ok=True)
    logger.info(f"✅ Upload directory ensured: {os.path.abspath(upload_path)}")
    return upload_path

def configure_upload_settings(server):
    """Configure upload settings"""
    server.config.update({
        'UPLOAD_FOLDER': 'uploads',
        'MAX_CONTENT_LENGTH': 50 * 1024 * 1024,  # 50MB max file size
        'UPLOAD_EXTENSIONS': {'.pdf', '.csv', '.xlsx', '.xls'},
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-' + str(hash(os.getcwd())))
    })

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
    
    logger.info(f"🔒 USER ROLE: {user_role}")
    logger.info(f"🔒 ALLOWED TABS: {allowed_tabs}")
    logger.info(f"🔒 VISIBLE TABS: {[t['id'] for t in visible_tabs]}")
    
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
            "border": f"2px solid {theme['brand_primary']}"
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
            "border": f"2px solid {theme.get('error', '#E53E3E')}",
            "backgroundColor": "transparent",
            "color": theme.get('error', '#E53E3E'),
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
            "borderBottom": f"1px solid {theme.get('border_light', theme['accent_bg'])}",
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
    """Create content based on active tab using csv_outputs_data_viz.csv"""
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
                    "Filter and analyze waste management data from csv_outputs_data_viz.csv with advanced controls.",
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
                        "📊 Select filters above and click 'Apply Filters' to view data from csv_outputs_data_viz.csv",
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
    elif active_tab == "tab-reports":
        return create_simple_tab_content("📋 Reports", "Report generation using csv_outputs_data_viz.csv will be available here.", theme_styles)
    elif active_tab == "tab-reviews":
        return create_simple_tab_content("⭐ Reviews", "Customer reviews and feedback will be displayed here.", theme_styles)
    elif active_tab == "tab-forecasting":
        return create_simple_tab_content("🔮 Forecasting", "Predictive analytics using csv_outputs_data_viz.csv will be available here.", theme_styles)
    elif active_tab == "tab-upload":
        return create_simple_tab_content("📤 Upload", "File upload and csv_outputs_data_viz.csv management tools will be available here.", theme_styles)
    else:
        return create_minimal_dashboard_content(theme_styles, user_data)

def create_minimal_dashboard_content(theme_styles, user_data):
    """Create minimal dashboard content using csv_outputs_data_viz.csv"""
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
                "Use filters below to analyze csv_outputs_data_viz.csv data",
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
        
        # ADD FILTER CONTAINER TO MAIN DASHBOARD
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
                create_stat_card("🏢", "Agencies", "3", "active", theme),
                create_stat_card("🗺️", "Clusters", "5", "regions", theme),
                create_stat_card("📍", "Sites", "8", "locations", theme),
                create_stat_card("✅", "Data Records", "433", "entries", theme),
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
        
        # ADD FILTERED DATA DISPLAY AREA
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
                        "📊 Apply filters above to view and analyze csv_outputs_data_viz.csv data",
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
        )
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
    Build the ENHANCED dashboard layout using csv_outputs_data_viz.csv
    
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
                    
                    # Tab content container - NOW INCLUDES csv_outputs_data_viz.csv
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
                                "Dashboard with csv_outputs_data_viz.csv Integration • ",
                                html.Span("🔍", style={"marginLeft": "0.5rem", "marginRight": "0.5rem"}),
                                f"Connected to csv_outputs_data_viz.csv • DD-MM-YYYY Format • Current time: {datetime.now().strftime('%H:%M:%S')}"
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

# Export the main functions
__all__ = [
    'build_enhanced_dashboard',
    'create_tab_content',
    'generate_sample_data',
    'get_embedded_csv_data',
    'get_filter_options_from_embedded_data', 
    'register_enhanced_csv_routes',
    'create_empty_themed_page',
    'register_dashboard_flask_routes',
    'get_current_theme',
    'ensure_upload_directory',
    'configure_upload_settings',
    'create_admin_hero_section',
    'create_navigation_tabs',
    'create_minimal_dashboard_content'
]