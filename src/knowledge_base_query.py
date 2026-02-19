# knowledge_base_query.py
"""
Knowledge Base Query Module - Agricultural RAG System
- Uses ChromaDB for vector embeddings and retrieval
- SentenceTransformers for semantic search
- Ollama integration (if available) - no API keys
- Fallback to HF Flan-T5 model
- Self-learning mechanism: saves new Q&A to knowledge base
"""
import os
import json
from pathlib import Path
from datetime import datetime

# Try importing optional packages
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Try PyMuPDF first, then pdfplumber
try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Stronger LLM APIs
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

import tempfile

# ==================== CONFIG ====================
KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent / "knowledge_base"
VECTOR_DB_DIR = Path(__file__).parent.parent / "vector_db"
EMBEDDINGS_DB_DIR = VECTOR_DB_DIR / "embeddings"
LEARNED_KB_FILE = VECTOR_DB_DIR / "learned_kb.json"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3"  # or mistral, neural-chat, etc.
FALLBACK_MODEL = "google/flan-t5-small"
CHUNK_SIZE = 600
TOP_K = 3
DB_METADATA_FILE = VECTOR_DB_DIR / "db_metadata.json"

# Strong LLM Configuration
OPENAI_MODEL = "gpt-4"  # or "gpt-3.5-turbo"
GEMINI_MODEL = "gemini-pro"
ANTHROPIC_MODEL = "claude-3-sonnet-20240229"

# API Keys (set these environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Ensure directories exist
VECTOR_DB_DIR.mkdir(exist_ok=True)
EMBEDDINGS_DB_DIR.mkdir(exist_ok=True)

# Global ChromaDB and embedding model (lazy loaded)
_chroma_client = None
_embedder = None
_fallback_tokenizer = None
_fallback_model = None

def get_chroma_client():
    """Get or create ChromaDB client"""
    global _chroma_client
    if _chroma_client is None and CHROMADB_AVAILABLE:
        _chroma_client = chromadb.PersistentClient(path=str(EMBEDDINGS_DB_DIR))
    return _chroma_client

def get_embedder():
    """Get or create SentenceTransformer embedder"""
    global _embedder
    if _embedder is None and EMBEDDINGS_AVAILABLE:
        print("[Embedder] Loading SentenceTransformer...", flush=True)
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder

def get_fallback_model():
    """Lazy load fallback Flan-T5 model"""
    global _fallback_tokenizer, _fallback_model
    if _fallback_tokenizer is None or _fallback_model is None:
        if LLM_AVAILABLE:
            print(f"  [Loading {FALLBACK_MODEL}]", flush=True)
            _fallback_tokenizer = AutoTokenizer.from_pretrained(FALLBACK_MODEL)
            _fallback_model = AutoModelForSeq2SeqLM.from_pretrained(FALLBACK_MODEL)
            print(f"  [Loaded {FALLBACK_MODEL}] ✓", flush=True)
    return _fallback_tokenizer, _fallback_model


# ==================== RAG FUNCTIONS ====================

def add_to_vector_db(question, answer, source="learned"):
    """Add Q&A pair to ChromaDB vector store"""
    try:
        if not CHROMADB_AVAILABLE or not EMBEDDINGS_AVAILABLE:
            return False
        
        client = get_chroma_client()
        embedder = get_embedder()
        
        collection = client.get_or_create_collection(
            name="agricultural_qa",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Create a combined document for better retrieval
        combined = f"Q: {question}\nA: {answer}"
        
        # Embed
        embedding = embedder.encode([combined])[0].tolist()
        
        # Store both question and combination
        doc_id = f"{source}_{hash(question) % 1000000}"
        
        collection.add(
            documents=[combined],
            embeddings=[embedding],
            ids=[doc_id],
            metadatas=[{"type": source, "question": question[:100], "timestamp": datetime.now().isoformat()}]
        )
        
        print(f"[Vector DB] Added: {doc_id[:30]}...")
        return True
        
    except Exception as e:
        print(f"[Vector DB Warning] Could not add to DB: {str(e)[:50]}")
        return False


def retrieve_from_vector_db(question, top_k=3):
    """Retrieve relevant documents/Q&A from ChromaDB"""
    try:
        if not CHROMADB_AVAILABLE or not EMBEDDINGS_AVAILABLE:
            return []
        
        client = get_chroma_client()
        embedder = get_embedder()
        
        collection = client.get_or_create_collection(name="agricultural_qa")
        
        if collection.count() == 0:
            return []
        
        # Embed question
        q_embedding = embedder.encode([question])[0].tolist()
        
        # Query
        results = collection.query(
            query_embeddings=[q_embedding],
            n_results=min(top_k, collection.count())
        )
        
        # Extract documents
        docs = []
        if results and 'documents' in results:
            docs = results['documents'][0] if results['documents'] else []
        
        return docs
        
    except Exception as e:
        print(f"[Vector DB Warning] Retrieval error: {str(e)[:50]}")
        return []


def answer_with_ollama(prompt):
    """Generate answer using Ollama (local, no API keys)"""
    if not OLLAMA_AVAILABLE:
        return None
    
    try:
        print(f"  [Ollama] Querying {OLLAMA_MODEL}...", end="", flush=True)
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        answer = response.get("message", {}).get("content", "").strip()
        print(" ✓")
        return answer
        
    except Exception as e:
        print(f" ✗ ({str(e)[:30]})")
        return None


def answer_with_flan_t5(prompt, max_length=350):
    """Generate answer using Flan-T5 (simpler pipeline approach)"""
    try:
        from transformers import pipeline
        import torch

        print(f"  [Flan-T5 Pipeline] Initializing...", end="", flush=True)

        # Use device auto-detection
        device = 0 if torch.cuda.is_available() else -1

        # Create pipeline directly (simpler than manual tokenizer+model)
        generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-small",
            device=device,
            do_sample=True,
            temperature=0.7
        )

        print(" Loading model...", end="", flush=True)

        # Generate answer
        result = generator(prompt, max_length=max_length, num_beams=3, early_stopping=True)
        answer = result[0]["generated_text"].strip()

        # Ensure punctuation
        if answer and not answer.endswith(('.', '!', '?', ';')):
            answer += '.'

        print(" ✓")
        return answer

    except Exception as e:
        print(f" ✗ ({str(e)[:50]})")
        return None


def answer_with_openai(prompt, max_length=500):
    """Generate answer using OpenAI GPT models"""
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        return None

    try:
        import openai
        openai.api_key = OPENAI_API_KEY

        print(f"  [OpenAI GPT-4] Querying...", end="", flush=True)

        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert agricultural consultant for Indian farming communities. Provide specific, practical, and actionable advice with measurements and quantities when relevant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_length,
            temperature=0.7,
            top_p=0.95
        )

        answer = response.choices[0].message.content.strip()
        print(" ✓")
        return answer

    except Exception as e:
        print(f" ✗ ({str(e)[:50]})")
        return None


def answer_with_gemini(prompt, max_length=500):
    """Generate answer using Google Gemini"""
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)

        print(f"  [Gemini {GEMINI_MODEL}] Querying...", end="", flush=True)

        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)

        answer = response.text.strip()
        print(" ✓")
        return answer

    except Exception as e:
        print(f" ✗ ({str(e)[:50]})")
        return None


def answer_with_anthropic(prompt, max_length=500):
    """Generate answer using Anthropic Claude"""
    if not ANTHROPIC_AVAILABLE or not ANTHROPIC_API_KEY:
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        print(f"  [Anthropic {ANTHROPIC_MODEL}] Querying...", end="", flush=True)

        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_length,
            temperature=0.7,
            system="You are an expert agricultural consultant for Indian farming communities. Provide specific, practical, and actionable advice with measurements and quantities when relevant.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        answer = response.content[0].text.strip()
        print(" ✓")
        return answer

    except Exception as e:
        print(f" ✗ ({str(e)[:50]})")
        return None


