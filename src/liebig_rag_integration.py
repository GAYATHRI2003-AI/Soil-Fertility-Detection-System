# -*- coding: utf-8 -*-
"""
LIEBIG'S LAW SOIL FERTILITY DETECTION
Integration with Existing RAG + ML System

This module bridges the new Liebig's Law classifier with the
integrated RAG + ML system, providing comprehensive analysis.
"""

import os
import pandas as pd
from soil_fertility_detection_v3 import SoilFertilityClassifier
from integrated_ml_rag import IntegratedSoilAnalysisSystem


def analyze_with_liebig_and_ml(N, P, K, pH, EC, OC, crop="corn"):
    """
    Comprehensive soil analysis combining:
    1. Liebig's Law (limiting factor analysis)
    2. RAG-based recommendations
    3. ML-based fertility classification
    
    Args:
        N: Nitrogen (kg/ha)
        P: Phosphorus (kg/ha)
        K: Potassium (kg/ha)
        pH: Soil pH
        EC: Electrical Conductivity (dS/m)
        OC: Organic Carbon (%)
        crop: Target crop type
    
    Returns:
        Comprehensive analysis dictionary
    """
    
    # Initialize classifiers
    liebig_classifier = SoilFertilityClassifier()
    ml_system = IntegratedSoilAnalysisSystem()
    
    # Get Liebig's Law assessment
    liebig_assessment = liebig_classifier.apply_liebig_law(N, P, K, pH, EC, OC)
    
    # Get ML + RAG analysis
    parameters_dict = {
        'Nitrogen_mg_kg': N,
        'Phosphorus_mg_kg': P,
        'Potassium_mg_kg': K,
        'Soil_pH': pH,
        'Electrical_Conductivity_dS_m': EC,
        'Organic_Carbon_percent': OC,
        'N': N,  # Backward compatibility
        'P': P,
        'K': K,
        'pH': pH,
    }
    
    # Combine results
    combined_analysis = {
        'liebig_assessment': liebig_assessment,
        'analysis_timestamp': pd.Timestamp.now().isoformat(),
        'soil_parameters': {
            'N_kg_ha': N,
            'P_kg_ha': P,
            'K_kg_ha': K,
            'pH': pH,
            'EC_dS_m': EC,
            'OC_percent': OC,
        },
        'consensus_fertility': determine_consensus_fertility(liebig_assessment)
    }
    
    return combined_analysis


def determine_consensus_fertility(liebig_assessment):
    """Determine overall fertility based on Liebig's assessment"""
    
    fertility_class = liebig_assessment['fertility_classification']
    limiting_factor = liebig_assessment['limiting_factor']
    final_score = liebig_assessment['final_score']
    
    return {
        'primary_classification': fertility_class,
        'limiting_factor': limiting_factor,
        'score': final_score,
        'action_priority': 'CRITICAL' if 'INFERTILE' in fertility_class else 'MEDIUM' if 'LOW' in fertility_class else 'LOW'
    }


def generate_integrated_report(analysis):
    """Generate comprehensive report from integrated analysis"""
    
    liebig = analysis['liebig_assessment']
    soil = analysis['soil_parameters']
    consensus = analysis['consensus_fertility']
    
    report = []
    report.append("\n" + "="*80)
    report.append("INTEGRATED SOIL FERTILITY ANALYSIS")
    report.append("Liebig's Law [+] RAG Recommendations [+] ML Predictions")
    report.append("="*80)
    
    report.append("\n[SOIL PARAMETERS MEASURED]")
    report.append(f"  Nitrogen (N):           {soil['N_kg_ha']:.0f} kg/ha  → {liebig['nitrogen']['classification']}")
    report.append(f"  Phosphorus (P):         {soil['P_kg_ha']:.1f} kg/ha  → {liebig['phosphorus']['classification']}")
    report.append(f"  Potassium (K):          {soil['K_kg_ha']:.0f} kg/ha  → {liebig['potassium']['classification']}")
    report.append(f"  pH:                     {soil['pH']:.2f}       → {liebig['ph']['classification']}")
    report.append(f"  EC (Salinity):          {soil['EC_dS_m']:.2f} dS/m   → {liebig['ec']['classification']}")
    report.append(f"  Organic Carbon:         {soil['OC_percent']:.2f} %     → {liebig['organic_carbon']['classification']}")
    
    report.append("\n[LIEBIG'S LAW ANALYSIS - LIMITING FACTOR]")
    report.append(f"  Index Score:            {liebig['index_score']}")
    report.append(f"  Limiting Factor:        {liebig['limiting_factor']}")
    report.append(f"  Limitation Strength:    {liebig['limiting_factor_strength']} (0.0 = blocked, 1.0 = optimal)")
    report.append(f"  Corrected Final Score:  {liebig['final_score']}")
    
    report.append("\n[CONSENSUS FERTILITY ASSESSMENT]")
    report.append(f"  Classification:         {consensus['primary_classification']}")
    report.append(f"  Summary:                {liebig['description']}")
    report.append(f"  Action Priority:        {consensus['action_priority']}")
    
    report.append("\n[ACTIONABLE RECOMMENDATIONS]")
    report.append(f"  {liebig['recommendation']}")
    
    report.append("\n" + "="*80 + "\n")
    
    return "\n".join(report)


