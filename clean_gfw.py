import requests
import re

SOURCE_URL = "https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/gfw.txt"
LIST_NAME = "GFW_List"

def build_ros_script():
    try:
        resp = requests.get(SOURCE_URL, timeout=30)
        resp.raise_for_status()
        clean_domains = set()
        for line in resp.text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "payload" in line:
                continue
            domain = line.replace('"', '').replace("'", "").strip()
            domain = re.sub(r'^[^a-zA-Z0-9]+', '', domain)
            domain = re.sub(r'[^a-zA-Z0-9]+$', '', domain)
            if "." in domain and len(domain) > 3:
                clean_domains.add(domain.lower())
        ros_commands = [f"/ip firewall address-list remove [find list={LIST_NAME}]"]
        for dom in sorted(list(clean_domains)):
            ros_commands.append(f"/ip firewall address-list add list={LIST_NAME} address=\"{dom}\"")
        with open("gfw_list.rsc", "w") as f:
            f.write("\n".join(ros_commands))
    except:
        pass

if __name__ == "__main__":
    build_ros_script()
