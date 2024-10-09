import os
import json
import yaml


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


def main():
    folder_path = input("Enter the path of the folder containing YAML files: ")
    new_json_path = input("Enter the path to save the new JSON file: ")


    # Convert YAML to JSON
    json_data = yaml_to_json(folder_path)

    # Save the new JSON data
    with open(new_json_path, 'w') as new_json_file:
        json.dump(json_data, new_json_file, indent=4)


if __name__ == '__main__':
    main()