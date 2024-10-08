import os
import yaml
import json
import pandas as pd

def read_yaml_files_to_json(folder_path):
    json_data = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            yaml_file_path = os.path.join(folder_path, filename)
            with open(yaml_file_path, 'r') as f:
                yaml_content = yaml.safe_load(f)
                # Use the file name (without extension) as the root object
                root_object = os.path.splitext(filename)[0]
                json_data[root_object] = yaml_content
    return json_data

def try_parse_json(value):
    try:
        # Try to parse the value as JSON
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        # If parsing fails, return the value as it is (assume it's a string)
        return value

def apply_changes_to_json(json_data, excel_file_path, sheet_name):
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
    
    for index, row in df.iterrows():
        service_name = row['Service name']
        change_request = row['Change Request']
        key_path = row['Key'].split('/')  # Split the key path into components
        value = row['Value']  # Read value directly as a raw string

        # Try to parse the value as JSON if it's JSON-like
        parsed_value = try_parse_json(value)

        if service_name in json_data:
            # Traverse the JSON to the target path
            obj = json_data[service_name]
            for key in key_path[:-1]:
                if key in obj:
                    obj = obj[key]
                else:
                    obj[key] = {}  # Create the key path if it doesn't exist

            # Perform the action (add, modify, delete)
            final_key = key_path[-1]
            if change_request == 'add' or change_request == 'modify':
                obj[final_key] = parsed_value  # Assign the parsed value (as JSON or string)
            elif change_request == 'delete':
                obj.pop(final_key, None)

    return json_data

def save_json_to_file(json_data, output_file):
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=4)

# Specify the folder path, excel file, and output file
folder_path = r'C:\Users\Surabhi\Desktop\Automation\CICD_Testing\cicd-poc\helm-charts\json-comparison\sit-values'

output_file = r'C:\Users\Surabhi\Desktop\Automation\CICD_Testing\cicd-poc\helm-charts\json-comparison\sit-values\config-sit2.json'


# Create a single JSON from YAML files
json_data = read_yaml_files_to_json(folder_path)

