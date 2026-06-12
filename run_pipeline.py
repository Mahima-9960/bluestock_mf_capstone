import os
import sys
import subprocess

def run_master_pipeline():
    print("==================================================")
    print("🚀 INITIALIZING BLUESTOCK MUTUAL FUND MASTER PIPELINE")
    print("==================================================")
    
    # Define the execution order of your project phases
    pipeline_steps = [
        {"name": "Data Ingestion", "path": "scripts/data_ingestion.py"},
        {"name": "ETL & Data Cleaning", "path": "scripts/etl_pipeline.py"},
        {"name": "Recommender System Engine", "path": "scripts/recommender.py"}
    ]
    
    for step in pipeline_steps:
        print(f"\n▶️ Running Phase: {step['name']} ({step['path']})...")
        
        # Verify the file actually exists before running to prevent crashes
        if not os.path.exists(step['path']):
            print(f"❌ Error: Could not find script at {step['path']}")
            print("Pipeline aborted.")
            sys.exit(1)
            
        try:
            # Execute the script cleanly
            subprocess.run(["python", step['path']], check=True)
            print(f"✅ {step['name']} completed successfully.")
            
        except subprocess.CalledProcessError as e:
            print(f"💥 Critical Error occurred during {step['name']}: {e}")
            print("Pipeline execution stopped.")
            sys.exit(1)

    print("\n==================================================")
    print("🎉 SUCCESS: Entire Mutual Fund Pipeline Executed!")
    print("==================================================")

if __name__ == "__main__":
    run_master_pipeline()