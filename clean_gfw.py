import requests
import re

SOURCE_URL = "https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/gfw.txt"
LIST_NAME = "GFW_List"

def build_ros_script():
    try:
        resp = requests.get(SOURCE_URL, timeout=30)
        resp.raise_for_status()
        
        # 提取域名
        domains = []
        for line in resp.text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"): continue
            domain = re.sub(r'[^a-zA-Z0-9\.\-]', '', line).lstrip('.')
            if domain: domains.append(domain)
        
        # 直接生成 add address=域名 的指令
        # 这样导入时 ROS 会自动在后台异步解析 IP
        ros_commands = [f"/ip firewall address-list remove [find list={LIST_NAME}]"]
        for dom in domains:
            ros_commands.append(f"/ip firewall address-list add list={LIST_NAME} address=\"{dom}\"")
                
        with open("gfw_list.rsc", "w") as f:
            f.write("\n".join(ros_commands))
        print(f"Success! {len(domains)} domains added.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_ros_script()
