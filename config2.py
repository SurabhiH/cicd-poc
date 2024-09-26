import os
import subprocess
import re
import json

def get_yaml_files(directory):
    """Return a list of YAML files in the specified directory."""
    return [f for f in os.listdir(directory) if f.endswith('.yaml')]

def git_diff(file_path):
    """Execute git diff command and return the output."""
    try:
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stdout + e.stderr

def filter_diff_content(diff_output):
    """Filter the diff content for relevant changes."""
    filtered_lines = []
    for line in diff_output.splitlines():
        if line.startswith("Diff for"):
            filtered_lines.append(line)
        elif line.startswith('+ ') or line.startswith('- '):
            # Ensure the line is longer than 1 character
            if len(line) > 1:
                filtered_lines.append(line)
    return filtered_lines

def extract_key_value_pairs(line):
    """Extract key-value pairs from a diff line."""
    match = re.search(r'(name|value)\s*:\s*"(.*?)"', line)
    if match:
        key, value = match.groups()
        return key, value
    return None, None

def update_config(config_path, merge_values):
    """Update the config-dev.json file based on merge-values."""
    # Load the JSON config
    try:
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
    except FileNotFoundError:
        print("The config-dev.json file was not found.")
        return
    except json.JSONDecodeError:
        print("The config-dev.json file is not a valid JSON.")
        return

    # Iterate through merge-values and update the config
    for var in merge_values:
        action, obj_name = var[:-3], var[:-3]  # 'add' or 'delete', and object name

        if obj_name in config_data:
            obj = config_data[obj_name]
        else:
            print(f"Object '{obj_name}' not found in config-dev.json.")
            continue

        if var.endswith("add"):
            for name, value in globals().get(var, {}).items():
                if name not in obj:
                    obj[name] = value  # Add if not a duplicate
                else:
                    print(f"Duplicate found: '{name}' already exists in '{obj_name}'")

        elif var.endswith("delete"):
            for name, value in globals().get(var, {}).items():
                if name in obj and obj[name] == value:
                    del obj[name]  # Remove the key-value pair
                else:
                    print(f"No matching key-value pair found for deletion in '{obj_name}'")

    # Save the updated config
    with open(config_path, 'w') as config_file:
        json.dump(config_data, config_file, indent=4)
    print("Config updated successfully.")

def main():
    directory = input("Enter the relative path to the desired folder: ")
    absolute_directory = os.path.abspath(directory)

    if not os.path.isdir(absolute_directory):
        print("The provided path is not a valid directory.")
        return

    os.chdir(absolute_directory)
    yaml_files = get_yaml_files(absolute_directory)

    if not yaml_files:
        print("No YAML files found in the directory.")
        return

    config_path = input("Enter the absolute path to the config-dev.json: ")

    merge_values = []

    with open("git-diff.txt", "w") as output_file:
        for yaml_file in yaml_files:
            diff_output = git_diff(yaml_file)

            if not diff_output.strip():
                continue

            filtered_output = filter_diff_content(f"Diff for {yaml_file}:\n{diff_output}")

            if filtered_output:
                output_file.write("\n".join(filtered_output) + "\n\n")
                print(f"Diff for {yaml_file} written to git-diff.txt.")

                additions = []
                deletions = []
                filename = None

                for line in filtered_output:
                    if line.startswith(f"Diff for {yaml_file}"):
                        filename = yaml_file.split(".")[0]
                    elif line.strip() == "":  # Encounter a blank line
                        break
                    elif line.startswith('+'):
                        key, value = extract_key_value_pairs(line)
                        if key == "name":
                            name = value.strip()
                        elif key == "value":
                            additions.append((name, value.strip()))  # Store as tuple
                    elif line.startswith('-'):
                        key, value = extract_key_value_pairs(line)
                        if key == "name":
                            name = value.strip()
                        elif key == "value":
                            deletions.append((name, value.strip()))  # Store as tuple

                # Create dynamically named lists for each filename
                if additions:
                    globals()[f"{filename}add"] = {name: value for name, value in additions}
                    merge_values.append(f"{filename}add")
                if deletions:
                    globals()[f"{filename}delete"] = {name: value for name, value in deletions}
                    merge_values.append(f"{filename}delete")

    print("merge-values =", merge_values)
    for var in merge_values:
        # Format the output correctly
        formatted_output = [f"'{name}':'{value}'" for name, value in globals().get(var, {}).items()]
        print(f"{var} = [{', '.join(formatted_output)}]")

    # Update the config file
    update_config(config_path, merge_values)

if __name__ == "__main__":
    main()