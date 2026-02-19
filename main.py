#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌱 AI SOIL DOCTOR v1.0
Your Intelligent Soil Health Companion

Core Features:
1. SOIL DIAGNOSIS: Comprehensive soil health analysis with 10+ parameters
2. CROP ADVISORY: Smart recommendations and seasonal planning
3. KNOWLEDGE BASE: Agricultural Q&A with document analysis
4. SEASON-CROP PREDICTION: Intelligent crop scheduling
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Setup paths
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def print_banner():
    """Display the application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                 🌱 AI SOIL DOCTOR v1.0                   ║
    ║         Your Intelligent Soil Health Companion           ║
    ╚══════════════════════════════════════════════════════════╝
    
    🔍 Diagnose • 🌾 Grow • 📊 Analyze • 📚 Learn
    """
    print(banner)

def show_main_menu():
    """Display the main menu with all available options."""
    menu = """
    ┌──────────────────────────────────────────────────────┐
    │                  MAIN MENU                           │
    ├──────────────────────────────────────────────────────┤
    │  1. 🩺  Soil Health Analysis (Liebig's Law)         │
    │  2. 🌾  Crop Advisory by Season                     │
    │  3. 🌱  Season-Crop Prediction                      │
    │  4. 📚  Knowledge Base (Agricultural Q&A)           │
    │  5. 🔄  Update Knowledge Base                       │
    │  6. ℹ️   About & Documentation                      │
    │  0. 🚪  Exit                                        │
    └─────────────────────────────────────────────────────┘
    """
    print(menu)

def soil_health_analysis():
    """Handle soil health analysis using Liebig's Law."""
    print("\n" + "="*60)
    print("🩺 SOIL HEALTH ANALYSIS (Liebig's Law of the Minimum)")
    print("="*60)
    print("\nOptions:")
    print("1. Manual Parameter Entry (10 parameters)")
    print("2. Batch Analysis from CSV File")
    print("3. View Example Analysis")
    print("4. Back to Main Menu")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        analyze_single_field()
    elif choice == "2":
        analyze_batch_csv()
    elif choice == "3":
        print("\n📊 Example soil analysis data available in: dataset/")
        print("CSV files: liebig_fertility_assessment.csv, soil_fertility_data.csv")
    elif choice == "4":
        return
    else:
        print("❌ Invalid option.")

def analyze_single_field():
    """Analyze a single field with 10 soil parameters."""
    try:
        from src.soil_fertility_detection_v3 import SoilFertilityClassifier
    except ImportError:
        print("❌ Soil Fertility Analysis module not available. Please install dependencies.")
        return
    
    print("\n" + "="*60)
    print("SINGLE FIELD SOIL ANALYSIS")
    print("="*60)
    print("\nEnter 10 soil parameters (press Enter for default values):\n")
    
    try:
        field_name = input("Field Name: ").strip() or "DefaultField"
        
        print("\n🌾 PRIMARY NUTRIENTS (kg/hectare)")
        N = float(input("Nitrogen (N) [typical: 150]: ") or "150")
        P = float(input("Phosphorus (P) [typical: 30]: ") or "30")
        K = float(input("Potassium (K) [typical: 150]: ") or "150")
        
        print("\n🌍 SOIL CHEMISTRY")
        pH = float(input("Soil pH [typical: 6.5]: ") or "6.5")
        EC = float(input("EC/Salinity in dS/m [typical: 1.0]: ") or "1.0")
        OC = float(input("Organic Carbon % [typical: 1.5]: ") or "1.5")
        
        print("\n💊 MICRONUTRIENTS (mg/kg)")
        S = float(input("Sulfur (S) [typical: 20]: ") or "20")
        Zn = float(input("Zinc (Zn) [typical: 1.0]: ") or "1.0")
        Fe = float(input("Iron (Fe) [typical: 20]: ") or "20")
        B = float(input("Boron (B) [typical: 1.0]: ") or "1.0")
        
        # Analyze
        classifier = SoilFertilityClassifier()
        report = classifier.generate_detailed_report(N, P, K, pH, EC, OC, field_name)
        
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        print(report)
        
        # Save option
        save = input("\n💾 Save results? (y/n): ").strip().lower()
        if save == 'y':
            import pandas as pd
            csv_file = f"dataset/{field_name}_analysis.csv"
            data = {
                'Field': [field_name], 'N': [N], 'P': [P], 'K': [K],
                'pH': [pH], 'EC': [EC], 'OC': [OC],
                'S': [S], 'Zn': [Zn], 'Fe': [Fe], 'B': [B]
            }
            df = pd.DataFrame(data)
            df.to_csv(csv_file, index=False)
            print(f"✅ Saved to {csv_file}")
            
    except ValueError:
        print("❌ Please enter valid numeric values.")
    except Exception as e:
        print(f"❌ Error: {e}")

