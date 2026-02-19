#!/usr/bin/env python
"""Debug the issue with LLM synthesis"""

from src.knowledge_base_query import check_dependencies, query_knowledge_base

print('Checking dependencies...')
missing = check_dependencies()
if missing:
    print(f'Missing: {missing}')
else:
    print('✓ All core dependencies present')

print('\nTesting vector DB query first (without LLM)...')
result_no_llm = query_knowledge_base('What are the key nutrients?', use_llm=False)
print(f'Result without LLM: {result_no_llm}')

print('\nTesting with LLM synthesis...')
try:
    result_with_llm = query_knowledge_base('What are the key nutrients?', use_llm=True)
    print(f'Result with LLM: {result_with_llm}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
