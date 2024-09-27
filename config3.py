import os
import subprocess
import json

# Step 1: List YAML files and perform git diff
def list_yaml_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.endswith('.yaml')]

def get_git_diff(file_path):
    result = subprocess.run(['git', 'diff', 'HEAD^', 'HEAD', file_path], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def write_git_diff_to_file(diff, filename, output_file):
    with open(output_file, 'a') as f:
        f.write(f"Diff for {filename}:\n")
        for line in diff.splitlines():
            if line.startswith('+ ') or line.startswith('- '):
                f.write(line + "\n")

# Step 2: Filter git diff output
def filter_git_diff(folder_path, output_file):
    yaml_files = list_yaml_files(folder_path)
    for yaml_file in yaml_files:
        diff = get_git_diff(os.path.join(folder_path, yaml_file))
        write_git_diff_to_file(diff, yaml_file, output_file)

# Step 3: Update the JSON file based on the git diff
def update_json_file(git_diff_file, json_file):
    # Load the config-dev.json file
    with open(json_file, 'r') as jf:
        config_data = json.load(jf)

    # Open git_diff.txt and process the differences
    with open(git_diff_file, 'r') as gd:
        lines = iter(gd)  # Create an iterator from the file
        current_filename = None
        temp_key, temp_value = None, None
        temp_old_value, temp_new_value = None, None
        
        for line in lines:
            if line.startswith("Diff for"):
                current_filename = line.split(' ')[2].strip().replace(":", "").replace(".yaml", "")
                # Initialize current_object as an empty dictionary if the filename doesn't exist
                current_object = config_data.get(current_filename, {})
            
            elif line.startswith("- ") and "value" in line:
                temp_old_value = line.split(":")[1].strip().replace('"', '')
                try:
                    next_line = next(lines)  # Get the next line
                    if next_line.startswith("+ ") and "value" in next_line:
                        temp_new_value = next_line.split(":")[1].strip().replace('"', '')
                        # Replace the old value with the new value in the JSON object
                        for key, value in current_object.items():
                            if value == temp_old_value:
                                current_object[key] = temp_new_value
                                break
                except StopIteration:
                    # Handle the case where there's no next line (end of file)
                    pass
            
            elif line.startswith("+ ") and "name" in line:
                temp_key = line.split(":")[1].strip().replace('"', '')
            
            elif line.startswith("+ ") and "value" in line and temp_key:
                temp_value = line.split(":")[1].strip().replace('"', '')
                # Add new key-value pair
                current_object[temp_key] = temp_value
                temp_key, temp_value = None, None  # Reset for next key-value pair
            
            elif line.startswith("- ") and "name" in line:
                temp_key = line.split(":")[1].strip().replace('"', '')
            
            elif line.startswith("- ") and "value" in line and temp_key:
                temp_value = line.split(":")[1].strip().replace('"', '')
                # Remove the key-value pair from the JSON object
                if temp_key in current_object and current_object[temp_key] == temp_value:
                    del current_object[temp_key]
                temp_key, temp_value = None, None  # Reset for next key-value pair
            
            # Ensure current_object is stored back in config_data
            if current_filename:
                config_data[current_filename] = current_object

    # Write the updated config data back to the JSON file
    with open(json_file, 'w') as jf:
        json.dump(config_data, jf, indent=4)

# Example usage
def main():
    folder_path = input("Enter the folder path: ").strip()  # Strip extra spaces
    json_file = input("Enter the path to config-dev.json file: ").strip()  # Strip extra spaces
    git_diff_file = 'git_diff.txt'

    # Change directory to the folder path
    os.chdir(folder_path)

    # Clear or create git_diff.txt
    with open(git_diff_file, 'w') as gd_file:
        pass  # This just clears any existing content

    # Step 1 & 2: Generate filtered git diff output
    filter_git_diff(folder_path, git_diff_file)

    # Step 3: Update the JSON file
    update_json_file(git_diff_file, json_file)

if __name__ == "__main__":
    main()
