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

        # Regex pattern to catch common prefix garbage: ^, .*, \., and leading dots
        prefix_pattern = re.compile(r'^(\^|\.\*|\\\.)+')
        # Regex pattern to catch suffix garbage: $
        suffix_pattern = re.compile(r'\$$')

        for line in raw_lines:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            # Step-by-step cleaning
            # 1. Strip the regex prefix (^.*\. or similar)
            tmp = prefix_pattern.sub('', line)
            # 2. Strip the regex suffix ($)
            tmp = suffix_pattern.sub('', tmp)
            # 3. Handle escaped dots (replace \. with .)
            tmp = tmp.replace('\\.', '.')
            # 4. Final trim of any accidental leading/trailing dots
            domain = tmp.strip('.')
            
            # Basic validation: must contain a dot and be at least 4 chars
            if "." in domain and len(domain) > 3:
                clean_domains.add(domain)
        
        # Sort alphabetically
        sorted_domains = sorted(list(clean_domains))
        
        # Build RouterOS script
        ros_commands = ["/ip dns static remove [find comment=\"GFW_AUTO\"]"]
        
        for dom in sorted_domains:
            # Using clean domain names for ROS v7 FWD type
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
