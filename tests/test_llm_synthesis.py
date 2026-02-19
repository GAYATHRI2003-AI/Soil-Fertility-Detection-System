#!/usr/bin/env python
"""Test the LLM-enhanced answer synthesis"""

from src.knowledge_base_query import query_knowledge_base

print('Testing LLM-enhanced answer synthesis...\n')
print('='*70)

# Test query
question = 'What are the key nutrients for soil fertility?'
print(f'Question: {question}')
print('\nProcessing with LLM synthesis (this may take 10-20 seconds on first run)...')
print('(Downloading FLAN-T5 model if needed...)')

result = query_knowledge_base(question, use_llm=True)

if result:
    print('\n' + '='*70)
    print(f'TITLE: {result.get("title", "N/A")}')
    print('='*70)
    print(f'\nANSWER:\n{result.get("answer", "No answer")}')
    print(f'\nConfidence: {result.get("confidence", 0)*100:.0f}%')
    print(f'Sources used: {result.get("source_count", 0)} documents')
    print('='*70)
else:
    print('No result returned')
