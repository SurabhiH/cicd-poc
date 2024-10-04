import os
import json
import csv
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

def update_image_name(json_data, txt_file_path):
    # Read the mappings from the text file
    with open(txt_file_path, 'r') as txt_file:
        mappings = {}
        for line in txt_file:
            if ':' in line:
                key, value = line.strip().split(':')
                mappings[key.strip()] = value.strip().strip('"')

    # Update JSON data based on mappings
    for root, content in json_data.items():
        if 'image' in content and 'image_name' in content['image']:
            image_key = content['image']['image_name']
            if root in mappings:
                json_data[root]['image']['image_name'] += mappings[root]

def compare_json_files(old_data, new_data):
    changes = []
    
    # Check for changes in the JSON files
    for root in new_data.keys():
        if root not in old_data:
            changes.append((root, 'add', '', json.dumps(new_data[root], indent=4), 'Root object added'))
        else:
            compare(old_data[root], new_data[root], root, changes)

    for root in old_data.keys():
        if root not in new_data:
            changes.append((root, 'delete', '', '', 'Root object deleted'))

    return changes

def compare(old, new, root, changes, path=''):
    if isinstance(old, dict):
        for key in old.keys():
            new_key_path = f"{path}/{key}" if path else key
            if key in new:
                compare(old[key], new[key], root, changes, new_key_path)
            else:
                changes.append((root, 'delete', new_key_path, json.dumps(old[key], indent=4), 'Deleted'))

        for key in new.keys():
            new_key_path = f"{path}/{key}" if path else key
            if key not in old:
                changes.append((root, 'add', new_key_path, json.dumps(new[key], indent=4), 'Added'))

    elif isinstance(old, list):
        for item in old:
            if item not in new:
                changes.append((root, 'delete', path, json.dumps(item, indent=4), 'Deleted'))

    else:
        if old != new:
            changes.append((root, 'modify', path, json.dumps(new, indent=4), 'Modified'))

def write_changes_to_csv(changes, csv_file_path):
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Service name', 'Change Request', 'Key', 'Value', 'Comment'])

        for change in changes:
            service_name, change_type, key, value, comment = change
            csv_writer.writerow([service_name, change_type, key, value, comment])

def main():
    folder_path = input("Enter the path of the folder containing YAML files: ")
    previous_json_path = input("Enter the path of the previous JSON file: ")
    new_json_path = input("Enter the path to save the new JSON file: ")
    txt_file_path = input("Enter the path of the text file with mappings: ")
    csv_file_path = input("Enter the path to save the changes CSV file: ")

    # Convert YAML to JSON
    json_data = yaml_to_json(folder_path)

    # Update image_name based on the text file
    update_image_name(json_data, txt_file_path)

    # Save the new JSON data
    with open(new_json_path, 'w') as new_json_file:
        json.dump(json_data, new_json_file, indent=4)

    # Load previous JSON data
    try:
        with open(previous_json_path, 'r') as old_file:
            old_data = json.load(old_file)
    except (json.JSONDecodeError, FileNotFoundError):
        print("Previous JSON file is invalid or not found.")
        old_data = {}

    # Compare JSON files
    changes = compare_json_files(old_data, json_data)

    # Write changes to CSV
    write_changes_to_csv(changes, csv_file_path)

if __name__ == '__main__':
    main()
