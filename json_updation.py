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
        # Execute the git diff command between the last two commits
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stdout + e.stderr  # Return both stdout and stderr if an error occurs

def extract_key_value_pairs(diff_output):
    """Extract key-value pairs from git diff output."""
    additions = {}
    deletions = []

    # Regex to match key-value pairs (assuming format "key: value")
    kv_pattern = re.compile(r'^(\+|\-)\s*([\w\.\-]+):\s*(.+)')

    lines = diff_output.splitlines()

    for line in lines:
        match = kv_pattern.match(line)
        if match:
            sign, key, value = match.groups()

            # Additions (lines starting with '+')
            if sign == '+':
                additions[key.strip()] = value.strip()

            # Deletions (lines starting with '-')
            elif sign == '-':
                deletions.append(key.strip())

    return additions, deletions

def update_json(json_file, additions, deletions):
    """Update JSON file based on additions and deletions."""
    try:
        # Load the current JSON content
        with open(json_file, 'r') as file:
            data = json.load(file)

        # Apply additions or updates
        for key, value in additions.items():
            data[key] = value  # Update or add the key-value pair

        # Apply deletions
        for key in deletions:
            if key in data:
                del data[key]  # Remove the key from the JSON if it exists

        # Save the updated JSON file
        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)

        print(f"JSON file '{json_file}' updated successfully.")

    except FileNotFoundError:
        print(f"Error: The file {json_file} does not exist.")
    except json.JSONDecodeError:
        print(f"Error: The file {json_file} is not a valid JSON file.")
    except Exception as e:
        print(f"An error occurred: {e}")

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

    # Iterate through each YAML file, perform git diff, and update JSON
    for yaml_file in yaml_files:
        print(f"Diff for {yaml_file}:\n")
        diff_output = git_diff(yaml_file)
        print(diff_output if diff_output else "No differences found.\n")

        # If there is a diff, extract key-value pairs
        if diff_output:
            additions, deletions = extract_key_value_pairs(diff_output)

            # Define corresponding JSON file (assuming the JSON file has the same name as the YAML file)
            json_file = yaml_file.replace('.yaml', '.json')

            # Check if the corresponding JSON file exists
            if os.path.isfile(json_file):
                # Update the JSON file based on additions and deletions
                update_json(json_file, additions, deletions)
            else:
                print(f"JSON file '{json_file}' does not exist. Skipping update.")

        print('-' * 200)

if __name__ == "__main__":
    main()
