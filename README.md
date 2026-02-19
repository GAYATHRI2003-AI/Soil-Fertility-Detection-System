# 🌱 AI Soil Doctor - Comprehensive Documentation

> **AI-Powered Agricultural Intelligence Platform for Soil Health Analysis**

---

## 📋 Table of Contents

1. [Executive Summary](https://www.google.com/search?q=%23-executive-summary)
2. [Quick Start](https://www.google.com/search?q=%23-quick-start)
3. [Project Structure](https://www.google.com/search?q=%23-project-structure)
4. [Core Features](https://www.google.com/search?q=%23-core-features)
5. [AI Models & Technologies](https://www.google.com/search?q=%23-ai-models--technologies-used)
6. [Scientific Methodology](https://www.google.com/search?q=%23-scientific-methodology)
7. [Regional Coverage](https://www.google.com/search?q=%23-regional-coverage)
8. [Troubleshooting](https://www.google.com/search?q=%23-troubleshooting)

---

## 📋 Executive Summary

**AI Soil Doctor v1.0** is a production-ready agricultural intelligence platform that combines cutting-edge AI technologies with agronomic science to provide comprehensive soil health analysis and actionable recommendations.

### Key Capabilities

* **AI-Powered Diagnostics**: Liebig's Law of the Minimum implementation.
* **Machine Learning**: Random Forest classifier with 80% accuracy.
* **RAG System**: 4-stage Retrieval-Augmented Generation pipeline.
* **Geospatial Analysis**: Interactive mapping and visualization.
* **Knowledge Base**: 37 research documents with AI-powered search.

### System Metrics

| Metric | Value |
| --- | --- |
| **ML Accuracy** | 80% |
| **Processing Speed** | < 2 seconds/field |
| **Knowledge Base** | 37 documents (~150 MB) |
| **Regional Coverage** | 15+ Indian states |

---

## 🚀 Quick Start

### Installation

```bash
# 1. Clone or download the project
cd soil

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py

```

### Main Menu Options

1. **🩺 SOIL DIAGNOSIS**: Analyze soil health (10 parameters).
2. **🌾 CROP ADVISORY**: Get crop recommendations by season.
3. **🌱 SEASON-CROP PRED**: Predict crops for seasons.
4. **📚 KNOWLEDGE BASE**: Ask AI-powered agricultural questions.
5. **🔄 UPDATE KNOWLEDGE DB**: Rebuild knowledge base from PDFs.

---

## 📁 Project Structure

```text
soil/
├── 📄 main.py                      # Main application entry point
├── 📄 README.md                    # This documentation
├── 📄 requirements.txt             # Python dependencies
├── 📁 src/                         # Source code modules (7 files)
│   ├── soil_fertility_detection_v3.py  # Liebig's Law implementation
│   ├── rag_system.py                   # RAG system core
│   └── geospatial_utils.py             # Geospatial analysis
├── 📁 docs/                         # Essential documentation (5 files)
└── 📁 dataset/                      # Data files (5 CSV files - optimized)

```

---

## 🔬 Scientific Methodology

### Liebig's Law of the Minimum

The system identifies the "limiting factor"—the specific nutrient or environmental condition that restricts yield, regardless of how abundant other nutrients are.

The fertility is calculated using an index score:


The final score is then adjusted by the **Limiting Factor** (the lowest value among pH, EC, and OC factors):


---

## 🌍 Regional Coverage

The platform supports major agricultural seasons in India:

* **KHARIF (Monsoon)**: Rice, Maize, Cotton, Soybean, Groundnut.
* **RABI (Winter)**: Wheat, Barley, Mustard, Gram, Peas.
* **ZAID (Summer)**: Watermelon, Cucumber, Fodder Crops.

---

### What to do next:

1. **Save as File**: Copy the text above and save it exactly as `README.md`.
2. **Verify Newlines**: Ensure there is a blank line between headers (like `##`) and the text below them so the Markdown renders correctly.
3. **Check Dependencies**: Ensure your `requirements.txt` includes the core libraries mentioned: `numpy`, `pandas`, `scikit-learn`, `matplotlib`, and `chromadb`.

