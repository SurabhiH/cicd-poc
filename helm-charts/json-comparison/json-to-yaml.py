import os
import yaml
import json

# Function to create YAML files with proper formatting
def create_yaml_files_from_json(json_file_path, output_folder):
    # Load the updated JSON file
    with open(json_file_path, 'r') as json_file:
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

# Main function to take input paths and create YAML files
def main():
    # Input JSON file path
    #json_file_path = input("Enter the path of the JSON file: ")
    json_file_path = r'C:\Users\Surabhi\Desktop\Automation\CICD_Testing\cicd-poc\helm-charts\json-comparison\sit-values copy\config-sit2.json'
    
    # Output folder path to store YAML files
    #output_folder = input("Enter the path of the folder to save the YAML files: ")
    output_folder = r'C:\Users\Surabhi\Desktop\Automation\CICD_Testing\cicd-poc\helm-charts\json-comparison\sit-values copy'

    # Create YAML files from the JSON file
    create_yaml_files_from_json(json_file_path, output_folder)


if __name__ == "__main__":
    main()