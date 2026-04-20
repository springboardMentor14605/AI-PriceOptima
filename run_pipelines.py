"""
PriceOptima | Master Data Pipeline Executable
Runs the Rule-Based pricing engine and the Advanced ML pipeline in series.
Ensures outputs are centralized for the Dashboard and Backend APIs.
"""
import os
import sys

def execute_pipeline():
    print("==========================================================")
    print("      INITIALIZING PRICEOPTIMA MASTER PIPELINE           ")
    print("==========================================================")
    
    scripts = [
        "scripts/milestone4_advanced_engine.py",
        "Demand Forecast/milestone5_advanced_ml.py"
    ]
    
    for script in scripts:
        script_path = os.path.abspath(script)
        if not os.path.exists(script_path):
            print(f"[!] Error: Script '{script}' not found.")
            continue
            
        print(f"\n>> Executing: {os.path.basename(script)}")
        import subprocess
        subprocess.run([sys.executable, script_path], check=True)
        
    print("\n==========================================================")
    print("      MASTER PIPELINE COMPLETE. MODELS DEPLOYED.         ")
    print("==========================================================")

if __name__ == "__main__":
    execute_pipeline()
