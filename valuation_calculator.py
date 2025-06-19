import numpy as np
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ValuationResult:
    method: str
    value: float
    confidence: float
    details: Dict

class ValuationCalculator:
    def __init__(self, data_processor):
        self.data_processor = data_processor
    
    def calculate_sales_comparison(self, property_id):
        """Calculate value using sales comparison approach"""
        subject = self.data_processor.get_property_details(property_id)
        comparables = self.data_processor.get_comparable_sales(property_id)
        
        if not subject or not comparables:
            return None
            
        # Calculate adjusted prices for comparables
        adjusted_prices = []
        adjustments = []
        
        for comp in comparables:
            # Simple adjustments (would be more sophisticated in reality)
            price_per_sqft = comp['sale_price'] / comp['sqft']
            
            # Adjust for size difference
            size_adjustment = (subject['sqft'] - comp['sqft']) * price_per_sqft * 0.5
            
            # Adjust for bedroom count
            bed_adjustment = (subject['bedrooms'] - comp['bedrooms']) * 10000
            
            # Adjust for bathroom count
            bath_adjustment = (subject['bathrooms'] - comp['bathrooms']) * 7500
            
            total_adjustment = size_adjustment + bed_adjustment + bath_adjustment
            adjusted_price = comp['sale_price'] + total_adjustment
            
            adjusted_prices.append(adjusted_price)
            adjustments.append({
                'comp_id': comp['id'],
                'original_price': comp['sale_price'],
                'adjustments': {
                    'size': size_adjustment,
                    'bedrooms': bed_adjustment,
                    'bathrooms': bath_adjustment
                },
                'adjusted_price': adjusted_price
            })
        
        # Calculate final value (weighted average)
        avg_value = np.mean(adjusted_prices)
        std_dev = np.std(adjusted_prices)
        confidence = min(1.0, max(0.5, 1 - (std_dev / avg_value)))
        
        return ValuationResult(
            method="sales_comparison",
            value=avg_value,
            confidence=confidence,
            details={
                'comparables': comparables,
                'adjustments': adjustments,
                'statistics': {
                    'mean': avg_value,
                    'median': np.median(adjusted_prices),
                    'std_dev': std_dev,
                    'min': min(adjusted_prices),
                    'max': max(adjusted_prices)
                }
            }
        )
    
    def calculate_income_approach(self, property_id):
        """Calculate value using income capitalization approach"""
        subject = self.data_processor.get_property_details(property_id)
        
        if not subject or 'annual_rent' not in subject:
            return None
            
        # Simple capitalization approach
        market_cap_rate = 0.06  # Would normally come from market data
        noi = subject['annual_rent'] * 0.75  # Assuming 25% expenses
        
        value = noi / market_cap_rate
        
        return ValuationResult(
            method="income_approach",
            value=value,
            confidence=0.7,  # Lower confidence due to simplified approach
            details={
                'noi': noi,
                'cap_rate': market_cap_rate,
                'annual_rent': subject['annual_rent']
            }
        )
    
    def calculate_cost_approach(self, property_id):
        """Calculate value using cost approach"""
        subject = self.data_processor.get_property_details(property_id)
        
        if not subject:
            return None
            
        # Simplified cost approach
        cost_per_sqft = 150  # Would vary by location and property type
        land_value = subject['lot_size'] * 2  # $2 per sqft for land
        
        building_value = subject['sqft'] * cost_per_sqft
        depreciation = building_value * 0.1  # Assuming 10% depreciation
        
        value = land_value + building_value - depreciation
        
        return ValuationResult(
            method="cost_approach",
            value=value,
            confidence=0.6,  # Lower confidence due to simplified approach
            details={
                'land_value': land_value,
                'building_value': building_value,
                'depreciation': depreciation,
                'cost_per_sqft': cost_per_sqft
            }
        )
    
    def calculate_valuation(self, property_id, method="sales_comparison"):
        """Calculate valuation using specified method"""
        if method == "sales_comparison":
            return self.calculate_sales_comparison(property_id)
        elif method == "income_approach":
            return self.calculate_income_approach(property_id)
        elif method == "cost_approach":
            return self.calculate_cost_approach(property_id)
        else:
            raise ValueError(f"Unknown valuation method: {method}")
