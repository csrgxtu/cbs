# -*- coding: utf8 -*-
import json
from typing import List
from tcp_latency import measure_latency
import logging, coloredlogs
from concurrent.futures.thread import ThreadPoolExecutor
from collections import OrderedDict
from model import *


logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


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
