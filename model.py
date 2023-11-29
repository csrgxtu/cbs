# -*- coding: utf8 -*-
import json

# 原始gui-config.json 对应的格式
class ServerConfig:
    def __init__(
            self, server: str, port: int, password: str,
            tcp_fast_open: bool, verify: bool, verify_certificate: bool,
            verfiy_hostname: bool, remarks: str
    ) -> None:
        self.server = server
        self.port = port
        self.password = password
        self.tcp_fast_open = tcp_fast_open
        self.verify = verify
        self.verify_certificate = verify_certificate
        self.verify_hostname = verfiy_hostname
        self.remarks = remarks
    
    def __repr__(self) -> str:
        """turn object into json str

        Returns:
            str: _description_
        """
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4
        )

# trojan 命令行特有格式
class TrojanTcpConfig:
    def __init__(self, tcp_fast_open: bool) -> None:
        self.no_delay = True
        self.keep_alive = True
        self.resue_port = False
        self.fast_open = tcp_fast_open
        self.fast_open_qlen = 20

    def __repr__(self) -> str:
        """turn object into json str

        Returns:
            str: _description_
        """
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4
        )

# trojan 命令行特有格式
class TrojanSSLConfig:
    def __init__(self, verify: bool, verify_hostname: bool) -> None:
        self.verify = verify
        self.verify_hostname = verify_hostname
        self.cert = ''
        self.cipher = ''
        self.cipher_tls13 = ''
        self.sni = ''
        self.alpn = ['h2', 'http/1.1']
        self.reuse_session = True
        self.session_ticket = False
        self.curves = ''

    def __repr__(self) -> str:
        """turn object into json str

        Returns:
            str: _description_
        """
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4
        )

# trojan 命令行特有格式
class TrojanConfig:
    def __init__(
            self, local_port: int, remote_addr: str, remote_port: int,
            password: str, trojan_tcp_cfg: TrojanTcpConfig, trojan_ssl_cfg: TrojanSSLConfig,
        ) -> None:
        self.run_type = 'client'
        self.local_addr = '127.0.0.1'
        self.local_port = local_port
        self.remote_addr = remote_addr
        self.remote_port = remote_port
        self.password = [password]
        self.log_level = 1
        self.tcp = trojan_tcp_cfg
        self.ssl = trojan_ssl_cfg

    def __repr__(self) -> str:
        """turn object into json str

        Returns:
            str: _description_
        """
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4
        )