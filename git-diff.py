import os
import subprocess

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

    # Iterate through each YAML file and show the git diff
    for yaml_file in yaml_files:
        print(f"Diff for {yaml_file}:\n")
        diff_output = git_diff(yaml_file)
        print(diff_output if diff_output else "No differences found.\n")
        print('-' * 40)

if __name__ == "__main__":
    main()
