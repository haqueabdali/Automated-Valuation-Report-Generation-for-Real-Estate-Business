import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValuationResult:
    method: str
    value: float
    confidence: float
    details: Dict = None

    def __init__(self, method: str, value: float, confidence: float, details: Dict = None):
        self.method = method
        self.value = value
        self.confidence = max(0.0, min(1.0, confidence))
        self.details = details or {}

class ValuationCalculator:
    def __init__(self, data_processor):
        self.data_processor = data_processor
    
    def calculate_sales_comparison(self, property_details: Dict) -> ValuationResult:
        """Calculate value using sales comparison approach"""
        try:
            if not property_details:
                raise ValueError("No property details provided")
                
            property_id = property_details.get('id')
            comparables = self.data_processor.get_comparable_sales(property_id)
            
            if not comparables:
                raise ValueError("No comparable sales found")
            
            adjusted_prices = []
            adjustments = []
            
            for comp in comparables:
                price_per_sqft = comp.get('sale_price', 0) / max(1, comp.get('sqft', 1))
                
                size_diff = property_details.get('sqft', 0) - comp.get('sqft', 0)
                bed_diff = property_details.get('bedrooms', 0) - comp.get('bedrooms', 0)
                bath_diff = property_details.get('bathrooms', 0) - comp.get('bathrooms', 0)
                
                size_adj = size_diff * price_per_sqft * 0.5
                bed_adj = bed_diff * 10000
                bath_adj = bath_diff * 7500
                
                total_adj = size_adj + bed_adj + bath_adj
                adjusted_price = comp.get('sale_price', 0) + total_adj
                
                adjusted_prices.append(adjusted_price)
                adjustments.append({
                    'comp_id': comp.get('id'),
                    'original_price': comp.get('sale_price'),
                    'adjustments': {
                        'size': size_adj,
                        'bedrooms': bed_adj,
                        'bathrooms': bath_adj
                    },
                    'adjusted_price': adjusted_price
                })
            
            if not adjusted_prices:
                raise ValueError("No valid comparable sales after adjustments")
                
            avg_value = np.mean(adjusted_prices)
            std_dev = np.std(adjusted_prices)
            confidence = min(1.0, max(0.5, 1 - (std_dev / avg_value))) if avg_value != 0 else 0.5
            
            return ValuationResult(
                method="sales_comparison",
                value=round(avg_value, 2),
                confidence=round(confidence, 2),
                details={
                    'comparables': comparables,
                    'adjustments': adjustments,
                    'statistics': {
                        'mean': round(avg_value, 2),
                        'median': round(np.median(adjusted_prices), 2),
                        'std_dev': round(std_dev, 2),
                        'min': round(min(adjusted_prices), 2),
                        'max': round(max(adjusted_prices), 2),
                        'count': len(adjusted_prices)
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Sales comparison valuation failed: {str(e)}")
            return ValuationResult(
                method="sales_comparison",
                value=0,
                confidence=0,
                details={'error': str(e)}
            )

    def calculate_income_approach(self, property_details: Dict) -> ValuationResult:
        """Calculate value using income capitalization approach"""
        try:
            if not property_details:
                raise ValueError("No property details provided")
                
            annual_rent = property_details.get('annual_rent')
            if annual_rent is None:
                raise ValueError("Annual rent data missing")
            
            market_cap_rate = 0.06
            noi = annual_rent * 0.75
            value = noi / market_cap_rate
            
            return ValuationResult(
                method="income_approach",
                value=round(value, 2),
                confidence=0.7,
                details={
                    'noi': round(noi, 2),
                    'cap_rate': market_cap_rate,
                    'annual_rent': annual_rent,
                    'expense_ratio': 0.25
                }
            )
            
        except Exception as e:
            logger.error(f"Income approach valuation failed: {str(e)}")
            return ValuationResult(
                method="income_approach",
                value=0,
                confidence=0,
                details={'error': str(e)}
            )

    def calculate_cost_approach(self, property_details: Dict) -> ValuationResult:
        """Calculate value using cost approach"""
        try:
            if not property_details:
                raise ValueError("No property details provided")
                
            sqft = property_details.get('sqft', 0)
            lot_size = property_details.get('lot_size', 0)
            
            cost_per_sqft = 150
            land_value_per_sqft = 2
            
            building_value = sqft * cost_per_sqft
            depreciation = building_value * 0.1
            land_value = lot_size * land_value_per_sqft
            value = land_value + building_value - depreciation
            
            return ValuationResult(
                method="cost_approach",
                value=round(value, 2),
                confidence=0.6,
                details={
                    'land_value': round(land_value, 2),
                    'building_value': round(building_value, 2),
                    'depreciation': round(depreciation, 2),
                    'cost_per_sqft': cost_per_sqft,
                    'land_value_per_sqft': land_value_per_sqft
                }
            )
            
        except Exception as e:
            logger.error(f"Cost approach valuation failed: {str(e)}")
            return ValuationResult(
                method="cost_approach",
                value=0,
                confidence=0,
                details={'error': str(e)}
            )

    def calculate_hybrid_valuation(self, property_details: Dict) -> ValuationResult:
        """Calculate hybrid valuation combining multiple methods"""
        try:
            sales_comp = self.calculate_sales_comparison(property_details)
            income = self.calculate_income_approach(property_details)
            cost = self.calculate_cost_approach(property_details)
            
            weights = {
                'sales_comparison': 0.5,
                'income_approach': 0.3,
                'cost_approach': 0.2
            }
            
            weighted_value = (
                sales_comp.value * weights['sales_comparison'] +
                income.value * weights['income_approach'] +
                cost.value * weights['cost_approach']
            )
            
            weighted_confidence = (
                sales_comp.confidence * weights['sales_comparison'] +
                income.confidence * weights['income_approach'] +
                cost.confidence * weights['cost_approach']
            )
            
            return ValuationResult(
                method="hybrid",
                value=round(weighted_value, 2),
                confidence=round(weighted_confidence, 2),
                details={
                    'components': {
                        'sales_comparison': sales_comp.details,
                        'income_approach': income.details,
                        'cost_approach': cost.details
                    },
                    'weights': weights
                }
            )
            
        except Exception as e:
            logger.error(f"Hybrid valuation failed: {str(e)}")
            return ValuationResult(
                method="hybrid",
                value=0,
                confidence=0,
                details={'error': str(e)}
            )

    def calculate_valuation(self, property_details: Dict, method: str = "hybrid") -> ValuationResult:
        """Calculate property valuation using specified method"""
        try:
            if not property_details:
                raise ValueError("No property details provided")
                
            if method == "sales_comparison":
                return self.calculate_sales_comparison(property_details)
            elif method == "income_approach":
                return self.calculate_income_approach(property_details)
            elif method == "cost_approach":
                return self.calculate_cost_approach(property_details)
            elif method == "hybrid":
                return self.calculate_hybrid_valuation(property_details)
            else:
                raise ValueError(f"Unknown valuation method: {method}")
                
        except Exception as e:
            logger.error(f"Valuation calculation failed: {str(e)}")
            return ValuationResult(
                method=method,
                value=0,
                confidence=0,
                details={'error': str(e)}
            )