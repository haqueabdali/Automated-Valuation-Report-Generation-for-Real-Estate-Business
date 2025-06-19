import pandas as pd
from config import PROPERTY_DATA_FILE, COMPARABLE_SALES_FILE

class DataProcessor:
    def __init__(self):
        self.property_data = None
        self.comparable_sales = None
        
    def load_data(self):
        """Load property and comparable sales data"""
        try:
            self.property_data = pd.read_csv(PROPERTY_DATA_FILE)
            self.comparable_sales = pd.read_csv(COMPARABLE_SALES_FILE)
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def get_property_details(self, property_id):
        """Get details for a specific property"""
        if self.property_data is None:
            self.load_data()
            
        property_details = self.property_data[self.property_data['id'] == property_id].to_dict('records')
        return property_details[0] if property_details else None
    
    def get_comparable_sales(self, property_id, radius_miles=5, max_comparables=5):
        """Get comparable sales for a property"""
        if self.comparable_sales is None:
            self.load_data()
            
        # Get the subject property details
        subject = self.get_property_details(property_id)
        if not subject:
            return None
            
        # Filter comparables (simplified logic - would be more complex in reality)
        comparables = self.comparable_sales[
            (self.comparable_sales['property_type'] == subject['property_type']) &
            (self.comparable_sales['bedrooms'].between(subject['bedrooms']-1, subject['bedrooms']+1)) &
            (self.comparable_sales['bathrooms'].between(subject['bathrooms']-0.5, subject['bathrooms']+0.5)) &
            (self.comparable_sales['sqft'].between(subject['sqft']*0.8, subject['sqft']*1.2))
        ].head(max_comparables)
        
        return comparables.to_dict('records')
