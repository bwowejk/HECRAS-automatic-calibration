# engine.py

"""
HEC-RAS Engine Module (Flexible)
-------------------------------------
Provides helper functions for initializing and controlling the HEC-RAS
COM interface, with configurable project path, plan, and version.
"""

import win32com.client
import pythoncom
import os
import sys

print("\n--- Running Engine ---\n")

# ------------------------------------------------------------
# Initialization and Connection
# ------------------------------------------------------------
def init_ras(progid="RAS66.HECRASController"):
    """
    Initialize COM and create a HEC-RAS controller.
    ... (rest of the function is unchanged) ...
    """
    pythoncom.CoInitialize()
    try:
        ras_ctrl = win32com.client.Dispatch(progid)
        print(f"✅ HEC-RAS COM object created: {progid}")
        return ras_ctrl
    except Exception as e:
        print(f"❌ Failed to create COM object ({progid}): {e}")
        pythoncom.CoUninitialize()
        sys.exit(1)


# ------------------------------------------------------------
# Project Handling
# ------------------------------------------------------------
def open_project(ras_ctrl, proj_file):
    """
    Open a HEC-RAS project file.
    ... (rest of the function is unchanged) ...
    """
    if not os.path.exists(proj_file):
        raise FileNotFoundError(f"Project file not found: {proj_file}")

    try:
        ras_ctrl.Project_Open(proj_file)
        print(f"📂 Project opened: {proj_file}")
    except Exception as e:
        print(f"❌ Failed to open project: {e}")
        close_ras(ras_ctrl)
        sys.exit(1)


def set_current_plan(ras_ctrl, plan_name):
    """
    Set the current plan for computation.
    ... (rest of the function is unchanged) ...
    """
    try:
        ras_ctrl.Plan_SetCurrent(plan_name)
        print(f"📑 Current plan set to: {plan_name}")
    except Exception as e:
        print(f"❌ Failed to set current plan: {e}")
        close_ras(ras_ctrl)
        sys.exit(1)


# ------------------------------------------------------------
# Computation
# ------------------------------------------------------------
# ------------------------------------------------------------
# Computation
# ------------------------------------------------------------
# ------------------------------------------------------------
# Computation
# ------------------------------------------------------------
def compute_plan(ras_ctrl):
    """
    Compute the currently active plan. This is a BLOCKING call, meaning
    Python will wait until the HEC-RAS simulation is complete.

    Parameters
    ----------
    ras_ctrl : COM object
        Active HEC-RAS controller.
    """
    print("⚙️ Starting plan computation (this may take a while)...")
    try:
        # Pass None for out-params; returns (success, num_messages, messages, ?)
        result = ras_ctrl.Compute_CurrentPlan(None, None, True)
        # Unpack assuming 4-tuple (extra element is likely an echo of blocking or dummy)
        success, num_messages, messages, _ = result

        if not success:
            raise RuntimeError("HEC-RAS computation failed (success=False).")

        if num_messages > 0:
            print("⚠️ Computation finished with messages/warnings:")
            # It's good practice to check for errors in the messages
            has_errors = False
            for msg_str in messages:
                print(f"   - {msg_str}")
                if "error" in msg_str.lower():
                    has_errors = True
            
            if has_errors:
                 # Raise an error to stop the GA from considering a failed run as successful
                 raise RuntimeError("HEC-RAS computation failed with errors.")

        print("✅ Plan computation completed successfully.")

    except Exception as e:
        # Re-raise the exception so the calling script (like your GA) can handle it.
        print(f"❌ Failed to compute plan: {e}")
        raise e


# ------------------------------------------------------------
# Closing / Cleanup
# ------------------------------------------------------------
def close_ras(ras_ctrl):
    """
    Close HEC-RAS and uninitialize COM.
    ... (rest of the function is unchanged) ...
    """
    try:
        ras_ctrl.QuitRas()
        print("🛑 HEC-RAS closed.")
    except Exception as e:
        print(f"⚠️ Failed to close HEC-RAS properly: {e}")
    finally:
        pythoncom.CoUninitialize()
        print("🔻 COM uninitialized.")

# ------------------------------------------------------------
# Convenience function for standalone testing
# ------------------------------------------------------------
if __name__ == "__main__":
    # Example: test with your paths
    base_dir = r"F:\HECRAS Unyama calibration\automatic_calibration\base_project"
    project_file = os.path.join(base_dir, "Unyama2D.prj")
    plan = "unyama_2017"

    ras = init_ras(progid="RAS66.HECRASController")
    open_project(ras, project_file)
    set_current_plan(ras, plan)
    compute_plan(ras)
    close_ras(ras)