import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
from io import BytesIO
import os
from utils import export_data_to_excel

def generate_summary_report(data):
    """
    Generate a summary report of contamination incidents
    
    Args:
        data (pd.DataFrame): Contamination data
        
    Returns:
        dict: Summary report content
    """
    if data.empty:
        return {
            "total_incidents": 0,
            "unique_locations": 0,
            "food_types": 0,
            "contaminant_types": 0,
            "avg_severity": 0,
            "by_food_type": pd.DataFrame(),
            "by_contaminant": pd.DataFrame(),
            "by_location": pd.DataFrame(),
            "by_month": pd.DataFrame(),
            "recent_incidents": pd.DataFrame()
        }
        
    # Calculate summary statistics
    total_incidents = len(data)
    unique_locations = data['location'].nunique()
    food_types = data['food_type'].nunique()
    contaminant_types = data['contaminant_type'].nunique()
    avg_severity = data['severity'].mean()
    
    # Group by food type
    by_food_type = data['food_type'].value_counts().reset_index()
    by_food_type.columns = ['Food Type', 'Count']
    
    # Group by contaminant type
    by_contaminant = data['contaminant_type'].value_counts().reset_index()
    by_contaminant.columns = ['Contaminant Type', 'Count']
    
    # Group by location (top 10)
    by_location = data['location'].value_counts().head(10).reset_index()
    by_location.columns = ['Location', 'Count']
    
    # Group by month
    data['month'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m')
    by_month = data.groupby('month').size().reset_index()
    by_month.columns = ['Month', 'Count']
    by_month = by_month.sort_values('Month')
    
    # Recent incidents
    recent_incidents = data.sort_values(by='date', ascending=False).head(5)
    
    return {
        "total_incidents": total_incidents,
        "unique_locations": unique_locations,
        "food_types": food_types,
        "contaminant_types": contaminant_types,
        "avg_severity": round(avg_severity, 2),
        "by_food_type": by_food_type,
        "by_contaminant": by_contaminant,
        "by_location": by_location,
        "by_month": by_month,
        "recent_incidents": recent_incidents
    }

def generate_detailed_report(data):
    """
    Generate a detailed report of contamination incidents
    
    Args:
        data (pd.DataFrame): Contamination data
        
    Returns:
        pd.DataFrame: Detailed report
    """
    # Return entire dataset with selected columns in the preferred order
    columns = [
        'date', 'location', 'food_type', 'contaminant_type', 'specific_contaminant', 
        'severity', 'detection_method', 'affected_population', 'economic_impact',
        'regulatory_action', 'corrective_measures', 'description', 'source'
    ]
    
    # Only include columns that exist in the dataset
    existing_columns = [col for col in columns if col in data.columns]
    
    # Sort by date descending
    return data[existing_columns].sort_values(by='date', ascending=False)

def generate_geographic_report(data):
    """
    Generate a geographic report of contamination incidents
    
    Args:
        data (pd.DataFrame): Contamination data
        
    Returns:
        pd.DataFrame: Geographic report
    """
    # Check if latitude and longitude exist
    if 'latitude' not in data.columns or 'longitude' not in data.columns:
        return pd.DataFrame()
    
    # Filter out rows without coordinates
    geo_data = data.dropna(subset=['latitude', 'longitude'])
    
    # Group by location
    location_counts = geo_data.groupby(['location', 'latitude', 'longitude']).size().reset_index()
    location_counts.columns = ['Location', 'Latitude', 'Longitude', 'Incident Count']
    
    # Calculate average severity by location
    severity_by_location = geo_data.groupby('location')['severity'].mean().reset_index()
    severity_by_location.columns = ['Location', 'Average Severity']
    
    # Merge counts and severity
    geo_report = pd.merge(location_counts, severity_by_location, on='Location', how='left')
    
    return geo_report

def generate_time_analysis_report(data):
    """
    Generate a time analysis report of contamination incidents
    
    Args:
        data (pd.DataFrame): Contamination data
        
    Returns:
        dict: Time analysis report
    """
    # Convert date to datetime
    data['date_dt'] = pd.to_datetime(data['date'])
    
    # Extract month and year
    data['month'] = data['date_dt'].dt.month
    data['year'] = data['date_dt'].dt.year
    data['month_name'] = data['date_dt'].dt.strftime('%b')
    data['month_year'] = data['date_dt'].dt.strftime('%b %Y')
    
    # Incidents by month
    monthly_incidents = data.groupby(['year', 'month', 'month_name']).size().reset_index()
    monthly_incidents.columns = ['Year', 'Month', 'Month Name', 'Count']
    monthly_incidents = monthly_incidents.sort_values(['Year', 'Month'])
    
    # Average severity by month
    severity_by_month = data.groupby(['year', 'month', 'month_name'])['severity'].mean().reset_index()
    severity_by_month.columns = ['Year', 'Month', 'Month Name', 'Average Severity']
    severity_by_month = severity_by_month.sort_values(['Year', 'Month'])
    
    # Incidents by year
    yearly_incidents = data.groupby('year').size().reset_index()
    yearly_incidents.columns = ['Year', 'Count']
    
    # Monthly trends for current year vs previous year
    current_year = data['year'].max()
    previous_year = current_year - 1
    
    current_year_data = monthly_incidents[monthly_incidents['Year'] == current_year]
    previous_year_data = monthly_incidents[monthly_incidents['Year'] == previous_year]
    
    return {
        "monthly_incidents": monthly_incidents,
        "severity_by_month": severity_by_month,
        "yearly_incidents": yearly_incidents,
        "current_year_data": current_year_data,
        "previous_year_data": previous_year_data
    }

def generate_food_safety_scorecard(data):
    """
    Generate a food safety scorecard
    
    Args:
        data (pd.DataFrame): Contamination data
        
    Returns:
        dict: Food safety scorecard
    """
    if data.empty:
        return {
            "high_risk_foods": pd.DataFrame(),
            "high_risk_contaminants": pd.DataFrame(),
            "highest_severity_incidents": pd.DataFrame(),
            "incident_trend": "No data",
            "average_severity": 0
        }
    
    # High risk foods (foods with highest average severity)
    high_risk_foods = data.groupby('food_type')['severity'].agg(['mean', 'count']).reset_index()
    high_risk_foods.columns = ['Food Type', 'Average Severity', 'Incident Count']
    high_risk_foods = high_risk_foods[high_risk_foods['Incident Count'] >= 2]  # At least 2 incidents
    high_risk_foods = high_risk_foods.sort_values('Average Severity', ascending=False).head(5)
    
    # High risk contaminants (contaminants with highest average severity)
    high_risk_contaminants = data.groupby('contaminant_type')['severity'].agg(['mean', 'count']).reset_index()
    high_risk_contaminants.columns = ['Contaminant Type', 'Average Severity', 'Incident Count']
    high_risk_contaminants = high_risk_contaminants[high_risk_contaminants['Incident Count'] >= 2]  # At least 2 incidents
    high_risk_contaminants = high_risk_contaminants.sort_values('Average Severity', ascending=False).head(5)
    
    # Highest severity incidents
    highest_severity_incidents = data.sort_values('severity', ascending=False).head(5)
    
    # Incident trend (last 6 months vs previous 6 months)
    data['date_dt'] = pd.to_datetime(data['date'])
    latest_date = data['date_dt'].max()
    six_months_ago = latest_date - pd.DateOffset(months=6)
    twelve_months_ago = latest_date - pd.DateOffset(months=12)
    
    last_6m_count = len(data[data['date_dt'] >= six_months_ago])
    previous_6m_count = len(data[(data['date_dt'] < six_months_ago) & (data['date_dt'] >= twelve_months_ago)])
    
    if previous_6m_count == 0:
        trend_percentage = 100  # Can't calculate percentage increase from zero
        incident_trend = "Increasing"
    else:
        trend_percentage = ((last_6m_count - previous_6m_count) / previous_6m_count) * 100
        incident_trend = "Increasing" if trend_percentage > 0 else "Decreasing" if trend_percentage < 0 else "Stable"
    
    return {
        "high_risk_foods": high_risk_foods,
        "high_risk_contaminants": high_risk_contaminants,
        "highest_severity_incidents": highest_severity_incidents,
        "incident_trend": incident_trend,
        "trend_percentage": abs(round(trend_percentage, 1)),
        "average_severity": round(data['severity'].mean(), 2)
    }

def export_report_to_excel(data, report_type):
    """
    Export a report to Excel format
    
    Args:
        data (pd.DataFrame): Contamination data
        report_type (str): Type of report to generate
        
    Returns:
        bytes: Excel file as bytes
    """
    # Create a BytesIO object to work with Excel without saving to disk
    output = BytesIO()
    
    # Create Excel writer
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Different sheets based on report type
        if report_type == "Summary Report":
            # Generate summary data
            summary = generate_summary_report(data)
            
            # Create metadata sheet
            metadata = pd.DataFrame({
                'Report Type': ['Summary Report'],
                'Generated On': [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                'Total Incidents': [summary['total_incidents']],
                'Unique Locations': [summary['unique_locations']],
                'Food Types': [summary['food_types']],
                'Average Severity': [summary['avg_severity']]
            })
            metadata.to_excel(writer, sheet_name='Report Info', index=False)
            
            # Create summary sheets
            summary['by_food_type'].to_excel(writer, sheet_name='By Food Type', index=False)
            summary['by_contaminant'].to_excel(writer, sheet_name='By Contaminant', index=False)
            summary['by_location'].to_excel(writer, sheet_name='By Location', index=False)
            summary['by_month'].to_excel(writer, sheet_name='By Month', index=False)
            summary['recent_incidents'].to_excel(writer, sheet_name='Recent Incidents', index=False)
            
        elif report_type == "Detailed Report":
            # Generate detailed data
            detailed = generate_detailed_report(data)
            
            # Create metadata sheet
            metadata = pd.DataFrame({
                'Report Type': ['Detailed Report'],
                'Generated On': [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                'Total Incidents': [len(data)],
                'Date Range': [f"{data['date'].min()} to {data['date'].max()}"]
            })
            metadata.to_excel(writer, sheet_name='Report Info', index=False)
            
            # Create detailed incidents sheet
            detailed.to_excel(writer, sheet_name='Detailed Incidents', index=False)
            
        elif report_type == "Geographic Report":
            # Generate geographic data
            geo_data = generate_geographic_report(data)
            
            # Create metadata sheet
            metadata = pd.DataFrame({
                'Report Type': ['Geographic Report'],
                'Generated On': [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                'Total Locations': [len(geo_data)],
                'Total Incidents': [len(data)]
            })
            metadata.to_excel(writer, sheet_name='Report Info', index=False)
            
            # Create locations sheet
            if not geo_data.empty:
                geo_data.to_excel(writer, sheet_name='Locations', index=False)
            else:
                pd.DataFrame({'Message': ['No geographic data available']}).to_excel(
                    writer, sheet_name='Locations', index=False)
            
        elif report_type == "Time Analysis":
            # Generate time analysis data
            time_data = generate_time_analysis_report(data)
            
            # Create metadata sheet
            metadata = pd.DataFrame({
                'Report Type': ['Time Analysis Report'],
                'Generated On': [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                'Date Range': [f"{data['date'].min()} to {data['date'].max()}"],
                'Total Incidents': [len(data)]
            })
            metadata.to_excel(writer, sheet_name='Report Info', index=False)
            
            # Create time analysis sheets
            time_data['monthly_incidents'].to_excel(writer, sheet_name='Monthly Incidents', index=False)
            time_data['severity_by_month'].to_excel(writer, sheet_name='Severity by Month', index=False)
            time_data['yearly_incidents'].to_excel(writer, sheet_name='Yearly Incidents', index=False)
            
        elif report_type == "Food Safety Scorecard":
            # Generate food safety data
            safety_data = generate_food_safety_scorecard(data)
            
            # Create metadata sheet
            metadata = pd.DataFrame({
                'Report Type': ['Food Safety Scorecard'],
                'Generated On': [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                'Date Range': [f"{data['date'].min()} to {data['date'].max()}"],
                'Total Incidents': [len(data)],
                'Average Severity': [safety_data['average_severity']],
                'Incident Trend': [f"{safety_data['incident_trend']} ({safety_data['trend_percentage']}%)"]
            })
            metadata.to_excel(writer, sheet_name='Scorecard Summary', index=False)
            
            # Create safety data sheets
            safety_data['high_risk_foods'].to_excel(writer, sheet_name='High Risk Foods', index=False)
            safety_data['high_risk_contaminants'].to_excel(writer, sheet_name='High Risk Contaminants', index=False)
            safety_data['highest_severity_incidents'].to_excel(writer, sheet_name='Highest Severity', index=False)
        
        # Add all data as raw data sheet
        data.to_excel(writer, sheet_name='Raw Data', index=False)
    
    # Get the bytes value from the output
    output.seek(0)
    return output.getvalue()

def display_summary_report(data):
    """Display summary report in the Streamlit interface"""
    summary = generate_summary_report(data)
    
    # Header
    st.markdown("## Food Contamination Summary Report")
    st.markdown(f"**Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Incidents", summary["total_incidents"])
    with col2:
        st.metric("Unique Locations", summary["unique_locations"])
    with col3:
        st.metric("Food Types", summary["food_types"])
    with col4:
        st.metric("Avg. Severity", summary["avg_severity"])
    
    # Visualizations
    st.markdown("### Incidents by Food Type")
    if not summary["by_food_type"].empty:
        fig = px.bar(summary["by_food_type"], x="Food Type", y="Count", 
                    color="Count", text="Count",
                    color_continuous_scale=px.colors.sequential.Viridis)
        fig.update_layout(autosize=True)
        st.plotly_chart(fig, use_container_width=True)
    
    # Two columns for contaminant and location
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Incidents by Contaminant Type")
        if not summary["by_contaminant"].empty:
            fig = px.pie(summary["by_contaminant"], values="Count", names="Contaminant Type", 
                        hole=0.3, color_discrete_sequence=px.colors.sequential.Viridis)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(summary["by_contaminant"], use_container_width=True)
    
    with col2:
        st.markdown("### Top Locations")
        if not summary["by_location"].empty:
            fig = px.bar(summary["by_location"].head(5), x="Location", y="Count", 
                        color="Count", text="Count",
                        color_continuous_scale=px.colors.sequential.Viridis)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(summary["by_location"], use_container_width=True)
    
    # Incidents over time
    st.markdown("### Incidents Over Time")
    if not summary["by_month"].empty and len(summary["by_month"]) > 1:
        fig = px.line(summary["by_month"], x="Month", y="Count", markers=True)
        fig.update_layout(xaxis_title="Month", yaxis_title="Number of Incidents")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent incidents
    st.markdown("### Recent Incidents")
    if not summary["recent_incidents"].empty:
        st.dataframe(summary["recent_incidents"], use_container_width=True)

def display_food_safety_scorecard(data):
    """Display food safety scorecard in the Streamlit interface"""
    scorecard = generate_food_safety_scorecard(data)
    
    # Header
    st.markdown("## Food Safety Scorecard")
    st.markdown(f"**Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Incidents", len(data))
    with col2:
        st.metric("Average Severity", scorecard["average_severity"])
    with col3:
        if scorecard["incident_trend"] == "Increasing":
            st.metric("6-Month Trend", f"{scorecard['incident_trend']} ↑", 
                     delta=f"{scorecard['trend_percentage']}%", delta_color="inverse")
        elif scorecard["incident_trend"] == "Decreasing":
            st.metric("6-Month Trend", f"{scorecard['incident_trend']} ↓", 
                     delta=f"-{scorecard['trend_percentage']}%")
        else:
            st.metric("6-Month Trend", scorecard["incident_trend"])
    
    # High risk foods
    st.markdown("### High Risk Foods")
    if not scorecard["high_risk_foods"].empty:
        col1, col2 = st.columns([2, 3])
        with col1:
            st.dataframe(scorecard["high_risk_foods"])
        with col2:
            fig = px.bar(scorecard["high_risk_foods"], 
                       x="Food Type", y="Average Severity", 
                       color="Incident Count",
                       text="Average Severity",
                       color_continuous_scale=px.colors.sequential.Viridis)
            fig.update_layout(yaxis_range=[0, 5])
            st.plotly_chart(fig, use_container_width=True)
    
    # High risk contaminants
    st.markdown("### High Risk Contaminants")
    if not scorecard["high_risk_contaminants"].empty:
        col1, col2 = st.columns([2, 3])
        with col1:
            st.dataframe(scorecard["high_risk_contaminants"])
        with col2:
            fig = px.bar(scorecard["high_risk_contaminants"], 
                       x="Contaminant Type", y="Average Severity", 
                       color="Incident Count",
                       text="Average Severity",
                       color_continuous_scale=px.colors.sequential.Viridis)
            fig.update_layout(yaxis_range=[0, 5])
            st.plotly_chart(fig, use_container_width=True)
    
    # Highest severity incidents
    st.markdown("### Highest Severity Incidents")
    if not scorecard["highest_severity_incidents"].empty:
        st.dataframe(scorecard["highest_severity_incidents"], use_container_width=True)