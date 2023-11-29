# -*- coding: utf8 -*-
import json
from typing import List
from tcp_latency import measure_latency
import logging, coloredlogs
from concurrent.futures.thread import ThreadPoolExecutor
from collections import OrderedDict


logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


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

class ServerConfigManager(object):
    def __init__(self, gui_config_file, out_config_file):
        """
        gui_config_file, json file, which looks like following:
        {
            "configs": [{
                "server": "****",
                "server_port": 443,
                "password": "****",
                "tcp_fast_open": true,
                "verfiy": true,
                "verify_certificate": true,
                "verify_hostname": true,
                "remarks": "***"
            }]
        }
        """
        self.gui_config_file = gui_config_file
        self.out_config_file = out_config_file

        self.server_configs = []
        self.load_configs()

    def load_configs(self):
        """
        load configs from json file
        """
        with open(self.gui_config_file, 'r') as file_handler:
            configs = json.loads(file_handler.read()).get('configs', [])
            for cfg in configs:
                self.server_configs.append(
                    ServerConfig(
                        server=cfg.get('server'),
                        port=cfg.get('server_port'),
                        password=cfg.get('password'),
                        tcp_fast_open=cfg.get('tcp_fast_open'),
                        verify=cfg.get('verify'),
                        verify_certificate=cfg.get('verify_certificate'),
                        verfiy_hostname=cfg.get('verify_hostname'),
                        remarks=cfg.get('remarks')
                    )
                )

    def write_config(self, server_config: ServerConfig, port: int) -> None:
        """write a config to file

        Args:
            server_config (ServerConfig): _description_
            port (int): _description_
        """
        tcp_cfg = TrojanTcpConfig(server_config.tcp_fast_open)
        ssl_cfg = TrojanSSLConfig(
            server_config.verify,
            server_config.verify_hostname
        )
        trojan_cfg = TrojanConfig(
            port, server_config.server, server_config.port, server_config.password,
            trojan_tcp_cfg=tcp_cfg, trojan_ssl_cfg=ssl_cfg
        )
        with open(self.out_config_file, 'w') as file_handler:
            file_handler.write(str(trojan_cfg))

    def get_servers(self, region: str) -> List[ServerConfig]:
        """get or filter available servers from original configs

        Args:
            region (str): _description_

        Returns:
            List[ServerConfig]: _description_
        """
        servers = []
        for sc in self.server_configs:
            if not region:
                servers.append(sc)
                continue

            if region in sc.server:
                servers.append(sc)
        return servers

class ChoseBestServer(object):
    def __init__(self, server_configs: List[ServerConfig]) -> None:
        self.server_configs = server_configs

        self.server_config_map = {}
        for sc in self.server_configs:
            self.server_config_map.update({sc.server: sc})

        self.result = dict()
        self.server_latency_in_order = OrderedDict()

    def cbs(self):
        with ThreadPoolExecutor(max_workers=10) as excutor:
            excutor.map(self.set_latency_for_server, self.server_configs)

        # sort by latency
        sorted_servers = sorted(self.result, key=self.result.get)
        for server in sorted_servers:
            self.server_latency_in_order.update({
                server: self.result.get(server)
            })

        logger.info('Latency Results:')
        for k, v in self.server_latency_in_order.items():
            logger.info(f'{self.server_config_map[k].server}:{self.server_config_map[k].port} --> {v} ms')

        return self.server_config_map[sorted_servers[0]]

    def set_latency_for_server(self, server_config: ServerConfig) -> None:
        """test latency

        Args:
            server_config (ServerConfig): _description_
        """
        latencies = measure_latency(host=server_config.server, port=server_config.port, timeout=1)
        logger.debug(
            '{}:{} latency: {} ms'.format(
                server_config.server, server_config.port,
                latencies[0] if latencies[0] else 'timeout'
            )
        )
        self.result[server_config.server] = latencies[0] if latencies[0] else 10000
