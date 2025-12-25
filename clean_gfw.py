import requests
import re

SOURCE_URL = "https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/gfw.txt"
GW_IP = "10.10.10.3"
LIST_NAME = "GFW_List"

def build_ros_script():
    try:
        resp = requests.get(SOURCE_URL, timeout=30)
        resp.raise_for_status()
        
        clean_domains = set()
        for line in resp.text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"): continue
            # 清理正则符号，只保留纯域名
            tmp = re.sub(r'[^a-zA-Z0-9\.\-]', '', line)
            domain = re.sub(r'^[^a-zA-Z0-9]+', '', tmp)
            if "." in domain and len(domain) > 3 and domain[0].isalnum():
                clean_domains.add(domain)
        
        ros_commands = ["/ip dns static remove [find comment=\"GFW_AUTO\"]"]
        for dom in sorted(list(clean_domains)):
            # 这里是核心：指定匹配后自动加入 GFW_List
            cmd = f"/ip dns static add name=\"{dom}\" type=FWD forward-to={GW_IP} match-subdomain=yes address-list={LIST_NAME} comment=\"GFW_AUTO\""
            ros_commands.append(cmd)
            
        with open("gfw_list.rsc", "w") as f:
            f.write("\n".join(ros_commands))
        print("Success generated DNS FWD script.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_ros_script()
