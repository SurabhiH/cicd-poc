import os
import json
import yaml
import subprocess

def get_yaml_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.endswith('.yaml')]

def git_diff(yaml_file):
    command = ["git", "diff", "HEAD^", "--", yaml_file]
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    return result.stdout

def filter_diff(diff_output, yaml_file):
    filtered_lines = []
    filtered_lines.append(f"Diff for {yaml_file}:")
    
    for line in diff_output.splitlines():
        if line.startswith("+ ") or line.startswith("- "):
            filtered_lines.append(line)
    
    return "\n".join(filtered_lines)

def write_diff_to_file(diff_text, output_file='git_diff.txt'):
    with open(output_file, 'a') as f:
        f.write(diff_text + "\n")

def update_json_file(config_path, yaml_file, diff_text):
    with open(config_path, 'r') as f:
        config = json.load(f)

    temp_key = None
    temp_value = None
    temp_old_value = None
    temp_new_value = None
    
    for line in diff_text.splitlines():
        if line.startswith(f"Diff for {yaml_file}:"):
            continue
        
        if line.startswith("+ "):
            parts = line[2:].strip().split(": ")
            if len(parts) == 2:
                key, value = parts
                if key == "name":
                    temp_key = value
                elif key == "value" and temp_key is not None:
                    temp_value = value
                    config[yaml_file][temp_key] = temp_value

        elif line.startswith("- "):
            parts = line[2:].strip().split(": ")
            if len(parts) == 2:
                key, value = parts
                if key == "value":
                    temp_old_value = value
                    # find and replace
                    for k, v in config[yaml_file].items():
                        if v == temp_old_value:
                            config[yaml_file][k] = temp_new_value
                elif key == "name":
                    temp_key = value
                    # remove the old entry
                    if temp_key in config[yaml_file]:
                        del config[yaml_file][temp_key]

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def main():
    folder_path = input("Enter the folder path containing YAML files: ")
    config_path = input("Enter the path to config-dev.json file: ")

    yaml_files = get_yaml_files(folder_path)

    for yaml_file in yaml_files:
        diff_output = git_diff(os.path.join(folder_path, yaml_file))
        filtered_diff = filter_diff(diff_output, yaml_file)
        write_diff_to_file(filtered_diff)
        update_json_file(config_path, yaml_file, filtered_diff)

if __name__ == "__main__":
    main()