def analyze_batch_csv():
    """Analyze multiple fields from CSV."""
    try:
        from src.liebig_rag_integration import batch_analyze_fields
    except ImportError:
        print("❌ Batch Analysis module not available. Please install dependencies.")
        return
    
    print("\n" + "="*60)
    print("BATCH FIELD ANALYSIS")
    print("="*60)
    
    csv_path = input("\nEnter CSV file path: ").strip()
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return
    
    try:
        results = batch_analyze_fields(csv_path)
        print("\n" + "="*60)
        print("BATCH ANALYSIS RESULTS")
        print("="*60)
        print(results.to_string(index=False))
        
        output_file = csv_path.replace('.csv', '_liebig_results.csv')
        results.to_csv(output_file, index=False)
        print(f"\n✅ Results saved to {output_file}")
    except Exception as e:
        print(f"❌ Error: {e}")

def crop_advisory():
    """Display crop recommendations by season."""
    try:
        from src.season_crop_predictor import crops_for_season, get_season_details
    except ImportError:
        print("❌ Crop Advisor module not available. Please install dependencies.")
        return
    
    print("\n" + "="*60)
    print("🌾 CROP ADVISORY BY SEASON")
    print("="*60)
    
    season = input("\nEnter season (Kharif/Rabi/Zaid): ").strip().capitalize()
    
    crops = crops_for_season(season)
    details = get_season_details(season)
    
    if crops and details:
        print(f"\n✅ SEASON: {season.upper()}")
        print(f"   Sowing: {details['sowing']}")
        print(f"   Harvesting: {details['harvesting']}")
        print(f"   Description: {details['description']}")
        print(f"\n🌱 RECOMMENDED CROPS:")
        for i, crop in enumerate(crops, 1):
            print(f"   {i}. {crop}")
    else:
        print("❌ Unknown season. Please use: Kharif, Rabi, or Zaid")

def season_crop_prediction():
    """Predict seasons for crops or crops for seasons."""
    try:
        from src.season_crop_predictor import crops_for_season, season_for_crop
    except ImportError:
        print("❌ Season-Crop Predictor module not available. Please install dependencies.")
        return
    
    print("\n" + "="*60)
    print("🌱 SEASON-CROP PREDICTION")
    print("="*60)
    
    print("\n1. Find crops for a season")
    print("2. Find seasons for a crop")
    
    choice = input("\nSelect (1/2): ").strip()
    
    if choice == "1":
        season = input("Enter season (Kharif/Rabi/Zaid): ").strip().capitalize()
        crops = crops_for_season(season)
        if crops:
            print(f"\n✅ Crops that grow in {season}:")
            for crop in crops:
                print(f"   • {crop}")
        else:
            print("❌ Unknown season.")
            
    elif choice == "2":
        crop = input("Enter crop name: ").strip()
        seasons = season_for_crop(crop)
        if seasons:
            print(f"\n✅ {crop} can be grown in: {', '.join(seasons)}")
        else:
            print("❌ Unknown crop.")
    else:
        print("❌ Invalid choice.")

