import os
import json
import pandas as pd

# Constants
TEMPLATE_FOLDER = "templates"  # Folder containing all template files
INPUT_EXCEL = "data.xlsx"  # The input Excel file
OUTPUT_FILE = "auto.tfvars"      # Output file

# Function to load templates dynamically
def load_templates(template_folder):
    """
    Load all template files from the specified folder.
    Returns a dictionary with filenames as keys and file content as values.
    """
    templates = {}
    for file_name in os.listdir(template_folder):
        if file_name.endswith(".txt"):
            with open(os.path.join(template_folder, file_name), "r") as file:
                templates[file_name.replace(".txt", "")] = file.read()
    return templates

# Function to replace placeholders in a template
def replace_placeholders(template, data):
    """
    Replace placeholders in the template with values from the data dictionary.
    Handles missing data and nested structures gracefully.
    """
    for key, value in data.items():
        placeholder = f"<<{key}>>"
        if isinstance(value, (dict, list)):
            # Convert nested structures to JSON strings (for Terraform compatibility)
            value = json.dumps(value, indent=2).replace('"', '')  # Terraform-friendly syntax
        elif value is None:
            value = ""  # Replace None with empty string
        template = template.replace(placeholder, str(value))
    return template

# Function to parse Excel input file
def parse_excel(file_path):
    """
    Parse the input Excel file into a dictionary where each sheet represents a resource type.
    """
    excel_data = pd.ExcelFile(file_path)
    data = {}
    for sheet_name in excel_data.sheet_names:
        data[sheet_name] = excel_data.parse(sheet_name).fillna("").to_dict(orient="records")
    return data

# Function to generate the auto.tfvars content
def generate_tfvars(data, templates):
    """
    Generate the auto.tfvars content by applying data to templates.
    """
    tfvars_content = ""

    # Add the global section first (if it exists)
    if "global" in templates:
        tfvars_content += templates["global"] + "\n"

    # Iterate through each resource type (e.g., topics, buckets)
    for resource_type, records in data.items():
        if resource_type in templates:
            template = templates[resource_type]
            
            # Extract the first and last lines of the template
            template_lines = template.splitlines()
            first_line = template_lines[0] + "\n"
            last_line = template_lines[-1]
            
            # Add first line to the tfvars_content
            tfvars_content += first_line
            
            # Iterate over the records for this resource type
            for idx, record in enumerate(records):
                # Replace placeholders and generate content for the current record
                resource_content = replace_placeholders(template, record)
                
                # Remove the first and last line content to avoid duplication
                resource_content = "\n".join(resource_content.splitlines()[1:-1])  # Removing first and last lines
                
                # Append the resource content
                tfvars_content += resource_content + "\n"
            
            # Add last line to the tfvars_content
            tfvars_content += last_line + "\n\n"
        else:
            print(f"Warning: No template found for resource type '{resource_type}'")
    
    return tfvars_content

# Main function
def main():
    # Ensure the template folder exists
    if not os.path.exists(TEMPLATE_FOLDER):
        raise FileNotFoundError(f"The template folder '{TEMPLATE_FOLDER}' does not exist.")
    
    # Load templates
    templates = load_templates(TEMPLATE_FOLDER)
    print(f"Loaded templates: {list(templates.keys())}")

    # Parse input Excel file
    if not os.path.exists(INPUT_EXCEL):
        raise FileNotFoundError(f"The input Excel file '{INPUT_EXCEL}' does not exist.")
    data = parse_excel(INPUT_EXCEL)

    # Generate auto.tfvars content
    tfvars_content = generate_tfvars(data, templates)

    # Write to output file
    with open(OUTPUT_FILE, "w") as file:
        file.write(tfvars_content)

    print(f"Successfully generated '{OUTPUT_FILE}'.")

# Entry point
if __name__ == "__main__":
    main()
