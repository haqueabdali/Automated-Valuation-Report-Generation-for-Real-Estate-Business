from docxtpl import DocxTemplate
from config import REPORT_TEMPLATE
from datetime import datetime
from pathlib import Path
from config import OUTPUT_DIR, COMPANY_NAME, COMPANY_LOGO
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt
import os

class ReportGenerator:
    def __init__(self):
        self.template = None
    def _create_default_template():
        """Generate a valid default template if missing"""
        doc = Document()
    
        # Add styles
        styles = doc.styles
        title_style = styles['Title']
        title_style.font.size = Pt(24)
    
        # Add content with placeholders
        doc.add_paragraph('{company_name}', style='Title')
        doc.add_paragraph('VALUATION REPORT', style='Heading 1')
        doc.add_paragraph('{report_date}', style='Heading 2')
    
        # Add property details section
        doc.add_paragraph('PROPERTY DETAILS', style='Heading 1')
        doc.add_paragraph('Address: {property.address}')
        doc.add_paragraph('City: {property.city}')
        # Add more placeholders as needed...
    
        # Save the document
        template_path = Path(REPORT_TEMPLATE)
        template_path.parent.mkdir(exist_ok=True)
        doc.save(template_path)
        print(f"Created new template at {template_path}")
        
    def generate_report(self, property_details, valuation_results, output_filename=None):
        """Generate a valuation report with proper template handling"""
        try:
            # Verify template exists (using the imported REPORT_TEMPLATE)
            if not Path(REPORT_TEMPLATE).exists():
                self._create_default_template()
                """raise FileNotFoundError(
                    f"Template file not found at: {REPORT_TEMPLATE}\n"
                    f"Expected path: {Path(REPORT_TEMPLATE).absolute()}"
                )"""
            try:
                doc = DocxTemplate(REPORT_TEMPLATE)
                # Rest of your report generation code...
            except Exception as e:
                # Final fallback - create fresh template and retry
                self._create_default_template()
                doc = DocxTemplate(REPORT_TEMPLATE)
                # Retry report generation...
                # Rest of your existing report generation code...
                doc = DocxTemplate(REPORT_TEMPLATE)  # Use the imported constant
            
            context = {
                'company_name': COMPANY_NAME,
                'report_date': datetime.now().strftime("%B %d, %Y"),
                'property': property_details,
                'valuation': self._prepare_valuation_data(valuation_results),
                'charts': self._generate_charts(valuation_results, property_details['id'])
            }
        
            doc.render(context)
        
            # Save the document
            if not output_filename:
                output_filename = f"valuation_report_{property_details['id']}_{datetime.now().strftime('%Y%m%d')}.docx"
        
            output_path = Path(OUTPUT_DIR) / output_filename
            doc.save(output_path)
        
            return str(output_path)
        
        except Exception as e:
            print(f"Report generation failed: {str(e)}")
            raise
    
    def _prepare_valuation_data(self, valuation_results):
        """Prepare valuation data for the report"""
        if not isinstance(valuation_results, list):
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
