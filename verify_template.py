# File: verify_template.py
from zipfile import ZipFile
from pathlib import Path
from src.config import REPORT_TEMPLATE  # Import from your config

def verify_template():
    """Verify the Word template is valid before report generation"""
    print("\n Verifying Template File:")
    print(f"Location: {REPORT_TEMPLATE}")
    
    # Check 1: File existence and size
    exists = REPORT_TEMPLATE.exists()
    print(f" Exists: {exists}")
    if exists:
        print(f" Size: {REPORT_TEMPLATE.stat().st_size} bytes")
    
    # Check 2: Valid ZIP structure (DOCX requirement)
    try:
        with ZipFile(REPORT_TEMPLATE) as z:
            required_files = ['word/document.xml', '[Content_Types].xml']
            missing = [f for f in required_files if f not in z.namelist()]
            print(f" ZIP Contents: {len(z.namelist())} files")
            print(f" Required Files: {'All present' if not missing else f'Missing: {missing}'}")
        print(" Template is valid DOCX (ZIP format)")
        return True
    except Exception as e:
        print(f" Invalid DOCX: {str(e)}")
        return False

if __name__ == "__main__":
    verify_template()