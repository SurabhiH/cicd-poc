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

        key_path = key.split('//')

        if change_request == 'delete' and (pd.isna(value) or value == ""):
            print(f"Value is empty for delete operation in row {index + 1} for key '{key}'. Skipping...")
            continue  # Skip processing for deletes with empty value

        if pd.isna(value) or value == "":
            print(f"Error: Value for key '{key}' in row {index + 1} is empty.")
            raise ValueError(f"Empty value encountered in row {index + 1} for key '{key}'.")

        parsed_value = try_parse_json(value)

        if service_name in json_data:
            obj = json_data[service_name]
            for k in key_path[:-1]:
                if k not in obj:
                    obj[k] = {}
                obj = obj[k]

            final_key = key_path[-1]

            # Check if the object is a list or dict before accessing
            if final_key in obj:
                if isinstance(obj[final_key], list):
                    # Handle list case here
                    if change_request == 'add':
                        obj[final_key].append(parsed_value)
                        print(f"Added to '{final_key}' in '{service_name}': {parsed_value}")
                    elif change_request == 'modify':
                        for entry in obj[final_key]:
                            if entry['name'] == parsed_value['name']:
                                entry['value'] = parsed_value['value']
                                print(f"Modified '{final_key}' entry in '{service_name}': {parsed_value}")
                                break
                    elif change_request == 'delete':
                        obj[final_key] = [entry for entry in obj[final_key] if entry['name'] != parsed_value['name']]
                        print(f"Deleted entry from '{final_key}' in '{service_name}'.")

                elif isinstance(obj[final_key], dict):
                    # Handle dict case here
                    if change_request == 'modify':
                        obj[final_key] = parsed_value
                        print(f"Modified '{final_key}' in '{service_name}': {parsed_value}")
                    elif change_request == 'add':
                        obj[final_key] = parsed_value
                        print(f"Added '{final_key}' in '{service_name}': {parsed_value}")
                    elif change_request == 'delete':
                        del obj[final_key]
                        print(f"Deleted '{final_key}' from '{service_name}'.")
            else:
                print(f"Warning: Attempted to modify non-existent key '{final_key}' in '{service_name}'.")

    return json_data



def save_json_to_file(json_data, output_file):
    if os.path.exists(output_file):
        pass
    else:
    # Create the directory if it does not exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write the JSON data to the file
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=4)


# Function to create YAML files with proper formatting
def create_yaml_files_from_json(updated_output_file, output_folder):
    # Load the updated JSON file
    with open(updated_output_file, 'r') as json_file:
        json_data = json.load(json_file)

    # Check if the output folder exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate through each root object in the JSON data
    for root_object, data in json_data.items():
        yaml_file_path = os.path.join(output_folder, f"{root_object}.yaml")

        # Process each key-value pair to handle lists of dictionaries and dictionaries
        processed_data = process_json_data(data)

        # Save the processed data to a YAML file
        with open(yaml_file_path, 'w') as yaml_file:
            yaml.dump(processed_data, yaml_file, default_flow_style=False, sort_keys=False)

# Function to process JSON data
def process_json_data(data):
    if isinstance(data, list):
        # Process lists of dictionaries
        return [process_json_data(item) for item in data]
    elif isinstance(data, dict):
        # For dictionaries, format them as JSON strings
        return {key: process_json_data(value) for key, value in data.items()}
    elif isinstance(data, str):
        # Enclose string values in double quotes
        return str(data)
    elif isinstance(data, (int, float, bool)):
        # Return non-string types as is
        return data
    elif data is None:
        # Return empty string for NoneType values
        return '""'
    else:
        # If data is something else, return it as a string
        return f'"{data}"'


def main():
    # Specify the folder path, excel file, and output file
    folder_path = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x-1\cicd-poc\helm-charts\json-comparison\sit-values'
    excel_file_path = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x\cicd-poc\release-note.xlsx'
    initial_output_file = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x-1\cicd-poc\helm-charts\json-comparison\sit-values\config-sit.json'
    updated_output_file = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x\cicd-poc\helm-charts\json-comparison\sit-values\config-sit.json'
    # Output folder path to store YAML files
    output_folder = r'C:\Users\Surabhi\Desktop\Automation\Test\promote-x\cicd-poc\helm-charts\json-comparison\sit-values'
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


    # Create YAML files from the JSON file
    create_yaml_files_from_json(updated_output_file, output_folder)


if __name__ == "__main__":
    main()
