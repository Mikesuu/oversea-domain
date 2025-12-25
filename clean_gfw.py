import requests
import re

SOURCE_URL = "https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/gfw.txt"
LIST_NAME = "GFW_List"

def build_ros_script():
    try:
        resp = requests.get(SOURCE_URL, timeout=30)
        resp.raise_for_status()
        
        # 提取并深度清洗域名
        clean_domains = set()
        for line in resp.text.splitlines():
            line = line.strip()
            # 跳过注释、空行和明显的 payload 标记
            if not line or line.startswith("#") or "payload" in line:
                continue
            
            # 正则清洗：只保留字母、数字、点和中划线，且必须以字母或数字开头
            # 去掉开头的 -. 等符号
            domain = re.sub(r'^[^a-zA-Z0-9]+', '', line)
            # 确保是一个有效的域名格式
            if "." in domain and len(domain) > 3:
                clean_domains.add(domain.lower())
        
        ros_commands = [f"/ip firewall address-list remove [find list={LIST_NAME}]"]
        
        # 生成纯净的 add 命令
        for dom in sorted(list(clean_domains)):
            ros_commands.append(f"/ip firewall address-list add list={LIST_NAME} address=\"{dom}\"")
                
        with open("gfw_list.rsc", "w") as f:
            f.write("\n".join(ros_commands))
        print(f"Success! {len(clean_domains)} pure domains generated.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_ros_script()
