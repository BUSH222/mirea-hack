import subprocess
import os
#этот пресет выполняется единожды для настройки exp сервера на мастер сервере
def install_packages():
    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'dnsmasq'])

def setup_dhcp():
    dhcp_config = """
    interface=eth0
    dhcp-range=192.168.1.10,192.168.1.100,12h
    dhcp-boot=pxelinux.0
    enable-tftp
    tftp-root=/var/lib/tftpboot
    """
    with open('/etc/dnsmasq.conf', 'w') as f:
        f.write(dhcp_config)

def setup_tftp():
    if not os.path.exists('/var/lib/tftpboot'):
        os.mkdir('/var/lib/tftpboot')
        # очевидно скачать надо больше
        os.system('wget -P /var/lib/tftpboot https://releases.ubuntu.com/22.04/ubuntu-22.04-desktop-amd64.iso')

def start_services():
    subprocess.run(['sudo', 'systemctl', 'restart', 'dnsmasq'])

if __name__ == "__main__":
    install_packages()
    setup_dhcp()
    setup_tftp()
    start_services()