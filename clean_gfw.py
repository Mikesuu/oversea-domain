import requests

# Source URL from Loyalsoldier/clash-rules
SOURCE_URL = "https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/gfw.txt"
# Your Sidecar Gateway IP
GW_IP = "10.10.10.3"
# RouterOS Address List name
LIST_NAME = "GFW_List"

def build_ros_script():
    try:
        # Fetch the latest GFW list
        print(f"Fetching data from {SOURCE_URL}...")
        resp = requests.get(SOURCE_URL, timeout=30)
        resp.raise_for_status()
        
        # Filter: 
        # 1. Strip whitespace
        # 2. Ignore comments (#) and empty lines
        # 3. Ensure it's a domain (contains a dot)
        # 4. Remove leading dots (e.g., .google.com -> google.com)
        domains = [
            l.strip().lstrip('.') 
            for l in resp.text.splitlines() 
            if l.strip() and not l.startswith("#") and "." in l
        ]
        
        # Remove duplicates while preserving order
        unique_domains = list(dict.fromkeys(domains))
        
        # Start building RouterOS script (.rsc)
        ros_commands = []
        
        # Step 1: Clean up existing rules with our specific comment
        ros_commands.append("/ip dns static remove [find comment=\"GFW_AUTO\"]")
        
        # Step 2: Add pure domain forwarding rules
        # Format: /ip dns static add name="domain.com" type=FWD forward-to=X.X.X.X match-subdomain=yes address-list=LIST
        for dom in unique_domains:
            cmd = (
                f"/ip dns static add name=\"{dom}\" type=FWD "
                f"forward-to={GW_IP} match-subdomain=yes "
                f"address-list={LIST_NAME} comment=\"GFW_AUTO\""
            )
            ros_commands.append(cmd)
            
        # Write to file
        with open("gfw_list.rsc", "w") as f:
            f.write("\n".join(ros_commands))
            
        print(f"Success! Processed {len(unique_domains)} pure domains.")
        print("File 'gfw_list.rsc' is ready for RouterOS v7.")
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    build_ros_script()
