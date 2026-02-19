import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime

# Try importing Ollama for local LLM support
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("[WARNING] Ollama not installed. Install with: pip install ollama")

class SoilDoctorChatbot:
    """
    Advanced Soil Doctor Chatbot with intelligent model selection
    Uses different local LLMs based on query complexity and type
    """

    # Model configurations with their strengths
    MODEL_CONFIGS = {
        "gemma3:1b": {
            "name": "Gemma 3 (1B)",
            "size": "Ultra-Small",
            "ram": "4GB - 8GB",
            "best_for": "Fast responses on basic hardware. Great for simple Q&A.",
            "use_case": ["simple_qa", "basic_info", "quick_answers"]
        },
        "gemma3:4b": {
            "name": "Gemma 3 (4B)",
            "size": "Small",
            "ram": "4GB - 8GB",
            "best_for": "Fast responses on basic hardware. Great for simple Q&A.",
            "use_case": ["simple_qa", "basic_info", "quick_answers"]
        },
        "deepseek-r1:7b": {
            "name": "DeepSeek R1 (7B)",
            "size": "Medium",
            "ram": "8GB - 12GB",
            "best_for": "The best for logic. It \"thinks\" before answering, perfect for complex soil diagnosis.",
            "use_case": ["complex_diagnosis", "soil_analysis", "technical_questions", "problem_solving"]
        },
        "llama3.1:8b": {
            "name": "Llama 4 (8B)",
            "size": "Medium",
            "ram": "8GB - 12GB",
            "best_for": "The best all-rounder. Excellent for natural, human-like conversation.",
            "use_case": ["conversation", "general_chat", "explanation", "advice"]
        },
        "qwen2.5-coder:7b": {
            "name": "Qwen 3 Coder (7B)",
            "size": "Medium",
            "ram": "8GB - 12GB",
            "best_for": "If you need the chatbot to help you write code or analyze CSV data.",
            "use_case": ["coding", "data_analysis", "technical_help", "csv_processing"]
        }
    }

    def __init__(self, knowledge_base_dir: str = "knowledge_base"):
        """Initialize the Soil Doctor Chatbot."""
        self.knowledge_base_dir = Path(knowledge_base_dir)
        self.vector_db_dir = "vector_db"
        self.embedding_model = "all-MiniLM-L6-v2"
        self.chat_history: List[Dict[str, str]] = []
        self.max_history = 5  # Keep last 5 messages in history
        self.available_models = self._check_available_models()

        # Initialize the vector database
        self._init_vector_db()

    def _check_available_models(self) -> List[str]:
        """Check which Ollama models are available locally."""
        if not OLLAMA_AVAILABLE:
            return []

        try:
            models = ollama.list()
            available = []
            for model in models.get('models', []):
                model_name = model['name'].split(':')[0]  # Get base name without tag
                if model_name in [k.split(':')[0] for k in self.MODEL_CONFIGS.keys()]:
                    available.append(model['name'])
            return available
        except Exception as e:
            print(f"[WARNING] Could not check Ollama models: {e}")
            return []

    def _init_vector_db(self):
        """Initialize or load the vector database."""
        # Create vector DB directory if it doesn't exist
        os.makedirs(self.vector_db_dir, exist_ok=True)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=self.vector_db_dir)
        self.collection = self.client.get_or_create_collection("soil_knowledge")

        # Load the embedding model
        self.embedder = SentenceTransformer(self.embedding_model)

        # Build the vector database if it's empty
        if self.collection.count() == 0:
            self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build the knowledge base from documents."""
        from src.document_analyzer import DocumentAnalyzer

        print("🔍 Building knowledge base from documents...")
        analyzer = DocumentAnalyzer()

        # Process all files in the knowledge base directory
        for file_path in self.knowledge_base_dir.glob("*"):
            if file_path.suffix.lower() in ['.pdf', '.jpg', '.jpeg', '.png']:
                try:
                    print(f"Processing: {file_path.name}")
                    result = analyzer.process_document(str(file_path))

                    # Add text content to vector DB
                    if 'layout' in result and result['layout'].get('has_text'):
                        for page in result['layout']['pages']:
                            for block in page['blocks']:
                                if block['type'] == 'text' and block['text'].strip():
                                    self._add_to_knowledge(block['text'])

                    # Add OCR text from images
                    if 'images' in result:
                        for img in result['images']:
                            if 'text' in img and img['text'].strip():
                                self._add_to_knowledge(img['text'])

                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

        print(f"✅ Knowledge base built with {self.collection.count()} chunks")

    def _add_to_knowledge(self, text: str, chunk_size: int = 1000):
        """Add text to the knowledge base in chunks."""
        # Split text into chunks
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        # Generate embeddings and add to collection
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            embedding = self.embedder.encode(chunk).tolist()
            doc_id = f"doc_{len(self.collection.get()['ids'])}"

            self.collection.add(
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{"source": "knowledge_base", "chunk": i}],
                ids=[doc_id]
            )

    def _analyze_query_type(self, query: str) -> str:
        """
        Analyze query to determine the best model to use.
        Returns: query_type (general, technical, creative, coding)
        """
        query_lower = query.lower()

        # Check for coding/data analysis queries
        coding_keywords = ['code', 'python', 'script', 'csv', 'data', 'analyze', 'program', 'function', 'class', 'programming']
        if any(keyword in query_lower for keyword in coding_keywords):
            return "coding"

        # Check for technical/scientific queries
        technical_keywords = ['how does', 'why does', 'explain', 'science', 'technical', 'mechanism', 'process', 'analysis']
        if any(keyword in query_lower for keyword in technical_keywords):
            return "technical"

        # Check for creative queries
        creative_keywords = ['imagine', 'create', 'design', 'story', 'poem', 'creative', 'what if']
        if any(keyword in query_lower for keyword in creative_keywords):
            return "creative"

        # Default to general for all other queries
        return "general"

    def _select_best_model(self, query_type: str) -> Tuple[str, Dict]:
        """
        Select the best available model for the query type.
        Returns: (model_name, model_config)
        """
        if not self.available_models:
            return None, None

        # Priority order for each query type
        model_priority = {
            "general": ["llama3.1:8b", "deepseek-r1:7b", "gemma3:4b"],
            "technical": ["deepseek-r1:7b", "llama3.1:8b", "qwen2.5-coder:7b"],
            "creative": ["llama3.1:8b", "gemma3:4b", "deepseek-r1:7b"],
            "coding": ["qwen2.5-coder:7b", "deepseek-r1:7b", "llama3.1:8b"]
        }

        # Find first available model in priority order
        for model_base in model_priority.get(query_type, ["llama3.1:8b"]):
            for available_model in self.available_models:
                if available_model.startswith(model_base.split(':')[0]):
                    config_key = [k for k in self.MODEL_CONFIGS.keys() if k.startswith(model_base.split(':')[0])][0]
                    return available_model, self.MODEL_CONFIGS[config_key]

        # Fallback to first available model
        if self.available_models:
            model = self.available_models[0]
            config_key = [k for k in self.MODEL_CONFIGS.keys() if k.startswith(model.split(':')[0])][0]
            return model, self.MODEL_CONFIGS[config_key]

        return None, None

    def _get_relevant_context(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve relevant context from the knowledge base."""
        try:
            query_embedding = self.embedder.encode(query).tolist()

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []

    def _generate_response_with_llm(self, query: str, context: List[str], model_name: str) -> str:
        """Generate response using the selected Ollama model."""
        if not OLLAMA_AVAILABLE:
            return self._generate_fallback_response(query, context)

        try:
            # Create enhanced prompt with context
            context_text = "\n\n".join(context) if context else ""

            system_prompt = """You are a versatile AI assistant with expertise in agriculture, soil science, and general knowledge.
You can answer questions on any topic - from soil fertility and farming to general science, technology, or everyday questions.
Always provide well-structured, complete answers using proper sentences that end with appropriate punctuation.
Be helpful, informative, and engaging. Use your specialized knowledge of Indian agriculture when relevant, but draw from general knowledge for other topics.
Structure your responses clearly and comprehensively."""

            user_prompt = f"""Context information (if relevant):
{context_text}

User question: {query}

Please provide a comprehensive, well-structured answer. Use complete sentences ending with proper punctuation. Be helpful and informative."""

            response = ollama.chat(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False,
                options={"temperature": 0.7, "top_p": 0.9}
            )

            raw_response = response['message']['content'].strip()
            # Format the response to ensure proper structure
            return self._format_response(raw_response)

        except Exception as e:
            print(f"Error with Ollama model {model_name}: {e}")
            return self._generate_fallback_response(query, context)

    def _format_response(self, response: str) -> str:
        """Format response to ensure complete sentences with proper punctuation."""
        if not response or not response.strip():
            return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."

        response = response.strip()

        # Handle very short responses
        if len(response) < 10:
            if not response.endswith(('.', '!', '?')):
                response += '.'
            return response

        # Split into sentences more carefully
        import re

        # Split on sentence endings, but be more careful with abbreviations
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', response)

        formatted_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Skip if it's just punctuation or too short
                if len(sentence) < 3:
                    continue

                # Ensure sentence ends with punctuation
                if not sentence.endswith(('.', '!', '?')):
                    # Don't add period if it ends with quote or parenthesis
                    if not sentence.endswith('"', "'", ')', ']'):
                        sentence += '.'
                    else:
                        # Add period before closing punctuation
                        sentence = sentence[:-1] + '.' + sentence[-1]

                formatted_sentences.append(sentence)

        # If no sentences were formatted, return the original with punctuation
        if not formatted_sentences:
            if not response.endswith(('.', '!', '?')):
                response += '.'
            return response

        return ' '.join(formatted_sentences)

    def _generate_fallback_response(self, query: str, context: List[str]) -> str:
        """Fallback response generation when Ollama is not available."""
        if not context:
            return "I couldn't find relevant information to answer your question. Please try rephrasing your query or ask something else."

        # Simple response generation based on context
        context_text = "\n\n".join(context)

        # Simple heuristic for response generation
        if "crop" in query.lower() and "recommend" in query.lower():
            response = f"Based on the available information, here are some crop recommendations. {context_text[:500]}... For more specific recommendations, please provide details about your soil type and region."
        elif "soil" in query.lower() and "type" in query.lower():
            response = f"Here's what I found about soil types in India. {context_text[:500]}... Would you like more specific information about a particular region's soil?"
        else:
            response = f"Here's what I found in the knowledge base. {context_text[:500]}... Would you like me to elaborate on any of these points?"

        return self._format_response(response)

    def chat(self):
        """Start the chat interface."""
        print("\n" + "="*80)
        print("🌱 AI SOIL DOCTOR - ADVANCED CHAT ASSISTANT".center(80))
        print("Intelligent model selection for specific answers".center(80))
        print("="*80)

        if not self.available_models:
            print("\n⚠️  No Ollama models detected. Please install Ollama and pull models:")
            print("   ollama pull gemma3:1b")
            print("   ollama pull deepseek-r1:7b")
            print("   ollama pull llama3.1:8b")
            print("   ollama pull qwen2.5-coder:7b")
        else:
            print(f"\n✅ Available models: {len(self.available_models)}")
            for model in self.available_models:
                config = self._get_model_config(model)
                if config:
                    print(f"   • {config['name']} - {config['best_for']}")

        print("\nType 'exit' to end the conversation")
        print("Type 'models' to see available models")
        print("="*80 + "\n")

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Thank you for using AI Soil Doctor. Have a great day! 🌱")
                    break

                if user_input.lower() == 'models':
                    self._show_models()
                    continue

                if not user_input:
                    continue

                # Add user message to history
                self.chat_history.append({"role": "user", "content": user_input})

                # Analyze query type and select model
                query_type = self._analyze_query_type(user_input)
                model_name, model_config = self._select_best_model(query_type)

                print(f"\n🔍 Query type: {query_type}")
                if model_config:
                    print(f"🤖 Using model: {model_config['name']} ({model_config['best_for']})")
                else:
                    print("🤖 Using intelligent response system")

                # Get relevant context
                context = self._get_relevant_context(user_input)

                # Generate response
                if model_name and model_config:
                    response = self._generate_response_with_llm(user_input, context, model_name)
                else:
                    response = self._generate_fallback_response(user_input, context)

                # Response is already formatted in the generation methods

                # Add assistant response to history
                self.chat_history.append({"role": "assistant", "content": response})

                # Keep only the most recent messages
                if len(self.chat_history) > self.max_history * 2:
                    self.chat_history = self.chat_history[-self.max_history*2:]

                # Print response
                print("\n🤖 " + "\n".join([f"   {line}" for line in response.split('\n')]))

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n⚠️  An error occurred: {str(e)}")
                continue

    def _get_model_config(self, model_name: str) -> Optional[Dict]:
        """Get model configuration for a given model name."""
        base_name = model_name.split(':')[0]
        for key, config in self.MODEL_CONFIGS.items():
            if key.startswith(base_name):
                return config
        return None

    def _show_models(self):
        """Display available models and their capabilities."""
        print("\n🤖 AVAILABLE MODELS:")
        print("="*60)

        for model_key, config in self.MODEL_CONFIGS.items():
            base_name = model_key.split(':')[0]
            available = any(m.startswith(base_name) for m in self.available_models)

            status = "✅ Available" if available else "❌ Not installed"
            print(f"\n{model_key.upper()}")
            print(f"   Status: {status}")
            print(f"   Size: {config['size']}")
            print(f"   RAM: {config['ram']}")
            print(f"   Best for: {config['best_for']}")

        print(f"\n📊 Total models available: {len(self.available_models)}/{len(self.MODEL_CONFIGS)}")

def start_chatbot():
    """Initialize and start the chatbot."""
    try:
        print("Initializing AI Soil Doctor Advanced Chatbot...")
        chatbot = SoilDoctorChatbot()
        chatbot.chat()
    except Exception as e:
        print(f"Failed to start chatbot: {str(e)}")
        print("Please make sure all dependencies are installed and try again.")

if __name__ == "__main__":
    start_chatbot()
