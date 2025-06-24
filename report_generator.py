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

    def _create_default_template(self):  # Added self
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
    
        # Save the document
        template_path = Path(REPORT_TEMPLATE)
        template_path.parent.mkdir(exist_ok=True)
        doc.save(template_path)
        print(f"Created new template at {template_path}")

    def ensure_valid_template(self):  # Added self
        """Guarantee we have a valid template file"""
        template_path = Path(REPORT_TEMPLATE)
        
        # Create directory if needed
        template_path.parent.mkdir(exist_ok=True)
    
        # Create new template if missing or invalid
        if not template_path.exists() or template_path.stat().st_size == 0:
            print("Creating new valid template...")
            self._create_default_template()
    
        return template_path
        
    def generate_report(self, property_details, valuation_results, output_filename=None):
        """Generate a valuation report with proper template handling"""
        try:
            # Ensure output directory exists
            Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
            # Generate charts first
            charts = self._generate_charts(valuation_results, property_details['id'])

            # Prepare context data
            context = {
                'company_name': COMPANY_NAME,
                'report_date': datetime.now().strftime("%B %d, %Y"),
                'property': property_details,
                'valuation': self._prepare_valuation_data(valuation_results),
                'charts': self._generate_charts(valuation_results, property_details['id'])
            }
            
            # Get guaranteed valid template
            template_path = self.ensure_valid_template()  # Now properly called with self
        
            # Verify the file is truly a DOCX
            if not template_path.suffix == '.docx':
                raise ValueError("Template must be .docx format")
            
            # Load with docxtpl
            try:
                doc = DocxTemplate(template_path)
            except Exception as e:
                # If still failing, create ultra-simple template
                self._create_default_template()
                doc = DocxTemplate(template_path)
            
            # Render and save document
            doc.render(context)
            
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
            return {
                'primary_method': valuation_results.method.replace('_', ' ').title(),
                'primary_value': "${:,.2f}".format(valuation_results.value),
                'primary_confidence': f"{int(valuation_results.confidence * 100)}%",
                'primary_details': valuation_results.details,
                'final_value': "${:,.2f}".format(valuation_results.value),
                'valuation_date': datetime.now().strftime("%B %d, %Y")
            }
            
        primary = valuation_results[0]
        return {
            'primary_method': primary.method.replace('_', ' ').title(),
            'primary_value': "${:,.2f}".format(primary.value),
            'primary_confidence': f"{int(primary.confidence * 100)}%",
            'primary_details': primary.details,
            'final_value': "${:,.2f}".format(primary.value),
            'valuation_date': datetime.now().strftime("%B %d, %Y")
        }
    
    def _generate_charts(self, valuation_results, property_id):
        """Generate charts for the report with proper error handling"""
        charts = {}
    
        try:
            # Determine primary valuation method
            primary = valuation_results[0] if isinstance(valuation_results, list) else valuation_results
        
            if primary.method == "sales_comparison":
                # Ensure output directory exists
                Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
            
                # Extract comparison data
                comp_data = primary.details['comparables']
                adjustments = primary.details['adjustments']
            
                # Prepare data for plotting
                comp_ids = [f"Comp {i+1}" for i in range(len(comp_data))]
                sale_prices = [c['sale_price'] for c in comp_data]
                adjusted_prices = [a['adjusted_price'] for a in adjustments]
            
                # Create figure
                plt.figure(figsize=(10, 6))
                bar_width = 0.35
                index = range(len(comp_ids))
            
                # Plot bars
                plt.bar(index, sale_prices, bar_width, 
                    color='skyblue', label='Original Sale Price')
                plt.bar([i + bar_width for i in index], adjusted_prices, bar_width,
                    color='orange', label='Adjusted Price')
            
                # Formatting
                plt.xlabel('Comparable Properties')
                plt.ylabel('Price ($)')
                plt.title('Sales Comparison Analysis')
                plt.xticks([i + bar_width/2 for i in index], comp_ids)
                plt.legend()
                plt.grid(True, linestyle='--', alpha=0.6)
                plt.tight_layout()
            
                # Save the chart
                chart_path = Path(OUTPUT_DIR) / f"sales_comparison_{property_id}.png"
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
            
                charts['sales_comparison'] = str(chart_path)
            
        except Exception as e:
            print(f"Chart generation failed: {str(e)}")
    
        return charts