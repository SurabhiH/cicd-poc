import os
import subprocess
import json
import re

def get_yaml_files(directory):
    """Return a list of YAML files in the specified directory."""
    return [f for f in os.listdir(directory) if f.endswith('.yaml')]

def git_diff(file_path):
    """Execute git diff command and return the output."""
    try:
        # Execute the git diff command
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stdout + e.stderr  # Return both stdout and stderr if an error occurs

def process_diff_output(file_path):
    """Process the git diff output and return the changes as a dictionary."""
    diff_output = git_diff(file_path)
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # If no differences are found, return None
    if "No differences found." in diff_output:
        return None

    # Initialize the add and delete lists for this file's changes
    changes = {
        "add": [],
        "delete": []
    }

    # Split the diff output by lines and iterate over each line
    for line in diff_output.splitlines():
        if line.startswith('+') and not line.startswith('+++'):
            # Line was added, add to "add" list
            changes['add'].append(line[1:].strip())
        elif line.startswith('-') and not line.startswith('---'):
            # Line was deleted, add to "delete" list
            changes['delete'].append(line[1:].strip())
    
    # Return the dictionary containing the changes
    return {file_name: changes} if changes['add'] or changes['delete'] else None

def update_json_with_diff(json_data, diff_changes):
    """Update the config-dev.json with the changes from git diff."""
    for yaml_file, changes in diff_changes.items():
        if yaml_file in json_data:
            # Update the existing object in the JSON
            for add_entry in changes['add']:
                key, value = parse_key_value(add_entry)
                if key and key not in json_data[yaml_file]:
                    json_data[yaml_file][key] = value

            for delete_entry in changes['delete']:
                key, value = parse_key_value(delete_entry)
                if key and key in json_data[yaml_file]:
                    del json_data[yaml_file][key]
        else:
            print(f"Error: {yaml_file} not found in the JSON file.")

def parse_key_value(line):
    """Parse a line of key-value pair."""
    match = re.match(r'(\S+):\s*["\']?([^"\']+)["\']?', line)
    return match.groups() if match else (None, None)

def main():
    # Ask for the relative directory input
    directory = input("Enter the relative path to the desired folder: ")

    # Get the absolute path
    absolute_directory = os.path.abspath(directory)

    if not os.path.isdir(absolute_directory):
        print("The provided path is not a valid directory.")
        return

    # Change to the specified directory
    os.chdir(absolute_directory)

    # Get YAML files in the directory
    yaml_files = get_yaml_files(absolute_directory)

    if not yaml_files:
        print("No YAML files found in the directory.")
        return

    # Open a file to store the diff output
    with open('git_diff.txt', 'w') as diff_file:
        all_diffs = {}
        
        for yaml_file in yaml_files:
            print(f"Processing diff for {yaml_file}...\n")
            diff_output = git_diff(yaml_file)
            if diff_output:
                diff_file.write(f"Diff for {yaml_file}:\n{diff_output}\n{'-'*100}\n")
                changes = process_diff_output(yaml_file)
                if changes:
                    all_diffs.update(changes)

    # If there are no changes, exit the program
    if not all_diffs:
        print("No differences found in any of the YAML files.")
        return

    # Read the existing JSON configuration file
    try:
        with open('config-dev.json', 'r') as json_file:
            config_data = json.load(json_file)
    except FileNotFoundError:
        print("config-dev.json file not found.")
        return
    except json.JSONDecodeError:
        print("Error parsing config-dev.json file.")
        return

    # Update the JSON data with the changes from the diffs
    update_json_with_diff(config_data, all_diffs)

    # Save the updated JSON back to the file
    with open('config-dev.json', 'w') as json_file:
        json.dump(config_data, json_file, indent=4)

    print("JSON file has been updated based on the git diffs.")

if __name__ == "__main__":
    main()
