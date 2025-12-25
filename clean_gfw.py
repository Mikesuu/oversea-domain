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
        
        raw_lines = resp.text.splitlines()
        clean_domains = set()

        for line in raw_lines:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            # AGGRESSIVE CLEANING:
            # 1. Remove anything that isn't a word character, a dot, or a hyphen
            # This kills ^, *, +, \, $, etc. in one go
            tmp = re.sub(r'[^a-zA-Z0-9\.\-]', '', line)
            
            # 2. Remove leading dots (e.g., .google.com becomes google.com)
            domain = tmp.lstrip('.')
            
            # 3. Final validation: Must have at least one dot and be long enough
            # Also ensure it doesn't end with a dot
            if "." in domain and len(domain) > 3 and not domain.endswith('.'):
                clean_domains.add(domain)
        
        # Sort alphabetically
        sorted_domains = sorted(list(clean_domains))
        
        # Build RouterOS script commands
        ros_commands = ["/ip dns static remove [find comment=\"GFW_AUTO\"]"]
        
        for dom in sorted_domains:
            # Using clean domain names for ROS v7 FWD type
            # name="google.com" (No more + or ^ symbols)
            cmd = (
                f"/ip dns static add name=\"{dom}\" type=FWD "
                f"forward-to={GW_IP} match-subdomain=yes "
                f"address-list={LIST_NAME} comment=\"GFW_AUTO\""
            )
            ros_commands.append(cmd)
            
        with open("gfw_list.rsc", "w") as f:
            f.write("\n".join(ros_commands))
            
        print(f"Success! Generated {len(sorted_domains)} clean domain entries.")
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    build_ros_script()
