import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

class Visualization:
    """
    Class for creating visualizations of food contamination data.
    """
    
    def __init__(self):
        """
        Initialize the Visualization class.
        """
        pass
    
    def create_food_type_chart(self, data):
        """
        Create a bar chart showing contamination incidents by food type.
        
        Args:
            data (pd.DataFrame): The contamination data
            
        Returns:
            plotly.graph_objects.Figure: A bar chart visualization
        """
        # Count incidents by food type
        food_counts = data['food_type'].value_counts().reset_index()
        food_counts.columns = ['Food Type', 'Count']
        
        # Create the chart
        fig = px.bar(
            food_counts, 
            x='Food Type', 
            y='Count',
            title='Contamination Incidents by Food Type',
            color='Count',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            xaxis_title='Food Type',
            yaxis_title='Number of Incidents',
            coloraxis_showscale=False
        )
        
        return fig
    
    def create_location_chart(self, data):
        """
        Create a bar chart showing contamination incidents by location.
        
        Args:
            data (pd.DataFrame): The contamination data
            
        Returns:
            plotly.graph_objects.Figure: A bar chart visualization
        """
        # Count incidents by location (top 10)
        location_counts = data['location'].value_counts().reset_index()
        location_counts.columns = ['Location', 'Count']
        location_counts = location_counts.head(10)  # Show only top 10 locations
        
        # Create the chart
        fig = px.bar(
            location_counts, 
            x='Location', 
            y='Count',
            title='Top 10 Locations with Contamination Incidents',
            color='Count',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            xaxis_title='Location',
            yaxis_title='Number of Incidents',
            coloraxis_showscale=False
        )
        
        return fig
    
    def create_severity_chart(self, data):
        """
        Create a histogram showing the distribution of severity levels.
        
        Args:
            data (pd.DataFrame): The contamination data
            
        Returns:
            plotly.graph_objects.Figure: A histogram visualization
        """
        # Create the chart
        fig = px.histogram(
            data, 
            x='severity',
            nbins=5,
            title='Distribution of Contamination Severity',
            color_discrete_sequence=['#3366CC']
        )
        
        fig.update_layout(
            xaxis_title='Severity Level (1-5)',
            yaxis_title='Number of Incidents',
            bargap=0.1
        )
        
        return fig
    
    def create_time_series_chart(self, data):
        """
        Create a time series chart showing contamination incidents over time.
        
        Args:
            data (pd.DataFrame): The contamination data
            
        Returns:
            plotly.graph_objects.Figure: A line chart visualization
        """
        # Ensure date column is datetime type
        data_copy = data.copy()
        if not pd.api.types.is_datetime64_any_dtype(data_copy['date']):
            data_copy['date'] = pd.to_datetime(data_copy['date'])
        
        # Count incidents by date
        time_data = data_copy.groupby(pd.Grouper(key='date', freq='M')).size().reset_index(name='Count')
        
        # Create the chart
        fig = px.line(
            time_data, 
            x='date', 
            y='Count',
            title='Contamination Incidents Over Time',
            markers=True
        )
        
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Number of Incidents'
        )
        
        return fig
    
    def create_contaminant_type_chart(self, data):
        """
        Create a pie chart showing the distribution of contaminant types.
        
        Args:
            data (pd.DataFrame): The contamination data
            
        Returns:
            plotly.graph_objects.Figure: A pie chart visualization
        """
        # Count incidents by contaminant type
        contaminant_counts = data['contaminant_type'].value_counts().reset_index()
        contaminant_counts.columns = ['Contaminant Type', 'Count']
        
        # Create the chart
        fig = px.pie(
            contaminant_counts, 
            names='Contaminant Type', 
            values='Count',
            title='Distribution of Contaminant Types'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    def create_severity_by_food_chart(self, data):
        """
        Create a box plot showing severity distribution by food type.
        
        Args:
            data (pd.DataFrame): The contamination data
            
        Returns:
            plotly.graph_objects.Figure: A box plot visualization
        """
        # Create the chart
        fig = px.box(
            data, 
            x='food_type', 
            y='severity',
            title='Severity Distribution by Food Type',
            color='food_type'
        )
        
        fig.update_layout(
            xaxis_title='Food Type',
            yaxis_title='Severity Level',
            showlegend=False
        )
        
        return fig
    
    def create_contaminant_by_food_heatmap(self, data):
        """
        Create a heatmap showing contaminant types by food type.
        
        Args:
            data (pd.DataFrame): The contamination data
            
        Returns:
            plotly.graph_objects.Figure: A heatmap visualization
        """
        # Create a crosstab of food type vs contaminant type
        heatmap_data = pd.crosstab(data['food_type'], data['contaminant_type'])
        
        # Create the heatmap
        fig = px.imshow(
            heatmap_data,
            title='Contaminant Types by Food Type',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            xaxis_title='Contaminant Type',
            yaxis_title='Food Type'
        )
        
        return fig
        
    def create_severity_by_month_chart(self, data):
        """
        Create a heatmap showing severity levels by month.
        
        Args:
            data (pd.DataFrame): The contamination data
            
        Returns:
            plotly.graph_objects.Figure: A heatmap visualization
        """
        # Ensure date column is datetime type
        data_copy = data.copy()
        if not pd.api.types.is_datetime64_any_dtype(data_copy['date']):
            data_copy['date'] = pd.to_datetime(data_copy['date'])
        
        # Extract month and year
        data_copy['month'] = data_copy['date'].dt.month_name()
        data_copy['year'] = data_copy['date'].dt.year
        
        # Group by month and year and calculate average severity
        monthly_severity = data_copy.groupby(['year', 'month'])['severity'].mean().reset_index()
        
        # Create a pivot table
        pivot_data = monthly_severity.pivot(index='month', columns='year', values='severity')
        
        # Sort the months in chronological order
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        pivot_data = pivot_data.reindex(month_order)
        
        # Create the heatmap
        fig = px.imshow(
            pivot_data,
            title='Average Severity by Month and Year',
            color_continuous_scale='RdYlGn_r',  # Red for high severity, green for low
            labels=dict(x="Year", y="Month", color="Avg. Severity")
        )
        
        fig.update_layout(
            xaxis_title='Year',
            yaxis_title='Month'
        )
        
        return fig
        
    def create_geographic_scatter_chart(self, data):
        """
        Create a scatter plot of contamination incidents on a map.
        
        Args:
            data (pd.DataFrame): The contamination data
            
        Returns:
            plotly.graph_objects.Figure: A scatter map visualization
        """
        # Check if latitude and longitude columns exist
        if 'latitude' in data.columns and 'longitude' in data.columns:
            # Create the scatter map
            fig = px.scatter_geo(
                data,
                lat='latitude',
                lon='longitude',
                color='severity',
                size='severity',
                hover_name='location',
                hover_data=['food_type', 'contaminant_type', 'date'],
                title='Geographic Distribution of Contamination Incidents',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(
                geo=dict(
                    showland=True,
                    landcolor='rgb(243, 243, 243)',
                    countrycolor='rgb(204, 204, 204)'
                )
            )
            
            return fig
        else:
            # Create a text chart indicating missing lat/lon data
            fig = go.Figure()
            fig.add_annotation(
                text="Geographic data (latitude/longitude) not available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20)
            )
            
            fig.update_layout(
                title='Geographic Distribution of Contamination Incidents',
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            
            return fig
            
    def create_contamination_tree_map(self, data):
        """
        Create a treemap visualization showing hierarchical data of contamination incidents.
        
        Args:
            data (pd.DataFrame): The contamination data
            
        Returns:
            plotly.graph_objects.Figure: A treemap visualization
        """
        # Create a copy of the data
        data_copy = data.copy()
        
        # Count incidents by food type and contaminant type
        tree_data = data_copy.groupby(['food_type', 'contaminant_type']).size().reset_index(name='count')
        
        # Create the treemap
        fig = px.treemap(
            tree_data,
            path=['food_type', 'contaminant_type'],
            values='count',
            title='Hierarchical View of Contamination Incidents',
            color='count',
            color_continuous_scale='RdBu'
        )
        
        fig.update_layout(
            margin=dict(t=50, l=25, r=25, b=25)
        )
        
        return fig
        
    def create_severity_distribution_by_contaminant(self, data):
        """
        Create a violin plot showing the distribution of severity by contaminant type.
        
        Args:
            data (pd.DataFrame): The contamination data
            
        Returns:
            plotly.graph_objects.Figure: A violin plot visualization
        """
        # Create the violin plot
        fig = px.violin(
            data, 
            x='contaminant_type', 
            y='severity',
            title='Severity Distribution by Contaminant Type',
            color='contaminant_type',
            box=True,
            points="all"
        )
        
        fig.update_layout(
            xaxis_title='Contaminant Type',
            yaxis_title='Severity Level',
            showlegend=False
        )
        
        return fig
