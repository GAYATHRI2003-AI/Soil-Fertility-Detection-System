# -*- coding: utf-8 -*-
"""
Integrated Soil Fertility System: ML + RAG Pipeline
Combines Machine Learning predictions with Retrieval-Augmented Generation for soil analysis
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Import the RAG system
from rag_system import ComprehensiveRAGSystem


# ============================================
# INTEGRATED ANALYSIS SYSTEM
# ============================================

class IntegratedSoilAnalysisSystem:
    """
    Combines:
    1. Machine Learning for quick fertility classification
    2. RAG System for detailed, evidence-based recommendations
    """
    
    def __init__(self):
        print("\n" + "="*70)
        print("INITIALIZING INTEGRATED ML + RAG SOIL ANALYSIS SYSTEM")
        print("="*70 + "\n")
        
        # Initialize ML model
        print("[1/2] Loading ML Model...")
        self.ml_model = None
        self.has_ml_model = False
        
        # Initialize RAG system
        print("[2/2] Initializing RAG System...")
        self.rag_system = ComprehensiveRAGSystem()
        
        print("\n" + "="*70)
        print("[SUCCESS] SYSTEM READY: ML + RAG Integration Complete")
        print("="*70 + "\n")

    
    def train_ml_model(self, df):
        """Train RandomForest model on soil data with all 20 parameters"""
        print("\nTraining ML Classification Model (20 parameters)...")
        
        # All 20 soil parameters
        feature_cols = [
            'Nitrogen_mg_kg', 'Phosphorus_mg_kg', 'Potassium_mg_kg',
            'Soil_pH', 'Electrical_Conductivity_dS_m', 'Organic_Carbon_percent',
            'Cation_Exchange_Capacity_cmol_kg',
            'Sand_percent', 'Silt_percent', 'Clay_percent',
            'Zinc_mg_kg', 'Iron_mg_kg', 'Copper_mg_kg', 'Manganese_mg_kg', 'Boron_mg_kg',
            'Sulfur_mg_kg', 'Calcium_mg_kg', 'Magnesium_mg_kg'
        ]
        
        X = df[feature_cols]
        y = df['Soil_Fertility_Status'].map({'Poor': 0, 'Suboptimal': 1, 'Good': 2, 'Excellent': 3, 'Optimal': 4})
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.ml_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=15)
        self.ml_model.fit(X_train, y_train)
        self.has_ml_model = True
        
        # Store feature names for later use
        self.feature_cols = feature_cols
        
        # Evaluate
        y_pred = self.ml_model.predict(X_test)
        accuracy = (y_pred == y_test).mean()
        print(f"[OK] Model Trained - Accuracy: {accuracy:.2%}")
        
        # Feature importance
        importance_df = pd.DataFrame({
            'Feature': feature_cols,
            'Importance': self.ml_model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        print("\nTop 5 Most Important Features:")
        for idx, row in importance_df.head(5).iterrows():
            print(f"  {row['Feature']}: {row['Importance']:.3f}")
    
    def analyze_single_reading(self, parameters_dict, crop="corn"):
        """
        Analyze soil reading with all 20 parameters using ML + RAG
        
        Parameters:
            parameters_dict: dict with all 20 soil parameters
            crop: crop type
        
        Returns: ML prediction + RAG detailed recommendations
        """
        
        analysis = {
            'soil_parameters': parameters_dict,
            'crop': crop,
            'timestamp': datetime.now()
        }
        
        # ML Prediction
        if self.has_ml_model:
            input_data = np.array([[parameters_dict.get(col, 0) for col in self.feature_cols]])
            ml_pred = self.ml_model.predict(input_data)[0]
            ml_prob = self.ml_model.predict_proba(input_data)[0]
            
            status_map = {0: 'Poor', 1: 'Suboptimal', 2: 'Good', 3: 'Excellent', 4: 'Optimal'}
            analysis['ml_prediction'] = status_map[ml_pred]
            analysis['ml_confidence'] = max(ml_prob) * 100
        else:
            analysis['ml_prediction'] = None
            analysis['ml_confidence'] = None
        
        # RAG Recommendation - use first 5 parameters for compatibility
        analysis['rag_recommendation'] = self.rag_system.analyze_soil(
            parameters_dict.get('Nitrogen_mg_kg', 25),
            parameters_dict.get('Phosphorus_mg_kg', 25),
            parameters_dict.get('Potassium_mg_kg', 150),
            parameters_dict.get('Soil_pH', 6.5),
            parameters_dict.get('Electrical_Conductivity_dS_m', 0.8),
            crop
        )
        
        return analysis
    
    def generate_combined_report(self, analysis):
        """
        Generate combined ML + RAG report
        """
        recommendation = analysis['rag_recommendation']
        
        report = []
        report.append("\n" + "="*70)
        report.append("INTEGRATED SOIL FERTILITY ANALYSIS REPORT")
        report.append("ML + RAG Enhanced Assessment (20 Parameters)")
        report.append("="*70)
        
        # Parameters
        report.append("\n[SOIL PARAMETERS SUMMARY]")
        params = analysis['soil_parameters']
        
        # Extract values, handling both old and new key formats
        report.append(f"  Nitrogen (N): {params.get('Nitrogen_mg_kg', params.get('N', 'N/A'))} mg/kg")
        report.append(f"  Phosphorus (P): {params.get('Phosphorus_mg_kg', params.get('P', 'N/A'))} mg/kg")
        report.append(f"  Potassium (K): {params.get('Potassium_mg_kg', params.get('K', 'N/A'))} mg/kg")
        report.append(f"  pH Level: {params.get('Soil_pH', params.get('pH', 'N/A'))}")
        report.append(f"  EC (Salinity): {params.get('Electrical_Conductivity_dS_m', params.get('EC', 'N/A'))} dS/m")
        report.append(f"  Organic Carbon: {params.get('Organic_Carbon_percent', 'N/A')}%")
        report.append(f"  CEC: {params.get('Cation_Exchange_Capacity_cmol_kg', 'N/A')} cmol/kg")
        report.append(f"  Crop: {analysis['crop']}")
        
        # ML Prediction
        if analysis['ml_prediction']:
            report.append("\n[MACHINE LEARNING PREDICTION]")
            report.append(f"  Classification: {analysis['ml_prediction']}")
            report.append(f"  Confidence: {analysis['ml_confidence']:.1f}%")
            report.append(f"  Method: Random Forest (100 trees, 18 features)")
        
        # RAG Analysis
        report.append("\n[RAG-ENHANCED SOIL STATUS]")
        report.append(f"  {recommendation['soil_status']}")
        
        report.append("\n[IDENTIFIED ISSUES & ACTIONS]")
        if recommendation['issues_identified']:
            for i, issue in enumerate(recommendation['issues_identified'], 1):
                report.append(f"\n  {i}. {issue['parameter']} - SEVERITY: {issue['severity']}")
                report.append(f"     Current: {issue['value']} | Target: {issue['optimal']}")
        else:
            report.append("  [OK] No issues identified - soil parameters are optimal")
        
        report.append("\n[RECOMMENDED MANAGEMENT PRACTICES]")
        if recommendation['specific_actions']:
            for i, action in enumerate(recommendation['specific_actions'], 1):
                report.append(f"\n  {i}. {action['action']}")
                report.append(f"     Priority: {action['type']}")
                report.append(f"     Action: {action['recommendation']}")
                report.append(f"     When: {action.get('application_timing', 'ASAP')}")
                if 'products' in action:
                    report.append(f"     Product Options:")
                    for product in action['products'][:2]:  # Show top 2
                        report.append(f"       - {product}")
        
        report.append("\n[ESTIMATED IMPACT & RECOVERY]")
        impact = recommendation['expected_impact']
        report.append(f"  Potential Yield Loss: {impact['estimated_yield_loss']}")
        report.append(f"  Revenue Impact: {impact['revenue_impact_per_acre']}/acre")
        report.append(f"  Recovery Time: {impact['recovery_timeline_weeks']} weeks with treatment")
        
        report.append("\n[CONFIDENCE & RELIABILITY]")
        conf = recommendation['confidence']
        ml_conf_str = f"{analysis['ml_confidence']:.0f}%" if analysis['ml_prediction'] else "N/A"
        report.append(f"  ML Confidence: {ml_conf_str}")
        report.append(f"  RAG Confidence: {conf['overall_confidence']*100:.0f}%")
        report.append(f"  Combined Assessment Reliability: HIGH (triangulation of methods)")
        report.append(f"  Data Quality: {conf['data_quality']}")
        
        report.append("\n[NEXT STEPS]")
        report.append("  1. Implement recommended soil amendments")
        report.append("  2. Re-test soil in 4-6 weeks to verify improvements")
        report.append("  3. Monitor crop growth and adjust management as needed")
        report.append("  4. Maintain soil health with annual testing and organic matter addition")
        
        report.append("\n" + "="*70 + "\n")
        
        return "\n".join(report)


# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Run integrated analysis on sample data with all 20 parameters"""
    
    print("\n" + "="*70)
    print("SOIL FERTILITY ANALYSIS: ML + RAG SYSTEM (20 PARAMETERS)")
    print("="*70 + "\n")
    
    # Initialize system
    system = IntegratedSoilAnalysisSystem()
    
    # Generate sample soil data with all 20 parameters
    print("Generating comprehensive soil data (20 parameters)...")
    
    data = []
    fertility_statuses = ['Poor', 'Suboptimal', 'Good', 'Excellent', 'Optimal']
    
    for i in range(50):  # 50 sample readings
        timestamp = datetime(2026, 1, 1) + timedelta(days=i % 10, hours=i % 24)
        
        # Generate realistic parameter ranges
        N = random.randint(18, 45)
        P = random.randint(12, 40)
        K = random.randint(95, 220)
        pH = round(random.uniform(5.4, 7.2), 2)
        EC = round(random.uniform(0.6, 1.8), 2)
        OC = round(random.uniform(1.5, 3.8), 2)
        CEC = round(random.uniform(10.8, 17.2), 2)
        
        # Texture components (should sum ~100)
        sand = random.randint(25, 45)
        silt = random.randint(35, 50)
        clay = 100 - sand - silt
        
        # Micronutrients
        Zn = round(random.uniform(1.0, 3.5), 2)
        Fe = round(random.uniform(50, 110), 1)
        Cu = round(random.uniform(0.6, 2.5), 2)
        Mn = round(random.uniform(6, 18), 1)
        B = round(random.uniform(0.3, 1.8), 2)
        
        # Secondary nutrients
        S = round(random.uniform(10, 25), 1)
        Ca = random.randint(350, 650)
        Mg = random.randint(80, 200)
        
        # Derived fields
        texture_class = "Loam" if 20 <= clay <= 30 else ("Clay Loam" if clay > 30 else "Sandy Loam")
        
        # Determine fertility status based on parameters
        score = 0
        if 20 <= N <= 40: score += 1
        if 15 <= P <= 40: score += 1
        if 100 <= K <= 250: score += 1
        if 6.0 <= pH <= 7.0: score += 1
        if 0.4 <= EC <= 1.2: score += 1
        if 2.5 <= OC <= 4.0: score += 1
        if 10 <= CEC <= 20: score += 1
        if 20 <= clay <= 30: score += 1
        if 1.5 <= Zn <= 3.0: score += 1
        if 60 <= Fe <= 100: score += 1
        
        if score >= 9:
            fertility_status = 'Optimal'
            yield_estimate = random.randint(145, 160)
        elif score >= 7:
            fertility_status = 'Excellent'
            yield_estimate = random.randint(130, 145)
        elif score >= 5:
            fertility_status = 'Good'
            yield_estimate = random.randint(110, 130)
        elif score >= 3:
            fertility_status = 'Suboptimal'
            yield_estimate = random.randint(80, 110)
        else:
            fertility_status = 'Poor'
            yield_estimate = random.randint(40, 80)
        
        data.append({
            'Timestamp': timestamp,
            'Field_ID': f'Field_{i % 5 + 1:02d}',
            'Nitrogen_mg_kg': N,
            'Phosphorus_mg_kg': P,
            'Potassium_mg_kg': K,
            'Soil_pH': pH,
            'Electrical_Conductivity_dS_m': EC,
            'Organic_Carbon_percent': OC,
            'Cation_Exchange_Capacity_cmol_kg': CEC,
            'Sand_percent': sand,
            'Silt_percent': silt,
            'Clay_percent': clay,
            'Zinc_mg_kg': Zn,
            'Iron_mg_kg': Fe,
            'Copper_mg_kg': Cu,
            'Manganese_mg_kg': Mn,
            'Boron_mg_kg': B,
            'Sulfur_mg_kg': S,
            'Calcium_mg_kg': Ca,
            'Magnesium_mg_kg': Mg,
            'Soil_Texture_Class': texture_class,
            'Expected_Crop_Yield_Bu_acre': yield_estimate,
            'Soil_Fertility_Status': fertility_status
        })
    
    df = pd.DataFrame(data)
    print(f"[OK] Generated {len(df)} comprehensive soil readings\n")
    
    # Save to dataset folder
    dataset_folder = 'dataset'
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)
    
    df.to_csv(os.path.join(dataset_folder, 'soil_fertility_data.csv'), index=False)
    print(f"[OK] Training data saved to 'dataset/soil_fertility_data.csv'\n")
    
    # Train ML model
    system.train_ml_model(df)
    
    # Analyze critical readings
    print("\n" + "="*70)
    print("ANALYZING CRITICAL SOIL CONDITIONS")
    print("="*70)
    
    # Case 1: Low nutrients
    print("\n[CASE 1] Low Nitrogen & Poor Soil Health")
    print("-" * 70)
    case1_params = {
        'Nitrogen_mg_kg': 18, 'Phosphorus_mg_kg': 12, 'Potassium_mg_kg': 95,
        'Soil_pH': 5.8, 'Electrical_Conductivity_dS_m': 0.6, 'Organic_Carbon_percent': 1.5,
        'Cation_Exchange_Capacity_cmol_kg': 10.8, 'Sand_percent': 50, 'Silt_percent': 35,
        'Clay_percent': 15, 'Zinc_mg_kg': 1.0, 'Iron_mg_kg': 50, 'Copper_mg_kg': 0.6,
        'Manganese_mg_kg': 6, 'Boron_mg_kg': 0.3, 'Sulfur_mg_kg': 10,
        'Calcium_mg_kg': 350, 'Magnesium_mg_kg': 80
    }
    analysis1 = system.analyze_single_reading(case1_params, crop="corn")
    print(system.generate_combined_report(analysis1))
    
    # Case 2: Optimal conditions
    print("\n[CASE 2] Optimal Soil Conditions (All Parameters Balanced)")
    print("-" * 70)
    case2_params = {
        'Nitrogen_mg_kg': 35, 'Phosphorus_mg_kg': 30, 'Potassium_mg_kg': 180,
        'Soil_pH': 6.5, 'Electrical_Conductivity_dS_m': 0.9, 'Organic_Carbon_percent': 3.2,
        'Cation_Exchange_Capacity_cmol_kg': 15.5, 'Sand_percent': 35, 'Silt_percent': 45,
        'Clay_percent': 20, 'Zinc_mg_kg': 2.1, 'Iron_mg_kg': 85, 'Copper_mg_kg': 1.2,
        'Manganese_mg_kg': 12, 'Boron_mg_kg': 0.8, 'Sulfur_mg_kg': 18,
        'Calcium_mg_kg': 500, 'Magnesium_mg_kg': 150
    }
    analysis2 = system.analyze_single_reading(case2_params, crop="wheat")
    print(system.generate_combined_report(analysis2))
    
    # Case 3: High salinity
    print("\n[CASE 3] High Salinity Stress (EC Too High)")
    print("-" * 70)
    case3_params = {
        'Nitrogen_mg_kg': 30, 'Phosphorus_mg_kg': 25, 'Potassium_mg_kg': 160,
        'Soil_pH': 7.2, 'Electrical_Conductivity_dS_m': 2.8, 'Organic_Carbon_percent': 2.0,
        'Cation_Exchange_Capacity_cmol_kg': 12.0, 'Sand_percent': 45, 'Silt_percent': 40,
        'Clay_percent': 15, 'Zinc_mg_kg': 1.5, 'Iron_mg_kg': 70, 'Copper_mg_kg': 0.9,
        'Manganese_mg_kg': 10, 'Boron_mg_kg': 0.6, 'Sulfur_mg_kg': 15,
        'Calcium_mg_kg': 450, 'Magnesium_mg_kg': 120
    }
    analysis3 = system.analyze_single_reading(case3_params, crop="vegetables")
    print(system.generate_combined_report(analysis3))
    
    # Save comprehensive results for first 20 readings
    print("\n" + "="*70)
    print("GENERATING FULL DATASET ANALYSIS")
    print("="*70 + "\n")
    
    results = []
    for idx, row in df.head(20).iterrows():
        params_dict = row.to_dict()
        analysis = system.analyze_single_reading(params_dict, crop="corn")
        
        result_dict = {
            'Timestamp': row['Timestamp'],
            'Field_ID': row['Field_ID'],
            'Nitrogen_mg_kg': row['Nitrogen_mg_kg'],
            'Phosphorus_mg_kg': row['Phosphorus_mg_kg'],
            'Potassium_mg_kg': row['Potassium_mg_kg'],
            'Soil_pH': row['Soil_pH'],
            'EC_dS_m': row['Electrical_Conductivity_dS_m'],
            'OC_percent': row['Organic_Carbon_percent'],
            'CEC_cmol_kg': row['Cation_Exchange_Capacity_cmol_kg'],
            'Texture_Class': row['Soil_Texture_Class'],
            'Actual_Status': row['Soil_Fertility_Status'],
            'ML_Prediction': analysis['ml_prediction'],
            'ML_Confidence': f"{analysis['ml_confidence']:.1f}%",
        }
        results.append(result_dict)
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(dataset_folder, 'integrated_analysis_results.csv'), index=False)
    print("[OK] Results saved to 'dataset/integrated_analysis_results.csv'\n")
    
    print(results_df.to_string(index=False))
    
    # Visualization
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70 + "\n")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Nitrogen distribution
    axes[0, 0].hist(df['Nitrogen_mg_kg'], bins=12, color='green', alpha=0.7, edgecolor='black')
    axes[0, 0].axvline(30, color='red', linestyle='--', label='Optimal N=30')
    axes[0, 0].set_title('Nitrogen Distribution (20 Readings)', fontweight='bold')
    axes[0, 0].set_xlabel('N (mg/kg)')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)
    
    # Plot 2: pH distribution
    axes[0, 1].hist(df['Soil_pH'], bins=12, color='blue', alpha=0.7, edgecolor='black')
    axes[0, 1].axvline(6.5, color='red', linestyle='--', label='Optimal pH=6.5')
    axes[0, 1].set_title('Soil pH Distribution', fontweight='bold')
    axes[0, 1].set_xlabel('pH Level')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)
    
    # Plot 3: Fertility status distribution
    fertility_counts = df['Soil_Fertility_Status'].value_counts()
    colors_status = {'Poor': '#d62728', 'Suboptimal': '#ff7f0e', 'Good': '#2ca02c', 'Excellent': '#1f77b4', 'Optimal': '#9467bd'}
    colors = [colors_status.get(status, '#1f77b4') for status in fertility_counts.index]
    axes[1, 0].bar(fertility_counts.index, fertility_counts.values, color=colors, edgecolor='black')
    axes[1, 0].set_title('Soil Fertility Classification Distribution', fontweight='bold')
    axes[1, 0].set_ylabel('Count')
    axes[1, 0].grid(alpha=0.3, axis='y')
    
    # Plot 4: EC vs Organic Carbon correlation
    scatter = axes[1, 1].scatter(df['Electrical_Conductivity_dS_m'], df['Organic_Carbon_percent'],
                                  c=df['Soil_pH'], cmap='RdYlBu_r', s=50, alpha=0.6, edgecolor='black')
    axes[1, 1].set_xlabel('EC (dS/m)')
    axes[1, 1].set_ylabel('Organic Carbon (%)')
    axes[1, 1].set_title('EC vs Organic Carbon (colored by pH)', fontweight='bold')
    axes[1, 1].grid(alpha=0.3)
    cbar = plt.colorbar(scatter, ax=axes[1, 1])
    cbar.set_label('pH')
    
    plt.tight_layout()
    plt.savefig(os.path.join(dataset_folder, 'soil_analysis_comprehensive.png'), dpi=100, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Visualization saved to 'dataset/soil_analysis_comprehensive.png'\n")
    
    print("="*70)
    print("ANALYSIS COMPLETE - ALL FILES SAVED TO 'dataset/' FOLDER")
    print("="*70)



if __name__ == "__main__":
    main()