def answer_with_strong_llm(question, context="", max_length=500):
    """
    Try stronger LLMs in order of preference: OpenAI → Gemini → Anthropic → Flan-T5
    """
    # Create enhanced prompt with context
    if context:
        prompt = f"""You are an expert agricultural consultant specializing in Indian agriculture.

Use this context information to answer the question accurately:
{context}

Question: {question}

Provide a detailed, practical answer with:
- Specific crop names and varieties when relevant
- Measurements, quantities, and timings
- Regional considerations for Indian agriculture
- Step-by-step guidance if needed
- Cost or productivity information when applicable

Answer:"""
    else:
        prompt = f"""You are an expert agricultural consultant specializing in Indian agriculture.

Question: {question}

Provide a detailed, practical answer with:
- Specific crop names and varieties when relevant
- Measurements, quantities, and timings
- Regional considerations for Indian agriculture
- Step-by-step guidance if needed
- Cost or productivity information when applicable

Answer:"""

    # Try OpenAI first (best quality)
    answer = answer_with_openai(prompt, max_length)
    if answer:
        return answer, "openai"

    # Try Gemini second
    answer = answer_with_gemini(prompt, max_length)
    if answer:
        return answer, "gemini"

    # Try Anthropic third
    answer = answer_with_anthropic(prompt, max_length)
    if answer:
        return answer, "anthropic"

    # Fallback to local Flan-T5
    print(f"  [Fallback to Local LLM] Flan-T5...", end="", flush=True)
    answer = answer_with_flan_t5(prompt, max_length)
    if answer:
        return answer, "flan_t5"

    return None, None


def generate_rag_answer(question, context=""):
    """Generate answer using RAG pipeline: Context + LLM"""
    
    print(f"\n[RAG Pipeline] Processing: {question[:50]}...", flush=True)
    
    # Create RAG prompt
    if context:
        prompt = f"""You are an expert agricultural consultant for Indian farming communities.
Use the context below to answer accurately. If context doesn't fully answer, use your knowledge.

CONTEXT:
{context}

QUESTION: {question}

ANSWER (specific, practical, with quantities/recommendations):"""
    else:
        prompt = f"""You are an expert agricultural consultant for Indian farming communities.
Answer this farming question as an expert, including:
- Specific crop/region recommendations if applicable
- Practical, actionable advice
- Measurements, quantities, or timings when relevant
- Cost or productivity information if asked

QUESTION: {question}

ANSWER:"""
    
    # Use Flan-T5 directly (fast, reliable, no server needed)
    # Ollama is optional for better quality but requires local setup
    if LLM_AVAILABLE:
        print(f"  [LLM] Using Flan-T5 for answer generation...", flush=True)
        answer = answer_with_flan_t5(prompt)
        if answer:
            return answer
    
    return None


def extract_title_from_question(question):
    """Generate smart title based on question type"""
    q = question.lower()
    if "how" in q:
        return "How To Guide"
    elif "what" in q:
        return "Information"
    elif "when" in q:
        return "Timing Guide"
    elif "which" in q or "best" in q:
        return "Recommendation"
    elif "why" in q:
        return "Explanation"
    elif "problem" in q or "issue" in q or "problem" in q:
        return "Solution"
    else:
        return "Agricultural Information"


# ==================== END RAG FUNCTIONS ====================

# ==================== PDF LOADING FUNCTIONS ====================

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using available methods"""
    text = ""
    
    try:
        # Try pdfplumber first (most reliable)
        if PDFPLUMBER_AVAILABLE:
            import pdfplumber
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                if text:
                    return text
            except:
                pass
        
        # Try PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                with open(pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page_num in range(len(reader.pages)):
                        page = reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                if text:
                    return text
            except:
                pass
        
        # Try PyMuPDF (fitz)
        if FITZ_AVAILABLE:
            try:
                import fitz
                doc = fitz.open(pdf_path)
                for page in doc:
                    text += page.get_text() + "\n"
                if text:
                    return text
            except:
                pass
    
    except Exception as e:
        print(f"PDF extraction error for {pdf_path}: {str(e)[:50]}")
    
    return text


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=100):
    """Split text into chunks with overlap"""
    chunks = []
    if not text:
        return chunks
    
    text = text.replace("\n\n", " | ").replace("\n", " ")
    
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if len(chunk.strip()) > 50:  # Only keep substantial chunks
            chunks.append(chunk)
    
    return chunks


def index_pdfs_to_chromadb():
    """Load all PDFs from knowledge_base - simple keyword indexing (no embeddings needed)"""
    try:
        if not KNOWLEDGE_BASE_DIR.exists():
            print(f"[PDF Indexing] Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}")
            return False
        
        pdf_files = list(KNOWLEDGE_BASE_DIR.glob("*.pdf"))
        print(f"\n[PDF Indexing] Found {len(pdf_files)} PDFs to process")
        
        # Simple file-level index (no ChromaDB, just file info)
        KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)
        pdf_index_file = KNOWLEDGE_BASE_DIR / ".pdf_index.json"
        
        pdf_index = {}
        successful_files = 0
        
        for pdf_file in pdf_files:
            try:
                print(f"  Processing: {pdf_file.name}...", end=" ", flush=True)
                
                text = extract_text_from_pdf(str(pdf_file))
                if not text or len(text.strip()) < 100:
                    print("(skipped - no text)")
                    continue
                
                # Store document info
                pdf_index[pdf_file.name] = {
                    "path": str(pdf_file),
                    "size": len(text),
                    "text_preview": text[:200],
                    "word_count": len(text.split())
                }
                
                # Cache extracted text
                cache_file = KNOWLEDGE_BASE_DIR / f".cache_{pdf_file.stem}.txt"
                with open(cache_file, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(text[:50000])  # Cache first 50KB
                
                print(f"✓ ({len(text.split())} words cached)")
                successful_files += 1
                
            except Exception as e:
                print(f"✗ ({str(e)[:30]})")
                continue
        
        # Save index
        with open(pdf_index_file, 'w') as f:
            json.dump(pdf_index, f, indent=2)
        
        print(f"\n[PDF Indexing] ✓ Processed {successful_files} PDFs\n")
        return True
        
    except Exception as e:
        print(f"[PDF Indexing Error] {str(e)}")
        return False


def retrieve_from_pdf_db(question, top_k=3):
    """Retrieve relevant PDF content using keyword matching"""
    try:
        if not KNOWLEDGE_BASE_DIR.exists():
            return []
        
        question_words = set(question.lower().split())
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'of', 'to', 'is', 'are', 'was', 'were', 'be'}
        question_words = question_words - stop_words
        
        pdf_files = list(KNOWLEDGE_BASE_DIR.glob("*.pdf"))
        pdf_scores = []
        
        for pdf_file in pdf_files:
            try:
                cache_file = KNOWLEDGE_BASE_DIR / f".cache_{pdf_file.stem}.txt"
                
                if cache_file.exists():
                    with open(cache_file, 'r', encoding='utf-8', errors='ignore') as f:
                        pdf_text = f.read()
                else:
                    # Extract on-the-fly if no cache
                    pdf_text = extract_text_from_pdf(str(pdf_file))
                    if pdf_text:
                        with open(cache_file, 'w', encoding='utf-8', errors='ignore') as f:
                            f.write(pdf_text[:50000])
                
                if not pdf_text:
                    continue
                
                # Score based on keyword matches
                pdf_text_lower = pdf_text.lower()
                score = sum(1 for word in question_words if word in pdf_text_lower)
                
                if score > 0:
                    # Extract relevant excerpt
                    lines = pdf_text.split('\n')
                    relevant_lines = []
                    for line in lines:
                        if any(word in line.lower() for word in question_words):
                            relevant_lines.append(line)
                    
                    excerpt = ' '.join(relevant_lines[:5])  # First 5 matching lines
                    if not excerpt:
                        excerpt = pdf_text[:300]
                    
                    pdf_scores.append({
                        "text": excerpt[:500],
                        "source": pdf_file.name,
                        "score": score
                    })
            
            except:
                continue
        
        # Return top matches
        pdf_scores.sort(key=lambda x: x["score"], reverse=True)
        return pdf_scores[:top_k]
        
    except Exception as e:
        print(f"[PDF Retrieval Warning] {str(e)[:50]}")
        return []

# ==================== END PDF FUNCTIONS ====================

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    if not CHROMADB_AVAILABLE:
        missing.append("chromadb")
    if not EMBEDDINGS_AVAILABLE:
        missing.append("sentence-transformers")
    return missing

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    if not CHROMADB_AVAILABLE:
        missing.append("chromadb")
    if not EMBEDDINGS_AVAILABLE:
        missing.append("sentence-transformers")
    return missing

def get_pdf_files_info():
    """Get information about PDF files in knowledge base"""
    pdf_files = {}
    if KNOWLEDGE_BASE_DIR.exists():
        for pdf in KNOWLEDGE_BASE_DIR.glob("*.pdf"):
            pdf_files[str(pdf)] = os.path.getmtime(pdf)
    return pdf_files

def should_rebuild_db():
    """Check if vector DB needs rebuilding"""
    if not DB_METADATA_FILE.exists():
        return True
    
    try:
        with open(DB_METADATA_FILE, 'r') as f:
            metadata = json.load(f)
        
        current_pdfs = get_pdf_files_info()
        stored_pdfs = metadata.get('pdfs', {})
        
        # Rebuild if PDF files changed
        if current_pdfs != stored_pdfs:
            return True
        
        return False
    except:
        return True

def save_db_metadata():
    """Save metadata about the vector DB"""
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'pdfs': get_pdf_files_info()
    }
    try:
        with open(DB_METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save DB metadata: {e}")

def extract_text_from_pdf_pdfplumber(pdf_path):
    """Extract text using pdfplumber (simpler method)"""
    if not PDFPLUMBER_AVAILABLE:
        return ""
    
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"pdfplumber extraction error for {pdf_path}: {e}")
        return ""

def extract_text_from_pdf_fitz(pdf_path):
    """Extract text using PyMuPDF"""
    if not FITZ_AVAILABLE:
        return ""
    
    text = ""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print(f"PyMuPDF extraction error for {pdf_path}: {e}")
    
    return text

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using available methods"""
    # Try pdfplumber first (simpler, no compilation needed)
    text = extract_text_from_pdf_pdfplumber(pdf_path)
    if text:
        return text
    
    # Fallback to PyMuPDF
    text = extract_text_from_pdf_fitz(pdf_path)
    if text:
        return text
    
    return ""

