import requests

# Source URL
SOURCE_URL = "https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/gfw.txt"
# Target sidecar gateway IP
GW_IP = "10.10.10.3"
# ROS Address List name
LIST_NAME = "GFW_List"

def build_ros_script():
    try:
        resp = requests.get(SOURCE_URL, timeout=30)
        resp.raise_for_status()
        
        # Filter: ignore comments, empty lines, and ensure it looks like a domain
        domains = [l.strip() for l in resp.text.splitlines() if l.strip() and not l.startswith("#") and "." in l]
        
        # ROS Commands
        # 1. Clean old rules first
        output = ["/ip dns static remove [find comment=\"GFW_AUTO\"]"]
        
        # 2. Add new rules
        # Using type=FWD for ROS v7 (more efficient than complex regex)
        for dom in domains:
            # Match domain and all subdomains
            line = f"/ip dns static add name=\"{dom}\" type=FWD forward-to={GW_IP} match-subdomain=yes address-list={LIST_NAME} comment=\"GFW_AUTO\""
            output.append(line)
            
        with open("gfw_list.rsc", "w") as f:
            f.write("\n".join(output))
            print(f"Success: {len(domains)} domains processed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_ros_script()
