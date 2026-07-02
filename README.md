# 🛡️ Finguard: Secure Fraud Detection RAG

**Privacy-First Financial Forensics Powered by CyborgDB**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python\&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Vector_DB-CyborgDB_Encrypted-red?logo=lock\&logoColor=white)](https://www.cyborg.co/)
[![AI](https://img.shields.io/badge/LangChain-RAG-orange?logo=chainlink\&logoColor=white)](https://www.langchain.com/)
[![Security](https://img.shields.io/badge/Data-AES_256-green?logo=security\&logoColor=white)](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **fraud_detection** is a secure **Retrieval-Augmented Generation (RAG)** pipeline designed to detect anomalies and flag potential fraud in sensitive financial documents.
>
> Financial data demands absolute privacy. Unlike standard RAG implementations, it leverages **CyborgDB** to ensure that all transaction embeddings are **encrypted at rest and in transit**. We enable AI-driven insights without ever exposing raw financial vectors to plain-text vulnerabilities.

---

## 📸 Demo & Dashboard

### 📉 Fraud Analysis Dashboard

![Fraud Detection UI](./static/ui_screenshot.png)
*Real-time analysis of transaction logs with risk scoring, powered by secure RAG retrieval.*

### 🎥 Watch the System in Action

[![FinGuard Demo](https://img.youtube.com/vi/OIHUFWAG0HI/0.jpg)](https://www.youtube.com/watch?v=OIHUFWAG0HI)
*Click the thumbnail above to see the Encrypted Fraud Detection pipeline flow.*

---

## 🔒 The Encrypted Architecture (ML Flow)

We utilize **CyborgDB** to maintain a "Zero-Trust" architecture for vector storage.

```mermaid
graph TD
    subgraph "Ingestion Phase"
        A[Synthetic Data Generator] -->|Create Logs| B(Data Ingestion)
        B -->|Generate Embeddings| C[Hugging Face Transformer]
        C -->|Encrypt & Store| D[(CyborgDB Encrypted Cloud)]
    end

    subgraph "Inference Phase"
        E[User Query] --> R{Router LLM}
        
        %% Chat Branch (Zero Latency)
        R -->|Chat Mode| L[Direct LLM Response]
        L --> I[Analyst Dashboard]

        %% Search Branch (RAG)
        R -->|Search Mode| F[Embed Query]
        F -->|Encrypted Similarity Search| D
        D -->|Retrieve Decrypted Context| G[Transaction Context]
        G -->|Combine with Risk Prompt| H[Main LLM Chain]
        H -->|Generate Risk Report| I
    end

    %% --- STYLING (Dark Theme for GitHub Visibility) ---
    
    %% Standard Nodes (Dark Grey)
    style A fill:#2d2d2d,stroke:#ffffff,stroke-width:2px,color:#fff
    style B fill:#2d2d2d,stroke:#ffffff,stroke-width:2px,color:#fff
    style C fill:#2d2d2d,stroke:#ffffff,stroke-width:2px,color:#fff
    style E fill:#2d2d2d,stroke:#ffffff,stroke-width:2px,color:#fff
    style F fill:#2d2d2d,stroke:#ffffff,stroke-width:2px,color:#fff
    style G fill:#2d2d2d,stroke:#ffffff,stroke-width:2px,color:#fff
    style H fill:#2d2d2d,stroke:#ffffff,stroke-width:2px,color:#fff

    %% Key Nodes (Colored Accents)
    %% CyborgDB (Dark Red)
    style D fill:#4a151b,stroke:#ff6b6b,stroke-width:2px,stroke-dasharray: 5 5,color:#fff
    
    %% Router (Dark Gold)
    style R fill:#3d3100,stroke:#ffd700,stroke-width:2px,color:#fff
    
    %% Direct Chat (Dark Green)
    style L fill:#0d3329,stroke:#00ff41,stroke-width:2px,color:#fff
    
    %% Dashboard (Dark Blue)
    style I fill:#0e2a35,stroke:#00f0ff,stroke-width:2px,color:#fff
```

---

## 📊 Security & Performance Benchmarks

In financial contexts, speed matters, but security is non-negotiable. We benchmarked the impact of CyborgDB's encryption on retrieval latency.  
Click here to view the full interactive `benchmark.html` report.

![Security & Performance Benchmarks](./static/benchmark.png)


---

## 🚀 Key Features

* **CyborgDB Integration**: Industry-first encrypted vector search. Even if the database is compromised, the vectors remain unreadable.
* **Context-Aware Forensics**: Queries like `"Show me transactions over $10k sent to offshore accounts"` retrieve exact matches from the encrypted index.
* **Hybrid Analysis**: Combines semantic search (RAG) with rule-based filtering for maximum fraud detection coverage.
* **Persistent Secure Indexing**: Ingest terabytes of logs once; query securely forever.
* **Synthetic Data Genration**:Gerates Synthetic data using Faker library.

---

## 🛠️ Tech Stack

**Component — Technologies**

* Vector Database — CyborgDB (Encrypted Storage)
* Orchestration — LangChain, Python
* Embeddings — Hugging Face (sentence-transformers/all-MiniLM-L6-v2)
* Web Interface —  Flask 
* Data Processing — Pandas, NumPy

---

## 🏗️ Deployment & Setup

### Prerequisites

* Python 3.11
* CyborgDB API Key (Required for encrypted storage)
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/Nossks/fraud_detection.git
cd fraud_detection
```

### 2. Set up Virtual Environment

```bash
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\Activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables and api key

Create a `.env` file. You must provide CyborgDB credentials to enable the encrypted layer.

```env
# AI Models
HUGGINGFACEHUB_API_TOKEN=hf_your_token_here
GOOGLE_API_KEY=api_key
```

```
set cyborg db api key in data ingestion file located at src/components
```
### 5. Run the Application

Run the Prediction Pipeline :

```bash
python prediction.py
```

Launch the Dashboard:

```bash
python app.py
```

---

## 📂 Project Structure

```
fraud_detection/
├── app.py                  # Application entry point
├── src/                    # Core logic (pipelines, components, utils)
├── data/                   # Datasets and vector stores
├── notebooks/              # Experiments and prototyping
├── static/ & templates/    # Frontend assets
├── logs/                   # Runtime logs
├── requirements.txt
└── README.md

```

---

## 🔮 Future Scope

* [ ] Real-time Stream Processing: Hooking into Kafka for live transaction monitoring.
* [ ] Graph RAG: Using Knowledge Graphs to detect syndicate fraud rings.
* [ ] Multi-Modal Support: Scanning scanned checks and invoices (OCR).

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and create a pull request.

---

## 📄 License

This project is licensed under the MIT License.

---
