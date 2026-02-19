import os
from pathlib import Path
from src.document_analyzer import DocumentAnalyzer
import json

def analyze_knowledge_base():
    """Analyze the knowledge base documents and extract useful information."""
    # Initialize the document analyzer
    analyzer = DocumentAnalyzer(output_dir="extracted_images")
    
    # List of knowledge base files
    knowledge_files = [
        "knowledge_base/CROPREGIONSOFINDIA.pdf",
        "knowledge_base/1664010343_Physical Map of India.jpg",
        "knowledge_base/1664008981_Political Map of India (English), 2020.jpg"
    ]
    
    # Process each file
    for file_path in knowledge_files:
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"\n⚠️  File not found: {file_path}")
            continue
            
        print(f"\n🔍 Analyzing: {file_path}")
        print("=" * 80)
        
        try:
            # Process the document
            result = analyzer.process_document(str(full_path))
            
            # Print summary of the analysis
            if 'error' in result:
                print(f"❌ Error processing {file_path}: {result['error']}")
                continue
                
            print(f"📄 File type: {result.get('file_type', 'unknown').upper()}")
            
            # Print layout information for PDFs
            if result.get('layout'):
                layout = result['layout']
                print(f"📑 Document has {layout['page_count']} pages")
                print(f"   - Contains text: {'Yes' if layout['has_text'] else 'No'}")
                print(f"   - Contains images: {'Yes' if layout['has_images'] else 'No'}")
                
                # Print a summary of each page
                for i, page in enumerate(layout['pages'], 1):
                    print(f"   - Page {i}: {len(page['blocks'])} blocks, {page['image_count']} images")
            
            # Print information about extracted images
            if result.get('images'):
                print(f"🖼️  Extracted {len(result['images'])} images")
                for i, img in enumerate(result['images'][:3], 1):  # Show first 3 images
                    print(f"   {i}. Page {img['page']}: {img['width']}x{img['height']} {img['ext'].upper()}")
                if len(result['images']) > 3:
                    print(f"   ... and {len(result['images']) - 3} more images")
            
            # Print extracted text for images
            if full_path.suffix.lower() in ['.jpg', '.jpeg', '.png'] and 'text' in result:
                preview = (result['text'][:200] + '...') if len(result['text']) > 200 else result['text']
                print(f"📝 Extracted text (preview):\n{preview}")
            
            # Save detailed results to a JSON file
            output_file = f"analysis_{full_path.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Detailed analysis saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    print("🛠️  AI Soil Doctor - Knowledge Base Analyzer")
    print("=" * 50)
    print("This tool will analyze the knowledge base documents and extract useful information.\n")
    
    analyze_knowledge_base()
    
    print("\n✅ Analysis complete!")
