import json
#import collections

def compare_and_update(source_file, destination_file):
    # Load source and destination config files
    with open(source_file, 'r') as f:
        source_config = json.load(f)

    with open(destination_file, 'r') as f:
        destination_config = json.load(f)

    # Function to recursively compare and update nested dictionaries
    def recursive_compare(src, dest):
        # Handle additions and updates
        for key in src.keys():
            if key not in dest:
                print(f"Adding new key: {key} with value: {src[key]}")
                dest[key] = src[key]  # Add the new key
            else:
                if isinstance(src[key], dict) and isinstance(dest[key], dict):
                    recursive_compare(src[key], dest[key])
                elif isinstance(src[key], list) and isinstance(dest[key], list):
                    # Handle lists: preserve order and add new items
                    for item in src[key]:
                        if item not in dest[key]:
                            print(f"Adding new item to list at '{key}': {item}")
                            dest[key].append(item)  # Append the new item
                    # Check for deletions
                    for item in dest[key][:]:  # Iterate over a copy to avoid modification errors
                        if item not in src[key]:
                            print(f"Removing item from list at '{key}': {item}")
                            dest[key].remove(item)  # Remove item from the destination
                elif src[key] != dest[key]:
                    print(f"Updating key: {key} from {dest[key]} to {src[key]}")
                    dest[key] = src[key]  # Update the value

        # Handle removals in the destination
        for key in list(dest.keys()):  # Use list() to avoid modifying during iteration
            if key not in src:
                print(f"Removing key from destination: {key}")
                del dest[key]  # Remove the key

    # Compare and update destination config
    recursive_compare(source_config, destination_config)

    # Write updated destination config back to file
    with open(destination_file, 'w') as f:
        json.dump(destination_config, f, indent=2)

    print(f"Updated destination config file: {destination_file}")

# Usage
# File paths for source and destination config files
def main():
    source_file = input("Enter the source json-file:  ") # "'C://Users//Surabhi//Desktop//Automation//CICD_Testing//cicd-poc//helm-charts//test-values//config-dev.json'
    destination_file = input("Enter the destination json-file:  ")  # 'C://Users//Surabhi//Desktop//Automation//CICD_Testing//cicd-poc//helm-charts//test-values//config-sit.json'

    compare_and_update(source_file, destination_file)


if __name__ == "__main__":
    main()