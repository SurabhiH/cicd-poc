import ruamel.yaml
import json
import os

# Load the JSON file
def load_json_file(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

# Create a YAML file based on data from the JSON root object
def create_yaml_file(yaml_file_path, json_data):
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True  # Preserve quotes and formatting
    with open(yaml_file_path, 'w') as f:
        yaml.dump(json_data, f)
    print(f"Created YAML file: {yaml_file_path}")

# Main function to create YAML files from JSON data
def create_yaml_files_from_json(yaml_folder_path, json_data):
    # Ensure the folder exists
    if not os.path.exists(yaml_folder_path):
        os.makedirs(yaml_folder_path)

    for root_object, data in json_data.items():
        yaml_file_path = os.path.join(yaml_folder_path, f"{root_object}.yaml")
        create_yaml_file(yaml_file_path, data)

    print("\nYAML files have been created based on the JSON data.")

# Get user input for paths
def main():
    yaml_folder_path = input("Enter the path to the folder where YAML files will be created: ")
    json_file_path = input("Enter the path to the JSON file: ")

    # Load the JSON data
    json_data = load_json_file(json_file_path)

    # Create YAML files from JSON data
    create_yaml_files_from_json(yaml_folder_path, json_data)

# Main entry point
if __name__ == "__main__":
    main()
