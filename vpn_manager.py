# -*- coding: utf8 -*-
import sys
import os
import time
import subprocess
import logging, coloredlogs
from cbs import ServerConfigManager, ChoseBestServer


logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


def set_best_server_config(gui_config_file, config_file):
    """
    chose best server and set it into config.json
    :param gui_config_file: str
    :param config_file: str
    :return: None
    """
    conf_manager = ServerConfigManager(
        gui_config_file=gui_config_file,
        out_config_file=config_file
    )
    cbs = ChoseBestServer(conf_manager.get_servers())
    cbs = ChoseBestServer(conf_manager.get_servers())
    best_server = cbs.cbs()
    logger.info('Best server: {}'.format(best_server))
    config = conf_manager.get_config_by_server(best_server)
    conf_manager.write_config(
        config.get('server'), config.get('server_port'), config.get('password')
    )
    logger.info('Config writed to json file: {}'.format(config))


def main(gui_config_file, config_file):
    """
    start trojan with config file
    :param gui_config_file: str
    :param config_file: str
    :return: None
    """
    while True:
        # run with trojan
        process = subprocess.Popen(['./bin/trojan', '-c', config_file])

        time.sleep(5 * 60)
        if process:
            set_best_server_config(gui_config_file, config_file)
            process.kill()
            logger.info('Kill current trojan and chose best server again')

if __name__ == "__main__":
    gui_config_file = './gui-config.json'
    config_file = './config.json'

    if len(sys.argv) != 1:
        logger.error('Usage: python3 vpn_manager.py')
        exit(1)

    if not os.path.isfile(gui_config_file) or not os.path.isfile(config_file):
        logger.error('Error, Plz create your gui_config.json and config.json file from template')
        exit(1)

    set_best_server_config(gui_config_file, config_file)
    main(gui_config_file, config_file)
