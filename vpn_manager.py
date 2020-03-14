# -*- coding: utf8 -*-
import time
import subprocess
import logging, coloredlogs
from cbs import ServerConfigManager, ChoseBestServer


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


def set_best_server_config():
    """
    chose best server and set it into config.json
    """
    conf_manager = ServerConfigManager(
        gui_config_file='../gui-config.json',
        out_config_file='./config.json'
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


def main():
    while True:
        # run with trojan
        process = subprocess.Popen(['../trojan/trojan', '-c', 'config.json'])

        time.sleep(5 * 60)
        if process:
            set_best_server_config()
            process.kill()
            logger.info('Kill current trojan and chose best server again')

if __name__ == "__main__":
    set_best_server_config()
    main()
