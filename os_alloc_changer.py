import os
import subprocess
#файловая система pxe сервера настроена так, что для каждой ноды есть свой домен, на котором лежит нужная ос
# мы денамически изменяем файлы этой ос, так как нода при перезапуске вытаскивает файлы из этого адреса pxe
def change_os_on_pxe_server(node_id,changing_os_name):
    pid = subprocess.check_output(f"pgrep pypxe_{node_id}")
    os.system(f"kill {pid}")
    os.system(f"rm -rf {node_id}/netbot")
    os.system(f"cp -R os_database/{changing_os_name} {node_id}/netbot")
    os.system(f"sudo python -m pypxe_{node_id}.server --dhcp")