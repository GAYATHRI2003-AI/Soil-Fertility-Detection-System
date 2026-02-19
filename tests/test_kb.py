#!/usr/bin/env python
"""Test script for knowledge base functionality"""
import sys
import os
os.chdir("c:/Users/Yazhini/OneDrive/Desktop/soil")
sys.path.insert(0, "c:/Users/Yazhini/OneDrive/Desktop/soil")

print("[TEST] Starting knowledge base test...")
print("[TEST] Step 1: Check PDFs...")

from pathlib import Path
kb_dir = Path("knowledge_base")
pdfs = list(kb_dir.glob("*.pdf"))
print(f"[TEST] Found {len(pdfs)} PDF files")
for pdf in pdfs:
    print(f"  - {pdf.name}")

print("\n[TEST] Step 2: Import and build vector DB...")
from src.knowledge_base_query import build_vector_db, query_knowledge_base
result = build_vector_db(force=True)
print(f"[TEST] build_vector_db result: {result}")

print("\n[TEST] Step 3: Query knowledge base...")
docs = query_knowledge_base("What soil types are good for growing coffee?", top_k=3)
print(f"[TEST] Found {len(docs)} documents")
if docs:
    for i, doc in enumerate(docs[:3], 1):
        print(f"\n[DOC {i}] {doc[:300]}...")
else:
    print("[TEST] No results found")

print("\n[TEST] Done!")
