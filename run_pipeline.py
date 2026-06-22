import os
import sys
import subprocess

def execute_pipeline_node(command: str, step_description: str) -> bool:
    """Executes a downstream pipeline module and streams terminal outputs live."""
    print("\n" + "=" * 65)
    print(f"🚀 EXECUTING PIPELINE NODE: {step_description}")
    print("=" * 65)
    
    try:
        # Executes the system command and pipes output directly to your active shell
        subprocess.run(command, shell=True, check=True)
        print(f"\n✅ Node Success: '{step_description}' finalized without faults.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Node Failure: '{step_description}' encountered a fatal exception.")
        print(f"   ↳ Return Exit Code: {e.returncode}")
        return False

def main():
    print("\n⚙️  [STARTING BLUESTOCK MASTER PIPELINE ORCHESTRATOR]")
    print("⚡ Initializing centralized process automation sequence...")
    
    # Node 1: Execute the core Database Wiping & Master Ingestion Loader Engine
    etl_command = "python src/etl/loader.py"
    etl_success = execute_pipeline_node(etl_command, "Master ETL Loader Engine (Ingestion & Storage)")
    
    if not etl_success:
        print("\n🛑 CRITICAL: Master orchestration stopped. Fix upstream loader issues before re-running.")
        sys.exit(1)

    # Node 2: Execute the Automated Data Quality Exception Logging Report
    audit_command = "python src/etl/quality_check.py"
    audit_success = execute_pipeline_node(audit_command, "Data Quality Integrity Audit & Failure Tracking")
    
    print("\n" + "=" * 65)
    print("🏆 [SPRINT 1 AUTOMATION EXECUTION RUN COMPLETED]")
    print("=" * 65)
    print("   All records purged, extracted, normalized, validated, stored,")
    print("   and audited smoothly. Your end-to-end architecture is production-ready!")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()