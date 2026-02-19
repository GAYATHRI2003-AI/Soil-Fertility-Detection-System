#!/usr/bin/env python
"""Interactive test of the Knowledge Base with LLM synthesis"""

if __name__ == "__main__":
    from src.knowledge_base_query import query_knowledge_base
    
    print("\n" + "="*70)
    print("🌾 AI SOIL DOCTOR - Knowledge Base with LLM Synthesis")
    print("="*70)
    
    # Test multiple questions
    test_questions = [
        "What is nitrogen and why is it important for crops?",
        "How to improve soil pH for alkaline soils?",
        "What are the best practices for soil conservation?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'─'*70}")
        print(f"Question {i}: {question}")
        print(f"{'─'*70}")
        
        result = query_knowledge_base(question, use_llm=True)
        
        if result and result.get("source_count", 0) > 0:
            print(f"\n📖 {result['title'].upper()}")
            print(f"\n{result['answer']}\n")
            print(f"Confidence: {result.get('confidence', 0)*100:.0f}% | Sources: {result.get('source_count', 0)}")
        else:
            print("No relevant results found.")
    
    print(f"\n{'─'*70}")
    print("Testing complete!")
    print(f"{'─'*70}\n")
