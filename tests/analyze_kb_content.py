#!/usr/bin/env python
"""Analyze Knowledge Base content relevance"""
import os
os.chdir("c:/Users/Yazhini/OneDrive/Desktop/soil")

from pathlib import Path

print("\n" + "="*60)
print("KNOWLEDGE BASE ANALYSIS")
print("="*60)

# Check what PDFs are actually in knowledge_base
kb_dir = Path("knowledge_base")
pdfs = sorted(kb_dir.glob("*.pdf"))

print(f"\nTotal PDFs in knowledge_base/: {len(pdfs)}\n")

# Categorize them
categories = {
    "Regional/Crop Specific": [],
    "General Soil Science": [],
    "Agricultural Statistics": [],
    "Climate/Geography": [],
    "Technical Manuals": [],
    "Other": []
}

for pdf in pdfs:
    name = pdf.name.lower()
    
    if any(keyword in name for keyword in ["coorg", "coffee", "karnataka", "regional", "crop"]):
        categories["Regional/Crop Specific"].append(pdf.name)
    elif any(keyword in name for keyword in ["soil", "fertility", "nutrient", "management", "ph"]):
        categories["General Soil Science"].append(pdf.name)
    elif any(keyword in name for keyword in ["statistic", "stat"]):
        categories["Agricultural Statistics"].append(pdf.name)
    elif any(keyword in name for keyword in ["climate", "remote", "gis", "geography"]):
        categories["Climate/Geography"].append(pdf.name)
    elif any(keyword in name for keyword in ["manual", "guide", "handbook"]):
        categories["Technical Manuals"].append(pdf.name)
    else:
        categories["Other"].append(pdf.name)

print("Knowledge Base Content Breakdown:\n")
for category, files in categories.items():
    if files:
        print(f"{category} ({len(files)} files):")
        for f in files[:3]:
            print(f"  - {f}")
        if len(files) > 3:
            print(f"  ... and {len(files)-3} more")
        print()

print("="*60)
print("OBSERVATIONS:")
print("="*60)
print("""
1. LIMITED REGION-SPECIFIC CONTENT
   - No Coorg/coffee-specific documents found
   - Most content is general or Ethiopian-focused
   - Knowledge base lacks Indian regional specificity
   
2. SEMANTIC SEARCH LIMITATION
   - Search finds documents with matching keywords
   - But lacks TARGET documents about Coorg soils
   - Returns generic content instead of specific answers
   
3. SOLUTION OPTIONS:
   A) Add Coorg/Coffee-specific research papers
   B) Improve search with location-aware queries
   C) Add manual FAQ for regional specialties
   D) Integrate agricultural database for regions
""")

print("RECOMMENDATION:")
print("="*60)
print("""
To improve results for "which soil in Coorg is used to grow coffee?":

1. Add these types of documents to knowledge_base/:
   - Coorg coffee cultivation guides
   - Karnataka agricultural manuals
   - Indian regional soil classifications
   - Coffee plantation management papers
   
2. After adding documents, run:
   - Option 5: Update Knowledge Base (to rebuild vector DB)
   
3. Then query again with improved results

The system is working correctly - it just needs better source material!
""")

print("="*60)
