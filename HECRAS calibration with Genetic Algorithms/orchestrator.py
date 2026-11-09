# -*- coding: utf-8 -*-
"""
Created on Sat Jan 24 15:46:13 2026

@author: Administrator 2
"""

# -*- coding: utf-8 -*-
"""
HEC-RAS Orchestrator
--------------------
1. Generates 24 simulation plans (4 Geometries x 6 Return Periods).
2. Updates the .prj file.
3. Runs the HEC-RAS engine for all created plans sequentially.
"""

import os
import sys
import time

# --- Import your modules ---
# Ensure engine.py and plan_generator.py are in the same folder or python path
from engine import init_ras, open_project, set_current_plan, compute_plan, close_ras
from plan_generator import create_new_plan  # Assuming you saved the previous code as plan_generator.py

# -----------------------
# Configuration
# -----------------------
BASE_PROJECT_DIR = r"F:\HECRAS Unyama calibration\automatic_calibration\base_project"
PROJECT_NAME = "Unyama2D"
BASE_PROJ_FILE = os.path.join(BASE_PROJECT_DIR, f"{PROJECT_NAME}.prj")
PROGID = "RAS66.HECRASController"

# 1. Base Plans (The Source Geometries)
#    Format: "Plan Name Prefix": "Source Plan Extension"
BASE_PLANS = {
    "Bypass channel":        "p03",
    "Channelization 2D":     "p06",
    "Channelization_Bridge": "p07",
    "Levee_FW":              "p08"
}

# 2. Unsteady Flow Data (The Return Periods)
#    Format: Return Period (int/str): "Flow File Extension"
FLOW_DATA = {
    2:   "u03",
    5:   "u04",
    10:  "u05",
    25:  "u06",
    50:  "u07",
    200: "u09"
}

# -----------------------
# Helper: Check if plan exists
# -----------------------
def get_existing_plan_id(prj_path, plan_title):
    """
    Checks .prj file to see if a plan with 'plan_title' already exists.
    Returns the short ID (e.g., 'p12') if found, else None.
    """
    current_title = None
    current_file = None
    
    with open(prj_path, 'r') as f:
        lines = f.readlines()
        
    # Simple parser to map Titles to Files
    # HEC-RAS .prj files list plans, but the mapping is loose. 
    # Validating by reading the actual .pXX files is safer.
    
    # Quick scan of directory for .pXX files is more robust
    dir_path = os.path.dirname(prj_path)
    base_name = os.path.splitext(os.path.basename(prj_path))[0]
    
    for file in os.listdir(dir_path):
        if file.startswith(base_name) and file.split('.')[-1].startswith('p') and file.split('.')[-1][1:].isdigit():
            full_path = os.path.join(dir_path, file)
            try:
                with open(full_path, 'r') as pf:
                    for line in pf:
                        if line.strip().startswith(f"Plan Title={plan_title}"):
                            # Found it! Return extension (e.g., 'p12')
                            return file.split('.')[-1]
            except:
                continue
    return None

# -----------------------
# Main Execution
# -----------------------
def main():
    print("\n==========================================")
    print("   HEC-RAS BATCH PLAN GENERATOR & RUNNER  ")
    print("==========================================\n")

    # List to store the specific plan names (Titles) we want to run
    plans_to_run = []

    # ---------------------------------------------------------
    # PHASE 1: Plan Generation (Manipulating Text Files)
    # ---------------------------------------------------------
    print("--- Phase 1: Checking/Generating Plans ---")
    
    for base_name, source_ext in BASE_PLANS.items():
        for rp, flow_ext in FLOW_DATA.items():
            
            # Construct the Naming Convention
            # e.g., "Bypass channel 2yr"
            new_title = f"{base_name} {rp}yr"
            new_short_id = f"{base_name[:10]} {rp}yr" # Short ID max ~16 chars
            
            # Check if this specific combo already exists to avoid duplicates
            existing_ext = get_existing_plan_id(BASE_PROJ_FILE, new_title)
            
            if existing_ext:
                print(f"🔹 Plan already exists: '{new_title}' ({existing_ext})")
            else:
                # Create it using the logic from plan_generator.py
                print(f"🔸 Creating new plan: '{new_title}'...")
                create_new_plan(
                    BASE_PROJ_FILE,
                    source_ext,      # Source (e.g. p03)
                    flow_ext,        # Target Flow (e.g. u03)
                    new_title,       # Title
                    new_short_id     # Short ID
                )
            
            # Add to our execution list
            plans_to_run.append(new_title)

    print(f"\n✅ Phase 1 Complete. {len(plans_to_run)} plans ready for computation.\n")
    
    # ---------------------------------------------------------
    # PHASE 2: Execution (Running HEC-RAS Engine)
    # ---------------------------------------------------------
    print("--- Phase 2: Running Computations ---")
    
    # Initialize Engine ONCE
    ras = init_ras(PROGID)
    open_project(ras, BASE_PROJ_FILE)

    failed_plans = []

    for plan_name in plans_to_run:
        print(f"\n👉 Loading Plan: '{plan_name}'")
        try:
            # 1. Set Plan
            set_current_plan(ras, plan_name)
            
            # 2. Compute
            # Note: This is blocking. It will wait for the run to finish.
            compute_plan(ras)
            
            # 3. (Optional) Post-Processing Placeholder
            # If you want to run your extraction/Jaccard here:
            # result_file = ... (derive from plan name)
            # extract_inundation(result_file, ...)
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR processing '{plan_name}': {e}")
            failed_plans.append(plan_name)
            # We continue to the next plan instead of crashing the whole script
            continue

    # Cleanup
    close_ras(ras)
    
    print("\n==========================================")
    print("             BATCH RUN COMPLETE           ")
    print("==========================================")
    if failed_plans:
        print(f"⚠️ The following {len(failed_plans)} plans failed:")
        for fp in failed_plans:
            print(f" - {fp}")
    else:
        print("🎉 All plans computed successfully!")

if __name__ == "__main__":
    main()