import requests
import re

# Domain list source
SOURCE_URL = "https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/gfw.txt"
# Sidecar gateway IP address
GW_IP = "10.10.10.3"
# RouterOS Address List name
LIST_NAME = "GFW_List"

def build_ros_script():
    try:
        print(f"Fetching data from {SOURCE_URL}...")
        resp = requests.get(SOURCE_URL, timeout=30)
        resp.raise_for_status()
        
        raw_domains = resp.text.splitlines()
        clean_domains = []

        for line in raw_domains:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            # Cleaning logic: remove regex characters to get pure domains
            # 1. Remove regex prefixes like ^, .*, \.
            domain = re.sub(r'^(\^|\.\*|\\\.)+', '', line)
            # 2. Remove regex suffix $
            domain = re.sub(r'\$$', '', domain)
            # 3. Strip any remaining leading or trailing dots
            domain = domain.strip('.')
            
            # Basic validation: must contain a dot and be of reasonable length
            if "." in domain and len(domain) > 3:
                clean_domains.append(domain)
        
        # Remove duplicates and sort alphabetically
        unique_domains = sorted(list(set(clean_domains)))
        
        # Build RouterOS .rsc script
        ros_commands = []
        # Step 1: Remove existing entries managed by this script
        ros_commands.append("/ip dns static remove [find comment=\"GFW_AUTO\"]")
        
        # Step 2: Add pure domain forwarding rules for ROS v7
        for dom in unique_domains:
            # Use type=FWD with match-subdomain=yes for optimal performance
            cmd = (
                f"/ip dns static add name=\"{dom}\" type=FWD "
                f"forward-to={GW_IP} match-subdomain=yes "
                f"address-list={LIST_NAME} comment=\"GFW_AUTO\""
            )
            ros_commands.append(cmd)
            
        # Write the output file
        with open("gfw_list.rsc", "w") as f:
            f.write("\n".join(ros_commands))
            
        print(f"Success! Processed {len(unique_domains)} clean domains.")
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    build_ros_script()
