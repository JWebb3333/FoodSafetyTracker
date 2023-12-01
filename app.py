import streamlit as st
import pandas as pd
import os
import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_manager import DataManager
from visualization import Visualization
from utils import export_data_to_csv, export_data_to_excel
from auth import setup_auth, check_auth, get_user_info, is_admin
from reports import display_summary_report, display_food_safety_scorecard, export_report_to_excel

# Page configuration
st.set_page_config(
    page_title="Food Contamination Research Database",
    page_icon="🔬",
    layout="wide",
)

# Custom CSS to enhance UI
st.markdown("""
<style>
    .main-header {
        font-family: 'Roboto', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        font-family: 'Roboto', sans-serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: #333333;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .chart-container {
        border-radius: 10px;
        background-color: #FFFFFF;
        padding: 20px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    .stat-card {
        background-color: #F8F9FA;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1E88E5;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #666666;
    }
    
    .data-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .data-table th {
        background-color: #F0F2F6;
        padding: 12px;
        text-align: left;
        font-weight: 600;
    }
    
    .data-table td {
        padding: 10px;
        border-bottom: 1px solid #E0E0E0;
    }
    
    /* Severity levels color coding */
    .severity-low {
        color: #4CAF50;
        font-weight: 500;
    }
    
    .severity-medium {
        color: #FF9800;
        font-weight: 500;
    }
    
    .severity-high {
        color: #F44336;
        font-weight: 500;
    }
    
    /* Improved form styling */
    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Better button styling */
    .stButton button {
        background-color: #1E88E5;
        color: white;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #1565C0;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Temporarily disable authentication for testing
# authenticator, authentication_status, username = setup_auth()
# Set dummy authentication values for testing
st.session_state.authentication_status = True
st.session_state.username = "admin"
st.session_state.name = "Administrator"

# Initialize session state variables if they don't exist
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

if 'visualization' not in st.session_state:
    st.session_state.visualization = Visualization()

# Check if authenticated
if check_auth():
    # Display user information and logout button in sidebar
    user_info = get_user_info()
    
    # Title and description
    st.markdown("<h1 class='main-header'>Food Contamination Research Database</h1>", unsafe_allow_html=True)
    st.markdown(f"""
    Welcome, **{user_info['name']}**! This application helps researchers collect, analyze, and document food contamination incidents.
    Use the navigation sidebar to access different features.
    """)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", 
                        ["Dashboard", "Data Entry", "Search & Filter", "Visualization", "Export & Reports", "Documentation & Help"])

# Dashboard page
if page == "Dashboard":
    st.markdown("<h2 class='sub-header'>Dashboard</h2>", unsafe_allow_html=True)
    
    # Summary statistics
    data = st.session_state.data_manager.get_data()
    
    if data.empty:
        st.info("No data available yet. Use the Data Entry page to add contamination incidents.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Incidents", len(data))
        with col2:
            st.metric("Unique Locations", data['location'].nunique())
        with col3:
            st.metric("Food Types", data['food_type'].nunique())
        
        # Recent incidents
        st.subheader("Recent Incidents")
        st.dataframe(data.sort_values(by='date', ascending=False).head(5))
        
        # Quick visualization
        st.subheader("Contamination by Severity")
        fig = st.session_state.visualization.create_severity_chart(data)
        st.plotly_chart(fig, use_container_width=True)

# Data Entry page
elif page == "Data Entry":
    st.markdown("<h2 class='sub-header'>Add New Contamination Incident</h2>", unsafe_allow_html=True)
    
    with st.form("contamination_form"):
        # Basic information
        st.subheader("Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date of Incident", datetime.date.today())
        with col2:
            location = st.text_input("Location (City, State/Province, Country)")
        
        # Geographic coordinates (optional)
        st.markdown("##### Geographic Coordinates (Optional)")
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0, 
                                       help="Enter latitude value between -90 and 90")
        with col2:
            longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0,
                                       help="Enter longitude value between -180 and 180")
        use_coordinates = st.checkbox("Include geographic coordinates", value=False)
        
        # Food details
        st.subheader("Food Details")
        food_type = st.selectbox("Food Type", [
            "Meat", "Poultry", "Seafood", "Dairy", "Produce", 
            "Grains", "Processed Foods", "Beverages", "Other"
        ])
        if food_type == "Other":
            food_type_other = st.text_input("Specify Food Type")
        else:
            food_type_other = None
        
        # Contamination details
        st.subheader("Contamination Details")
        contaminant_type = st.selectbox("Contaminant Type", [
            "Bacterial", "Viral", "Parasitic", "Chemical", "Physical", 
            "Allergen", "Natural Toxin", "Other"
        ])
        if contaminant_type == "Other":
            contaminant_type_other = st.text_input("Specify Contaminant Type")
        else:
            contaminant_type_other = None
        
        specific_contaminant = st.text_input("Specific Contaminant (e.g., E. coli, Salmonella, etc.)")
        
        # Detection method
        detection_method = st.selectbox("Detection Method", [
            "Laboratory Testing", "Visual Inspection", "Consumer Report", 
            "Routine Monitoring", "Surveillance Program", "Other"
        ])
        
        # Severity and impact
        st.subheader("Severity and Impact")
        severity = st.slider("Severity Level", 1, 5, 3, 
                            help="1 = Minimal risk, 5 = Severe health risk")
        
        affected_population = st.text_input("Affected Population", 
                                          help="Number or demographic of people affected, if known")
        
        economic_impact = st.text_input("Economic Impact", 
                                       help="Estimated economic cost, if known (e.g., $10,000)")
        
        # Response information
        st.subheader("Response Information")
        regulatory_action = st.text_area("Regulatory Action", height=80,
                                        help="Any actions taken by regulatory bodies (e.g., recalls, warnings)")
        
        corrective_measures = st.text_area("Corrective Measures", height=80,
                                         help="Steps taken to address the contamination")
        
        # Description
        st.subheader("Additional Information")
        description = st.text_area("Description of Incident", 
                                height=100, 
                                help="Include details about how the contamination was discovered, impacts, etc.")
        
        # Source information
        source = st.text_input("Source of Information (e.g., research paper, health department report)")
        
        # Submit button
        submitted = st.form_submit_button("Save Incident")
        
        if submitted:
            # Process form data
            data_dict = {
                "date": date.strftime("%Y-%m-%d"),
                "location": location,
                "food_type": food_type_other if food_type == "Other" else food_type,
                "contaminant_type": contaminant_type_other if contaminant_type == "Other" else contaminant_type,
                "specific_contaminant": specific_contaminant,
                "severity": severity,
                "description": description,
                "source": source,
                "detection_method": detection_method,
                "affected_population": affected_population,
                "regulatory_action": regulatory_action,
                "economic_impact": economic_impact,
                "corrective_measures": corrective_measures
            }
            
            # Add geographic coordinates if checkbox is selected
            if use_coordinates:
                data_dict["latitude"] = latitude
                data_dict["longitude"] = longitude
            
            # Validate required fields
            if not location or (food_type == "Other" and not food_type_other) or \
               (contaminant_type == "Other" and not contaminant_type_other):
                st.error("Please fill in all required fields.")
            else:
                # Save data
                st.session_state.data_manager.add_entry(data_dict)
                st.success("Contamination incident successfully recorded!")

# Search & Filter page
elif page == "Search & Filter":
    st.markdown("<h2 class='sub-header'>Search & Filter Contamination Data</h2>", unsafe_allow_html=True)
    
    data = st.session_state.data_manager.get_data()
    
    if data.empty:
        st.info("No data available yet. Use the Data Entry page to add contamination incidents.")
    else:
        # Simple search by text
        search_term = st.text_input("Search by any field", "")
        
        # Advanced filters
        st.subheader("Advanced Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Date range filter
            date_range = st.date_input(
                "Date Range",
                value=(data['date'].min() if not data.empty else datetime.date.today(),
                       data['date'].max() if not data.empty else datetime.date.today()),
                key="date_range"
            )
        
        with col2:
            # Food type filter
            food_types = ['All'] + sorted(data['food_type'].unique().tolist())
            food_filter = st.selectbox("Food Type", food_types)
        
        with col3:
            # Contaminant type filter
            contaminant_types = ['All'] + sorted(data['contaminant_type'].unique().tolist())
            contaminant_filter = st.selectbox("Contaminant Type", contaminant_types)
        
        # Severity filter
        severity_range = st.slider(
            "Severity Range", 
            int(data['severity'].min() if not data.empty else 1),
            int(data['severity'].max() if not data.empty else 5),
            (int(data['severity'].min() if not data.empty else 1), 
             int(data['severity'].max() if not data.empty else 5))
        )
        
        # Filter data based on user selections
        filtered_data = data.copy()
        
        # Apply text search if provided
        if search_term:
            filtered_data = filtered_data[filtered_data.astype(str).apply(
                lambda row: row.str.contains(search_term, case=False).any(), axis=1)]
        
        # Apply date filter
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_data = filtered_data[(filtered_data['date'] >= start_date.strftime('%Y-%m-%d')) & 
                                         (filtered_data['date'] <= end_date.strftime('%Y-%m-%d'))]
        
        # Apply food type filter
        if food_filter != 'All':
            filtered_data = filtered_data[filtered_data['food_type'] == food_filter]
        
        # Apply contaminant filter
        if contaminant_filter != 'All':
            filtered_data = filtered_data[filtered_data['contaminant_type'] == contaminant_filter]
        
        # Apply severity filter
        filtered_data = filtered_data[(filtered_data['severity'] >= severity_range[0]) & 
                                     (filtered_data['severity'] <= severity_range[1])]
        
        # Display results
        st.subheader(f"Results: {len(filtered_data)} incidents found")
        if not filtered_data.empty:
            st.dataframe(filtered_data, use_container_width=True)
        else:
            st.warning("No results match your search criteria.")

# Visualization page
elif page == "Visualization":
    st.markdown("<h2 class='sub-header'>Data Visualization</h2>", unsafe_allow_html=True)
    
    data = st.session_state.data_manager.get_data()
    
    if data.empty:
        st.info("No data available yet. Use the Data Entry page to add contamination incidents.")
    else:
        # Choose visualization type
        viz_type = st.selectbox(
            "Select Visualization",
            ["Contamination by Food Type", 
             "Contamination by Location", 
             "Severity Distribution", 
             "Contamination Over Time",
             "Contaminant Types Distribution",
             "Severity by Food Type",
             "Contaminant by Food Heatmap",
             "Severity by Month",
             "Geographic Distribution",
             "Contamination Tree Map",
             "Severity by Contaminant Type"]
        )
        
        if viz_type == "Contamination by Food Type":
            fig = st.session_state.visualization.create_food_type_chart(data)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Contamination by Location":
            fig = st.session_state.visualization.create_location_chart(data)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Severity Distribution":
            fig = st.session_state.visualization.create_severity_chart(data)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Contamination Over Time":
            fig = st.session_state.visualization.create_time_series_chart(data)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Contaminant Types Distribution":
            fig = st.session_state.visualization.create_contaminant_type_chart(data)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Severity by Food Type":
            fig = st.session_state.visualization.create_severity_by_food_chart(data)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Contaminant by Food Heatmap":
            fig = st.session_state.visualization.create_contaminant_by_food_heatmap(data)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Severity by Month":
            fig = st.session_state.visualization.create_severity_by_month_chart(data)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Geographic Distribution":
            st.info("Note: This visualization requires latitude and longitude data. If you've added this data, it will be displayed on a map.")
            fig = st.session_state.visualization.create_geographic_scatter_chart(data)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Contamination Tree Map":
            fig = st.session_state.visualization.create_contamination_tree_map(data)
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "Severity by Contaminant Type":
            fig = st.session_state.visualization.create_severity_distribution_by_contaminant(data)
            st.plotly_chart(fig, use_container_width=True)
        
        # Visualization description
        st.markdown("### Insights")
        st.write("Use these visualizations to identify patterns in contamination incidents.")

# Export & Reports page
elif page == "Export & Reports":
    st.markdown("<h2 class='sub-header'>Export & Reports</h2>", unsafe_allow_html=True)
    
    data = st.session_state.data_manager.get_data()
    
    if data.empty:
        st.info("No data available yet. Use the Data Entry page to add contamination incidents.")
    else:
        # Create tabs for different report functions
        report_tabs = st.tabs(["Export Data", "Standard Reports", "Advanced Reports", "Custom Reports"])
        
        with report_tabs[0]:  # Export Data
            st.subheader("Export Data")
            
            # Export options
            export_format = st.radio("Select export format:", ["CSV", "Excel"])
            
            # Filter options for export
            include_all = st.checkbox("Include all data", value=True)
            
            if not include_all:
                st.write("Select data to include:")
                
                # Date range filter
                date_range = st.date_input(
                    "Date Range",
                    value=(data['date'].min(), data['date'].max()),
                    key="export_date_range"
                )
                
                # Food type filter
                food_types = sorted(data['food_type'].unique().tolist())
                selected_food_types = st.multiselect("Food Types", food_types, default=food_types)
                
                # Apply filters
                filtered_data = data.copy()
                
                # Apply date filter
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    start_date, end_date = date_range
                    filtered_data = filtered_data[(filtered_data['date'] >= start_date.strftime('%Y-%m-%d')) & 
                                                (filtered_data['date'] <= end_date.strftime('%Y-%m-%d'))]
                
                # Apply food type filter
                if selected_food_types:
                    filtered_data = filtered_data[filtered_data['food_type'].isin(selected_food_types)]
                
                export_data = filtered_data
            else:
                export_data = data
            
            # Preview data
            st.subheader("Data Preview")
            st.dataframe(export_data.head(5), use_container_width=True)
            
            # Export buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if export_format == "CSV":
                    if st.button("Export to CSV"):
                        csv_data = export_data_to_csv(export_data)
                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name=f"food_contamination_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                else:  # Excel
                    if st.button("Export to Excel"):
                        excel_data = export_data_to_excel(export_data)
                        st.download_button(
                            label="Download Excel",
                            data=excel_data,
                            file_name=f"food_contamination_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
        
        with report_tabs[1]:  # Standard Reports
            st.subheader("Standard Reports")
            
            report_type = st.selectbox(
                "Select Report Type",
                ["Summary Report", "Detailed Incident Report", "Trend Analysis"]
            )
            
            # Report date range
            st.markdown("##### Select Report Date Range")
            report_date_range = st.date_input(
                "Date Range",
                value=(data['date'].min(), data['date'].max()),
                key="report_date_range"
            )
            
            # Filter data for report
            report_data = data.copy()
            if isinstance(report_date_range, tuple) and len(report_date_range) == 2:
                start_date, end_date = report_date_range
                report_data = report_data[(report_data['date'] >= start_date.strftime('%Y-%m-%d')) & 
                                         (report_data['date'] <= end_date.strftime('%Y-%m-%d'))]
            
            # Generate report button
            col1, col2 = st.columns([3, 1])
            with col2:
                generate_report = st.button("Generate Report")
                export_report = st.download_button(
                    label="Export Report to Excel",
                    data=export_report_to_excel(report_data, report_type) if not report_data.empty else b"",
                    file_name=f"{report_type.replace(' ', '_').lower()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    disabled=report_data.empty
                )
            
            # Display different report types
            if report_data.empty:
                st.info("No data available for the selected date range.")
            elif generate_report:
                if report_type == "Summary Report":
                    # Summary report
                    display_summary_report(report_data)
                    
                elif report_type == "Detailed Incident Report":
                    # Detailed incident report
                    st.markdown("## Detailed Food Contamination Incident Report")
                    st.markdown(f"**Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(f"**Report Period:** {report_date_range[0]} to {report_date_range[1]}")
                    st.markdown(f"**Total Incidents:** {len(report_data)}")
                    st.markdown("---")
                    
                    for _, row in report_data.iterrows():
                        st.markdown(f"### Incident on {row['date']}")
                        
                        # Create columns for basic info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**Location:** {row['location']}")
                            st.markdown(f"**Food Type:** {row['food_type']}")
                        with col2:
                            st.markdown(f"**Contaminant Type:** {row['contaminant_type']}")
                            st.markdown(f"**Specific Contaminant:** {row['specific_contaminant']}")
                        with col3:
                            st.markdown(f"**Severity:** {row['severity']}/5")
                            st.markdown(f"**Detection Method:** {row.get('detection_method', 'Not recorded')}")
                        
                        # Additional details
                        st.markdown("##### Impact Information")
                        
                        if 'affected_population' in row and row['affected_population']:
                            st.markdown(f"**Affected Population:** {row['affected_population']}")
                        
                        if 'economic_impact' in row and row['economic_impact']:
                            st.markdown(f"**Economic Impact:** {row['economic_impact']}")
                        
                        # Response information
                        if 'regulatory_action' in row and row['regulatory_action']:
                            st.markdown("##### Response Information")
                            st.markdown(f"**Regulatory Action:** {row['regulatory_action']}")
                        
                        if 'corrective_measures' in row and row['corrective_measures']:
                            st.markdown(f"**Corrective Measures:** {row['corrective_measures']}")
                        
                        # Description and source
                        st.markdown("##### Additional Information")
                        st.markdown(f"**Description:** {row['description']}")
                        st.markdown(f"**Source:** {row['source']}")
                        st.markdown("---")
                
                elif report_type == "Trend Analysis":
                    # Trend analysis report
                    st.markdown("## Food Contamination Trend Analysis")
                    st.markdown(f"**Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(f"**Analysis period:** {report_data['date'].min()} to {report_data['date'].max()}")
                    st.markdown(f"**Total incidents:** {len(report_data)}")
                    
                    # Time series chart
                    st.markdown("### Contamination Incidents Over Time")
                    fig = st.session_state.visualization.create_time_series_chart(report_data)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Year-over-year comparison if data spans multiple years
                    years = pd.to_datetime(report_data['date']).dt.year.unique()
                    if len(years) > 1:
                        st.markdown("### Year-Over-Year Comparison")
                        # Convert date to datetime
                        report_data['date_dt'] = pd.to_datetime(report_data['date'])
                        report_data['month'] = report_data['date_dt'].dt.month
                        report_data['year'] = report_data['date_dt'].dt.year
                        report_data['month_name'] = report_data['date_dt'].dt.strftime('%b')
                        
                        # Group by year and month
                        monthly_counts = report_data.groupby(['year', 'month', 'month_name']).size().reset_index()
                        monthly_counts.columns = ['Year', 'Month', 'Month Name', 'Count']
                        
                        # Create a line chart for each year
                        import plotly.graph_objects as go
                        fig = go.Figure()
                        
                        for year in sorted(years):
                            year_data = monthly_counts[monthly_counts['Year'] == year]
                            if not year_data.empty:
                                # Sort by month
                                year_data = year_data.sort_values('Month')
                                fig.add_trace(go.Scatter(
                                    x=year_data['Month Name'],
                                    y=year_data['Count'],
                                    mode='lines+markers',
                                    name=str(year)
                                ))
                        
                        fig.update_layout(
                            xaxis_title="Month",
                            yaxis_title="Number of Incidents",
                            legend_title="Year"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Two columns for severity and contaminants
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Severity by food type
                        st.markdown("### Average Severity by Food Type")
                        severity_by_food = report_data.groupby('food_type')['severity'].mean().reset_index()
                        severity_by_food.columns = ['Food Type', 'Average Severity']
                        severity_by_food = severity_by_food.sort_values('Average Severity', ascending=False)
                        
                        # Create a bar chart
                        fig = px.bar(severity_by_food, 
                                   x='Food Type', 
                                   y='Average Severity',
                                   color='Average Severity',
                                   text='Average Severity',
                                   color_continuous_scale=px.colors.sequential.Viridis)
                        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                        fig.update_layout(yaxis_range=[0, 5])
                        st.plotly_chart(fig, use_container_width=True)
                        st.dataframe(severity_by_food)
                    
                    with col2:
                        # Most common contaminants
                        st.markdown("### Most Common Contaminants")
                        common_contaminants = report_data['specific_contaminant'].value_counts().head(10).reset_index()
                        common_contaminants.columns = ['Contaminant', 'Count']
                        
                        # Create a bar chart
                        fig = px.bar(common_contaminants, 
                                   x='Contaminant', 
                                   y='Count',
                                   color='Count',
                                   text='Count',
                                   color_continuous_scale=px.colors.sequential.Viridis)
                        fig.update_traces(texttemplate='%{text}', textposition='outside')
                        st.plotly_chart(fig, use_container_width=True)
                        st.dataframe(common_contaminants)
        
        with report_tabs[2]:  # Advanced Reports
            st.subheader("Advanced Reports")
            
            advanced_report_type = st.selectbox(
                "Select Advanced Report Type",
                ["Food Safety Scorecard", "Geographic Report", "Time Analysis"]
            )
            
            # Report date range
            st.markdown("##### Select Report Date Range")
            advanced_report_date_range = st.date_input(
                "Date Range",
                value=(data['date'].min(), data['date'].max()),
                key="advanced_report_date_range"
            )
            
            # Filter data for report
            advanced_report_data = data.copy()
            if isinstance(advanced_report_date_range, tuple) and len(advanced_report_date_range) == 2:
                start_date, end_date = advanced_report_date_range
                advanced_report_data = advanced_report_data[(advanced_report_data['date'] >= start_date.strftime('%Y-%m-%d')) & 
                                                          (advanced_report_data['date'] <= end_date.strftime('%Y-%m-%d'))]
            
            # Generate report button
            col1, col2 = st.columns([3, 1])
            with col2:
                generate_advanced_report = st.button("Generate Advanced Report")
                export_advanced_report = st.download_button(
                    label="Export Report to Excel",
                    data=export_report_to_excel(advanced_report_data, advanced_report_type) if not advanced_report_data.empty else b"",
                    file_name=f"{advanced_report_type.replace(' ', '_').lower()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    disabled=advanced_report_data.empty
                )
            
            # Display different report types
            if advanced_report_data.empty:
                st.info("No data available for the selected date range.")
            elif generate_advanced_report:
                if advanced_report_type == "Food Safety Scorecard":
                    # Food safety scorecard
                    display_food_safety_scorecard(advanced_report_data)
                
                elif advanced_report_type == "Geographic Report":
                    # Check if latitude and longitude exist
                    if 'latitude' not in advanced_report_data.columns or 'longitude' not in advanced_report_data.columns:
                        st.warning("Geographic data (latitude/longitude) is not available. Please add this data to incidents for a geographic report.")
                    else:
                        # Filter out rows without coordinates
                        geo_data = advanced_report_data.dropna(subset=['latitude', 'longitude'])
                        
                        if geo_data.empty:
                            st.warning("No geographic coordinates found in the selected data.")
                        else:
                            st.markdown("## Geographic Distribution Report")
                            st.markdown(f"**Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            st.markdown(f"**Report Period:** {advanced_report_date_range[0]} to {advanced_report_date_range[1]}")
                            
                            # Map visualization
                            st.markdown("### Geographic Distribution of Contamination Incidents")
                            fig = st.session_state.visualization.create_geographic_scatter_chart(geo_data)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Group by location
                            location_counts = geo_data.groupby(['location', 'latitude', 'longitude']).size().reset_index()
                            location_counts.columns = ['Location', 'Latitude', 'Longitude', 'Incident Count']
                            
                            # Calculate average severity by location
                            severity_by_location = geo_data.groupby('location')['severity'].mean().reset_index()
                            severity_by_location.columns = ['Location', 'Average Severity']
                            
                            # Merge counts and severity
                            geo_report = pd.merge(location_counts, severity_by_location, on='Location', how='left')
                            
                            # Display table of locations with incident counts
                            st.markdown("### Contamination Incidents by Location")
                            st.dataframe(geo_report.sort_values('Incident Count', ascending=False), use_container_width=True)
                
                elif advanced_report_type == "Time Analysis":
                    # Time analysis report
                    st.markdown("## Time Analysis Report")
                    st.markdown(f"**Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(f"**Analysis period:** {advanced_report_data['date'].min()} to {advanced_report_data['date'].max()}")
                    
                    # Convert date to datetime
                    advanced_report_data['date_dt'] = pd.to_datetime(advanced_report_data['date'])
                    
                    # Extract month and year
                    advanced_report_data['month'] = advanced_report_data['date_dt'].dt.month
                    advanced_report_data['year'] = advanced_report_data['date_dt'].dt.year
                    advanced_report_data['month_name'] = advanced_report_data['date_dt'].dt.strftime('%b')
                    advanced_report_data['month_year'] = advanced_report_data['date_dt'].dt.strftime('%b %Y')
                    
                    # Incidents by month
                    monthly_incidents = advanced_report_data.groupby(['year', 'month', 'month_name']).size().reset_index()
                    monthly_incidents.columns = ['Year', 'Month', 'Month Name', 'Count']
                    monthly_incidents = monthly_incidents.sort_values(['Year', 'Month'])
                    
                    # Average severity by month
                    severity_by_month = advanced_report_data.groupby(['year', 'month', 'month_name'])['severity'].mean().reset_index()
                    severity_by_month.columns = ['Year', 'Month', 'Month Name', 'Average Severity']
                    severity_by_month = severity_by_month.sort_values(['Year', 'Month'])
                    
                    # Create a time series with both incident count and severity
                    st.markdown("### Contamination Incidents Over Time")
                    
                    # Create a figure with two y-axes
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    
                    # Create trace for incident counts
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    
                    # Add traces
                    fig.add_trace(
                        go.Scatter(
                            x=monthly_incidents['Month Name'] + ' ' + monthly_incidents['Year'].astype(str),
                            y=monthly_incidents['Count'],
                            name="Incident Count",
                            line=dict(color='blue')
                        ),
                        secondary_y=False,
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=severity_by_month['Month Name'] + ' ' + severity_by_month['Year'].astype(str),
                            y=severity_by_month['Average Severity'],
                            name="Average Severity",
                            line=dict(color='red')
                        ),
                        secondary_y=True,
                    )
                    
                    # Add figure title
                    fig.update_layout(
                        title_text="Contamination Incidents and Severity Over Time",
                        xaxis=dict(
                            title="Month",
                            tickangle=45
                        )
                    )
                    
                    # Set y-axes titles
                    fig.update_yaxes(title_text="Incident Count", secondary_y=False)
                    fig.update_yaxes(title_text="Average Severity", secondary_y=True)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Seasonal analysis - group by month
                    st.markdown("### Seasonal Patterns")
                    monthly_pattern = advanced_report_data.groupby('month_name')['severity'].agg(['mean', 'count']).reset_index()
                    monthly_pattern.columns = ['Month', 'Average Severity', 'Incident Count']
                    
                    # Sort by month order
                    month_order = {
                        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                    }
                    monthly_pattern['month_num'] = monthly_pattern['Month'].map(month_order)
                    monthly_pattern = monthly_pattern.sort_values('month_num')
                    
                    # Create bar chart
                    import plotly.graph_objects as go
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=monthly_pattern['Month'],
                        y=monthly_pattern['Incident Count'],
                        name='Incident Count',
                        marker_color='royalblue'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=monthly_pattern['Month'],
                        y=monthly_pattern['Average Severity'],
                        name='Average Severity',
                        marker_color='crimson',
                        mode='lines+markers',
                        yaxis='y2'
                    ))
                    
                    # Create a secondary Y axis
                    fig.update_layout(
                        title_text='Seasonal Patterns in Contamination Incidents',
                        yaxis=dict(
                            title='Incident Count',
                            side='left'
                        ),
                        yaxis2=dict(
                            title='Average Severity',
                            overlaying='y',
                            side='right',
                            rangemode='normal',
                            range=[0, 5]
                        ),
                        xaxis=dict(
                            title='Month'
                        ),
                        legend=dict(
                            x=0,
                            y=1,
                            bgcolor='rgba(255, 255, 255, 0)',
                            bordercolor='rgba(255, 255, 255, 0)'
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display data tables
                    st.markdown("### Monthly Data")
                    st.dataframe(monthly_pattern[['Month', 'Incident Count', 'Average Severity']], use_container_width=True)
        
        with report_tabs[3]:  # Custom Reports
            st.subheader("Custom Reports")
            
            st.markdown("""
            Build a custom report by selecting specific report components and filters.
            This allows you to create focused reports tailored to your specific research needs.
            """)
            
            # Filter data for custom report
            st.markdown("##### Select Data Range and Filters")
            custom_date_range = st.date_input(
                "Date Range",
                value=(data['date'].min(), data['date'].max()),
                key="custom_date_range"
            )
            
            # Row for filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Food type filter
                all_food_types = sorted(data['food_type'].unique().tolist())
                selected_food_types = st.multiselect("Food Types", all_food_types, 
                                                  default=all_food_types if len(all_food_types) <= 3 else all_food_types[:3])
            
            with col2:
                # Contaminant filter
                all_contaminant_types = sorted(data['contaminant_type'].unique().tolist())
                selected_contaminant_types = st.multiselect("Contaminant Types", all_contaminant_types,
                                                          default=all_contaminant_types if len(all_contaminant_types) <= 3 else all_contaminant_types[:3])
            
            with col3:
                # Severity filter
                min_severity = int(data['severity'].min()) if not data.empty else 1
                max_severity = int(data['severity'].max()) if not data.empty else 5
                severity_range = st.slider("Severity Range", min_severity, max_severity, (min_severity, max_severity))
            
            # Filter data based on selections
            custom_report_data = data.copy()
            
            # Apply date filter
            if isinstance(custom_date_range, tuple) and len(custom_date_range) == 2:
                start_date, end_date = custom_date_range
                custom_report_data = custom_report_data[(custom_report_data['date'] >= start_date.strftime('%Y-%m-%d')) & 
                                                      (custom_report_data['date'] <= end_date.strftime('%Y-%m-%d'))]
            
            # Apply food type filter
            if selected_food_types:
                custom_report_data = custom_report_data[custom_report_data['food_type'].isin(selected_food_types)]
            
            # Apply contaminant filter
            if selected_contaminant_types:
                custom_report_data = custom_report_data[custom_report_data['contaminant_type'].isin(selected_contaminant_types)]
            
            # Apply severity filter
            custom_report_data = custom_report_data[(custom_report_data['severity'] >= severity_range[0]) & 
                                                 (custom_report_data['severity'] <= severity_range[1])]
            
            # Select report components
            st.markdown("##### Select Report Components")
            
            # Two columns for component selection
            col1, col2 = st.columns(2)
            
            with col1:
                include_summary = st.checkbox("Summary Statistics", value=True)
                include_by_food = st.checkbox("Incidents by Food Type", value=True)
                include_by_contaminant = st.checkbox("Incidents by Contaminant", value=True)
                include_severity_dist = st.checkbox("Severity Distribution", value=True)
                include_recent = st.checkbox("Recent Incidents", value=True)
            
            with col2:
                include_time_series = st.checkbox("Time Series Analysis", value=True)
                include_geo = st.checkbox("Geographic Distribution", value=True)
                include_food_safety = st.checkbox("Food Safety Metrics", value=False)
                include_seasonal = st.checkbox("Seasonal Analysis", value=False)
                include_detailed = st.checkbox("Detailed Incident List", value=False)
            
            # Generate report button
            generate_custom_report = st.button("Generate Custom Report")
            
            # Display custom report
            if generate_custom_report:
                if custom_report_data.empty:
                    st.warning("No data available for the selected filters.")
                else:
                    st.markdown("## Custom Contamination Analysis Report")
                    st.markdown(f"**Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(f"**Analysis period:** {custom_report_data['date'].min()} to {custom_report_data['date'].max()}")
                    st.markdown(f"**Total incidents:** {len(custom_report_data)}")
                    st.markdown("---")
                    
                    # Create report components based on selections
                    
                    # Summary Statistics
                    if include_summary:
                        st.markdown("### Summary Statistics")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Incidents", len(custom_report_data))
                        with col2:
                            st.metric("Unique Locations", custom_report_data['location'].nunique())
                        with col3:
                            st.metric("Food Types", custom_report_data['food_type'].nunique())
                        with col4:
                            st.metric("Avg. Severity", round(custom_report_data['severity'].mean(), 2))
                    
                    # Incidents by Food Type
                    if include_by_food and len(custom_report_data) > 0:
                        st.markdown("### Incidents by Food Type")
                        fig = st.session_state.visualization.create_food_type_chart(custom_report_data)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Incidents by Contaminant
                    if include_by_contaminant and len(custom_report_data) > 0:
                        st.markdown("### Incidents by Contaminant Type")
                        fig = st.session_state.visualization.create_contaminant_type_chart(custom_report_data)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Severity Distribution
                    if include_severity_dist and len(custom_report_data) > 0:
                        st.markdown("### Severity Distribution")
                        fig = st.session_state.visualization.create_severity_chart(custom_report_data)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Two column layout for next section
                    if include_time_series or include_recent:
                        col1, col2 = st.columns([3, 2])
                        
                        with col1:
                            # Time Series Analysis
                            if include_time_series and len(custom_report_data) > 1:
                                st.markdown("### Contamination Over Time")
                                fig = st.session_state.visualization.create_time_series_chart(custom_report_data)
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Recent Incidents
                            if include_recent and len(custom_report_data) > 0:
                                st.markdown("### Recent Incidents")
                                recent = custom_report_data.sort_values(by='date', ascending=False).head(5)
                                st.dataframe(recent, use_container_width=True)
                    
                    # Geographic Distribution
                    if include_geo and 'latitude' in custom_report_data.columns and 'longitude' in custom_report_data.columns:
                        geo_data = custom_report_data.dropna(subset=['latitude', 'longitude'])
                        if not geo_data.empty:
                            st.markdown("### Geographic Distribution")
                            fig = st.session_state.visualization.create_geographic_scatter_chart(geo_data)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No geographic data available for the selected incidents.")
                    
                    # Food Safety Metrics
                    if include_food_safety and len(custom_report_data) > 0:
                        st.markdown("### Food Safety Metrics")
                        
                        # High risk foods (foods with highest average severity)
                        high_risk_foods = custom_report_data.groupby('food_type')['severity'].agg(['mean', 'count']).reset_index()
                        high_risk_foods.columns = ['Food Type', 'Average Severity', 'Incident Count']
                        high_risk_foods = high_risk_foods[high_risk_foods['Incident Count'] >= 1]
                        high_risk_foods = high_risk_foods.sort_values('Average Severity', ascending=False).head(5)
                        
                        if not high_risk_foods.empty:
                            st.markdown("#### Highest Risk Foods")
                            fig = px.bar(high_risk_foods, 
                                       x="Food Type", y="Average Severity", 
                                       color="Incident Count",
                                       text="Average Severity",
                                       color_continuous_scale=px.colors.sequential.Viridis)
                            fig.update_layout(yaxis_range=[0, 5])
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Seasonal Analysis
                    if include_seasonal and len(custom_report_data) > 0:
                        st.markdown("### Seasonal Analysis")
                        
                        # Convert date to datetime
                        custom_report_data['date_dt'] = pd.to_datetime(custom_report_data['date'])
                        custom_report_data['month_name'] = custom_report_data['date_dt'].dt.strftime('%b')
                        
                        # Create monthly aggregates
                        monthly_data = custom_report_data.groupby('month_name').agg({
                            'severity': ['mean', 'median', 'std'],
                            'date': 'count'
                        })
                        monthly_data.columns = ['Avg Severity', 'Median Severity', 'Std Deviation', 'Incident Count']
                        monthly_data = monthly_data.reset_index()
                        
                        # Sort by month order
                        month_order = {
                            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                        }
                        monthly_data['month_num'] = monthly_data['month_name'].map(month_order)
                        monthly_data = monthly_data.sort_values('month_num')
                        
                        # Display heatmap
                        fig = st.session_state.visualization.create_severity_by_month_chart(custom_report_data)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Display table
                        st.dataframe(monthly_data[['month_name', 'Incident Count', 'Avg Severity', 'Median Severity']], use_container_width=True)
                    
                    # Detailed Incident List
                    if include_detailed and len(custom_report_data) > 0:
                        st.markdown("### Detailed Incident List")
                        st.dataframe(custom_report_data.sort_values(by='date', ascending=False), use_container_width=True)

# Documentation & Help page
elif page == "Documentation & Help":
    st.markdown("<h2 class='sub-header'>Documentation & Help</h2>", unsafe_allow_html=True)
    
    # Create tabs for different documentation sections
    doc_tabs = st.tabs(["Getting Started", "Data Entry Guide", "Search Tips", "Visualization Guide", "Export Guide", "FAQ"])
    
    with doc_tabs[0]:  # Getting Started
        st.markdown("<h3 class='sub-header'>Getting Started</h3>", unsafe_allow_html=True)
        st.markdown("""
        ### Welcome to the Food Contamination Research Database
        
        This application helps researchers collect, analyze, and document food contamination incidents. 
        Here's how to get started:
        
        1. **Dashboard**: View summary statistics and recent incidents
        2. **Data Entry**: Add new contamination incidents to the database
        3. **Search & Filter**: Find specific contamination incidents
        4. **Visualization**: Create visual representations of your data
        5. **Export & Reports**: Generate reports and export data
        
        Use the navigation sidebar on the left to move between these sections.
        """)
        
        # SVG workflow diagram
        workflow_svg = """
        <svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
            <style>
                .box { fill: #f0f8ff; stroke: #2c3e50; stroke-width: 2; }
                .arrow { stroke: #2c3e50; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
                .title { font-family: Arial; font-size: 16px; font-weight: bold; text-anchor: middle; }
                .desc { font-family: Arial; font-size: 12px; text-anchor: middle; }
                .heading { font-family: Arial; font-size: 24px; font-weight: bold; text-anchor: middle; }
            </style>
            
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#2c3e50" />
                </marker>
            </defs>
            
            <rect width="100%" height="100%" fill="#ffffff" />
            
            <text x="400" y="40" class="heading">Food Contamination Research Database Workflow</text>
            
            <!-- Dashboard -->
            <rect x="100" y="80" width="160" height="80" rx="5" class="box" />
            <text x="180" y="110" class="title">Dashboard</text>
            <text x="180" y="130" class="desc">Overview &amp; Summary</text>
            
            <!-- Data Entry -->
            <rect x="100" y="200" width="160" height="80" rx="5" class="box" />
            <text x="180" y="230" class="title">Data Entry</text>
            <text x="180" y="250" class="desc">Add New Incidents</text>
            
            <!-- Search & Filter -->
            <rect x="320" y="80" width="160" height="80" rx="5" class="box" />
            <text x="400" y="110" class="title">Search &amp; Filter</text>
            <text x="400" y="130" class="desc">Find Specific Data</text>
            
            <!-- Visualization -->
            <rect x="320" y="200" width="160" height="80" rx="5" class="box" />
            <text x="400" y="230" class="title">Visualization</text>
            <text x="400" y="250" class="desc">Analyze Patterns</text>
            
            <!-- Export & Reports -->
            <rect x="540" y="80" width="160" height="80" rx="5" class="box" />
            <text x="620" y="110" class="title">Export &amp; Reports</text>
            <text x="620" y="130" class="desc">Share &amp; Document</text>
            
            <!-- Documentation -->
            <rect x="540" y="200" width="160" height="80" rx="5" class="box" />
            <text x="620" y="230" class="title">Documentation</text>
            <text x="620" y="250" class="desc">Help &amp; Reference</text>
            
            <!-- Flow Arrows -->
            <path d="M 260 120 L 310 120" class="arrow" />
            <path d="M 480 120 L 530 120" class="arrow" />
            <path d="M 180 160 L 180 190" class="arrow" />
            <path d="M 400 160 L 400 190" class="arrow" />
            <path d="M 620 160 L 620 190" class="arrow" />
            <path d="M 260 240 L 310 240" class="arrow" />
            <path d="M 480 240 L 530 240" class="arrow" />
            
            <!-- Cycle arrow -->
            <path d="M 700 240 Q 750 240 750 140 Q 750 40 400 40" class="arrow" />
            
            <text x="400" y="350" class="desc">This diagram shows the primary workflow through the application modules.</text>
            <text x="400" y="370" class="desc">Users typically start at the Dashboard, then move through the other sections as needed.</text>
        </svg>
        """
        st.markdown(workflow_svg, unsafe_allow_html=True)
        st.caption("Application Workflow Diagram")
    
    with doc_tabs[1]:  # Data Entry Guide
        st.markdown("<h3 class='sub-header'>Data Entry Guide</h3>", unsafe_allow_html=True)
        st.markdown("""
        ### How to Add New Contamination Incidents
        
        The Data Entry page allows you to record detailed information about food contamination incidents.
        
        #### Required Fields:
        - **Date of Incident**: When the contamination was discovered
        - **Location**: Where the contamination occurred
        - **Food Type**: Category of food that was contaminated
        - **Contaminant Type**: Category of the contaminant
        
        #### Optional but Recommended Fields:
        - **Geographic Coordinates**: For mapping visualizations
        - **Specific Contaminant**: Particular agent (e.g., E. coli O157:H7)
        - **Severity Level**: From 1 (minor) to 5 (severe)
        - **Detection Method**: How the contamination was discovered
        - **Affected Population**: Demographics or number of people affected
        - **Economic Impact**: Financial implications
        - **Regulatory Actions**: Official response
        - **Corrective Measures**: Steps taken to address the contamination
        
        #### Tips for Quality Data Entry:
        - Be as specific and detailed as possible
        - Include numerical data when available
        - Cite sources for information
        - Update entries if more information becomes available
        """)
        
        # Example form image or diagram could be added here
    
    with doc_tabs[2]:  # Search Tips
        st.markdown("<h3 class='sub-header'>Search & Filter Tips</h3>", unsafe_allow_html=True)
        st.markdown("""
        ### How to Find Specific Contamination Incidents
        
        The Search & Filter page offers several ways to locate specific data points:
        
        #### Basic Search:
        - Use the search field to search across all columns
        - Search is case-insensitive
        - Partial matches are supported
        
        #### Advanced Filtering:
        - **Date Range**: Limit results to a specific time period
        - **Food Type**: Filter by category of food
        - **Contaminant Type**: Filter by category of contaminant
        - **Severity Range**: Filter by severity level
        
        #### Tips for Effective Searching:
        - Start with broad filters and gradually narrow down
        - Combine multiple filters for precise results
        - Export filtered results for further analysis
        """)
    
    with doc_tabs[3]:  # Visualization Guide
        st.markdown("<h3 class='sub-header'>Visualization Guide</h3>", unsafe_allow_html=True)
        st.markdown("""
        ### How to Create and Interpret Visualizations
        
        The Visualization page helps you identify patterns and trends in contamination data.
        
        #### Available Visualization Types:
        
        ##### Basic Charts:
        - **Contamination by Food Type**: Bar chart showing incident counts by food category
        - **Contamination by Location**: Bar chart of top locations with incidents
        - **Severity Distribution**: Histogram showing severity level distribution
        - **Contamination Over Time**: Line chart showing incidents over time
        - **Contaminant Types Distribution**: Pie chart of contaminant categories
        
        ##### Advanced Charts:
        - **Severity by Food Type**: Box plot showing severity distribution across food types
        - **Contaminant by Food Heatmap**: Heatmap showing relationship between food and contaminants
        - **Severity by Month**: Heatmap of average severity across months and years
        - **Geographic Distribution**: Map showing incident locations (requires coordinates)
        - **Contamination Tree Map**: Hierarchical view of food and contaminant relationships
        - **Severity by Contaminant Type**: Violin plot of severity distribution by contaminant
        
        #### Tips for Data Visualization:
        - Compare multiple visualization types for comprehensive insights
        - Look for unusual patterns or clusters
        - Consider seasonal or geographic trends
        - Export visualizations for reports or presentations
        """)
    
    with doc_tabs[4]:  # Export Guide
        st.markdown("<h3 class='sub-header'>Export & Reports Guide</h3>", unsafe_allow_html=True)
        st.markdown("""
        ### How to Export Data and Generate Reports
        
        The Export & Reports page allows you to extract data and create structured reports.
        
        #### Export Options:
        - **CSV Format**: For use with spreadsheet applications
        - **Excel Format**: For more advanced spreadsheet features
        
        #### Filter Before Export:
        - Include all data or apply filters
        - Filter by date range
        - Select specific food types
        
        #### Report Types:
        - **Summary Report**: Overview of incidents with key statistics
        - **Detailed Incident Report**: Comprehensive information about each incident
        - **Trend Analysis**: Patterns over time with visualizations
        
        #### Tips for Reports:
        - Generate reports regularly for ongoing monitoring
        - Use filtered data for focused reports
        - Include visualizations to enhance understanding
        - Save reports for historical comparison
        """)
    
    with doc_tabs[5]:  # FAQ
        st.markdown("<h3 class='sub-header'>Frequently Asked Questions</h3>", unsafe_allow_html=True)
        
        with st.expander("How do I add geographic coordinates?"):
            st.markdown("""
            In the Data Entry form, look for the Geographic Coordinates section. Enter the latitude 
            and longitude values, then check the "Include geographic coordinates" box to save them with your entry.
            
            You can find coordinates using online tools like Google Maps (right-click on a location and select 
            "What's here?" to see coordinates).
            """)
        
        with st.expander("Can I edit or delete entries after submitting them?"):
            st.markdown("""
            Currently, the application doesn't support direct editing of entries through the interface.
            
            To modify entries:
            1. Export the data to CSV
            2. Make your changes in a spreadsheet application
            3. Reimport the data (this requires developer assistance)
            
            Future versions may include edit/delete functionality.
            """)
        
        with st.expander("How do I interpret the severity levels?"):
            st.markdown("""
            The severity levels range from 1 to 5:
            
            - **Level 1**: Minimal risk to public health, no reported illnesses
            - **Level 2**: Low risk, minor illnesses possible but limited in scope
            - **Level 3**: Moderate risk, multiple illnesses reported but not severe
            - **Level 4**: High risk, serious illnesses, hospitalizations possible
            - **Level 5**: Severe risk, life-threatening, fatalities possible or reported
            """)
        
        with st.expander("What file formats can I use for export?"):
            st.markdown("""
            Currently, the application supports:
            
            - **CSV (Comma Separated Values)**: Compatible with most spreadsheet applications
            - **Excel (.xlsx)**: Native Microsoft Excel format
            
            Both formats preserve all data fields and can be analyzed in external tools.
            """)
        
        with st.expander("How often is the database updated?"):
            st.markdown("""
            The database is updated in real-time as users enter new incident information.
            
            All data is stored locally and changes are saved immediately when you submit new entries.
            """)
            
    # Help and support section    
    st.markdown("<h3 class='sub-header'>Help and Support</h3>", unsafe_allow_html=True)
    st.markdown("""
    If you need additional help or have questions not covered in this documentation,
    please contact your system administrator or email support@foodcontaminationdb.org.
    
    ### Reporting Issues
    
    If you encounter problems with the application, please provide:
    
    1. The page where the issue occurred
    2. A description of what you were trying to do
    3. Any error messages you received
    4. Steps to reproduce the issue
    """)
    
    # Version information
    st.markdown("---")
    st.caption(f"Food Contamination Research Database v1.0 | Last Updated: March 31, 2025")