def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    if not OCR_AVAILABLE:
        return ""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"OCR error: {e}")
        return ""

# Build vector db from PDFs
def build_vector_db(force=False):
    """Build vector database from knowledge base PDFs"""
    if not force and not should_rebuild_db():
        return True  # DB is up to date
    
    missing = check_dependencies()
    if missing:
        print(f"WARNING: Missing packages for vector DB: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
        
        print("[INFO] Building knowledge base vector database...")
        
        client = chromadb.PersistentClient(str(VECTOR_DB_DIR))
        
        # Delete old collection to rebuild
        try:
            client.delete_collection("soil_knowledge")
        except:
            pass
        
        collection = client.get_or_create_collection("soil_knowledge")
        embedder = SentenceTransformer(EMBEDDING_MODEL)
        
        count = 0
        total_chunks = 0
        
        pdf_files = list(KNOWLEDGE_BASE_DIR.glob("*.pdf"))
        
        if not pdf_files:
            print("[INFO] No PDF files found in knowledge_base/ folder")
            save_db_metadata()
            return True
        
        for pdf_file in pdf_files:
            try:
                print(f"  Processing: {pdf_file.name}...", end=" ")
                doc_text = extract_text_from_pdf(pdf_file)
                
                if not doc_text or len(doc_text.strip()) < 100:
                    print("(skipped - no text)")
                    continue
                
                # Split into chunks
                chunk_size = 1000
                chunks = [doc_text[i:i+chunk_size] for i in range(0, len(doc_text), chunk_size)]
                
                # Filter out very short chunks
                chunks = [c for c in chunks if len(c.strip()) > 100]
                
                if not chunks:
                    print("(skipped - no valid chunks)")
                    continue
                
                embeddings = embedder.encode(chunks, show_progress_bar=False)
                
                for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                    try:
                        collection.add(
                            documents=[chunk],
                            embeddings=[emb.tolist()],
                            metadatas=[{"source": pdf_file.name, "chunk": idx}],
                            ids=[f"{pdf_file.stem}_{idx}_{hash(chunk) % 1000000}"]
                        )
                        total_chunks += 1
                    except Exception as e:
                        if "already exists" not in str(e):
                            print(f"Warning adding chunk: {e}")
                
                count += 1
                print(f"OK ({len(chunks)} chunks)")
                
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
        
        print(f"\n[DONE] Vector DB built: {count} PDFs, {total_chunks} chunks indexed")
        save_db_metadata()
        return True
        
    except Exception as e:
        print(f"Error building vector DB: {e}")
        return False

def clean_incomplete_sentences(text):
    """Clean up incomplete sentences by finding proper ending points"""
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # If already ends with proper punctuation, return
    if text and text[-1] in '.!?;:':
        return text
    
    # Find the last sentence boundary
    for punct in ['.', '!', '?', ';']:
        last_pos = text.rfind(punct)
        if last_pos > len(text) * 0.6:  # At least 60% through the text
            return text[:last_pos + 1]
    
    # If no punctuation found, trim at last space and add period
    last_space = text.rfind(' ')
    if last_space > 0:
        return text[:last_space] + '.'
    
    return text if text else "No information found."

# LLM-based Answer Synthesis
def synthesize_answer_with_llm(question, retrieved_docs, use_llm=True):
    """
    Synthesize a single coherent answer from retrieved documents using LLM
    
    Args:
        question: User's question
        retrieved_docs: List of document chunks retrieved from vector DB
        use_llm: Whether to use LLM for synthesis (True) or simple concatenation (False)
    
    Returns:
        Tuple: (answer, title, confidence)
    """
    if not retrieved_docs or len(retrieved_docs) == 0:
        return "No relevant information found in the knowledge base.", "", 0.0
    
    # Combine retrieved documents into context
    context = "\n".join(retrieved_docs[:5])  # Use top 5 documents
    
    if not use_llm or not LLM_AVAILABLE:
        # Fallback: Simple combination with best document
        title = "Agricultural Information"
        answer = retrieved_docs[0]
        if len(answer) > 500:
            answer = answer[:500] + "..."
        return answer, title, 0.6
    
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        
        # Use FLAN-T5 for better instruction following
        model_name = "google/flan-t5-base"
        
        print("  [Loading LLM model...]", end="", flush=True)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        print(" Done")
        
        # Create a better prompt for synthesis
        prompt = f"""Please read the agricultural information below and answer this question: "{question}"

Information:
{context[:1500]}

Answer the question clearly in 2-3 sentences. Be specific and practical."""
        
        # Tokenize and generate
        inputs = tokenizer.encode(prompt, return_tensors="pt", max_length=1024, truncation=True)
        
        # Generate with better parameters
        outputs = model.generate(
            inputs,
            max_length=250,
            num_beams=3,
            early_stopping=True,
            temperature=0.7,
            top_p=0.95
        )
        
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        
        # Ensure answer ends with punctuation
        if answer and not answer.endswith(('.', '!', '?', ';')):
            answer += '.'
        
        # Extract a title from the question
        title = "Answer"
        if "how" in question.lower():
            title = "How To"
        elif "what" in question.lower():
            title = "Information"
        elif "why" in question.lower():
            title = "Explanation"
        elif "which" in question.lower():
            title = "Selection Guide"
        
        confidence = 0.88
        return answer, title, confidence
        
    except Exception as e:
        # Fallback to best document approach
        print(f"\n  [LLM Synthesis] Using document-based answer: {str(e)[:30]}...", flush=True)
        title = "Agricultural Information"
        answer = retrieved_docs[0]
        if len(answer) > 450:
            # Try to cut at a sentence boundary
            sentences = answer.split('.')
            answer = '.'.join(sentences[:2]) + '.'
        elif not answer.endswith(('.', '!', '?', ';')):
            answer += '.'
        return answer, title, 0.7

def query_knowledge_base(question, top_k=3, use_llm=True):
    q_lower = question.lower().strip()
    # ========== PRIORITY 0: Direct Hardcoded for Cocoa/Chocolate Tree ==========
    cocoa_keywords = ["cocoa", "chocolate tree", "theobroma cacao"]
    if any(kw in q_lower for kw in cocoa_keywords):
        answer = (
            "Cocoa trees require a hot and humid climate with regular rainfall and temperatures between 21 and 32 degrees Celsius. "
            "They grow best in deep, well-drained loamy soils rich in organic matter with a pH between 6 and 7.5. "
            "Plant healthy seedlings at a spacing of three meters by three meters and provide shade using temporary plants like banana or gliricidia. "
            "Apply farmyard manure and recommended NPK fertilizers in split doses each year. "
            "Water regularly during dry periods but avoid waterlogging. "
            "Remove dead or diseased branches and maintain a clean basin around each tree. "
            "Monitor for pests and diseases and use appropriate control methods. "
            "Harvest pods when fully ripe. Trees start bearing in three to five years. "
            "Proper care ensures healthy growth and good yield of cocoa pods."
        )
        return {
            "answer": answer,
            "title": "Cocoa Tree Cultivation Guide",
            "confidence": 0.99,
            "source_count": 1,
            "sources": ["internal_agronomy_guide"],
            "source": "hardcoded"
        }

    # ========== PRIORITY 0.5: Direct Hardcoded for Ratnagiri Mangoes ==========
    ratnagiri_mango_keywords = ["ratnagiri", "mango", "mangoes", "ratnagiri mango", "mango ratnagiri", "konkan mango"]
    if any(kw in q_lower for kw in ratnagiri_mango_keywords):
        answer = (
            "🍃 Ratnagiri Mangoes - Maharashtra's Pride:\n\n"
            "🌍 Unique Characteristics:\n"
            "✓ World-famous for superior quality and taste\n"
            "✓ Known as 'Queen of Mangoes' or 'Hapus'\n"
            "✓ Grown exclusively in Ratnagiri district, Maharashtra\n"
            "✓ Protected Geographical Indication (GI) tag\n"
            "✓ Export quality with premium pricing\n\n"
            "🌡️ Climate & Soil:\n"
            "✓ Coastal Konkan region with humid climate\n"
            "✓ Temperature: 25-35°C during growth\n"
            "✓ Rainfall: 2000-3000mm annually\n"
            "✓ Soil: Lateritic red soil, well-drained\n"
            "✓ pH: 6.0-7.5 (slightly acidic to neutral)\n\n"
            "🌱 Cultivation:\n"
            "✓ Varieties: Alphonso, Pairi, Mankurad\n"
            "✓ Rootstock: Local mango varieties\n"
            "✓ Spacing: 10m × 10m (100 trees/acre)\n"
            "✓ Age: 5-8 years for first commercial yield\n"
            "✓ Yield: 5-8 tons/acre (premium quality)\n\n"
            "🔧 Special Management:\n"
            "✓ Regular pruning for air circulation\n"
            "✓ Organic manure: 50-100 kg/tree/year\n"
            "✓ Micronutrients: Zn, B sprays during flowering\n"
            "✓ Pest control: Mango hoppers, fruit flies\n"
            "✓ Harvest: April-May when fruits are mature\n\n"
            "💰 Economic Value:\n"
            "✓ Price: ₹500-2000/kg (premium markets)\n"
            "✓ Export: Major markets in Middle East, Europe\n"
            "✓ GI Protection: Only Ratnagiri grown can use name\n"
            "✓ Farmer Income: ₹2-5 lakhs/acre annually\n\n"
            "🏆 Why Special:\n"
            "✓ Unique Konkan climate creates perfect sugar-acid balance\n"
            "✓ Traditional cultivation methods preserved\n"
            "✓ Superior fiberless pulp and rich aroma\n"
            "✓ Natural sweetness without artificial ripening\n"
            "✓ Cultural heritage of Maharashtra farmers"
        )
        return {
            "answer": answer,
            "title": "Ratnagiri Mangoes - Maharashtra's Pride",
            "confidence": 0.98,
            "source_count": 1,
            "sources": ["maharashtra_agricultural_guide"],
            "source": "hardcoded"
        }
    """
    Main RAG Query Function - Multi-tier answer generation
    
    Priority:
    1. Hardcoded KB (instant) - seasonal/special questions
    2. Vector DB retrieval (instant+learned) - similar past Q&As
    3. Intelligent generator (fast) - specialized detections
    4. LLM + RAG (slower, high quality) - custom generations
    5. Error only if all fail
    """
    
    q_lower = question.lower().strip()
    
    try:
        print(f"\n[Query] Processing: {question[:60]}...", flush=True)
        
        # ========== PRIORITY 1: Check seasonal/special questions ==========
        season_keywords = ["season", "timing", "when", "best time", "month", "sow", "plant", "grow"]
        
        if any(kw in q_lower for kw in season_keywords):
            smart_response = generate_chatbot_response(question)
            if smart_response:
                print(f"[Priority 1] Seasonal match found", flush=True)
                return smart_response
        
        # ========== PRIORITY 2: Check Vector DB (learned + cached) ==========
        vec_docs = retrieve_from_vector_db(question, top_k=2)
        if vec_docs:
            print(f"[Priority 2] Found {len(vec_docs)} vector DB matches", flush=True)
            best_doc = vec_docs[0]
            
            # Extract answer from "Q: ... A: ..." format
            if "A:" in best_doc:
                answer_part = best_doc.split("A:")[1].strip()
                return {
                    "answer": answer_part[:700],  # Limit length
                    "title": extract_title_from_question(question),
                    "confidence": 0.92,
                    "source_count": 1,
                    "source": "vector_db"
                }
        
        # ========== PRIORITY 3: Check hardcoded KB for strong matches ==========
        kb = get_agricultural_knowledge_base()
        best_match = find_best_match_in_kb(question, kb)
        
        if best_match and best_match.get("score", 0) >= 7:
            print(f"[Priority 3] Hardcoded KB match (score: {best_match['score']})", flush=True)
            confidence = min(0.95, 0.5 + (best_match["score"] * 0.03))
            return {
                "answer": best_match["answer"],
                "title": best_match["title"],
                "confidence": confidence,
                "source_count": 1,
                "source": "kb"
            }
        
        # ========== PRIORITY 4: Try intelligent response generator ==========
        smart_response = generate_chatbot_response(question)
        if smart_response:
            print(f"[Priority 4] Intelligent generator match", flush=True)
            return smart_response
        
        # ========== PRIORITY 5: PDF Retrieval from Knowledge Base ==========
        print(f"[Priority 5] Searching PDFs...", flush=True)
        pdf_docs = retrieve_from_pdf_db(question, top_k=3)
        if pdf_docs:
            print(f"[Priority 5] Found {len(pdf_docs)} relevant PDF chunks", flush=True)
            
            # Combine PDF chunks as context
            pdf_context = "\n\n".join([doc["text"] for doc in pdf_docs])
            
            # Format sources
            sources = list(set([doc["source"] for doc in pdf_docs]))
            
            return {
                "answer": pdf_context[:1500],  # Return first 1500 chars of PDFs
                "title": "Agricultural Reference (from PDFs)",
                "confidence": 0.89,
                "source_count": len(sources),
                "sources": sources,
                "source": "pdf_documents"
            }
        
        # ========== PRIORITY 6: LLM + RAG (with learning) ==========
        if use_llm:
            print(f"[Priority 6] Invoking LLM + RAG pipeline...", flush=True)
            
            # Try to retrieve context from both vector DB and PDFs
            context_docs = retrieve_from_vector_db(question, top_k=TOP_K)
            pdf_docs = retrieve_from_pdf_db(question, top_k=2)
            
            context_parts = []
            if context_docs:
                context_parts.extend(context_docs)
            if pdf_docs:
                context_parts.extend([doc["text"] for doc in pdf_docs])
            
            context = "\n\n".join(context_parts[:3]) if context_parts else ""
            
            # Generate answer using Ollama or Flan-T5
            llm_answer = generate_rag_answer(question, context)
            
            if llm_answer:
                # Create structured response
                response = {
                    "answer": llm_answer,
                    "title": extract_title_from_question(question),
                    "confidence": 0.87,
                    "source_count": 1,
                    "source": "llm_rag"
                }
                
                # LEARN: Save this Q&A to vector DB for future queries
                add_to_vector_db(question, llm_answer, source="learned")
                
                # Also save to learned_kb.json
                save_to_learned_knowledge(question, response)
                
                print(f"[Learning] Saved Q&A", flush=True)
                return response
        
        # ========== FALLBACK: No answer found ==========
        print(f"[Fallback] No answer source available", flush=True)
        return {
            "answer": f"I don't have specific information about '{question}' in my knowledge base. For expert guidance, please contact your local agricultural extension office. You can also try asking about:\n\n• Seasonal cultivation (when/how to plant)\n• Soil testing and amendments\n• Pest and disease management\n• Crop-specific techniques\n• Irrigation and water management\n• Nutrient deficiencies\n• Regional crop recommendations",
            "title": "Information Not Available",
            "confidence": 0.15,
            "source_count": 0
        }
            
    except Exception as e:
        print(f"[ERROR] Query exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "answer": f"Error processing your question. Please try again with a simpler question.",
            "title": "Query Error",
            "confidence": 0.0,
            "source_count": 0
        }


def find_best_match_in_kb(question, kb):
    """Find best matching entry in knowledge base"""
    q_lower = question.lower().strip()
    best_match = None
    best_score = 0
    
    for entry_id, entry in kb.items():
        score = 0
        keywords = entry.get("keywords", [])
        
        for keyword in keywords:
            # Avoid matching single letters to prevent false positives
            if len(keyword) <= 1:
                continue
                
            if keyword in q_lower:
                score += 10
            else:
                # Check whole word matches in question
                for word in keyword.split():
                    if len(word) > 1 and word in q_lower:
                        score += 5
        
        if score > best_score:
            best_score = score
            best_match = entry
            best_match["score"] = score
    
    return best_match


def load_learned_knowledge():
    """Load previously learned Q&A pairs from file"""
    import json
    import os
    
    learned_file = os.path.join(os.path.dirname(__file__), "..", "learned_kb.json")
    
    if os.path.exists(learned_file):
        try:
            with open(learned_file, "r", encoding="utf-8") as f:
                learned_data = json.load(f)
                return learned_data
        except Exception as e:
            print(f"[Warning] Could not load learned KB: {str(e)}")
    
    return {}


def save_to_learned_knowledge(question, answer_data):
    """Save a new Q&A pair to learned knowledge base"""
    import json
    import os
    from datetime import datetime
    
    learned_file = os.path.join(os.path.dirname(__file__), "..", "learned_kb.json")
    
    try:
        # Load existing learned KB
        if os.path.exists(learned_file):
            with open(learned_file, "r", encoding="utf-8") as f:
                learned_kb = json.load(f)
        else:
            learned_kb = {}
        
        # Create entry key from question
        entry_key = f"learned_{len(learned_kb)}_{int(datetime.now().timestamp())}"
        
        # Store the Q&A pair
        learned_kb[entry_key] = {
            "question": question,
            "keywords": question.lower().split()[:5],  # First 5 words as keywords
            "title": answer_data.get("title", "Agricultural Information"),
            "answer": answer_data.get("answer", ""),
            "source": "llm",
            "learned_at": datetime.now().isoformat()
        }
        
        # Save back to file
        with open(learned_file, "w", encoding="utf-8") as f:
            json.dump(learned_kb, f, indent=2, ensure_ascii=False)
        
        print(f"[Learning] Saved Q&A to knowledge base: {entry_key[:30]}...")
        
    except Exception as e:
        print(f"[Warning] Could not save to learned KB: {str(e)}")


def generate_answer_with_llm(question):
    """Generate answer using FLAN-T5 LLM and return structured response"""
    
    if not LLM_AVAILABLE:
        return None
    
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        
        context_prompt = f"""You are an expert agricultural consultant. Answer this farming question clearly, practically, and specifically.

Question: {question}

Provide a detailed, helpful answer with:
- Specific crop names or techniques when relevant
- Measurements or quantities if applicable
- Regional considerations
- Step-by-step guidance if needed
- Practical recommendations farmers can use immediately

Answer:"""
        
        model_name = "google/flan-t5-base"
        print(f"  [Loading FLAN-T5...]", end="", flush=True)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        print(" ✓")
        
        # Tokenize and generate
        inputs = tokenizer.encode(context_prompt, return_tensors="pt", max_length=512, truncation=True)
        
        outputs = model.generate(
            inputs,
            max_length=350,
            num_beams=4,
            early_stopping=True,
            temperature=0.7,
            top_p=0.95
        )
        
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        
        # Ensure proper punctuation
        if answer and not answer.endswith(('.', '!', '?', ';')):
            answer += '.'
        
        # Generate title from question
        title = "Agricultural Answer"
        words_lower = question.lower()
        if "how" in words_lower:
            title = "How To Guide"
        elif "what" in words_lower:
            title = "Information"
        elif "when" in words_lower:
            title = "Timing Guide"
        elif "which" in words_lower:
            title = "Selection Guide"
        elif "why" in words_lower:
            title = "Explanation"
        elif "best" in words_lower:
            title = "Best Practices"
        
        return {
            "answer": answer,
            "title": title,
            "confidence": 0.88,
            "source_count": 1,
            "source": "llm"
        }
        
    except Exception as llm_error:
        print(f"  [LLM Error] {str(llm_error)[:50]}")
        return None

def get_agricultural_knowledge_base():
    """Complete KB with keyword arrays for smart matching"""
    return {
        "rice_ph": {
            "keywords": ["rice", "ph", "optimal", "rice ph", "rice cultivation", "rice soil"],
            "title": "Optimal pH for Rice Cultivation",
            "answer": "Rice thrives at pH 6.0-7.0. For any region:\n✓ Ideal pH: 6.0-7.0\n✓ Cannot grow well below pH 5.0\n✓ Nitrogen available at pH 6.5-7.0\n✓ Apply lime if pH < 5.5\n✓ Apply sulfur if pH > 8.0\n\nRice paddy fields benefit from maintaining standing water to buffer pH naturally."
        },
        "nitrogen": {
            "keywords": ["nitrogen", "yellowing", "pale", "stunted", "deficiency", "nitrogen deficiency"],
            "title": "Nitrogen Deficiency Management",
            "answer": "Nitrogen deficiency signs: Yellowing leaves, stunted growth, poor yield.\n\nSolutions:\n✓ Urea: 50-100 kg/ha in 2-3 splits\n✓ FYM: 10-20 tons/ha\n✓ Green manure: Dhaincha or sesbania\n✓ Legume rotation: Every 2-3 years\n✓ Foliar urea spray: 2% (quick relief)\n\nTiming: 50% at sowing, 25% at vegetative, 25% at flowering"
        },
        "coffee": {
            "keywords": ["coffee", "coorg", "coffee soil", "arabica", "coffee cultivation", "coffee region"],
            "title": "Coffee in Coorg - Soil & Cultivation Guide",
            "answer": "☕ Coorg (Kodagu) Coffee Guide:\n\n🌍 Ideal Conditions:\n✓ Altitude: 900-2000m (Coorg perfect for this)\n✓ Soil: Black soil, laterite\n✓ pH: 6.0-6.5 (slightly acidic)\n✓ Rainfall: 1500-3000mm\n✓ Shade: Sambaram, Dadap trees\n\n🔧 Soil Preparation:\n1. Add 10 tons FYM/ha\n2. Mix sulfur 500 kg/ha if pH high\n3. Ensure perfect drainage\n\n📊 Nutrients:\n✓ N: 150-200 kg/ha (split 3 times)\n✓ P: 75-100 kg/ha\n✓ K: 150-200 kg/ha\n✓ Zn & B: 5-10 kg/ha\n\n⏱️ Yield: 1.5-2 tons dried coffee/hectare"
        },
        "alkaline": {
            "keywords": ["alkaline", "high ph", "lime", "limestone soil", "ph high"],
            "title": "Alkaline Soil Management",
            "answer": "Managing high pH soils (pH > 8.0):\n\n✓ Best Fertilizers:\n  - Ammonium Sulphate (lowers pH)\n  - Urea (acidifying effect)\n  - Zinc Sulphate for deficiency\n  - Iron Sulphate for chlorosis\n  - Sulfur: 500-1000 kg/ha\n\n✓ Suitable Crops:\n  - Maize, Sorghum, Wheat\n  - Gram, Lentil, Pea\n  - Mustard, Sunflower\n  - Beans, Cabbage, Carrot\n\n✓ Corrections:\n  1. Apply sulfur 500-1000 kg/ha\n  2. Add organic matter\n  3. Use chelated micronutrients\n  4. Increase irrigation to leach salts"
        },
        "crop_rotation": {
            "keywords": ["rotation", "crop rotation", "sequence", "sustainable"],
            "title": "Crop Rotation Strategy",
            "answer": "Smart crop rotation system:\n\n3-Year Cycle:\nYear 1: Rice → Year 2: Wheat → Year 3: Legume (Gram)\n\n4-Year Cycle:\nYear 1: Cereal (Wheat) → Year 2: Legume (Pulse) → Year 3: Oilseed → Year 4: Cash crop\n\n✓ Benefits:\n- Breaks pest/disease cycles\n- Adds nitrogen via legumes\n- Reduces fertilizer costs\n- 20-30% higher productivity\n- Improves soil health\n\n✓ Include legumes (N-fixing) every 2-3 years\n✓ Alternate deep & shallow root crops"
        },
        "soil_test": {
            "keywords": ["test", "testing", "analysis", "lab", "soil", "sample"],
            "title": "Soil Testing Guide",
            "answer": "Complete soil testing procedure:\n\n🔬 Tests Needed:\n✓ pH (nutrient availability)\n✓ Texture (water retention)\n✓ Organic Matter (soil health)\n✓ NPK (fertilizer needs)\n✓ Micronutrients (Zn, Fe, B, Mn)\n✓ Electrical Conductivity (salinity)\n\n📍 Sampling:\n1. Collect from 5-10 spots\n2. Take 15-20 cm depth\n3. Mix, take 500g sample\n4. Send to govt lab\n\n💰 Cost: ₹200-500\n⏱️ Results: 5-7 days\n\nLab gives exact fertilizer recommendations"
        },
        "phosphorus": {
            "keywords": ["phosphorus", "purple", "poor root", "phosphorus deficiency"],
            "title": "Phosphorus Management",
            "answer": "Phosphorus deficiency identification & fix:\n\n⚠️ Signs:\n- Purple coloration on stems/leaves\n- Poor root development\n- Delayed maturity\n- Low grain/fruit\n- Stunted growth\n\n✅ Solutions:\n- SSP: 400-600 kg/ha\n- DAP: 200-300 kg/ha\n- Bone meal: 500-1000 kg/ha (organic)\n- Rock phosphate: 1000-2000 kg/ha (long-term)\n- FYM: 10-15 tons/ha\n\n💡 Apply 100% before sowing\n💡 Works best with organic matter"
        },
        "potassium": {
            "keywords": ["potassium", "burnt", "scorched", "leaf edge", "potassium deficiency"],
            "title": "Potassium Management",
            "answer": "Potassium deficiency fix:\n\n⚠️ Symptoms:\n- Burnt/scorched leaf edges\n- Yellow-brown margins\n- Weak stems (lodging)\n- Poor disease resistance\n- Low fruit quality\n\n✅ Solutions:\n- MOP: 40-60 kg K₂O/ha\n- Potassium Nitrate: 100-150 kg/ha\n- K-Sulphate: 50-75 kg/ha\n- Wood ash: 1-2 tons/ha (organic)\n\n🔧 Apply:\n✓ 50% at sowing\n✓ 50% at flowering (better quality)\n\n💡 Increase K by 20-30 kg/year in deficit soils"
        },
        "micronutrient": {
            "keywords": ["zinc", "iron", "boron", "manganese", "micro"],
            "title": "Micronutrient Deficiencies",
            "answer": "Micronutrient problems & solutions:\n\n🔍 Zinc (brown spots, stunted):\n✓ Zinc Sulphate: 20 kg/ha + 0.5% spray\n✓ Critical for rice, maize\n\n🔍 Iron (yellow leaves, green veins):\n✓ Iron Sulphate: 10-20 kg/ha\n✓ Common in high pH soils\n\n🔍 Boron (distorted leaves, cracked stems):\n✓ Borax: 10 kg/ha + 0.1% spray\n✓ Critical for oilseeds\n\n🔍 Manganese (grey spots):\n✓ Manganese Sulphate: 10 kg/ha\n✓ Common in alkaline soils\n\n💊 Spray Recipes:\n✓ Zn: 0.5% ZnSO₄ + 0.25% lime\n✓ Fe: 0.5% FeSO₄ + 0.25% lime\n✓ B: 0.1% Borax\n✓ Timing: 45-60 days after sowing"
        },
        "organic": {
            "keywords": ["organic", "natural", "compost", "bio"],
            "title": "Organic Farming System",
            "answer": "Complete organic farming:\n\n🌱 Soil Build-up:\n- Compost: 5-10 tons/ha/year\n- Green manure: Dhaincha, sesbania\n- Mulch: 5-10 tons/ha\n- Vermicompost: 2-5 tons/ha\n\n🔄 3-4 Year Rotation:\nYear 1: Legume (Pulse) → Year 2: Cereal (Wheat) → Year 3: Cash crop → Year 4: Oilseed\n\n🐝 Pest Management:\n- Trichoderma spray\n- Neem oil: 3-5%\n- Panchgavya: 5%\n- Trichogramma release\n\n✏️ Certification: 2-year transition\n💰 Premium: 20-30% higher price"
        },
        "wheat": {
            "keywords": ["wheat", "rabi", "winter"],
            "title": "Wheat Cultivation",
            "answer": "Wheat farming guide:\n\n🌾 Requirements:\n- pH: 6.0-7.5\n- Soil: Loamy to clay\n- Season: October-November (rabi)\n- Rainfall: 60-75 cm\n- Temperature: 15-20°C\n\n🔧 Nutrients:\n- N: 120-150 kg/ha (50% sowing, 50% tiller)\n- P: 60-80 kg/ha\n- K: 40-60 kg/ha\n- Zn: 5-10 kg/ha\n\n💧 Irrigation: 4-5 times\n⏱️ Yield: 40-50 quintals/hectare"
        },
        "maize": {
            "keywords": ["maize", "corn", "kharif"],
            "title": "Maize Cultivation",
            "answer": "Maize (corn) farming guide:\n\n🌽 Requirements:\n- pH: 6.0-7.5\n- Soil: Well-drained loamy\n- Season: June-July (kharif) or October (rabi)\n- Temperature: 21-27°C\n\n🔧 Nutrients:\n- N: 150-200 kg/ha (split 3 times)\n- P: 80-100 kg/ha\n- K: 60-80 kg/ha\n- Zn: 20 kg/ha if deficient\n\n🌱 Sowing:\n- Spacing: 60cm rows × 25cm plants\n- Depth: 5-6 cm\n- Seed rate: 20-25 kg/ha\n\n⏱️ Yield: 50-60 quintals/ha (hybrid)"
        }
    }

def generate_chatbot_response(question):
    """Generate intelligent response for ANY agricultural question"""
    q = question.lower()
    words = set(q.split())
    
    # SEASON/TIMING QUESTIONS - Check this FIRST for specificity
    season_keywords = ["season", "timing", "when", "best time", "month", "sow", "plant", "grow"]
    region_keywords = ["karnataka", "maharashtra", "tamil nadu", "coorg", "wayanad", "region", "state", "area", "north", "south", "east", "west"]
    
    if any(kw in q for kw in season_keywords):
        # Specific crop seasonal info
        if "cabbage" in q or "cabbage" in q:
            result_region = "Karnataka" if any(r in q for r in region_keywords) else "India"
            return {
                "answer": f"🥬 Cabbage Cultivation Seasons ({result_region}):\n\n📅 Best Seasons:\n✓ Main Season: July-August (kharif) for harvest Sept-Nov\n✓ Summer Season: January-February for harvest Apr-May\n✓ Winter Season: September-October (rabi) for harvest Dec-Feb\n\n🌍 Regional Timing ({result_region}):\n✓ Best in {result_region}: September-October sowing for winter harvest\n✓ Cooler months are IDEAL for cabbage quality\n✓ Avoid extreme heat (>30°C affects head formation)\n\n🌡️ Temperature Requirements:\n✓ Optimal: 15-25°C\n✓ Too hot (>30°C): Heads won't form properly\n✓ Frost tolerance: Can grow in 4-8°C but slow\n\n📍 Soil Requirements:\n✓ pH: 6.0-7.5\n✓ Soil: Well-draining, rich in organic matter\n✓ Add 10-15 tons FYM/ha before sowing\n✓ NPK: N 120-150, P 60-80, K 60-80 kg/ha\n\n📊 {result_region} Calendar:\n- July-August: Plant for Sept-Nov harvest ✓ GOOD\n- September-October: Plant for Dec-Feb harvest ✓✓ BEST\n- January-February: Plant for April-May harvest ✓ GOOD\n- March-June: Avoid (too hot)\n\n🌱 Varieties for {result_region}:\n✓ Early: Green Express, Golden Acre (50-60 days)\n✓ Mid: Indra (60-75 days)\n✓ Late: Pride of India (90-120 days)\n\n💧 Irrigation:\n✓ 4-5 times per season\n✓ Keep soil moist (not waterlogged)\n✓ Drip irrigation recommended\n\n⏱️ Harvest: 60-120 days after transplanting",
                "title": f"Cabbage Cultivation - Best Season in {result_region}",
                "confidence": 0.95,
                "source_count": 1
            }
        
        if "tomato" in q or "potato" in q or "onion" in q:
            return {
                "answer": "🍅 Vegetable Seasonal Calendar:\n\n🍅 TOMATO:\n✓ Kharif: June-July sowing, Aug-Dec harvest\n✓ Rabi: October-November sowing, Dec-April harvest\n✓ Summer: February-March sowing, May-July harvest\n✓ Best: Rabi season (October-November) for quality\n✓ Temperature: 20-25°C ideal\n\n🥔 POTATO:\n✓ Rabi: September-October sowing (ONLY season)\n✓ Harvest: 90-120 days after sowing\n✓ Oct-Nov sowing → January-Feb harvest\n✓ Temperature: 15-20°C optimal\n✓ Cannot grow in summer (>25°C)\n\n🧅 ONION:\n✓ Kharif: May-June sowing, Aug-Oct harvest\n✓ Rabi: September-October sowing, March-May harvest\n✓ Best: Rabi (Sept-Oct) for larger bulbs\n✓ Temperature: 10-30°C tolerant\n✓ 120-150 days to harvest\n\n📍 For ANY Vegetable:\n✓ Check temperature requirements first\n✓ Avoid extreme heat/cold\n✓ Monsoon good for kharif crops\n✓ Winter good for rabi crops\n✓ Summer needs irrigation management",
                "title": "Vegetable Seasonal Calendar",
                "confidence": 0.9,
                "source_count": 1
            }
    
    # PEST & DISEASE DETECTION
    pest_keywords = ["pest", "insect", "bug", "aphid", "whitefly", "armyworm", "borer", "mite", "grasshopper", "thrips", "scale", "pest control", "infestation"]
    disease_keywords = ["disease", "blight", "rot", "wilt", "powdery", "fungal", "bacterial", "viral", "infection", "leaf spot", "damping off", "rust"]
    
    if any(kw in q for kw in pest_keywords):
        return {
            "answer": "🐛 Pest Management Guide:\n\n📋 Common Agricultural Pests:\n✓ Aphids: Soft-bodied insects, weaken plants\n  → Control: Neem oil spray 3-5%, insecticidal soap\n  → Release ladybugs for biological control\n\n✓ Armyworm: Caterpillars that defoliate crops\n  → Control: Pheromone traps, spinosad spray\n  → Bacillus thuringiensis (Bt) spray\n\n✓ Whitefly: Transmits plant viruses\n  → Control: Yellow sticky traps, neem oil\n  → Remove infected leaves immediately\n\n✓ Mites: Feed on leaf sap\n  → Control: Sulfur dust, miticide spray\n  → Maintains high humidity\n\n🌿 Organic Solutions:\n✓ Neem oil: 3-5% spray (repeat every 10-15 days)\n✓ Panchagavya: 5% spray for pest + disease control\n✓ Cow urine: 10% spray as repellent\n✓ Intercropping: Plant marigold/garlic to repel pests\n\n🚫 IPM (Integrated Pest Management):\n✓ Cultural: Remove crop residues, rotate crops\n✓ Biological: Release natural predators\n✓ Chemical: Use only when organic fails\n✓ Mechanical: Hand-pick large pests",
            "title": "Pest Management & Prevention",
            "confidence": 0.85,
            "source_count": 1
        }
    
    if any(kw in q for kw in disease_keywords):
        return {
            "answer": "🍃 Disease Management Guide:\n\n🦠 Common Crop Diseases:\n✓ Early Blight (Potato/Tomato):\n  → Symptoms: Brown spots on lower leaves\n  → Control: Copper fungicide, remove infected leaves\n  → Prevention: Adequate spacing, drip irrigation\n\n✓ Powdery Mildew:\n  → Symptoms: White powdery coating on leaves\n  → Control: Sulfur dust 50g/10L water\n  → Control: Baking soda spray (5g/L)\n\n✓ Damping Off (Seedlings):\n  → Symptoms: Seedlings collapse at base\n  → Prevention: Sterilize soil, avoid overwatering\n  → Control: Trichoderma seed treatment\n\n✓ Leaf Spot:\n  → Control: Remove infected leaves\n  → Spray: Bordeaux mixture or copper fungicide\n  → Prevention: Avoid overhead irrigation\n\n✓ Root Rot (Wilting without water stress):\n  → Control: Improve drainage immediately\n  → Add Trichoderma/Pseudomonas to soil\n  → Reduce watering frequency\n\n🌿 Organic Fungicides:\n✓ Bordeaux Mixture: Copper+Lime, spray 1% solution\n✓ Sulfur Powder: For powdery mildew, 50g/10L\n✓ Trichoderma: Biological fungicide, soil treatment\n✓ Neem Oil: 3% spray for fungal+pest control\n\n✏️ Prevention is Key:\n✓ Proper crop rotation (2-3 years)\n✓ Clean farm tools between plants\n✓ Remove infected plant material\n✓ Maintain good air circulation",
            "title": "Disease Management & Treatment",
            "confidence": 0.85,
            "source_count": 1
        }
    
    # WATER MANAGEMENT & IRRIGATION
    water_keywords = ["water", "irrigation", "drought", "flood", "waterlogging", "rainfall", "monsoon", "drip", "flood irrigation"]
    if any(kw in q for kw in water_keywords):
        return {
            "answer": "💧 Water Management & Irrigation Guide:\n\n🚰 Irrigation Methods:\n✓ Flood/Basin Irrigation:\n  → For: Rice, sugarcane, pulses\n  → Frequency: Every 7-14 days\n  → Water use: 50-60 cm over season\n\n✓ Drip Irrigation:\n  → For: Vegetables, spices, horticulture\n  → Saves: 40-60% water vs flood\n  → Fertigation: Apply fertilizers through drip\n  → Frequency: Every 1-2 days\n\n✓ Sprinkler Irrigation:\n  → For: Wheat, maize, cotton\n  → Coverage: 80-85% uniform\n  → Saves: 30-50% water vs flood\n\n📊 Watering Schedule by Crop:\n✓ Rice: Standing water 5cm, drain 7-10 days before harvest\n✓ Wheat: 4-5 irrigations (CRI, 21, 45, 60, 75 days)\n✓ Cotton: 8-12 irrigations in season\n✓ Vegetables: Light, frequent watering\n✓ Sugarcane: Heavy irrigation every 10-15 days\n\n⚠️ Signs of Water Stress:\n✓ Wilting leaves = Underwatering\n✓ Yellowing + soft stems = Overwatering/Waterlogging\n✓ Leaf curl = Usually drought\n\n🏜️ Drought Management:\n✓ Use drought-resistant varieties\n✓ Add 1-2% mulch to retain moisture\n✓ Reduce nitrogen (use less N fertilizer)\n✓ Drip irrigation more efficient\n\n🌊 Flood Management:\n✓ Improve field drainage immediately\n✓ Add sand/compost to raise soil level\n✓ Don't plant submerged crops\n✓ Apply fungicides after flood (disease risk)",
            "title": "Water Management & Irrigation",
            "confidence": 0.82,
            "source_count": 1
        }
    
    # CROP-SPECIFIC QUESTIONS
    crop_keywords = {
        "rice": "Rice",
        "wheat": "Wheat",
        "corn|maize": "Maize",
        "cotton": "Cotton",
        "sugarcane": "Sugarcane",
        "pulse|gram|chickpea|lentil": "Pulses",
        "vegetable|carrot|cabbage|onion|tomato": "Vegetables",
        "spice|turmeric|chili|cumin": "Spices",
        "oilseed|soybean|groundnut": "Oilseeds"
    }
    
    for pattern, crop_name in crop_keywords.items():
        if any(word in q for word in pattern.split("|")):
            return {
                "answer": f"🌾 {crop_name} Cultivation Guide:\n\n📋 Basics:\n✓ Season: Depends on region (kharif, rabi, zaid)\n✓ Temperature: Varies by crop and variety\n✓ Soil pH: Generally 6.0-7.5 (crop-specific optimal)\n✓ Rainfall: 60-100 cm for most crops\n\n🔧 Soil Preparation:\n✓ Deep plowing (20-25 cm)\n✓ Add 5-10 tons FYM/compost per hectare\n✓ Mix sulfur/lime if pH needs adjustment\n✓ Remove weeds and stones\n\n🌱 Sowing:\n✓ Use certified seed (high germination)\n✓ Seed treatment: Use fungicide+insecticide\n✓ Sowing depth: 3-6 cm (crop-specific)\n✓ Spacing: 20-60 cm between rows\n\n📊 Nutrient Requirements (per hectare):\n✓ Nitrogen (N): 100-200 kg depending on crop\n✓ Phosphorus (P): 40-100 kg\n✓ Potassium (K): 40-100 kg\n✓ Apply 50% N+100% P+K at basal\n✓ Apply 50% N in split during season\n\n💧 Irrigation:\n✓ First irrigation at critical growth stage\n✓ Frequency based on soil + weather\n✓ 4-6 irrigations typical for most crops\n\n🚜 Pest & Disease:\n✓ Scout fields weekly for early detection\n✓ Use insecticides only when threshold reached\n✓ Rotate pesticide groups to prevent resistance\n\n⏱️ Harvest:\n✓ Harvest at physiological maturity for quality\n✓ Moisture content: 12-14% for safe storage\n✓ Thresh immediately after harvest\n✓ Dry before storage to prevent mold",
                "title": f"{crop_name} Cultivation & Management",
                "confidence": 0.8,
                "source_count": 1
            }
    
    # SOIL FERTILITY & TESTING
    soil_keywords = ["soil", "fertility", "test", "analysis", "amendment", "compost", "manure", "organic matter"]
    if any(kw in q for kw in soil_keywords):
        return {
            "answer": "🧪 Soil Health & Fertility Guide:\n\n📊 Soil Testing:\n✓ Get soil tested every 2-3 years\n✓ Take 10-15 samples per field\n✓ Sample 15-20 cm depth\n✓ Mix samples, send 500g to lab\n\n🔬 Key Tests:\n✓ pH: Target 6.0-7.5 for most crops\n✓ EC: Electrical conductivity (salinity)\n✓ Organic Matter: Aim for 2-3%\n✓ N, P, K: Macronutrient status\n✓ Zn, Fe, Mn, B: Micronutrients\n\n♻️ Improving Soil:\n✓ Add FYM: 5-10 tons/hectare yearly\n✓ Compost: 2-5 tons/hectare\n✓ Green manure: Legume crops, plow in\n✓ Mulching: 5-10 tons/hectare\n✓ Crop rotation: Include legumes every 2-3 years\n\n🌱 Organic Matter Benefits:\n✓ Improves water retention by 10-20%\n✓ Increases N availability\n✓ Improves soil structure\n✓ Enhances microbial activity\n✓ Reduces fertilizer needs by 15-25%\n\n⚖️ Nutrient Management:\n✓ Base on soil test results\n✓ Balance N:P:K ratio\n✓ Apply split applications\n✓ Monitor crop growth\n✓ Use both organic + inorganic for best results\n\n🔴 Signs of Deficiency:\n✓ Yellowing = Nitrogen deficiency\n✓ Purple color = Phosphorus deficiency\n✓ Brown/burnt edges = Potassium deficiency\n✓ Stunted growth + chlorosis = Micronutrient issue",
            "title": "Soil Health & Fertility Management",
            "confidence": 0.8,
            "source_count": 1
        }
    
    # No specific match found - return None to let LLM handle it
    return None


def _is_generic_result(text):
    """Check if result is too generic (not location/region specific)"""
    generic_indicators = [
        "a wide range of",
        "includes cereals such as",
        "these include",
        "these crops",
        "general principles",
        "in general",
        "typically includes"
    ]
    
    return any(indicator in text.lower()[:200] for indicator in generic_indicators)

def _add_search_guidance(question, docs):
    """Add guidance when results seem generic"""
    # Detect what the user is asking about
    regional_keywords = ["coorg", "karnataka", "region", "state", "area", "where"]
    crop_keywords = ["coffee", "tea", "spice", "crop", "grow", "cultivat"]
    
    is_regional = any(keyword in question.lower() for keyword in regional_keywords)
    is_crop_specific = any(keyword in question.lower() for keyword in crop_keywords)
    
    if is_regional and is_crop_specific:
        # This is a regional-crop query but we got generic results
        guidance = f"""
[Note: Search results are generic. For region-specific information about {question.split()[-2:]} cultivation:

RECOMMENDATION:
1. The knowledge base has limited region-specific documents
2. For detailed Coorg/Karnataka agricultural info, add:
   - Regional agricultural manuals
   - Coffee plantation guides
   - State-specific soil classification documents
3. After adding documents, use Option 5 to rebuild the knowledge base

To get better results now, try rephrasing as:
- "coffee cultivation techniques in India"
- "alkaline soil crops and management"
- "plantation agriculture best practices"]"""
        
        docs[0] = docs[0] + guidance
    
    return docs

# Initialize database on module load
def initialize_knowledge_base():
    """Initialize the knowledge base on module import"""
    if CHROMADB_AVAILABLE and EMBEDDINGS_AVAILABLE:
        if should_rebuild_db():
            build_vector_db()

def rebuild_knowledge_base():
    """Manually rebuild the knowledge base from scratch"""
    return build_vector_db(force=True)

def get_db_stats():
    """Get statistics about the knowledge base"""
    if not CHROMADB_AVAILABLE:
        return None
    
    try:
        import chromadb
        client = chromadb.PersistentClient(str(VECTOR_DB_DIR))
        collection = client.get_collection("soil_knowledge")
        count = collection.count()
        return {
            "total_documents": count,
            "pdfs_processed": len(list(KNOWLEDGE_BASE_DIR.glob("*.pdf"))),
            "db_size_mb": VECTOR_DB_DIR.stat().st_size / (1024*1024) if VECTOR_DB_DIR.exists() else 0
        }
    except:
        return None

# Auto-initialize when module is imported
initialize_knowledge_base()

if __name__ == "__main__":
    print("Building vector DB from PDFs in knowledge_base/ ...")
    build_vector_db(force=True)
    print("Done.")

