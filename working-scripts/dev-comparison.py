import os
import subprocess
import json
import csv
import yaml
from openpyxl import Workbook
 
def clone_repo(github_url, branch_name, target_folder):
    try:
        os.makedirs(target_folder)  # Create the target folder
    except Exception as e:
        print(f"Error creating folder '{target_folder}': {e}")
        return
   
    # Clone the specified branch into the target folder
    try:
        subprocess.run(
            ["git", "clone", "--branch", branch_name, github_url, target_folder],
            check=True
        )
        print(f"Successfully cloned '{branch_name}' branch into '{target_folder}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning the repository: {e}")
 
def fetch_json(target_folder):
    json_path = ''
    for root, folders, files in os.walk(target_folder):
        if "dev-values" in folders:
            dev_values_path = os.path.join(root, "dev-values")
            for filename in os.listdir(dev_values_path):
                if filename == "config-dev.json":
                    json_path = os.path.join(dev_values_path, filename)
                    break
            if not json_path:
                # Create an empty config-dev.json if it doesn't exist
                json_path = os.path.join(dev_values_path, "config-dev.json")
                with open(json_path, 'w') as f:
                    json.dump({}, f)  # Create an empty JSON object
            break  # Exit after processing the 'dev-values' folder

    return json_path

 
def yaml_to_json(folder_path):
    json_data = {}
 
    # Convert YAML files to JSON structure
    for filename in os.listdir(folder_path):
        if filename.endswith('.yaml'):
            yaml_path = os.path.join(folder_path, filename)
            with open(yaml_path, 'r') as yaml_file:
                yaml_content = yaml.safe_load(yaml_file)
                json_data[filename[:-5]] = yaml_content  # Use filename without .yaml as the root key
 
    return json_data
 
def compare_json_files(old_data, new_data):
    changes = []
 
    # Check for changes in the JSON files
    for root in new_data.keys():
        if root not in old_data:
            changes.append((root, 'add', '', json.dumps(new_data[root], indent=4), 'root object added'))
        else:
            compare(old_data[root], new_data[root], root, changes)
 
    for root in old_data.keys():
        if root not in new_data:
            changes.append((root, 'delete', '', json.dumps(old_data[root], indent=4), 'root object deleted'))
 
    return changes
 

def compare(old, new, root, changes, path='', key='name'):
    if isinstance(old, dict):
        for k in old.keys():
            new_key_path = f"{path}//{k}" if path else k
            if k in new:
                compare(old[k], new[k], root, changes, new_key_path, key)
            else:
                changes.append((root, 'delete', new_key_path, json.dumps(old[k], indent=4), 'Deleted'))

        for k in new.keys():
            new_key_path = f"{path}//{k}" if path else k
            if k not in old:
                changes.append((root, 'add', new_key_path, json.dumps(new[k], indent=4), 'Added'))

    elif isinstance(old, list) and all(isinstance(i, dict) for i in old):
        # Handle lists of dictionaries
        old_dict = {item.get(key): item for item in old if key in item}
        new_dict = {item.get(key): item for item in new if key in item}

        # Check for modifications, deletions, and additions
        for old_key, old_item in old_dict.items():
            if old_key in new_dict:
                new_item = new_dict[old_key]
                if old_item != new_item:
                    changes.append((root, 'modify', f"{path}", json.dumps(new_item, indent=4), 'Modified'))
            else:
                changes.append((root, 'delete', path, json.dumps(old_item, indent=4), 'Deleted'))

        for new_key, new_item in new_dict.items():
            if new_key not in old_dict:
                changes.append((root, 'add', path, json.dumps(new_item, indent=4), 'Added'))

    elif isinstance(old, list):
        # Handle non-dictionary lists
        for i, old_item in enumerate(old):
            if i < len(new):
                if old_item != new[i]:
                    changes.append((root, 'modify', f"{path}[{i}]", json.dumps(new[i], indent=4), 'Modified'))
            else:
                changes.append((root, 'delete', f"{path}[{i}]", json.dumps(old_item, indent=4), 'Deleted'))

        for i in range(len(old), len(new)):
            changes.append((root, 'add', f"{path}[{i}]", json.dumps(new[i], indent=4), 'Added'))

    else:
        # Compare scalar values
        if old != new:
            changes.append((root, 'modify', path, json.dumps(new, indent=4), 'Modified'))


def find_excel_file(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.xlsx'):
                return os.path.join(folder_path, file)
    return None
 
 
def write_changes_to_excel(changes, excel_file_path, envs):
    # Create a new workbook and add sheets
    wb = Workbook()
 
    # Write the first sheet with full data
    first_sheet = wb.active
    first_sheet.title = envs[0]  # Name the first sheet
 
    # Write the headers
    first_sheet.append(['Service name', 'Change Request', 'Key', 'Value', 'Comment'])
 
    # Write the changes to the first sheet
    for change in changes:
        service_name, change_type, key, value, comment = change
        first_sheet.append([service_name, change_type, key, value, comment])
 
    # Write the remaining sheets (copy content but clear "Value" column)
    for env in envs[1:]:
        new_sheet = wb.create_sheet(title=env)
        new_sheet.append(['Service name', 'Change Request', 'Key', 'Value', 'Comment'])
 
        for row in first_sheet.iter_rows(min_row=2, values_only=True):
            # Copy all rows but clear the "Value" column (4th column)
            new_sheet.append([row[0], row[1], row[2], '', row[4]])
 
    # Save the workbook to a file
    wb.save(excel_file_path)
 
def get_input(prompt):
    attempts = 3
    for _ in range(attempts):
        value = input(prompt)
        if value:
            return value
        print("Input cannot be empty. Please try again.")
    print("Cannot proceed with execution as no input was entered.")
    exit(1)
 
def main():
    github_url = get_input("Add the Repository URL: ")
    promote_branch_x_1 = get_input("Add the previous branch name: ")
    promote_branch_x = get_input("Add the current branch name: ")
    target_folder_x_1 = get_input("Add the folder where the x-1 repo has to be cloned: ")  
    target_folder_x = get_input("Add the folder where the x repo has to be cloned: ")
 
    # Environment list (for this example, you can modify based on your use case)
    envs = ['dev', 'sit', 'uat']  # Example environments
 
    clone_repo(github_url, promote_branch_x_1, target_folder_x_1)
    print(target_folder_x_1)
 
    clone_repo(github_url, promote_branch_x, target_folder_x)
    print(target_folder_x)
 
    previous_json_path = fetch_json(target_folder_x_1)
    print(previous_json_path)
 
    new_json_path = fetch_json(target_folder_x)
    print(new_json_path)
 
    # Load previous JSON data
    try:
        with open(previous_json_path, 'r') as old_file:
            old_data = json.load(old_file)
    except (json.JSONDecodeError, FileNotFoundError):
        print("Previous JSON file is invalid or not found.")
        old_data = {}
 
    # Convert YAML to JSON
    dev_values_path = os.path.dirname(new_json_path)
    json_data = yaml_to_json(dev_values_path)
 
    # Save the new JSON data
    with open(new_json_path, 'w') as new_json_file:
        json.dump(json_data, new_json_file, indent=4)
 
    # Compare JSON files
    changes = compare_json_files(old_data, json_data)
 
    excel_file_path = find_excel_file(target_folder_x)
    if not excel_file_path:
        # If no existing Excel file is found, create a new one
        excel_file_path = os.path.join(target_folder_x, 'release-note.xlsx')
 
    # Write changes to Excel with multiple sheets
    write_changes_to_excel(changes, excel_file_path, envs)
 
if __name__ == '__main__':
    main()
