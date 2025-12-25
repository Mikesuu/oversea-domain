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
            
            # STEP 1: Remove all characters that are NOT letters, numbers, dots, or hyphens
            # This cleans out ^, *, +, \, $, etc.
            tmp = re.sub(r'[^a-zA-Z0-9\.\-]', '', line)
            
            # STEP 2: Remove any non-alphanumeric characters from the START of the string
            # This specifically fixes the "-." or "." or "-" at the beginning
            domain = re.sub(r'^[^a-zA-Z0-9]+', '', tmp)
            
            # STEP 3: Final validation
            # Must have at least one dot, be long enough, and start with a letter/number
            if "." in domain and len(domain) > 3 and domain[0].isalnum():
                clean_domains.add(domain)
        
        # Sort alphabetically
        sorted_domains = sorted(list(clean_domains))
        
        # Build RouterOS script
        ros_commands = ["/ip dns static remove [find comment=\"GFW_AUTO\"]"]
        
        for dom in sorted_domains:
            # name="google.com" (Clean, starts with alphanumeric)
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
