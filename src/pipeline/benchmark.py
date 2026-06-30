import os
import sys
import time
import json
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from src.components.data_ingestion import DataIngestion
from src.components.database_retrival import Retrieval
from src.logger import logging
from src.exception import CustomException

# Configuration
@dataclass
class BenchmarkConfig:
    report_html_path = os.path.join('benchmark_dashboard.html')
    raw_data_path = os.path.join('data', 'financial_synthetic.csv')
    concurrency_level = 5  # Simulate 5 simultaneous users
    warmup_queries = 20    # Queries to run before starting the timer

class Benchmark:
    def __init__(self):
        self.config = BenchmarkConfig()
        self.results_cache = []

    def _execute_single_query(self, query_id, query):
        """Helper function for parallel execution"""
        try:
            # Run the retrieval (The "Race")
            metrics, _ = self.retriever.initiate_retrival(self.cyborg_db, query)
            
            return {
                'query_id': query_id,
                'status': 'success',
                'faiss': metrics.get('faiss', metrics.get('faiss_db', 0)),
                'chroma': metrics.get('chroma', metrics.get('chroma_db', 0)),
                'cyborg': metrics.get('cyborg', metrics.get('cyborg_db', 0))
            }
        except Exception as e:
            return {'query_id': query_id, 'status': 'failed', 'error': str(e)}

    def run_benchmark(self, sample_size=500):
        logging.info("🚀 STARTING ADVANCED BENCHMARK PROTOCOL")
        try:
            # 1. SETUP
            logging.info("Phase 1: Initialization & Loading DBs...")
            ingestion = DataIngestion()
            _, self.cyborg_db = ingestion.initiate_data_ingestion()
            self.retriever = Retrieval()
            
            # Load Data
            if not os.path.exists(self.config.raw_data_path):
                raise FileNotFoundError("Run data generation first!")
            
            df = pd.read_csv(self.config.raw_data_path)
            real_sample = min(sample_size, len(df))
            queries = df['text'].sample(n=real_sample + self.config.warmup_queries).tolist()
            
            # Split Warmup vs Test
            warmup_q = queries[:self.config.warmup_queries]
            test_q = queries[self.config.warmup_queries:]
            
            # 2. WARMUP (Prime the Cache)
            logging.info(f"Phase 2: Warming up caches with {self.config.warmup_queries} queries...")
            for q in warmup_q:
                self.retriever.initiate_retrival(self.cyborg_db, q)
            logging.info("✅ Warmup Complete. Caches Hot.")

            # 3. STRESS TEST (Parallel Execution)
            logging.info(f"Phase 3: Stress Testing with {self.config.concurrency_level} Concurrent Threads...")
            
            start_time = time.time()
            final_results = []
            
            with ThreadPoolExecutor(max_workers=self.config.concurrency_level) as executor:
                # Submit all tasks
                future_to_query = {
                    executor.submit(self._execute_single_query, i, q): i 
                    for i, q in enumerate(test_q)
                }
                
                # Process as they complete
                for i, future in enumerate(as_completed(future_to_query)):
                    res = future.result()
                    if res['status'] == 'success':
                        final_results.append(res)
                    
                    if (i + 1) % 50 == 0:
                        logging.info(f"Processed {i + 1}/{real_sample} queries...")

            total_duration = time.time() - start_time
            logging.info(f"✅ Testing Complete. Duration: {total_duration:.2f}s")

            # 4. REPORTING
            self.generate_html_report(final_results, total_duration)
            return "Benchmark Completed"

        except Exception as e:
            raise CustomException(e, sys)

    def generate_html_report(self, results, total_duration):
        """Generates a High-Fidelity HTML Dashboard with Chart.js"""
        try:
            logging.info("Generating Interactive Dashboard...")
            df = pd.DataFrame(results)
            
            # --- CALCULATE METRICS ---
            engines = ['faiss', 'cyborg', 'chroma']
            stats = {}
            
            for eng in engines:
                if eng not in df.columns: continue
                d = df[eng]
                stats[eng] = {
                    'avg': d.mean() * 1000, # Convert to ms
                    'p95': d.quantile(0.95) * 1000,
                    'p99': d.quantile(0.99) * 1000,
                    'min': d.min() * 1000,
                    'max': d.max() * 1000
                }

            # QPS Calculation (Throughput)
            total_queries = len(df)
            qps = total_queries / total_duration

            # Overhead Calc
            base_p95 = stats['faiss']['p95']
            cyborg_p95 = stats['cyborg']['p95']
            overhead = ((cyborg_p95 - base_p95) / base_p95) * 100 if base_p95 > 0 else 0

            # --- HTML TEMPLATE INJECTION ---
            # We inject the python data directly into the JS variables
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>CyborgDB Performance Audit</title>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <style>
                    body {{ font-family: 'Segoe UI', sans-serif; background: #f4f7f6; padding: 20px; }}
                    .container {{ max_width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
                    h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                    .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 40px; }}
                    .card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }}
                    .card h3 {{ margin: 0; color: #7f8c8d; font-size: 0.9rem; text-transform: uppercase; }}
                    .card .val {{ font-size: 2rem; font-weight: bold; color: #2c3e50; margin-top: 10px; }}
                    .chart-container {{ position: relative; height: 300px; width: 100%; margin-bottom: 50px; }}
                    .footer {{ margin-top: 50px; font-size: 0.8rem; color: #bdc3c7; text-align: center; }}
                    .badge-good {{ color: #27ae60; }}
                    .badge-warn {{ color: #e67e22; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🛡️ CyborgDB Performance Audit</h1>
                    <p><strong>Date:</strong> {pd.Timestamp.now()} | <strong>Samples:</strong> {total_queries} | <strong>Concurrency:</strong> {self.config.concurrency_level} Users</p>
                    
                    <div class="summary-grid">
                        <div class="card">
                            <h3>Throughput</h3>
                            <div class="val">{qps:.1f} <span style="font-size:1rem">QPS</span></div>
                        </div>
                        <div class="card">
                            <h3>Avg Latency (Enc)</h3>
                            <div class="val">{stats['cyborg']['avg']:.1f} <span style="font-size:1rem">ms</span></div>
                        </div>
                        <div class="card">
                            <h3>P99 Latency (Enc)</h3>
                            <div class="val">{stats['cyborg']['p99']:.1f} <span style="font-size:1rem">ms</span></div>
                        </div>
                        <div class="card">
                            <h3>Privacy Overhead</h3>
                            <div class="val badge-warn">+{overhead:.1f}%</div>
                        </div>
                    </div>

                    <h2>1. Latency Distribution (Lower is Better)</h2>
                    <p>Comparison of P95 (Tail Latency) across storage engines.</p>
                    <div class="chart-container">
                        <canvas id="barChart"></canvas>
                    </div>

                    <h2>2. Stability Analysis</h2>
                    <p>Min vs Max latency spread. Tighter bars mean more stable performance.</p>
                    <div class="chart-container">
                        <canvas id="radarChart"></canvas>
                    </div>
                </div>

                <script>
                    // DATA INJECTION
                    const labels = ['FAISS (RAM)', 'CyborgDB (Encrypted)', 'Chroma (Disk)'];
                    const p95Data = [{stats['faiss']['p95']:.2f}, {stats['cyborg']['p95']:.2f}, {stats['chroma']['p95']:.2f}];
                    const avgData = [{stats['faiss']['avg']:.2f}, {stats['cyborg']['avg']:.2f}, {stats['chroma']['avg']:.2f}];
                    const maxData = [{stats['faiss']['max']:.2f}, {stats['cyborg']['max']:.2f}, {stats['chroma']['max']:.2f}];

                    // BAR CHART
                    new Chart(document.getElementById('barChart'), {{
                        type: 'bar',
                        data: {{
                            labels: labels,
                            datasets: [
                                {{ label: 'Avg Latency (ms)', data: avgData, backgroundColor: '#3498db' }},
                                {{ label: 'P95 Latency (ms)', data: p95Data, backgroundColor: '#2c3e50' }}
                            ]
                        }},
                        options: {{ responsive: true, maintainAspectRatio: false }}
                    }});

                    // RADAR CHART
                    new Chart(document.getElementById('radarChart'), {{
                        type: 'line',
                        data: {{
                            labels: labels,
                            datasets: [
                                {{
                                    label: 'Max Latency Spike (ms)',
                                    data: maxData,
                                    borderColor: '#e74c3c',
                                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                                    fill: true,
                                    tension: 0.4
                                }}
                            ]
                        }},
                        options: {{ responsive: true, maintainAspectRatio: false }}
                    }});
                </script>
            </body>
            </html>
            """
            
            with open(self.config.report_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            print("\n" + "="*50)
            print(f"📊 DASHBOARD GENERATED: {os.path.abspath(self.config.report_html_path)}")
            print(f"   Open this file in Chrome/Edge to see the interactive charts.")
            print("="*50 + "\n")

        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    b = Benchmark()
    b.run_benchmark(sample_size=500) # Increased default for better stats