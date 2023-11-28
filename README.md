# cbs
cbs -- choose best server, Mac的clash用起来太麻烦，不友好，因此本项目提供命令行版本的脚本帮助选择最优的服务器来上网（对于trojan命令的二次封装）。


## 依赖
1，有可用的第三方shadowsocks服务，这里是我目前用的：https://portal.shadowsocks.nz/clientarea.php

2，本机安装有Python3

## 原理
gui-config.json --> cbs.py --> best server in current network --> start trojan cmd with the best server config --> repeat previous processes every 5 mins

## Get started
1, clone the repo
```bash
git clone git@github.com:csrgxtu/cbs.git
```

2, install requirements
```bash
pip install -r requirements.txt
```

3, download the `gui-config.json` file from your vpn service portal page.

4, start the script, it will chose the best server considering your current network.
```bash
python vpn_manager.py
```
