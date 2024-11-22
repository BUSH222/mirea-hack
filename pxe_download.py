import requests
import paramiko
import time


pxe_server_ip = '192.168.1.1'
pxe_server_port = 22
username = 'your_username'
password = 'your_password'
config_file_path = '/path/to/config/file'
status_check_url = 'http://{}/status'.format(pxe_server_ip)


def read_config_file(sftp_client, config_file_path):
    with sftp_client.file(config_file_path, 'r') as config_file:
        return config_file.read()


def get_installation_status():
    try:
        response = requests.get(status_check_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching installation status: {e}")
        return None


def main():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(pxe_server_ip, port=pxe_server_port, username=username, password=password)


        sftp = ssh.open_sftp()
        config_content = read_config_file(sftp, config_file_path)
        print("Contents of config file:\n", config_content)


        while True:
            status = get_installation_status()
            if status:
                print("Current installation status:", status)
            time.sleep(10)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        ssh.close()


#ДОПИСАТЬ КОМАНДУ УСТАНОВКИ ОБРАЗА
if __name__ == "__main__":
    main()