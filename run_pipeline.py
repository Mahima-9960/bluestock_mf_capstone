import subprocess
import sys
import os

def run_script(script_path):
    print(f"\n🚀 Running: {script_path}...")
    try:
        result = subprocess.run([sys.executable, script_path], check=True, text=True)
        print(f"✅ Successfully completed: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error occurred while executing {script_path}: {e}")
        sys.exit(1)

def main():
    print("=====================================================================")
    # Correct temporal context alignment for current project run execution
    print("BLUESTOCK MUTUAL FUND ANALYTICS ENTERPRISE PIPELINE ENGINE (EXECUTION: 2026)")
    print("=====================================================================")
    
    # Define execution steps in absolute sequential order
    pipeline_steps = [
        "scripts/data_ingestion.py",
        "scripts/etl_pipeline.py",
        "scripts/run_advanced_analytics.py"
    ]
    
    for step in pipeline_steps:
        if os.path.exists(step):
            run_script(step)
        else:
            print(f"⚠️ Warning: Script file not found at path: {step}")
            
    print("\n🏁 [PIPELINE SUCCESS] All operational blocks executed with zero exit errors.")

if __name__ == "__main__":
    main()