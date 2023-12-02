import pandas as pd
import io

def export_data_to_csv(data):
    """
    Convert a DataFrame to CSV format for export.
    
    Args:
        data (pd.DataFrame): The data to export
        
    Returns:
        str: CSV data as a string
    """
    return data.to_csv(index=False).encode('utf-8')

def export_data_to_excel(data):
    """
    Convert a DataFrame to Excel format for export.
    
    Args:
        data (pd.DataFrame): The data to export
        
    Returns:
        bytes: Excel data as bytes
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='Contamination Data', index=False)
    output.seek(0)
    return output.getvalue()

def format_date(date_str):
    """
    Format a date string to a consistent format.
    
    Args:
        date_str (str): The date string to format
        
    Returns:
        str: Formatted date string (YYYY-MM-DD)
    """
    try:
        date_obj = pd.to_datetime(date_str)
        return date_obj.strftime('%Y-%m-%d')
    except:
        return date_str
        
def severity_color(severity):
    """
    Return a color code based on severity level.
    
    Args:
        severity (int): Severity level (1-5)
        
    Returns:
        str: Hex color code
    """
    colors = {
        1: "#4CAF50",  # Green
        2: "#8BC34A",  # Light Green
        3: "#FFC107",  # Amber
        4: "#FF9800",  # Orange
        5: "#F44336"   # Red
    }
    return colors.get(severity, "#9E9E9E")  # Default: Grey

def generate_summary_statistics(data):
    """
    Generate summary statistics from contamination data.
    
    Args:
        data (pd.DataFrame): The contamination data
        
    Returns:
        dict: Dictionary of summary statistics
    """
    if data.empty:
        return {
            "total_incidents": 0,
            "unique_locations": 0,
            "food_types": 0,
            "contaminant_types": 0,
            "avg_severity": 0
        }
    
    return {
        "total_incidents": len(data),
        "unique_locations": data['location'].nunique(),
        "food_types": data['food_type'].nunique(),
        "contaminant_types": data['contaminant_type'].nunique(),
        "avg_severity": round(data['severity'].mean(), 2)
    }
