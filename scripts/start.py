"""
🌱 AI SOIL DOCTOR - Quick Launcher
Simple launcher that handles import issues
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

print("=" * 70)
print("🌱 AI SOIL DOCTOR v1.0 - Agricultural Intelligence Platform")
print("=" * 70)
print()

def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           🌱 AI SOIL DOCTOR v1.0 🌱                          ║
    ║                                                              ║
    ║        Your Intelligent Soil Health Companion               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def show_main_menu():
    print("\n" + "=" * 70)
    print("MAIN MENU")
    print("=" * 70)
    print()
    print("1. 🩺 SOIL DIAGNOSIS")
    print("   → Analyze soil health with 10 parameters")
    print("   → Get Liebig's Law analysis")
    print("   → Receive actionable recommendations")
    print()
    print("2. 🌾 CROP ADVISORY")
    print("   → Get crop recommendations by season")
    print("   → View regional crop guidance")
    print("   → Plan your agricultural calendar")
    print()
    print("3. 📊 VIEW SAMPLE ANALYSIS")
    print("   → See example soil analysis")
    print("   → Understand the output format")
    print()
    print("4. ℹ️  HELP & DOCUMENTATION")
    print("   → View system information")
    print("   → Read user guide")
    print()
    print("5. 🚪 EXIT")
    print()
    print("=" * 70)

def soil_diagnosis():
    """Simple soil diagnosis using Liebig's Law"""
    from soil_fertility_detection_v3 import SoilFertilityClassifier
    
    print("\n" + "=" * 70)
    print("🩺 SOIL DIAGNOSIS - Liebig's Law Analysis")
    print("=" * 70)
    print()
    print("Enter soil parameters (or press Enter for sample data):")
    print()
    
    try:
        # Get user input
        field_name = input("Field Name [Sample Field]: ").strip() or "Sample Field"
        
        n_input = input("Nitrogen (N) in kg/ha [350]: ").strip()
        N = float(n_input) if n_input else 350
        
        p_input = input("Phosphorus (P) in kg/ha [25]: ").strip()
        P = float(p_input) if p_input else 25
        
        k_input = input("Potassium (K) in kg/ha [200]: ").strip()
        K = float(k_input) if k_input else 200
        
        ph_input = input("pH (0-14 scale) [6.5]: ").strip()
        pH = float(ph_input) if ph_input else 6.5
        
        ec_input = input("EC (dS/m) [0.8]: ").strip()
        EC = float(ec_input) if ec_input else 0.8
        
        oc_input = input("Organic Carbon (%) [3.0]: ").strip()
        OC = float(oc_input) if oc_input else 3.0
        
        print("\n" + "=" * 70)
        print("ANALYZING...")
        print("=" * 70)
        
        # Perform analysis
        classifier = SoilFertilityClassifier()
        report = classifier.generate_detailed_report(N, P, K, pH, EC, OC, field_name)
        
        print(report)
        
        # Save report
        output_file = f"reports/{field_name.replace(' ', '_')}_analysis.txt"
        os.makedirs("reports", exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"\n✓ Report saved to: {output_file}")
        
    except ValueError as e:
        print(f"\n❌ Error: Invalid input. Please enter numeric values.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def crop_advisory():
    """Crop advisory system"""
    from season_crop_predictor import crops_for_season, get_season_details
    
    print("\n" + "=" * 70)
    print("🌾 CROP ADVISORY - Seasonal Planning")
    print("=" * 70)
    print()
    print("Available Seasons:")
    print("1. Kharif (Monsoon Season: June-October)")
    print("2. Rabi (Winter Season: October-April)")
    print("3. Zaid (Summer Season: March-June)")
    print()
    
    season_map = {"1": "Kharif", "2": "Rabi", "3": "Zaid"}
    choice = input("Select season (1-3): ").strip()
    
    season = season_map.get(choice)
    if not season:
        print("❌ Invalid selection")
        return
    
    print(f"\n📅 {season.upper()} SEASON")
    print("=" * 70)
    
    # Get season details
    details = get_season_details(season)
    if details:
        print(f"\nSowing Period: {details['sowing']}")
        print(f"Harvesting Period: {details['harvesting']}")
        print(f"Major Regions: {', '.join(details['regions'])}")
    
    # Get crops
    crops = crops_for_season(season)
    if crops:
        print(f"\nRecommended Crops ({len(crops)}):")
        for i, crop in enumerate(crops, 1):
            print(f"  {i}. {crop}")
    
    print()

def sample_analysis():
    """Show sample analysis"""
    from soil_fertility_detection_v3 import SoilFertilityClassifier
    
    print("\n" + "=" * 70)
    print("📊 SAMPLE SOIL ANALYSIS")
    print("=" * 70)
    print()
    print("Sample Parameters:")
    print("  Field: Demo Farm")
    print("  N: 350 kg/ha")
    print("  P: 25 kg/ha")
    print("  K: 200 kg/ha")
    print("  pH: 6.5")
    print("  EC: 0.8 dS/m")
    print("  OC: 3.0%")
    print()
    
    classifier = SoilFertilityClassifier()
    report = classifier.generate_detailed_report(350, 25, 200, 6.5, 0.8, 3.0, "Demo Farm")
    print(report)

def show_help():
    """Show help and documentation"""
    print("\n" + "=" * 70)
    print("ℹ️  HELP & DOCUMENTATION")
    print("=" * 70)
    print()
    print("📚 SYSTEM INFORMATION")
    print()
    print("AI Soil Doctor v1.0 is a comprehensive agricultural intelligence")
    print("platform that combines:")
    print()
    print("  • Liebig's Law of the Minimum for soil fertility analysis")
    print("  • Machine Learning for classification (80% accuracy)")
    print("  • RAG system for expert recommendations")
    print("  • Geospatial analysis for mapping")
    print("  • Crop advisory for seasonal planning")
    print()
    print("📖 DOCUMENTATION")
    print()
    print("  • README.md - Comprehensive documentation")
    print("  • docs/ - Detailed guides and references")
    print("  • dataset/10_PARAMETERS_GUIDE.md - Parameter specifications")
    print()
    print("🎯 QUICK START")
    print()
    print("  1. Select 'Soil Diagnosis' from main menu")
    print("  2. Enter your soil parameters")
    print("  3. Get instant analysis and recommendations")
    print()
    print("💡 TIPS")
    print()
    print("  • Fix pH first - it's the gatekeeper of nutrients")
    print("  • Focus on the limiting factor identified")
    print("  • Re-test soil after each growing season")
    print()

def main():
    """Main application loop"""
    print_banner()
    
    while True:
        show_main_menu()
        choice = input("Select an option (1-5): ").strip()
        
        if choice == "1":
            soil_diagnosis()
        elif choice == "2":
            crop_advisory()
        elif choice == "3":
            sample_analysis()
        elif choice == "4":
            show_help()
        elif choice == "5":
            print("\n👋 Thank you for using AI Soil Doctor!")
            print("🌱 Have a great day! 🌾\n")
            break
        else:
            print("\n❌ Invalid choice. Please select 1-5.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("\nPlease check the documentation or contact support.")
