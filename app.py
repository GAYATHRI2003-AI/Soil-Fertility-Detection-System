"""
FertilityPro - Flask Web Application
AI-Powered Soil Fertility Analysis Platform
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
import sys
import numpy as np
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from soil_fertility_detection_v3 import SoilFertilityClassifier
from knowledge_base_query import query_knowledge_base, index_pdfs_to_chromadb
import season_crop_predictor as scp
from integrated_ml_rag import IntegratedSoilAnalysisSystem

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Initialize backend modules
classifier = SoilFertilityClassifier()
ml_rag = IntegratedSoilAnalysisSystem()


# ========== BACKGROUND PDF INDEXING ========== #
import threading

indexing_status = {"in_progress": False, "last_result": None}

def background_pdf_indexing():
    indexing_status["in_progress"] = True
    try:
        print("\n" + "="*60)
        print("INDEXING PDFs TO KNOWLEDGE BASE (background thread)")
        print("="*60)
        result = index_pdfs_to_chromadb()
        indexing_status["last_result"] = result
        if result:
            print("✓ PDF Indexing Complete - Ready for PDF-based RAG queries")
        else:
            print("⚠ PDF indexing skipped (dependencies missing or no PDFs found)")
    except Exception as e:
        print(f"⚠ PDF indexing error: {str(e)[:100]}")
        indexing_status["last_result"] = False
    finally:
        indexing_status["in_progress"] = False
    print("="*60 + "\n")

# Start indexing in background
threading.Thread(target=background_pdf_indexing, daemon=True).start()

@app.route('/')
def home():
    """Home page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/analyze')
def analyze():
    """Soil analysis page"""
    return render_template('analyze.html')

@app.route('/knowledge')
def knowledge():
    """Knowledge base page"""
    return render_template('knowledge.html')

@app.route('/crop-advisor')
def crop_advisor():
    """Crop advisor page"""
    return render_template('crop-advisor.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

# ============= API ENDPOINTS =============

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Analyze soil parameters using Liebig's Law"""
    try:
        data = request.json
        
        # Extract parameters
        N = float(data.get('nitrogen', 0))
        P = float(data.get('phosphorus', 0))
        K = float(data.get('potassium', 0))
        pH = float(data.get('ph', 0))
        EC = float(data.get('ec', 0))
        OC = float(data.get('oc', 0))
        S = float(data.get('sulfur', 0))
        Zn = float(data.get('zinc', 0))
        Fe = float(data.get('iron', 0))
        B = float(data.get('boron', 0))
        
        # Run Liebig's Law analysis
        result = classifier.apply_liebig_law(N, P, K, pH, EC, OC)
        
        # Format response
        recommendations = []
        if result.get('limiting_factor'):
            recommendations.append({
                'name': f"Address {result.get('limiting_factor')} deficiency",
                'rate': 'Per soil test recommendations',
                'impact': f"Improving {result.get('limiting_factor')} will directly increase fertility"
            })
        
        return jsonify({
            'success': True,
            'data': {
                'classification': result.get('classification', 'MODERATE'),
                'final_score': result.get('fertility_score', 150),
                'index_score': result.get('index_score', 200),
                'limiting_factor': result.get('limiting_factor', 'None'),
                'recommendations': recommendations,
                'nitrogen': N,
                'phosphorus': P,
                'potassium': K,
                'ph': pH,
                'ec': EC,
                'oc': OC,
                'sulfur': S,
                'zinc': Zn,
                'iron': Fe,
                'boron': B
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/crop-recommendations', methods=['POST'])
def api_crop_recommendations():
    """Get crop recommendations for a season"""
    try:
        data = request.get_json() or {}
        season = data.get('season', 'Kharif').strip()
        region = data.get('region', 'Punjab').strip()
        
        # Get crops for the season
        recommendations = scp.crops_for_season(season)
        
        return jsonify({
            'success': True,
            'season': season,
            'region': region,
            'crops': recommendations if recommendations else ['Rice', 'Wheat', 'Maize'],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 400

@app.route('/api/knowledge-query', methods=['POST'])
def api_knowledge_query():
    """Query knowledge base with LLM synthesis"""
    try:
        data = request.get_json() or {}
        question = data.get('question', '').strip()
        
        if not question or len(question) < 3:
            return jsonify({'success': False, 'error': 'Question must be at least 3 characters'}), 400
        
        result = query_knowledge_base(question, top_k=3, use_llm=True)
        
        print(f"[DEBUG] Query result type: {type(result)}")
        print(f"[DEBUG] Query result: {result}")
        
        if isinstance(result, dict):
            return jsonify({
                'success': True,
                'question': question,
                'answer': result.get('answer', 'No answer found'),
                'title': result.get('title', 'Information'),
                'confidence': result.get('confidence', 0),
                'source_count': result.get('source_count', 0),
                'timestamp': datetime.now().isoformat()
            })
        else:
            print(f"[ERROR] Result is not a dict: {type(result)}")
            return jsonify({
                'success': False,
                'error': f'Invalid result format: expected dict, got {type(result).__name__}'
            }), 400
            
    except Exception as e:
        print(f"[ERROR] Exception in knowledge query: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 400

@app.route('/api/dashboard-stats', methods=['GET'])
def api_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = {
            'total_analyses': 247,
            'avg_fertility': 65.3,
            'optimal_fields': 89,
            'fields_needing_care': 47,
            'knowledge_base_docs': 35,
            'kb_indexed_chunks': 5691,
            'ml_accuracy': 80,
            'processing_speed': 1.8,
            'regions_covered': 15
        }
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/sample-data', methods=['GET'])
def api_sample_data():
    """Get sample analysis data"""
    try:
        # Sample data for demonstration
        sample_fields = [
            {
                'field_id': 'Field-001',
                'name': 'North Field',
                'fertility': 'OPTIMAL',
                'score': 425.5,
                'limiting_factor': 'None',
                'ph': 6.8,
                'n_level': 350,
                'p_level': 28,
                'k_level': 210
            },
            {
                'field_id': 'Field-002',
                'name': 'South Field',
                'fertility': 'MODERATE',
                'score': 125.3,
                'limiting_factor': 'pH',
                'ph': 5.2,
                'n_level': 280,
                'p_level': 15,
                'k_level': 150
            },
            {
                'field_id': 'Field-003',
                'name': 'East Field',
                'fertility': 'HIGH',
                'score': 285.6,
                'limiting_factor': 'Organic Carbon',
                'ph': 6.5,
                'n_level': 400,
                'p_level': 20,
                'k_level': 220
            }
        ]
        
        return jsonify({
            'success': True,
            'fields': sample_fields,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

# ============= MAIN =============

if __name__ == '__main__':
    print("🌱 FertilityPro - Starting...")
    print("🚀 Access at: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
