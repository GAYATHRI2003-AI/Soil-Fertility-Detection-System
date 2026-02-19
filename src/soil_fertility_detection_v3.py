# -*- coding: utf-8 -*-
"""
Soil Fertility Detection System v3.0
Implements Liebig's Law of the Minimum with Scientific Thresholds
- Big Three (N-P-K) Classification
- pH Gatekeeper Logic
- EC (Salinity) Impact
- Organic Carbon Battery
- Index Score Calculation
"""

import pandas as pd
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple


# ============================================
# NUTRIENT CLASSIFICATION THRESHOLDS
# ============================================

class NutrientLevel(Enum):
    """Classification of nutrient levels"""
    INFERTILE = "Infertile"
    FERTILE = "Fertile"
    VERY_FERTILE = "Very Fertile"


@dataclass
class NutrientThresholds:
    """Scientific thresholds for soil nutrients (in kg/hectare)"""
    
    # Nitrogen (N)
    N_LOW = 280          # Below this: Infertile
    N_MEDIUM_UPPER = 560 # Above this: Very Fertile
    
    # Phosphorus (P)
    P_LOW = 10           # Below this: Infertile
    P_MEDIUM_UPPER = 25  # Above this: Very Fertile
    
    # Potassium (K)
    K_LOW = 110          # Below this: Infertile
    K_MEDIUM_UPPER = 280 # Above this: Very Fertile


@dataclass
class pHRanges:
    """pH classification for nutrient availability"""
    HIGHLY_ACIDIC_UPPER = 5.5
    OPTIMAL_LOWER = 6.0
    OPTIMAL_UPPER = 7.5
    ALKALINE_LOWER = 8.5


@dataclass
class ECRanges:
    """Electrical Conductivity (Salt) ranges in dS/m"""
    GOOD_UPPER = 2.0
    MODERATE_UPPER = 4.0
    SALINE_THRESHOLD = 4.0


@dataclass
class OCRanges:
    """Organic Carbon percentage ranges"""
    LOW_UPPER = 0.5
    AVERAGE_UPPER = 0.75
    HIGH_LOWER = 0.75


# ============================================
# FERTILITY CLASSIFICATION SYSTEM
# ============================================

