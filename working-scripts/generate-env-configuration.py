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
                root_object = os.path.splitext(filename)[0]
                json_data[root_object] = yaml_content
    return json_data

def try_parse_json(value):
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

def handle_data_env(json_data, service_name, change_request, parsed_value):
    """Handles modifications for 'data' and 'env' services."""
    obj = json_data.setdefault(service_name, [])
    
    if change_request == 'add':
        if not any(entry['name'] == parsed_value['name'] for entry in obj):
            obj.append(parsed_value)
            print(f"Added to '{service_name}': {parsed_value}")
        else:
            print(f"Warning: Entry with name '{parsed_value['name']}' already exists in '{service_name}'.")

    elif change_request == 'modify':
        for entry in obj:
            if entry['name'] == parsed_value['name']:
                entry.update(parsed_value)
                print(f"Modified entry in '{service_name}': {entry}")
                break
        else:
            print(f"Warning: Attempted to modify non-existent entry '{parsed_value['name']}' in '{service_name}'.")

    elif change_request == 'delete':
        json_data[service_name] = [entry for entry in obj if entry['name'] != parsed_value['name']]
        print(f"Deleted entry from '{service_name}' with name '{parsed_value['name']}'.")

def apply_changes_to_json(json_data, excel_file_path, sheet_name):
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

    for index, row in df.iterrows():
        service_name = row['Service name']
        change_request = row['Change Request']
        key = row['Key']
        comments = row['Comment']
        value = row['Value']

        # Handle addition of a root object
        if pd.isna(key) or key == "":
            if comments == "root object added":
                new_root_object = service_name
                if new_root_object not in json_data:
                    json_data[new_root_object] = {}
                    print(f"Added new root object: {new_root_object}")
                if not pd.isna(value) and value != "":
                    json_data[new_root_object] = try_parse_json(value)
                    print(f"Stored value in '{new_root_object}': {value}")
                continue
            elif comments == "root object deleted":
                if service_name in json_data:
                    del json_data[service_name]
                    print(f"Deleted root object: {service_name}")
                continue
            elif service_name in ['data', 'env']:
                pass # Skip the key checks for 'data' and 'env'
            else:
                print(f"Error: Key is missing or empty in row {index + 1}.")
                raise ValueError(f"Missing or empty key encountered in row {index + 1}.")

        parsed_value = try_parse_json(value)
        if service_name in ['data', 'env']:
            handle_data_env(json_data, service_name, change_request, parsed_value)
            continue

        # General handling for other services with keys
        key_path = key.split('//')
        obj = json_data.setdefault(service_name, {})

        for k in key_path[:-1]:
            obj = obj.setdefault(k, {})

        final_key = key_path[-1]
        
        if key_path[0] == "env":
                if change_request == 'add':
                    if final_key not in obj:
                        obj[final_key] = []
                    obj[final_key].append(parsed_value)
                    print(f"Added to '{final_key}' in '{service_name}': {parsed_value}")
                elif change_request == 'modify':
                    for entry in obj[final_key]:
                        if entry['name'] == parsed_value['name']:
                            entry['value'] = parsed_value['value']
                            print(f"Modified '{final_key}' entry in '{service_name}': {parsed_value}")
                            break
                elif change_request == 'delete':
                    if final_key in obj:
                        obj[final_key] = [entry for entry in obj[final_key] if entry['name'] != parsed_value['name']]
                        print(f"Deleted entry from '{final_key}' in '{service_name}'.")


        else:
            if change_request == 'modify':
                obj[final_key] = parsed_value
                print(f"Modified '{final_key}' in '{service_name}': {parsed_value}")
            elif change_request == 'add':
                obj[final_key] = parsed_value
                print(f"Added '{final_key}' in '{service_name}': {parsed_value}")
            elif change_request == 'delete' and final_key in obj:
                del obj[final_key]
                print(f"Deleted '{final_key}' from '{service_name}'.")

    return json_data

def save_json_to_file(json_data, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=4)

def create_yaml_files_from_json(updated_output_file, output_folder):
    with open(updated_output_file, 'r') as json_file:
        json_data = json.load(json_file)

    os.makedirs(output_folder, exist_ok=True)

    for root_object, data in json_data.items():
        yaml_file_path = os.path.join(output_folder, f"{root_object}.yaml")
        processed_data = process_json_data(data)
        
        with open(yaml_file_path, 'w') as yaml_file:
            yaml.dump(processed_data, yaml_file, default_flow_style=False, sort_keys=False)

def process_json_data(data):
    if isinstance(data, list):
        return [process_json_data(item) for item in data]
    elif isinstance(data, dict):
        return {key: process_json_data(value) for key, value in data.items()}
    return data

def main():
    folder_path = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x-1\cicd-poc\helm-charts\json-comparison\sit-values'
    excel_file_path = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x\cicd-poc\release-note.xlsx'
    initial_output_file = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x-1\cicd-poc\helm-charts\json-comparison\sit-values\config-sit.json'
    updated_output_file = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x\cicd-poc\helm-charts\json-comparison\sit-values\config-sit.json'
    output_folder = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x\cicd-poc\helm-charts\json-comparison\sit-values'
    
    sheet_name = input("Please enter the sheet name from which the values should be read: ")

    json_data = read_yaml_files_to_json(folder_path)
    save_json_to_file(json_data, initial_output_file)

    updated_json = apply_changes_to_json(json_data, excel_file_path, sheet_name)
    save_json_to_file(updated_json, updated_output_file)
    create_yaml_files_from_json(updated_output_file, output_folder)

if __name__ == "__main__":
    main()