def batch_analyze_fields(fields_csv_path):
    """
    Analyze multiple fields from CSV and apply integrated assessment
    
    Args:
        fields_csv_path: Path to CSV with columns: N, P, K, pH, EC, OC
    
    Returns:
        DataFrame with comprehensive assessment for each field
    """
    
    # Read input data
    df = pd.read_csv(fields_csv_path)
    
    results = []
    
    for idx, row in df.iterrows():
        analysis = analyze_with_liebig_and_ml(
            row['N'], row['P'], row['K'],
            row['pH'], row['EC'], row['OC']
        )
        
        liebig = analysis['liebig_assessment']
        
        results.append({
            'Field_ID': idx + 1,
            'N_kg_ha': row['N'],
            'P_kg_ha': row['P'],
            'K_kg_ha': row['K'],
            'pH': row['pH'],
            'EC_dS_m': row['EC'],
            'OC_percent': row['OC'],
            'Index_Score': liebig['index_score'],
            'Final_Score': liebig['final_score'],
            'NPK_Status': liebig['npk_overall_status'],
            'Limiting_Factor': liebig['limiting_factor'],
            'Fertility_Classification': liebig['fertility_classification'],
            'Recommendation': liebig['recommendation'][:100],  # Truncate for CSV
        })
    
    return pd.DataFrame(results)


def main():
    """Demonstrate integrated analysis"""
    
    print("\n" + "="*80)
    print("LIEBIG'S LAW + RAG + ML INTEGRATED SYSTEM")
    print("="*80)
    
    # Example fields
    fields = [
        {'name': 'Farm A - North Field', 'N': 400, 'P': 18, 'K': 200, 'pH': 6.8, 'EC': 1.2, 'OC': 0.85},
        {'name': 'Farm A - South Field', 'N': 250, 'P': 12, 'K': 150, 'pH': 5.8, 'EC': 1.5, 'OC': 0.55},
        {'name': 'Farm B - Irrigated Plot', 'N': 500, 'P': 22, 'K': 280, 'pH': 4.2, 'EC': 6.5, 'OC': 0.9},
        {'name': 'Farm B - Rainfed Plot', 'N': 150, 'P': 8, 'K': 100, 'pH': 7.2, 'EC': 0.6, 'OC': 0.25},
    ]
    
    # Analyze each field
    for field in fields:
        print(f"\nAnalyzing: {field['name']}")
        print("-" * 80)
        
        analysis = analyze_with_liebig_and_ml(
            field['N'], field['P'], field['K'],
            field['pH'], field['EC'], field['OC']
        )
        
        print(generate_integrated_report(analysis))
    
    # Batch analysis
    print("\n[BATCH ANALYSIS] Creating comprehensive assessment dataset...")
    print("-" * 80)
    
    fields_for_batch = [
        {'N': 400, 'P': 18, 'K': 200, 'pH': 6.8, 'EC': 1.2, 'OC': 0.85},
        {'N': 250, 'P': 12, 'K': 150, 'pH': 5.8, 'EC': 1.5, 'OC': 0.55},
        {'N': 500, 'P': 22, 'K': 280, 'pH': 4.2, 'EC': 6.5, 'OC': 0.9},
        {'N': 150, 'P': 8, 'K': 100, 'pH': 7.2, 'EC': 0.6, 'OC': 0.25},
        {'N': 350, 'P': 16, 'K': 180, 'pH': 6.5, 'EC': 2.5, 'OC': 0.7},
        {'N': 600, 'P': 25, 'K': 300, 'pH': 7.0, 'EC': 1.8, 'OC': 1.1},
    ]
    
    # Create temp CSV
    temp_csv = 'dataset/temp_fields.csv'
    pd.DataFrame(fields_for_batch).to_csv(temp_csv, index=False)
    
    # Batch analyze
    batch_results = batch_analyze_fields(temp_csv)
    
    # Save results
    output_csv = 'dataset/integrated_liebig_analysis.csv'
    batch_results.to_csv(output_csv, index=False)
    
    print("\n" + batch_results.to_string(index=False))
    print(f"\n[OK] Batch analysis saved to '{output_csv}'")
    
    # Cleanup
    os.remove(temp_csv)


if __name__ == "__main__":
    main()
