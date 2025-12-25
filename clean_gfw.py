import requests
import socket

SOURCE_URL = "https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/gfw.txt"
LIST_NAME = "GFW_List"

def build_ros_script():
    try:
        resp = requests.get(SOURCE_URL, timeout=30)
        resp.raise_for_status()
        domains = [l.strip().lstrip('.') for l in resp.text.splitlines() if l.strip() and not l.startswith("#")]
        
        ros_commands = [f"/ip firewall address-list remove [find list={LIST_NAME}]"]
        
        for dom in domains[:500]:
            try:
                ip = socket.gethostbyname(dom)
                ros_commands.append(f"/ip firewall address-list add list={LIST_NAME} address={ip} comment=\"{dom}\"")
            except:
                continue
                
        with open("gfw_list.rsc", "w") as f:
            f.write("\n".join(ros_commands))
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_ros_script()
