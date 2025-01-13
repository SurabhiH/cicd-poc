import os
import yaml
 
# Step 1: Read the keys from config.env file
def read_config_env(file_path):
    with open(file_path, 'r') as f:
        config_keys = [line.split('=')[0].strip() for line in f if line.strip()]
        print(config_keys)
    return config_keys
 
# Step 2: Read env.yaml file and return its data as a dictionary for easy lookup
def read_env_yaml(file_path):
    with open(file_path, 'r') as f:
        env_data = yaml.safe_load(f)
    return {item['name']: item.get('value', '') for item in env_data if 'name' in item}
 
# Step 3: Generate the environment-specific config.env file
def generate_env_config(config_keys, env_dict, output_file):
    with open(output_file, 'w') as f:
        for key in config_keys:
            if key in env_dict:
                # Write each key with its corresponding value from env.yaml
                f.write(f"{key}={env_dict[key]}\n")
 
# Main function to process each environment directory
def main():
    # Read the environments to update configs
    envs = input("Enter the envs to be promoted separated by a space: ").split()
 
    repo_x = rf'/Users/mgxr3734/Desktop/generate-config/promotion-x/promo-helm-charts'
    for foldername in os.listdir(repo_x):
        if foldername.endswith('helm-charts'):
 
            db_scripts_config_env_path = rf'/Users/mgxr3734/Desktop/generate-config/promotion-x/promo-helm-charts/{foldername}/dev-values/app-values/db-scripts-config-dev.env'
            config_keys = read_config_env(db_scripts_config_env_path)
 
            for env in envs:
                if env != "dev":
                    env_yaml_path = rf"/Users/mgxr3734/Desktop/generate-config/promotion-x/promo-helm-charts/{foldername}/{env}-values/app-values/env.yaml"
                    output_config_path = rf"/Users/mgxr3734/Desktop/generate-config/promotion-x/promo-helm-charts/{foldername}/{env}-values/app-values/db-scripts-config-{env}.env"
 
                    # Check if env.yaml exists in the current environment folder
                    if os.path.exists(env_yaml_path):
                        # Read env.yaml data and convert it to a dictionary for lookup
                        env_dict = read_env_yaml(env_yaml_path)
            
                        # Generate and write the environment-specific config.env file
                        generate_env_config(config_keys, env_dict, output_config_path)
                        print(f"Created {output_config_path} with matched keys.")
                    else:
                        print(f"{env_yaml_path} not found. Skipping.")
    
# Run the script
if __name__ == "__main__":
    main()
