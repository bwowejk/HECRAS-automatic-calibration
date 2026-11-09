import os
import re
import shutil

def get_next_plan_extension(project_file_path):
    """
    Scans the .prj file to find the highest plan number (pXX) 
    and returns the next available extension (e.g., 'p09').
    """
    max_num = 0
    with open(project_file_path, 'r') as f:
        for line in f:
            if line.strip().startswith("Plan File="):
                # Extract the extension (e.g., p03)
                parts = line.strip().split('=')
                if len(parts) > 1:
                    ext = parts[1]
                    # Check if it follows pXX format
                    if ext.startswith('p') and ext[1:].isdigit():
                        num = int(ext[1:])
                        if num > max_num:
                            max_num = num
    
    next_num = max_num + 1
    return f"p{next_num:02d}"

def create_new_plan(base_prj_path, source_plan_ext, new_flow_ext, new_plan_title, new_short_id):
    """
    Creates a new HEC-RAS plan file based on a source plan.
    
    Parameters:
    - base_prj_path: Full path to the .prj file
    - source_plan_ext: Extension of the base plan to copy (e.g., 'p03')
    - new_flow_ext: Extension of the new unsteady flow file (e.g., 'u03')
    - new_plan_title: The full title for the new plan
    - new_short_id: A short identifier (max 16 chars)
    
    Returns:
    - new_plan_ext: The extension of the newly created plan
    """
    
    base_dir = os.path.dirname(base_prj_path)
    project_name = os.path.splitext(os.path.basename(base_prj_path))[0]
    
    source_plan_file = os.path.join(base_dir, f"{project_name}.{source_plan_ext}")
    
    # 1. Determine next available plan extension
    new_plan_ext = get_next_plan_extension(base_prj_path)
    new_plan_file = os.path.join(base_dir, f"{project_name}.{new_plan_ext}")
    
    print(f"Creating new plan: {new_plan_ext} based on {source_plan_ext}")

    # 2. Read Source Plan and Modify Content
    with open(source_plan_file, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    for line in lines:
        if line.startswith("Plan Title="):
            new_lines.append(f"Plan Title={new_plan_title}\n")
        elif line.startswith("Short Identifier="):
            new_lines.append(f"Short Identifier={new_short_id}\n")
        elif line.startswith("Flow File="):
            # HEC-RAS usually stores just the extension (e.g., u03)
            new_lines.append(f"Flow File={new_flow_ext}\n")
        else:
            new_lines.append(line)
            
    # 3. Write the New Plan File
    with open(new_plan_file, 'w') as f:
        f.writelines(new_lines)
    print(f"✅ Created file: {new_plan_file}")

    # 4. Update the Project (.prj) File to include the new plan
    # We append the new Plan File line to the end of the lists in .prj
    with open(base_prj_path, 'r') as f:
        prj_lines = f.readlines()
    
    # We need to insert the new Plan File reference. 
    # Usually, we can just append it to the end of the file or after the last Plan File entry.
    # HEC-RAS is robust, but keeping it grouped is better.
    
    updated_prj_lines = []
    plan_added = False
    
    # Find the last occurrence of "Plan File=" to insert after it
    last_plan_index = -1
    for i, line in enumerate(prj_lines):
        if line.startswith("Plan File="):
            last_plan_index = i
            
    if last_plan_index != -1:
        prj_lines.insert(last_plan_index + 1, f"Plan File={new_plan_ext}\n")
    else:
        # If no plans exist (unlikely), append to end
        prj_lines.append(f"Plan File={new_plan_ext}\n")

    with open(base_prj_path, 'w') as f:
        f.writelines(prj_lines)
        
    print(f"✅ Registered {new_plan_ext} in project file.")
    
    return new_plan_ext

# ------------------------------------------------------------
# Execution for your specific request
# ------------------------------------------------------------
if __name__ == "__main__":
    # Update this path to your actual project path
    base_dir = r"F:\Unyama Interventions\from laptop\Unyama Interventions\Unyama Interventions\Flood protection wall"
    project_file = os.path.join(base_dir, "Unyama2D.prj")
    
    # INPUTS based on your request
    source_plan = "p03"           # Bypass channel
    target_flow = "u03"           # Flood Hydrograph (2yr)
    target_title = "Bypass channel 2yr"
    target_short_id = "Bypass 2yr"
    
    # Run the creation
    new_ext = create_new_plan(project_file, source_plan, target_flow, target_title, target_short_id)
    
    print(f"\n🎉 Success! New plan '{target_title}' created as extension .{new_ext}")
    print("You can now run this using your engine.py.")