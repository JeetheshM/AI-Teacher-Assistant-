import pdfplumber
import re
from typing import List, Dict, Any

class PDFParser:
    def extract_pages(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from a PDF file page by page.
        Returns a list of dicts containing 'page_number' and 'text'.
        """
        pages = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    cleaned_text = self._clean_text(text)
                    
                    # Only include non-empty pages
                    if cleaned_text:
                        pages.append({
                            "page_number": i + 1,  # 1-indexed page numbers
                            "text": cleaned_text
                        })
        except Exception as e:
            raise Exception(f"Failed to process PDF: {str(e)}")
            
        if not pages:
            raise Exception("No readable text was found in this PDF.")
            
        return pages

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Strip leading/trailing whitespace
        text = text.strip()
        # Collapse excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Collapse repeated spaces
        text = re.sub(r' {2,}', ' ', text)
        return text

