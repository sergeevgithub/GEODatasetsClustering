# 🧬 GEO Dataset Clustering Web Service

This project is a **Flask-based web service** that accepts a list of PMIDs (PubMed IDs), retrieves metadata of associated GEO datasets, processes their textual summaries, performs clustering based on text similarity, and generates interactive 2D and 3D visualizations.

---

## 🛠 Features

- Upload `.txt` file with PMIDs
- Fetch associated GEO datasets via NCBI E-utilities and web scraping
- Clean and aggregate metadata fields
- Perform text vectorization with **TF-IDF**
- Cluster with **KMeans** and **HDBSCAN**
- Reduce dimensions with **PCA**
- Generate interactive **Plotly** visualizations

---

## ⚙️ Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/sergeevgithub/GEODatasetsClustering.git
   cd GEODatasetsClustering
   ```
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Then open your browser and visit:
   ```
   http://127.0.0.1:5000
   ```