class SoilFertilityClassifier:
    """
    Comprehensive soil fertility detection system using:
    1. Big Three (N-P-K) evaluation
    2. pH gatekeeper logic
    3. EC impact assessment
    4. Organic carbon battery check
    5. Liebig's Law of the Minimum
    """
    
    def __init__(self):
        self.thresholds = NutrientThresholds()
        self.ph_ranges = pHRanges()
        self.ec_ranges = ECRanges()
        self.oc_ranges = OCRanges()
    
    def classify_nutrient_level(self, nutrient_value: float, nutrient_type: str) -> str:
        """
        Classify a single nutrient (N, P, or K) as Infertile, Fertile, or Very Fertile
        
        Args:
            nutrient_value: Amount in kg/ha
            nutrient_type: 'N', 'P', or 'K'
        
        Returns:
            Classification string
        """
        if nutrient_type == 'N':
            if nutrient_value < self.thresholds.N_LOW:
                return NutrientLevel.INFERTILE.value
            elif nutrient_value <= self.thresholds.N_MEDIUM_UPPER:
                return NutrientLevel.FERTILE.value
            else:
                return NutrientLevel.VERY_FERTILE.value
        
        elif nutrient_type == 'P':
            if nutrient_value < self.thresholds.P_LOW:
                return NutrientLevel.INFERTILE.value
            elif nutrient_value <= self.thresholds.P_MEDIUM_UPPER:
                return NutrientLevel.FERTILE.value
            else:
                return NutrientLevel.VERY_FERTILE.value
        
        elif nutrient_type == 'K':
            if nutrient_value < self.thresholds.K_LOW:
                return NutrientLevel.INFERTILE.value
            elif nutrient_value <= self.thresholds.K_MEDIUM_UPPER:
                return NutrientLevel.FERTILE.value
            else:
                return NutrientLevel.VERY_FERTILE.value
        
        return "Unknown"
    
    def assess_ph_gatekeeper(self, ph: float) -> Tuple[str, float]:
        """
        Assess pH impact on nutrient availability using gatekeeper logic.
        Even with high N-P-K, bad pH can make soil infertile.
        
        Args:
            ph: Soil pH value (0-14 scale)
        
        Returns:
            Tuple of (classification, correction_multiplier)
            - Correction multiplier: 0.0 (locked) to 1.0 (optimal)
        """
        if ph < self.ph_ranges.HIGHLY_ACIDIC_UPPER:
            # Highly acidic: Aluminum toxicity, nutrient lockup
            return ("Highly Acidic (< 5.5)", 0.2)
        elif ph < self.ph_ranges.OPTIMAL_LOWER:
            # Below optimal: Some nutrients tied up
            return ("Suboptimal (5.5-6.0)", 0.6)
        elif ph <= self.ph_ranges.OPTIMAL_UPPER:
            # Optimal: Maximum nutrient availability
            return ("Optimal (6.0-7.5)", 1.0)
        elif ph < self.ph_ranges.ALKALINE_LOWER:
            # Above optimal but acceptable
            return ("Slightly Alkaline (7.5-8.5)", 0.7)
        else:
            # Highly alkaline: Iron, phosphorus, zinc lockup
            return ("Highly Alkaline (> 8.5)", 0.2)
    
    def assess_ec_impact(self, ec: float) -> Tuple[str, float]:
        """
        Assess Electrical Conductivity (salt) impact on soil fertility.
        High salt creates osmotic stress preventing nutrient uptake.
        
        Args:
            ec: EC in dS/m (deciSiemens per meter)
        
        Returns:
            Tuple of (classification, correction_multiplier)
            - Correction multiplier: 0.0 (saline) to 1.0 (good)
        """
        if ec <= self.ec_ranges.GOOD_UPPER:
            # Good: Very fertile, low salt risk
            return ("Good (0-2 dS/m)", 1.0)
        elif ec <= self.ec_ranges.MODERATE_UPPER:
            # Moderate: Sensitive crops may struggle
            return ("Moderate (2-4 dS/m)", 0.6)
        else:
            # Saline: Only salt-tolerant plants can grow
            return ("Saline/Infertile (> 4 dS/m)", 0.1)
    
    def assess_organic_carbon(self, oc_percent: float) -> Tuple[str, float]:
        """
        Assess Organic Carbon as the "battery" of soil.
        OC provides biological activity and nutrient cycling capacity.
        
        Args:
            oc_percent: Organic carbon as percentage of dry soil
        
        Returns:
            Tuple of (classification, quality_multiplier)
            - Quality multiplier: 0.0 (dead) to 1.0 (rich)
        """
        if oc_percent < self.oc_ranges.LOW_UPPER:
            # Low: Dead or exhausted soil
            return ("Low (< 0.5%)", 0.2)
        elif oc_percent <= self.oc_ranges.AVERAGE_UPPER:
            # Average: Requires regular manure/compost
            return ("Average (0.5-0.75%)", 0.6)
        else:
            # High: Rich, fertile soil with high biological activity
            return ("High (> 0.75%)", 1.0)
    
    def calculate_index_score(self, N: float, P: float, K: float, OC: float) -> float:
        """
        Calculate the Fertility Index Score.
        Formula: (N + P + K) × Organic Carbon
        
        This represents the total nutrient pool multiplied by the
        biological capacity to cycle nutrients (OC).
        
        Args:
            N: Nitrogen in kg/ha
            P: Phosphorus in kg/ha
            K: Potassium in kg/ha
            OC: Organic carbon as percentage (convert to decimal)
        
        Returns:
            Index score (theoretical max ~1000 for very fertile soil)
        """
        # Normalize OC percentage to decimal (1.0% = 1.0, not 0.01)
        oc_decimal = OC / 100.0 if OC > 1.0 else OC
        
        index_score = (N + P + K) * oc_decimal
        return index_score
    
    def apply_liebig_law(self, N: float, P: float, K: float, pH: float, EC: float, OC: float) -> Dict:
        """
        Apply Liebig's Law of the Minimum:
        "Growth is dictated not by total resources available,
         but by the scarcest resource (the limiting factor)"
        
        Even if N, P, K are high, a single bad parameter (like pH or EC)
        can make the soil INFERTILE.
        
        Args:
            N: Nitrogen in kg/ha
            P: Phosphorus in kg/ha
            K: Potassium in kg/ha
            pH: Soil pH
            EC: Electrical conductivity in dS/m
            OC: Organic carbon percentage
        
        Returns:
            Comprehensive fertility assessment
        """
        
        # Step 1: Evaluate Big Three (N-P-K)
        n_class = self.classify_nutrient_level(N, 'N')
        p_class = self.classify_nutrient_level(P, 'P')
        k_class = self.classify_nutrient_level(K, 'K')
        
        # Determine overall NPK status
        npk_levels = [n_class, p_class, k_class]
        if all(level == NutrientLevel.VERY_FERTILE.value for level in npk_levels):
            npk_status = NutrientLevel.VERY_FERTILE.value
        elif all(level in [NutrientLevel.FERTILE.value, NutrientLevel.VERY_FERTILE.value] for level in npk_levels):
            npk_status = NutrientLevel.FERTILE.value
        else:
            npk_status = NutrientLevel.INFERTILE.value
        
        # Step 2: Apply pH Gatekeeper (can override high nutrients)
        ph_status, ph_correction = self.assess_ph_gatekeeper(pH)
        
        # Step 3: Assess EC (salt stress)
        ec_status, ec_correction = self.assess_ec_impact(EC)
        
        # Step 4: Check OC (biological battery)
        oc_status, oc_quality = self.assess_organic_carbon(OC)
        
        # Step 5: Calculate Index Score
        index_score = self.calculate_index_score(N, P, K, OC)
        
        # Step 6: Apply Liebig's Law - Find the Limiting Factor
        # The final fertility is determined by the WEAKEST link
        correction_factors = [ph_correction, ec_correction, oc_quality]
        limiting_factor_strength = min(correction_factors)
        
        # Determine which factor is limiting
        if ph_correction == limiting_factor_strength:
            limiting_factor = "pH (Nutrient Availability)"
        elif ec_correction == limiting_factor_strength:
            limiting_factor = "EC / Salinity (Osmotic Stress)"
        else:
            limiting_factor = "Organic Carbon (Biological Activity)"
        
        # Step 7: Final Fertility Classification
        # High Index Score + Good Correction Factor = Optimal Fertility
        final_score = index_score * limiting_factor_strength
        
        if final_score > 400 and limiting_factor_strength > 0.8 and ph_correction > 0.8:
            fertility_class = "OPTIMAL"
            description = "Excellent soil fertility with all parameters balanced"
        elif final_score > 200 and limiting_factor_strength > 0.6:
            fertility_class = "HIGH"
            description = "Good soil fertility, minor adjustments recommended"
        elif final_score > 100 and limiting_factor_strength > 0.3:
            fertility_class = "MODERATE"
            description = "Fair soil fertility, some limitations present"
        else:
            fertility_class = "LOW"
            description = "Poor soil fertility, significant improvements needed"
        
        # If any critical factor is very low, override to INFERTILE
        if limiting_factor_strength < 0.3:
            fertility_class = "INFERTILE"
            description = f"Infertile due to {limiting_factor} being the limiting factor"
        
        return {
            'nitrogen': {
                'value': N,
                'classification': n_class,
                'status': 'OK' if N >= self.thresholds.N_LOW else 'CRITICAL'
            },
            'phosphorus': {
                'value': P,
                'classification': p_class,
                'status': 'OK' if P >= self.thresholds.P_LOW else 'CRITICAL'
            },
            'potassium': {
                'value': K,
                'classification': k_class,
                'status': 'OK' if K >= self.thresholds.K_LOW else 'CRITICAL'
            },
            'npk_overall_status': npk_status,
            'ph': {
                'value': pH,
                'classification': ph_status,
                'correction_factor': ph_correction
            },
            'ec': {
                'value': EC,
                'classification': ec_status,
                'correction_factor': ec_correction
            },
            'organic_carbon': {
                'value': OC,
                'classification': oc_status,
                'quality_factor': oc_quality
            },
            'index_score': round(index_score, 2),
            'final_score': round(final_score, 2),
            'limiting_factor': limiting_factor,
            'limiting_factor_strength': round(limiting_factor_strength, 2),
            'fertility_classification': fertility_class,
            'description': description,
            'recommendation': self._generate_recommendation(N, P, K, pH, EC, OC, limiting_factor)
        }
    
    def _generate_recommendation(self, N: float, P: float, K: float, pH: float, EC: float, OC: float, limiting_factor: str) -> str:
        """Generate comprehensive soil fertility recommendations using an ecosystem-based approach"""
        
        recommendations = []
        
        # 1. SOIL HEALTH ASSESSMENT
        recommendations.append("🌱 SOIL HEALTH ASSESSMENT")
        recommendations.append("="*80)
        
        # Nutrient status
        recommendations.append("\nNUTRIENT STATUS:")
        if N < self.thresholds.N_LOW:
            recommendations.append("  • NITROGEN: Critical deficiency - Immediate action needed")
        elif N < self.thresholds.N_MEDIUM_UPPER:
            recommendations.append("  • NITROGEN: Below optimal - Consider supplementation")
            
        if P < self.thresholds.P_LOW:
            recommendations.append("  • PHOSPHORUS: Critical deficiency - Immediate action needed")
        elif P < self.thresholds.P_MEDIUM_UPPER:
            recommendations.append("  • PHOSPHORUS: Below optimal - Consider supplementation")
            
        if K < self.thresholds.K_LOW:
            recommendations.append("  • POTASSIUM: Critical deficiency - Immediate action needed")
        elif K < self.thresholds.K_MEDIUM_UPPER:
            recommendations.append("  • POTASSIUM: Below optimal - Consider supplementation")
        
        # Soil condition
        recommendations.append("\nSOIL CONDITION:")
        if pH < self.ph_ranges.HIGHLY_ACIDIC_UPPER:
            recommendations.append(f"  • pH: {pH:.1f} (Highly Acidic) - Requires pH adjustment")
        elif pH < self.ph_ranges.OPTIMAL_LOWER:
            recommendations.append(f"  • pH: {pH:.1f} (Slightly Acidic) - Monitor or adjust")
        else:
            recommendations.append(f"  • pH: {pH:.1f} (Within optimal range)")
            
        if EC > self.ec_ranges.MODERATE_UPPER:
            recommendations.append(f"  • SALINITY: {EC:.1f} dS/m (High) - Requires remediation")
        elif EC > self.ec_ranges.GOOD_UPPER:
            recommendations.append(f"  • SALINITY: {EC:.1f} dS/m (Moderate) - Monitor")
            
        if OC < self.oc_ranges.AVERAGE_UPPER:
            recommendations.append(f"  • ORGANIC MATTER: {OC:.1f}% (Low) - Needs improvement")
        
        # 2. ECO-FRIENDLY SOIL AMENDMENTS
        recommendations.append("\n🌿 RECOMMENDED ECO-FRIENDLY AMENDMENTS")
        recommendations.append("="*80)
        
        # Organic Matter (The "Fuel")
        recommendations.append("\n1. ORGANIC MATTER (The 'Fuel'):")
        recommendations.append("  • COMPOST/VERMICOMPOST: 2-3 tons/acre (rich in nutrients & microbes)")
        recommendations.append("  • GREEN MANURE: Grow and incorporate legumes (clover, alfalfa, cowpea)")
        recommendations.append("  • SEAWEED/KELP MEAL: 100-200 kg/acre (trace minerals & growth stimulants)")
        
        # Biofertilizers (The "Engine")
        recommendations.append("\n2. BIOFERTILIZERS (The 'Engine'):")
        if N < self.thresholds.N_MEDIUM_UPPER:
            recommendations.append("  • NITROGEN-FIXING BACTERIA: Rhizobium for legumes, Azotobacter for non-legumes")
        if P < self.thresholds.P_MEDIUM_UPPER:
            recommendations.append("  • PHOSPHATE SOLUBILIZING BACTERIA (PSB): Unlocks phosphorus in soil")
        recommendations.append("  • MYCORRHIZAL FUNGI: Improves nutrient and water uptake (apply at planting)")
        
        # Mineral Amendments (The "Foundations")
        recommendations.append("\n3. MINERAL AMENDMENTS (The 'Foundations'):")
        recommendations.append("  • ROCK DUST: 500-1000 kg/acre (provides 70+ trace minerals)")
        if pH < 6.0:
            recommendations.append("  • AGRICULTURAL LIME: 2-5 tons/acre (raises pH, adds calcium)")
        if EC > 2.0:
            recommendations.append("  • GYPSUM: 1-2 tons/acre (improves soil structure, reduces salinity)")
        recommendations.append("  • BIOCHAR: 2-5 tons/acre (improves water retention & microbial habitat)")
        
        # 3. SOIL BUILDING PRACTICES
        recommendations.append("\n🌍 SOIL BUILDING PRACTICES")
        recommendations.append("="*80)
        recommendations.append("  • COVER CROPPING: Plant nitrogen-fixing legumes in off-seasons")
        recommendations.append("  • CROP ROTATION: Rotate heavy feeders with soil builders")
        recommendations.append("  • REDUCED TILLAGE: Preserve soil structure and microbial life")
        recommendations.append("  • MULCHING: 2-4 inches of organic mulch to retain moisture")
        
        # 4. IMPLEMENTATION SCHEDULE
        recommendations.append("\n📅 RECOMMENDED IMPLEMENTATION")
        recommendations.append("="*80)
        recommendations.append("1. IMMEDIATE (0-2 weeks):")
        recommendations.append("   • Apply compost/vermicompost")
        recommendations.append("   • Inoculate with biofertilizers")
        recommendations.append("   • Apply mineral amendments based on soil test")
        
        recommendations.append("\n2. SHORT-TERM (2-8 weeks):")
        recommendations.append("   • Plant green manure/cover crops")
        recommendations.append("   • Apply foliar sprays (seaweed extract, compost tea)")
        
        recommendations.append("\n3. LONG-TERM (2+ months):")
        recommendations.append("   • Establish permanent soil cover")
        recommendations.append("   • Implement crop rotation plan")
        recommendations.append("   • Regular soil testing (every 6-12 months)")
        
        # 5. MONITORING & MAINTENANCE
        recommendations.append("\n🔍 MONITORING & MAINTENANCE")
        recommendations.append("="*80)
        recommendations.append("  • Test soil every 6-12 months")
        recommendations.append("  • Observe plant health and growth patterns")
        recommendations.append("  • Adjust practices based on results")
        recommendations.append("  • Keep records of inputs and outcomes")
        
        return "\n".join(recommendations)
    
    def generate_detailed_report(self, N: float, P: float, K: float, pH: float, EC: float, OC: float, field_name: str = "Field") -> str:
        """Generate comprehensive fertility report"""
        
        assessment = self.apply_liebig_law(N, P, K, pH, EC, OC)
        
        report = []
        report.append("\n" + "="*80)
        report.append(f"COMPREHENSIVE SOIL FERTILITY ANALYSIS - {field_name}")
        report.append("Using Liebig's Law of the Minimum")
        report.append("="*80)
        
        report.append("\n[PARAMETER CLASSIFICATIONS]")
        report.append(f"  Nitrogen (N):      {N:>7.0f} kg/ha -> {assessment['nitrogen']['classification']}")
        report.append(f"  Phosphorus (P):    {P:>7.1f} kg/ha -> {assessment['phosphorus']['classification']}")
        report.append(f"  Potassium (K):     {K:>7.0f} kg/ha -> {assessment['potassium']['classification']}")
        report.append(f"  NPK Overall:                    {assessment['npk_overall_status']}")
        
        report.append("\n[CRITICAL GATEWAY FACTORS]")
        report.append(f"  pH Level:          {pH:>7.2f}      -> {assessment['ph']['classification']} (Correction: {assessment['ph']['correction_factor']})")
        report.append(f"  EC (Salinity):     {EC:>7.2f} dS/m -> {assessment['ec']['classification']} (Correction: {assessment['ec']['correction_factor']})")
        report.append(f"  Organic Carbon:    {OC:>7.2f} %    -> {assessment['organic_carbon']['classification']} (Quality: {assessment['organic_carbon']['quality_factor']})")
        
        report.append("\n[LIEBIG'S LAW ANALYSIS]")
        report.append(f"  Fertility Index Score:         {assessment['index_score']}")
        report.append(f"  Limiting Factor:               {assessment['limiting_factor']}")
        report.append(f"  Limiting Factor Strength:      {assessment['limiting_factor_strength']} (out of 1.0)")
        report.append(f"  Final Corrected Score:         {assessment['final_score']}")
        
        report.append("\n[FINAL FERTILITY CLASSIFICATION]")
        report.append(f"  Status:    {assessment['fertility_classification']}")
        report.append(f"  Summary:   {assessment['description']}")
        
        report.append("\n[RECOMMENDATIONS]")
        report.append(f"  {assessment['recommendation']}")
        
        report.append("\n" + "="*80 + "\n")
        
        return "\n".join(report)


