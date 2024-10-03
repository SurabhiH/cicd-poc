import os
import yaml
import json

# Function to read YAML files and convert them into a JSON structure under a root object named after the YAML file
def yaml_files_to_json(folder_path, output_json_file):
    data = {}

    # Iterate over each YAML file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            yaml_file_path = os.path.join(folder_path, filename)
            root_object = os.path.splitext(filename)[0]  # Use the filename without extension as root object

            try:
                # Open and load the YAML file
                with open(yaml_file_path, 'r') as file:
                    yaml_data = yaml.safe_load(file)

                # Store the YAML content under the root object key
                data[root_object] = yaml_data

            except yaml.YAMLError as e:
                print(f"Error parsing YAML file {filename}: {e}")
            except Exception as e:
                print(f"An error occurred with file {filename}: {e}")

    # Write the consolidated JSON data to the specified output file
    try:
        with open(output_json_file, 'w') as json_out:
            json.dump(data, json_out, indent=2)
        
        print(f"Successfully converted all YAML files in {folder_path} to {output_json_file}")
    except Exception as e:
        print(f"Error writing to JSON file: {e}")

# Get folder path from user
folder_path = input("Enter the path of the folder containing YAML files: ")
output_json_file = 'dev-template/config.json'  # You can modify the output file name if needed

# Convert the YAML files to a consolidated JSON
yaml_files_to_json(folder_path, output_json_file)
