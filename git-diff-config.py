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

def modify_json(config_path, merge_values):
    # Load the config file
    with open(config_path, 'r') as json_file:
        config_data = json.load(json_file)

    for var in merge_values:
        object_name = var.split('add')[0] if 'add' in var else var.split('delete')[0]
        action = 'add' if 'add' in var else 'delete'
        items = globals().get(var, {})

        if object_name in config_data:
            object_data = config_data[object_name]

            if action == 'add':
                # Add key-value pairs
                for key, value in items.items():
                    if key not in object_data:
                        object_data[key] = value
                    else:
                        print(f"Duplicate found for {key} in {object_name}, skipping addition.")
            elif action == 'delete':
                # Delete key-value pairs
                for key in list(items.keys()):
                    if key in object_data:
                        del object_data[key]
                    else:
                        print(f"No key found for {key} in {object_name}, skipping deletion.")
        else:
            print(f"{object_name} not found in config-dev.json.")

    # Write the updated config back to the file
    with open(config_path, 'w') as json_file:
        json.dump(config_data, json_file, indent=4)

def main():
    directory = input("Enter the relative path to the desired folder: ")
    config_path = input("Enter the path to config-dev.json: ")
    
    absolute_directory = os.path.abspath(directory)
    
    if not os.path.isdir(absolute_directory):
        print("The provided path is not a valid directory.")
        return

    os.chdir(absolute_directory)
    yaml_files = get_yaml_files(absolute_directory)

    if not yaml_files:
        print("No YAML files found in the directory.")
        return

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

    modify_json(config_path, merge_values)

if __name__ == "__main__":
    main()
