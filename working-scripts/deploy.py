import subprocess
 
def deploy_service(text_file, env):
    
    with open(text_file, 'r') as file:
        first_col_values = file.readlines()
 
    # Execute Helm upgrade for each unique service in the first column
    for services in first_col_values:
        service = services.strip()
        # command = f"helm upgrade {service} helm-charts -f /Users/mgxr3734/Desktop/generate-config/promotion-x/cs-helm-charats/helm-charts/{env}-values/{service}.yaml"
        # result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(service)
    # return result
    
 
 
def main():
    env_name = "uat1"
    if not env_name:
        print("Error: ENV is not set.")
    # if not channel_name:
    #     print("Error: CHANNEL is not set.")
    text_file_path = rf"/Users/mgxr3734/Desktop/generate-config/promotion-x/cs-helm-charats/helm-charts/{env_name}-values/{env_name}.txt"
    deployment = deploy_service(text_file_path, env_name)
 
if __name__ == "__main__":
    main()
