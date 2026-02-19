import os
import fitz  # PyMuPDF
from PIL import Image
import io
import pytesseract
from typing import List, Dict, Tuple, Optional
import numpy as np
from pathlib import Path

class DocumentAnalyzer:
    """Class for analyzing documents and extracting information from PDFs and images."""
    
    def __init__(self, output_dir: str = "extracted_images"):
        """Initialize the DocumentAnalyzer with an output directory for extracted images."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_images_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract all images from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing image data and metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        doc = fitz.open(pdf_path)
        images = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Save image to file
                image = Image.open(io.BytesIO(image_bytes))
                image_ext = base_image["ext"]
                image_filename = f"page_{page_num+1}_img_{img_index+1}.{image_ext}"
                image_path = self.output_dir / image_filename
                image.save(image_path, format=image_ext.upper())
                
                images.append({
                    'page': page_num + 1,
                    'index': img_index,
                    'path': str(image_path),
                    'width': base_image['width'],
                    'height': base_image['height'],
                    'ext': image_ext,
                    'text': self._extract_text_from_image(image)
                })
                
        return images
    
    def _extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from an image using OCR."""
        try:
            return pytesseract.image_to_string(image)
        except Exception as e:
            print(f"Error in OCR: {e}")
            return ""
    
    def analyze_document_layout(self, pdf_path: str) -> Dict:
        """Analyze the layout of a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing layout information
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        doc = fitz.open(pdf_path)
        layout_data = {
            'page_count': len(doc),
            'pages': [],
            'has_text': False,
            'has_images': False
        }
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_dict = {
                'page_number': page_num + 1,
                'dimensions': {
                    'width': page.rect.width,
                    'height': page.rect.height
                },
                'blocks': [],
                'image_count': len(page.get_images(full=True))
            }
            
            # Extract text blocks
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if 'lines' in block:  # Text block
                    block_type = 'text'
                    text = '\n'.join([' '.join([span['text'] for span in line['spans']]) 
                                     for line in block['lines']])
                    page_dict['blocks'].append({
                        'type': 'text',
                        'text': text,
                        'bbox': block['bbox']
                    })
                    layout_data['has_text'] = True
                elif 'image' in block:  # Image block
                    page_dict['blocks'].append({
                        'type': 'image',
                        'bbox': block['bbox']
                    })
                    layout_data['has_images'] = True
            
            layout_data['pages'].append(page_dict)
        
        return layout_data
    
    def extract_tables(self, pdf_path: str) -> List[Dict]:
        """Extract tables from a PDF document.
        
        Note: This is a placeholder. In a production environment, you would use
        a specialized library like camelot, tabula, or pdfplumber.
        """
        # TODO: Implement table extraction using a specialized library
        return []
    
    def process_document(self, file_path: str) -> Dict:
        """Process a document and extract all relevant information."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_ext = os.path.splitext(file_path)[1].lower()
        result = {
            'file_path': file_path,
            'file_type': file_ext[1:] if file_ext else 'unknown',
            'images': [],
            'tables': [],
            'layout': None
        }
        
        try:
            if file_ext == '.pdf':
                result['images'] = self.extract_images_from_pdf(file_path)
                result['layout'] = self.analyze_document_layout(file_path)
                result['tables'] = self.extract_tables(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                # For image files, just run OCR
                image = Image.open(file_path)
                result['text'] = self._extract_text_from_image(image)
                result['dimensions'] = {
                    'width': image.width,
                    'height': image.height
                }
        except Exception as e:
            result['error'] = str(e)
            
        return result


# Example usage
if __name__ == "__main__":
    # Example usage
    analyzer = DocumentAnalyzer()
    
    # Example file path - replace with actual path
    test_pdf = "knowledge_base/CROPREGIONSOFINDIA.pdf"
    
    if os.path.exists(test_pdf):
        print(f"Analyzing document: {test_pdf}")
        result = analyzer.process_document(test_pdf)
        print(f"Extracted {len(result.get('images', []))} images")
        print(f"Document layout analysis complete. {result.get('layout', {}).get('page_count', 0)} pages analyzed.")
    else:
        print(f"Test file not found: {test_pdf}")
