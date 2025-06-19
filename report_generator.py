from docxtpl import DocxTemplate
from datetime import datetime
from pathlib import Path
from config import OUTPUT_DIR, COMPANY_NAME, COMPANY_LOGO
import matplotlib.pyplot as plt
import os

class ReportGenerator:
    def __init__(self):
        self.template = None
    
    def generate_report(self, property_details, valuation_results, output_filename=None):
        """Generate a valuation report"""
        # Prepare context data
        context = {
            'company_name': COMPANY_NAME,
            'report_date': datetime.now().strftime("%B %d, %Y"),
            'property': property_details,
            'valuation': self._prepare_valuation_data(valuation_results),
            'charts': self._generate_charts(valuation_results, property_details['id'])
        }
        
        # Load template
        doc = DocxTemplate("templates/report_template.docx")
        
        # Render document
        doc.render(context)
        
        # Save the document
        if not output_filename:
            output_filename = f"valuation_report_{property_details['id']}_{datetime.now().strftime('%Y%m%d')}.docx"
        
        output_path = OUTPUT_DIR / output_filename
        doc.save(output_path)
        
        # Clean up chart images
        for chart_path in context['charts'].values():
            if os.path.exists(chart_path):
                os.remove(chart_path)
        
        return output_path
    
    def _prepare_valuation_data(self, valuation_results):
        """Prepare valuation data for the report"""
        if isinstance(valuation_results, list):
            # Multiple valuation methods
            primary = valuation_results[0]
            secondary = valuation_results[1:] if len(valuation_results) > 1 else []
            
            return {
                'primary_method': primary.method.replace('_', ' ').title(),
                'primary_value': "${:,.2f}".format(primary.value),
                'primary_confidence': f"{int(primary.confidence * 100)}%",
                'primary_details': primary.details,
                'secondary_methods': [{
                    'method': v.method.replace('_', ' ').title(),
                    'value': "${:,.2f}".format(v.value),
                    'confidence': f"{int(v.confidence * 100)}%"
                } for v in secondary],
                'final_value': "${:,.2f}".format(primary.value),
                'valuation_date': datetime.now().strftime("%B %d, %Y")
            }
        else:
            # Single valuation method
            return {
                'primary_method': valuation_results.method.replace('_', ' ').title(),
                'primary_value': "${:,.2f}".format(valuation_results.value),
                'primary_confidence': f"{int(valuation_results.confidence * 100)}%",
                'primary_details': valuation_results.details,
                'secondary_methods': [],
                'final_value': "${:,.2f}".format(valuation_results.value),
                'valuation_date': datetime.now().strftime("%B %d, %Y")
            }
    
    def _generate_charts(self, valuation_results, property_id):
        """Generate charts for the report"""
        charts = {}
        
        # Sales comparison chart
        if isinstance(valuation_results, list):
            primary = valuation_results[0]
        else:
            primary = valuation_results
            
        if primary.method == "sales_comparison":
            comp_prices = [c['sale_price'] for c in primary.details['comparables']]
            adjusted_prices = [a['adjusted_price'] for a in primary.details['adjustments']]
            comp_ids = [f"Comp {i+1}" for i in range(len(comp_prices))]
            
            plt.figure(figsize=(8, 5))
            bar_width = 0.35
            index = range(len(comp_ids))
            
            plt.bar(index, comp_prices, bar_width, label='Sale Price')
            plt.bar([i + bar_width for i in index], adjusted_prices, bar_width, label='Adjusted Price')
            
            plt.xlabel('Comparable Properties')
            plt.ylabel('Price ($)')
            plt.title('Sales Comparison Analysis')
            plt.xticks([i + bar_width/2 for i in index], comp_ids)
            plt.legend()
            plt.tight_layout()
            
            chart_path = OUTPUT_DIR / f"sales_comparison_{property_id}.png"
            plt.savefig(chart_path)
            plt.close()
            
            charts['sales_comparison'] = str(chart_path)
        
        # Add other chart types as needed
        
        return charts
