import os
import json
import pandas as pd

# Constants
TEMPLATE_FOLDER = "templates"  # Folder containing all template files
INPUT_EXCEL = "data.xlsx"  # The input Excel file
OUTPUT_FILE = "auto.tfvars"  # Output file

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

# Function to handle pull_subscription template
def handle_pull_subscription_template(template, records):
    """
    Handles the pull_subscription template:
    - Adds the first line of the template only once at the start of the tfvars_content.
    - Adds the last line of the template only once at the end of the tfvars_content.
    - Adds the subs_topic section after create_schema if create_schema is true.
    """
    tfvars_content = ""
    template_lines = template.splitlines()
    
    # Extract the first and last lines of the template
    first_line = template_lines[0]
    last_line = template_lines[-1]
    
    # Start the content with the first line of the template
    tfvars_content += first_line + "\n"
    
    # Process each record
    for record in records:
        # Check if create_schema is true (no need to check for string case)
        create_schema = record.get("create_schema", False)  # Default to False if not found
        
        resource_content = ""
        subs_topic_inserted = False  # Flag to track if subs_topic has been added
        
        # Process each line of the template (excluding the first and last lines)
        for line in template_lines[1:-1]:
            resource_content += line + "\n"
            
            # If create_schema is true and we haven't inserted subs_topic yet, do it now
            if create_schema and "create_schema" in line and not subs_topic_inserted:
                # Define the subs_topic template
                subs_topic_template = """
                subs_topic = {
                    topic = <<topic>>
                    topic_labels = {
                        provisioningdate = <<provisioningdate>>
                    }
                    schema = <<schema>>
                    message_storage_policy = <<message_storage_policy>>
                }
                """
                
                # Replace placeholders in the subs_topic template
                subs_topic_content = replace_placeholders(subs_topic_template, record)
                
                # Add the subs_topic content after create_schema
                resource_content += subs_topic_content.strip() + "\n"
                
                # Mark that subs_topic has been inserted
                subs_topic_inserted = True
        
        # After processing all lines, replace placeholders for the whole resource
        resource_content = replace_placeholders(resource_content, record)
        
        tfvars_content += resource_content + "\n"
    
    # End the content with the last line of the template
    tfvars_content += last_line + "\n"
    
    return tfvars_content


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

            if resource_type == "pull_subscription":
                # Special handling for pull_subscription
                tfvars_content += handle_pull_subscription_template(template, records)
            else:
                # Generic handling for other templates
                template_lines = template.splitlines()
                first_line = template_lines[0] + "\n"
                last_line = template_lines[-1] + "\n\n"

                # Add the first line only once at the start of the section
                tfvars_content += first_line

                for record in records:
                    resource_content = replace_placeholders(template, record)
                    resource_lines = resource_content.splitlines()
                    resource_body = "\n".join(resource_lines[1:-1])  # Exclude first and last lines
                    tfvars_content += resource_body + "\n"

                # Add the last line only once at the end of the section
                tfvars_content += last_line
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
