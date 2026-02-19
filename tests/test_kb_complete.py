#!/usr/bin/env python
"""Test the updated knowledge base with complete sentences"""
import os
os.chdir("c:/Users/Yazhini/OneDrive/Desktop/soil")

from src.knowledge_base_query import query_knowledge_base, get_db_stats

print("="*60)
print("Knowledge Base Test")
print("="*60)

# Test the DB stats
stats = get_db_stats()
if stats:
    print(f"\nKnowledge Base Status:")
    print(f"  Documents indexed: {stats['total_documents']}")
    print(f"  PDFs processed: {stats['pdfs_processed']}")
    print(f"  Database size: {stats['db_size_mb']:.1f} MB")

# Test the Coorg coffee question
print("\n" + "="*60)
question = "which soil in coorg is used to grow coffee?"
print(f"Question: {question}")
print("="*60)

docs = query_knowledge_base(question, top_k=3)
print(f"\nResults found: {len(docs)}")

if docs:
    for i, doc in enumerate(docs, 1):
        # Verify it ends with punctuation
        if doc.endswith(('.', '!', '?', ';')):
            punctuation = "YES"
        else:
            punctuation = "NO (added)"
            if not doc.endswith(('.', '!', '?', ';')):
                doc = doc.rstrip() + '.'
        
        print(f"\n[Result {i}] (Ends with punctuation: {punctuation})")
        print(f"Length: {len(doc)} chars")
        print(f"Text: {doc[:300]}...")
else:
    print("\nNo results found.")

print("\n" + "="*60)
print("Test Complete")
print("="*60)
