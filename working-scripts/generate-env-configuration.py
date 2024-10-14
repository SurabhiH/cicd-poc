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
            else:
                print(f"Error: Key is missing or empty in row {index + 1}.")
                raise ValueError(f"Missing or empty key encountered in row {index + 1}.")

        key_path = key.split('/')

        if pd.isna(value) or value == "":
            print(f"Error: Value for key '{key}' in row {index + 1} is empty.")
            raise ValueError(f"Empty value encountered in row {index + 1} for key '{key}'.")

        parsed_value = try_parse_json(value)

        if service_name in json_data:
            obj = json_data[service_name]
            for key in key_path[:-1]:
                if key not in obj:
                    obj[key] = {}
                obj = obj[key]

            final_key = key_path[-1]
            if key_path[0] == "env":
                if change_request == 'add':
                    obj[final_key].append(parsed_value)
                elif change_request == 'modify':
                    for entry in obj[final_key]:
                        if entry['name'] == parsed_value['name']:
                            entry['value'] = parsed_value['value']
                elif change_request == 'delete':
                    obj[final_key] = [entry for entry in obj[final_key] if entry['name'] != parsed_value['name']]
            else:
                if change_request == 'add' or change_request == 'modify':
                    obj[final_key] = parsed_value
                elif change_request == 'delete':
                    obj.pop(final_key, None)

    return json_data

def save_json_to_file(json_data, output_file):
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=4)

def main():
    # Specify the folder path, excel file, and output file
    folder_path = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x-1\helm-charts\json-comparison\sit-values'
    excel_file_path = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x\release-note.xlsx'
    initial_output_file = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x-1\helm-charts\json-comparison\sit-values\config-sit.json'
    updated_output_file = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x\helm-charts\json-comparison\sit-values\config-sit.json'

    # Ask the user for the sheet name
    sheet_name = input("Please enter the sheet name from which the values should be read: ")

    # Create a single JSON from YAML files
    json_data = read_yaml_files_to_json(folder_path)

    # Save the initial JSON to a file
    save_json_to_file(json_data, initial_output_file)

    # Apply changes based on the Excel file and the selected sheet
    updated_json = apply_changes_to_json(json_data, excel_file_path, sheet_name)

    # Save the updated JSON to a file
    save_json_to_file(updated_json, updated_output_file)

if __name__ == "__main__":
    main()
