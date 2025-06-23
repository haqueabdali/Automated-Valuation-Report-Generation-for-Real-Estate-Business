import pandas as pd
import os
from config import PROPERTY_DATA_FILE, COMPARABLE_SALES_FILE

class DataProcessor:
    def __init__(self):
        self.property_data = None
        self.comparable_sales = None
        
    def load_data(self):
        """Load property and comparable sales data"""
        try:
            # Debug print to verify file paths
            print(f"Loading property data from: {PROPERTY_DATA_FILE}")
            print(f"Loading comparable sales from: {COMPARABLE_SALES_FILE}")
            
            # Check if files exist
            if not os.path.exists(PROPERTY_DATA_FILE):
                raise FileNotFoundError(f"Property data file not found: {PROPERTY_DATA_FILE}")
            if not os.path.exists(COMPARABLE_SALES_FILE):
                raise FileNotFoundError(f"Comparable sales file not found: {COMPARABLE_SALES_FILE}")
            
            # Load the data
            self.property_data = pd.read_csv(PROPERTY_DATA_FILE)
            self.comparable_sales = pd.read_csv(COMPARABLE_SALES_FILE)
            
            # Debug print to verify data
            print("Successfully loaded property data:")
            print(self.property_data.head())
            
            return True
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def get_property_details(self, property_id):
        """Get details for a specific property with robust type handling"""
        if self.property_data is None:
            if not self.load_data():
                return None
        try:
            property_id = str(property_id).strip()
            self.property_data['id'] = self.property_data['id'].astype(str).str.strip()
        
            # Debug output
            print(f"Searching for ID: '{property_id}'")
            print("Available IDs:", self.property_data['id'].tolist())
        
            # Find matching property
            matches = self.property_data[self.property_data['id'] == property_id]
        
            if len(matches) == 0:
                print("No match found. Potential issues:")
                print("- Leading/trailing spaces in CSV")
                print("- Different number formats (1 vs '1')")
                print("- Hidden special characters")
                return None
            
            return matches.iloc[0].to_dict()
    
        except Exception as e:
            print(f"Error in get_property_details: {str(e)}")
            return None
    
    def get_comparable_sales(self, property_id, radius_miles=5, max_comparables=5):
        """Get comparable sales for a property"""
        if self.comparable_sales is None:
            if not self.load_data():
                return None
                
        # Get the subject property details
        subject = self.get_property_details(property_id)
        if not subject:
            return None
            
        try:
            # Filter comparables (simplified logic)
            comparables = self.comparable_sales[
                (self.comparable_sales['property_type'] == subject['property_type']) &
                (self.comparable_sales['bedrooms'].between(subject['bedrooms']-1, subject['bedrooms']+1)) &
                (self.comparable_sales['bathrooms'].between(subject['bathrooms']-0.5, subject['bathrooms']+0.5)) &
                (self.comparable_sales['sqft'].between(subject['sqft']*0.8, subject['sqft']*1.2))
            ].head(max_comparables)
            
            return comparables.to_dict('records')
        except Exception as e:
            print(f"Error getting comparable sales: {str(e)}")
            return None