def knowledge_base_query():
    """Query the agricultural knowledge base with LLM-synthesized answers."""
    try:
        from src.knowledge_base_query import query_knowledge_base, get_db_stats
    except ImportError:
        print("Knowledge Base module not available. Please install dependencies.")
        return
    
    print("\n" + "="*60)
    print("🌾 AGRICULTURAL KNOWLEDGE BASE")
    print("="*60)
    print("\nAsk questions about Indian soil, crops, and agriculture.")
    print("(Powered by AI-synthesized answers from agricultural research)")
    
    # Show DB stats
    stats = get_db_stats()
    if stats:
        print(f"\n📚 Knowledge Base: {stats['total_documents']} documents from {stats['pdfs_processed']} PDFs")
    
    question = input("\n❓ Your question: ").strip()
    
    if not question:
        print("Please enter a question.")
        return
    
    print("\n⏳ Searching and synthesizing answer...")
    result = query_knowledge_base(question, use_llm=True)
    
    if result and result.get("source_count", 0) > 0:
        print("\n" + "="*60)
        print(f"📖 {result['title'].upper()}")
        print("="*60)
        
        # Display the synthesized answer
        answer = result.get("answer", "No information found.")
        print(f"\n{answer}\n")
        
        # Show confidence and source info
        confidence = result.get("confidence", 0.0)
        source_count = result.get("source_count", 0)
        
        print(f"{'─'*60}")
        print(f"✓ Confidence: {confidence*100:.0f}% | Sources: {source_count} document(s)")
        print(f"{'─'*60}\n")
    else:
        error_msg = result.get("answer", "") if result else ""
        print(f"\n❌ {error_msg}")
        print("\nTip: Add relevant PDFs to knowledge_base/ folder and rebuild to get better results.")

def rebuild_knowledge_base_menu():
    """Rebuild the knowledge base from PDFs."""
    try:
        from src.knowledge_base_query import rebuild_knowledge_base, get_db_stats
    except ImportError:
        print("Knowledge Base module not available.")
        return
    
    print("\n" + "="*60)
    print("REBUILD KNOWLEDGE BASE")
    print("="*60)
    print("\nThis will re-index all PDFs in knowledge_base/ folder.")
    
    confirm = input("\nRebuild now? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print("\nProcessing PDFs (this may take several minutes)...")
    result = rebuild_knowledge_base()
    
    if result:
        stats = get_db_stats()
        if stats:
            print("\n[DONE] Knowledge base rebuilt successfully!")
            print(f"  - Documents indexed: {stats['total_documents']}")
            print(f"  - PDFs processed: {stats['pdfs_processed']}")
            print(f"  - Database size: {stats['db_size_mb']:.1f} MB")
    else:
        print("\n[ERROR] Failed to rebuild knowledge base.")

def show_about():
    """Display about and documentation information."""
    about = """
    ┌──────────────────────────────────────────────────────┐
    │             📚 ABOUT AI SOIL DOCTOR                  |
    ├──────────────────────────────────────────────────────┤
    │                                                      │
    │  AI Soil Doctor v1.0                                 │
    │  Your Intelligent Soil Health Companion              │
    │                                                      │
    │  Features:                                           │
    │  • Soil health analysis using Liebig's Law           │
    │  • Intelligent crop recommendations                  │
    │  • Season-based crop planning                        │
    │  • Agricultural knowledge base queries               │
    │  • Data analysis & visualization                     │
    │                                                      │
    │  Documentation:                                      │
    │  📖 Read: docs/ folder                              │
    │  💾 Data: dataset/ folder                           │
    │  🖼️  Images: visualizations/ folder                 │
    │  💻 Code: src/ folder                               │
    │                                                      │
    │  Project Structure:                                  │
    │  • main.py - Entry point                             │
    │  • requirements.txt - Dependencies                   │
    │  • README.md - Main documentation                    │
    │                                                      │
    └──────────────────────────────────────────────────────┘
    """
    print(about)

def main():
    """Main application loop."""
    print_banner()
    
    while True:
        try:
            show_main_menu()
            choice = input("Select an option (0-6): ").strip()
            
            if choice == "1":
                soil_health_analysis()
            elif choice == "2":
                crop_advisory()
            elif choice == "3":
                season_crop_prediction()
            elif choice == "4":
                knowledge_base_query()
            elif choice == "5":
                rebuild_knowledge_base_menu()
            elif choice == "6":
                show_about()
            elif choice == "0":
                print("\nThank you for using AI Soil Doctor. Goodbye!")
                print("Keep farming smart!\n")
                break
            else:
                print("\nInvalid option. Please select 0-6.")
                
        except KeyboardInterrupt:
            print("\n\nProgram interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("   Please try again or select a different option.")

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("dataset", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Run application
    main()
