## working script for creating all the yaml files is below

import ruamel.yaml
import json
import os

# Load the YAML file with ruamel.yaml to preserve structure
def load_yaml_file(file_path):
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True  # Preserve quotes and formatting
    with open(file_path, 'r') as f:
        return yaml.load(f), yaml

# Load the JSON file
def load_json_file(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

# Recursive function to populate values from JSON into YAML
def populate_yaml(yaml_data, json_data, json_root, parent_key=""):
    for key, value in yaml_data.items():
        full_key_path = f"{parent_key}.{key}" if parent_key else key

        if isinstance(value, dict):
            # Recursively handle nested dictionaries
            if key in json_root:
                populate_yaml(value, json_data, json_root[key], full_key_path)
            else:
                print(f"Key '{full_key_path}' not found in JSON.")
        elif isinstance(value, list):
            # Handle lists, such as 'imagePullSecrets' or 'env.account_statement'
            for idx, item in enumerate(value):
                if isinstance(item, dict):
                    # Match each dictionary in the list by checking each key in the dictionary
                    for item_key, item_value in item.items():
                        if item_key in json_root[key][idx]:
                            json_value = json_root[key][idx][item_key]
                            if item_value == "" or item_value is None:  # Update only if the YAML value is empty
                                item[item_key] = json_value
                                print(f"Populating list key: {full_key_path}[{idx}].{item_key} with value: {json_value}")
                        else:
                            print(f"Key '{full_key_path}[{idx}].{item_key}' not found in JSON.")
        else:
            # Handle direct key-value pairs in the YAML
            if key in json_root:
                json_value = json_root[key]
                if value == "" or value is None:  # Update only if the YAML value is empty
                    yaml_data[key] = json_value
                    print(f"Populating key: {full_key_path} with value: {json_value}")
            else:
                print(f"Key '{full_key_path}' not found in JSON.")

# Save the updated YAML file
def save_yaml_file(file_path, yaml_data, yaml_instance):
    with open(file_path, 'w') as f:
        yaml_instance.dump(yaml_data, f)

# Main function to update all YAML files in a folder
def update_yaml_files_in_folder(yaml_folder_path, json_data):
    yaml_files = [f for f in os.listdir(yaml_folder_path) if f.endswith('.yaml')]

    for yaml_file in yaml_files:
        yaml_file_path = os.path.join(yaml_folder_path, yaml_file)
        yaml_file_name = yaml_file.split('.')[0]  # Extract root object name from YAML filename
        
        yaml_data, yaml_instance = load_yaml_file(yaml_file_path)
        
        if yaml_file_name in json_data:
            # Pass the corresponding root object of the JSON
            print(f"\nProcessing '{yaml_file}'...")
            populate_yaml(yaml_data, json_data, json_data[yaml_file_name])
            save_yaml_file(yaml_file_path, yaml_data, yaml_instance)
        else:
            print(f"\nError: No matching root object found in JSON for YAML file: {yaml_file_name}")


    # Get user input for paths
def main():
    yaml_folder_path = input("Enter the path to the folder containing YAML files: ")
    json_file_path = input("Enter the path to the JSON file: ")

    # Load the JSON data
    json_data = load_json_file(json_file_path)

    # Update all YAML files in the folder
    update_yaml_files_in_folder(yaml_folder_path, json_data)


# Main entry point
if __name__ == "__main__":

    main()