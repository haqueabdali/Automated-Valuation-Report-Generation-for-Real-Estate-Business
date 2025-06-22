from data_processor import DataProcessor
from valuation_calculator import ValuationCalculator
from report_generator import ReportGenerator
from config import DEFAULT_METHOD, VALUATION_METHODS
import argparse
import sys

def parse_arguments():
    """Improved argument parsing with custom error handling"""
    parser = argparse.ArgumentParser(
        description="Real Estate Valuation Report Generator",
        add_help=False  # We'll add custom help handling
    )
    
    # Required arguments
    required = parser.add_argument_group('required arguments')
    required.add_argument(
        'property_id',
        type=str,
        help="ID of the property to evaluate"
    )
    
    # Optional arguments
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument(
        '-m', '--method',
        type=str,
        default=DEFAULT_METHOD,
        choices=VALUATION_METHODS,
        help=f"Valuation method to use (default: {DEFAULT_METHOD})"
    )
    optional.add_argument(
        '-a', '--all-methods',
        action='store_true',
        help="Run all valuation methods and include in report"
    )
    optional.add_argument(
        '-h', '--help',
        action='help',
        help="Show this help message and exit"
    )
    
    # Custom error handling
    try:
        args = parser.parse_args()
        return args
    except argparse.ArgumentError as e:
        print(f"Error: {str(e)}")
        parser.print_help()
        sys.exit(2)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

def main():
    args = parse_arguments()
    
    try:
        # Initialize components
        data_processor = DataProcessor()
        valuation_calculator = ValuationCalculator(data_processor)
        report_generator = ReportGenerator()
        
        # Get property details
        property_details = data_processor.get_property_details(args.property_id)
        if not property_details:
            print(f"Error: Property with ID {args.property_id} not found")
            sys.exit(1)
        
        # Calculate valuation
        if args.all_methods:
            print("Running all valuation methods...")
            valuation_results = []
            for method in VALUATION_METHODS:
                print(f"Calculating {method}...")
                result = valuation_calculator.calculate_valuation(args.property_id, method)
                if result:
                    valuation_results.append(result)
            
            # Sort by confidence (highest first)
            valuation_results.sort(key=lambda x: x.confidence, reverse=True)
        else:
            print(f"Calculating valuation using {args.method} method...")
            valuation_results = valuation_calculator.calculate_valuation(args.property_id, args.method)
        
        # Generate report
        report_path = report_generator.generate_report(property_details, valuation_results)
        print(f"\nSuccessfully generated valuation report:\n{report_path}")
        
    except Exception as e:
        print(f"\nError during report generation: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()