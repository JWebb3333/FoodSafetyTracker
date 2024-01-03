import pandas as pd
import os
import datetime

class DataManager:
    """
    Class for managing food contamination data.
    Handles data operations such as loading, saving, and manipulating data.
    """
    
    def __init__(self, data_file="data/contamination_data.csv"):
        """
        Initialize the DataManager with a path to the data file.
        
        Args:
            data_file (str): Path to the CSV file where data is stored
        """
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self):
        """
        Load data from CSV file, or create an empty DataFrame if file doesn't exist.
        
        Returns:
            pd.DataFrame: The loaded data
        """
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Create or load data file
        if os.path.exists(self.data_file):
            try:
                data = pd.read_csv(self.data_file, parse_dates=['date'])
                return data
            except Exception as e:
                print(f"Error loading data: {e}")
                return self._create_empty_dataframe()
        else:
            return self._create_empty_dataframe()
    
    def _create_empty_dataframe(self):
        """
        Create an empty DataFrame with the required columns.
        
        Returns:
            pd.DataFrame: An empty DataFrame with the appropriate columns
        """
        return pd.DataFrame(columns=[
            'date', 'location', 'food_type', 'contaminant_type',
            'specific_contaminant', 'severity', 'description', 'source',
            'latitude', 'longitude', 'affected_population', 'detection_method',
            'regulatory_action', 'economic_impact', 'corrective_measures'
        ])
    
    def _save_data(self):
        """
        Save the current data to the CSV file.
        """
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        self.data.to_csv(self.data_file, index=False)
    
    def get_data(self):
        """
        Get the current data.
        
        Returns:
            pd.DataFrame: The current data
        """
        return self.data
    
    def add_entry(self, entry_data):
        """
        Add a new contamination incident entry to the data.
        
        Args:
            entry_data (dict): Dictionary containing the data for the new entry
        """
        # Convert to DataFrame row
        new_entry = pd.DataFrame([entry_data])
        
        # Append to the existing data
        self.data = pd.concat([self.data, new_entry], ignore_index=True)
        
        # Save the updated data
        self._save_data()
    
    def delete_entry(self, index):
        """
        Delete an entry from the data.
        
        Args:
            index (int): Index of the entry to delete
        """
        if 0 <= index < len(self.data):
            self.data = self.data.drop(index).reset_index(drop=True)
            self._save_data()
    
    def update_entry(self, index, updated_data):
        """
        Update an existing entry.
        
        Args:
            index (int): Index of the entry to update
            updated_data (dict): Dictionary containing the updated data
        """
        if 0 <= index < len(self.data):
            for key, value in updated_data.items():
                if key in self.data.columns:
                    self.data.at[index, key] = value
            self._save_data()
    
    def filter_data(self, filters):
        """
        Filter the data based on provided filters.
        
        Args:
            filters (dict): Dictionary of filters to apply
                Keys are column names, values are filter values
                
        Returns:
            pd.DataFrame: Filtered data
        """
        filtered_data = self.data.copy()
        
        for column, value in filters.items():
            if column in filtered_data.columns:
                filtered_data = filtered_data[filtered_data[column] == value]
        
        return filtered_data
    
    def search_data(self, search_term):
        """
        Search the data for a specific term across all columns.
        
        Args:
            search_term (str): Term to search for
            
        Returns:
            pd.DataFrame: Data containing the search term
        """
        if not search_term:
            return self.data
            
        # Convert search term and all columns to string for searching
        return self.data[self.data.astype(str).apply(
            lambda row: row.str.contains(search_term, case=False).any(), axis=1)]
