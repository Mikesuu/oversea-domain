import requests
import re

# Source: Loyalsoldier Clash Rules - GFW list
SOURCE_URL = "https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/gfw.txt"
# Target Gateway (Your Sidecar Gateway IP)
GATEWAY_IP = "10.10.10.3"
# Address List Name
LIST_NAME = "GFW_List"

def generate_ros_script():
    try:
        response = requests.get(SOURCE_URL)
        response.raise_for_status()
        lines = response.text.splitlines()
        
        # Filter valid domains only
        domains = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "." in line:
                domains.append(line)
        
        # Build ROS Script
        ros_commands = []
        ros_commands.append("/ip dns static")
        ros_commands.append("remove [find comment=\"GFW_AUTO_ADDED\"]")
        
        for dom in domains:
            # Escape dots for regex
            escaped_dom = dom.replace(".", "\\\\.")
            # Regex to match domain and all subdomains
            cmd = f"add regexp=\".*\\\\.{escaped_dom}\" forward-to={GATEWAY_IP} address-list={LIST_NAME} comment=\"GFW_AUTO_ADDED\""
            ros_commands.append(cmd)
            
        with open("gfw_list.rsc", "w") as f:
            f.write("\n".join(ros_commands))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_ros_script()
