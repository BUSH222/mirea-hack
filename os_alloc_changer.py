import os
# файловая система pxe сервера настроена так, что для каждой ноды есть свой домен, на котором лежит нужная ос
# мы динамически изменяем файлы этой ос, так как нода при перезапуске вытаскивает файлы из этого адреса pxe


def change_os_on_pxe_server(node_id, changing_os_name):
    os.system(f"rm -rf {node_id}/netbot")
    os.system(f"cp -R os_database/{changing_os_name} {node_id}/netbot")
    os.system(f"sudo python -m pypxe_{node_id}.server --dhcp")
