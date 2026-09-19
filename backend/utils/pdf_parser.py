import fitz  # PyMuPDF
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
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                cleaned_text = self._clean_text(text)
                
                # Only include non-empty pages
                if cleaned_text:
                    pages.append({
                        "page_number": page_num + 1,  # 1-indexed page numbers
                        "text": cleaned_text
                    })
            doc.close()
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

