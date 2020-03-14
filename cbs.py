# -*- coding: utf8 -*-
import json
from tcp_latency import measure_latency
import logging, coloredlogs
from concurrent.futures.thread import ThreadPoolExecutor
from collections import OrderedDict


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


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

        self.configs = dict()
        self.servers = list()
        self.load_configs()

    def load_configs(self):
        """
        load configs from json file
        """
        with open(self.gui_config_file, 'r') as file_handler:
            self.configs = json.loads(file_handler.read()).get('configs', [])

    def get_config_by_server(self, server):
        """
        get config from configs with server filter
        """
        for config in self.configs:
            if config.get('server') == server:
                return config
        return None

    def write_config(self, remote_addr, remote_port, password):
        """
        write config to json file
        """
        with open(self.out_config_file, 'r') as file_handler:
            config = json.loads(file_handler.read())
            logger.debug('output config file: {}'.format(config))
            config.update({
                'remote_addr': remote_addr,
                'remote_port': remote_port,
                'password': [password]
            })
        with open(self.out_config_file, 'w') as file_handler:
            file_handler.write(json.dumps(config))

    def get_servers(self):
        """
        get available servers from gui config file
        """
        return [config.get('server') for config in self.configs]

class ChoseBestServer(object):
    def __init__(self, servers):
        self.servers = servers
        self.result = dict()
        self.server_latency_in_order = OrderedDict()

    def cbs(self):
        with ThreadPoolExecutor(max_workers=10) as excutor:
            excutor.map(self.set_latency_for_server, self.servers)

        sorted_servers = sorted(self.result, key=self.result.get)
        for server in sorted_servers:
            self.server_latency_in_order.update({
                server: self.result.get(server)
            })

        logger.info('Latency Results:')
        for k, v in self.server_latency_in_order.items():
            logger.debug('{} latency {} ms'.format(k, v))
        return sorted_servers[0]

    def set_latency_for_server(self, server):
        latencies = measure_latency(host=server, timeout=1)
        logger.debug(
            '{} latency: {} ms'.format(
                server, latencies[0] if latencies[0] else 'timeout'
            )
        )
        self.result[server] = latencies[0] if latencies[0] else 10000
