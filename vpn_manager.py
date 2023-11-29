# -*- coding: utf8 -*-
import os
import time
import subprocess
import argparse
from cbs import ServerConfigManager, ChoseBestServer
from config import logger, regions


def set_best_server_config(gui_config_file: str, config_file: str, region: str, port: int) -> None:
    """chose best server and set it into config.json

    Args:
        gui_config_file (str): _description_
        config_file (str): _description_
        region (str): _description_
        port (int): _description_
    """
    conf_manager = ServerConfigManager(
        gui_config_file=gui_config_file,
        out_config_file=config_file
    )
    servers = conf_manager.get_servers(region)
    if not servers:
        logger.info('No available servers after filtered!!!')
        exit(1)
    
    cbs = ChoseBestServer(servers)
    best_server = cbs.cbs()
    logger.info('Best server: {}'.format(best_server))

    conf_manager.write_config(best_server, port)
    logger.info('Config writed to json file ...')


def main(gui_config_file: str, region: str, port: int) -> None:
    """start trojan with config file

    Args:
        gui_config_file (str): _description_
        region (str): _description_
        port (int): _description_
    """
    config_file = "./config.json"
    while True:
        set_best_server_config(gui_config_file, config_file, region, port)

        # run with trojan
        process = subprocess.Popen(['./bin/trojan', '-c', config_file])

        time.sleep(5 * 60)
        process.kill()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='vpn_manager.py',
        description='Start vpn with best server in current network connection'
    )
    parser.add_argument('-g', '--gui-config-file', required=True, help='Original gui-config.json file')
    parser.add_argument(
        '-r', '--region',
        choices=regions,
        default='', required=False, help='region to filter'
    )
    parser.add_argument(
        '-p', '--port', default=1080, required=False, help='local port trajan to listen'
    )
    args = parser.parse_args()

    gui_config_file, region, port = args.gui_config_file, args.region, args.port
    if not os.path.isfile(gui_config_file):
        logger.error('Error, Plz create your gui_config.json file from template or download from portal')
        exit(1)

    main(gui_config_file, region, port)
