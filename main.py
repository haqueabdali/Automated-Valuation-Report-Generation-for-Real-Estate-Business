from data_processor import DataProcessor
from valuation_calculator import ValuationCalculator
from report_generator import ReportGenerator
from config import DEFAULT_METHOD, VALUATION_METHODS
import argparse

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Real Estate Valuation Report Generator")
    parser.add_argument('property_id', type=str, help="ID of the property to evaluate")
    parser.add_argument('--method', type=str, default=DEFAULT_METHOD, 
                       choices=VALUATION_METHODS, help="Valuation method to use")
    parser.add_argument('--all-methods', action='store_true', 
                       help="Run all valuation methods and include in report")
    args = parser.parse_args()
    
    # Initialize components
    data_processor = DataProcessor()
    valuation_calculator = ValuationCalculator(data_processor)
    report_generator = ReportGenerator()
    
    # Get property details
    property_details = data_processor.get_property_details(args.property_id)
    if not property_details:
        print(f"Error: Property with ID {args.property_id} not found")
        return
    
    # Calculate valuation
    if args.all_methods:
        valuation_results = []
        for method in VALUATION_METHODS:
            result = valuation_calculator.calculate_valuation(args.property_id, method)
            if result:
                valuation_results.append(result)
        
        # Sort by confidence (highest first)
        valuation_results.sort(key=lambda x: x.confidence, reverse=True)
    else:
        valuation_results = valuation_calculator.calculate_valuation(args.property_id, args.method)
    
    # Generate report
    report_path = report_generator.generate_report(property_details, valuation_results)
    print(f"Successfully generated valuation report: {report_path}")

if __name__ == "__main__":
    main()
