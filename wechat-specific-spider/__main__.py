import socket
import yaml
import sys
import os





def get_host_ip():
    """
    利用 UDP 协议来实现的，生成一个UDP包，把自己的 IP 放如到 UDP 协议头中，然后从UDP包中获取本机的IP。
    这个方法并不会真实的向外部发包，所以用抓包工具是看不到的
    :return:
    """
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        if s:
            s.close()

    return ip

# print(get_host_ip())

abs_path = lambda file: os.path.abspath(os.path.join(os.path.dirname(__file__), file))

def load_conf():
    print(abs_path('./config.yaml'))
    conf = yaml.full_load(open(abs_path('./config.yaml'), encoding='utf-8'))
    base = conf.get('dir').get('base_dir')
    print(base)
    print(base + conf.get('dir').get('log_dir'))

load_conf()