# ============================================
# DEMONSTRATION AND TESTING
# ============================================

def main():
    """Run comprehensive fertility assessment demonstrations"""
    
    classifier = SoilFertilityClassifier()
    
    print("\n" + "="*80)
    print("SOIL FERTILITY DETECTION SYSTEM v3.0")
    print("Implementing Liebig's Law of the Minimum")
    print("="*80)
    
    # TEST CASE 1: High Nutrients but Bad pH (Liebig's Law Example)
    print("\n[TEST CASE 1] High Nutrients but Acidic pH (Liebig's Law Demonstration)")
    print("-" * 80)
    N1, P1, K1 = 500, 20, 250  # Very high nutrients
    pH1, EC1, OC1 = 4.5, 1.5, 0.8  # But pH is extremely acidic
    print(classifier.generate_detailed_report(N1, P1, K1, pH1, EC1, OC1, "Field A (High N-P-K, Low pH)"))
    
    # TEST CASE 2: Balanced Optimal Soil
    print("\n[TEST CASE 2] Optimal Balanced Soil")
    print("-" * 80)
    N2, P2, K2 = 400, 20, 200
    pH2, EC2, OC2 = 6.8, 1.2, 0.9
    print(classifier.generate_detailed_report(N2, P2, K2, pH2, EC2, OC2, "Field B (Optimal)"))
    
    # TEST CASE 3: Poor Soil (Multiple Deficiencies)
    print("\n[TEST CASE 3] Poor Soil (Multiple Deficiencies)")
    print("-" * 80)
    N3, P3, K3 = 100, 5, 80
    pH3, EC3, OC3 = 5.2, 0.8, 0.3
    print(classifier.generate_detailed_report(N3, P3, K3, pH3, EC3, OC3, "Field C (Poor)"))
    
    # TEST CASE 4: High Salinity Issue
    print("\n[TEST CASE 4] High Salinity (EC) Problem")
    print("-" * 80)
    N4, P4, K4 = 400, 18, 200
    pH4, EC4, OC4 = 6.5, 5.2, 0.8  # High EC limits fertility despite good nutrients
    print(classifier.generate_detailed_report(N4, P4, K4, pH4, EC4, OC4, "Field D (High Salinity)"))
    
    # TEST CASE 5: Low Organic Carbon
    print("\n[TEST CASE 5] Low Organic Carbon (Biological Exhaustion)")
    print("-" * 80)
    N5, P5, K5 = 350, 15, 180
    pH5, EC5, OC5 = 6.6, 1.0, 0.2  # Good pH and EC, but OC is limiting
    print(classifier.generate_detailed_report(N5, P5, K5, pH5, EC5, OC5, "Field E (Low OC)"))
    
    # Create comparison CSV
    print("\n[BATCH ANALYSIS MODE] Evaluating multiple fields...")
    print("-" * 80)
    
    fields_data = [
        {'name': 'Field A', 'N': 500, 'P': 20, 'K': 250, 'pH': 4.5, 'EC': 1.5, 'OC': 0.8},
        {'name': 'Field B', 'N': 400, 'P': 20, 'K': 200, 'pH': 6.8, 'EC': 1.2, 'OC': 0.9},
        {'name': 'Field C', 'N': 100, 'P': 5, 'K': 80, 'pH': 5.2, 'EC': 0.8, 'OC': 0.3},
        {'name': 'Field D', 'N': 400, 'P': 18, 'K': 200, 'pH': 6.5, 'EC': 5.2, 'OC': 0.8},
        {'name': 'Field E', 'N': 350, 'P': 15, 'K': 180, 'pH': 6.6, 'EC': 1.0, 'OC': 0.2},
    ]
    
    results = []
    for field in fields_data:
        assessment = classifier.apply_liebig_law(
            field['N'], field['P'], field['K'],
            field['pH'], field['EC'], field['OC']
        )
        results.append({
            'Field': field['name'],
            'N_kg_ha': field['N'],
            'P_kg_ha': field['P'],
            'K_kg_ha': field['K'],
            'pH': field['pH'],
            'EC_dS_m': field['EC'],
            'OC_percent': field['OC'],
            'Index_Score': assessment['index_score'],
            'Final_Score': assessment['final_score'],
            'Limiting_Factor': assessment['limiting_factor'],
            'Fertility_Class': assessment['fertility_classification']
        })
    
    results_df = pd.DataFrame(results)
    results_df.to_csv('dataset/liebig_fertility_assessment.csv', index=False)
    print("\n" + results_df.to_string(index=False))
    print("\n[OK] Results saved to 'dataset/liebig_fertility_assessment.csv'")


if __name__ == "__main__":
    main()
