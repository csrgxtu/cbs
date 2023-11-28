# cbs
cbs -- choose best server，基于当前网络状况选择最优的服务器。

* Mac的clash不好用，莫名其妙。
* 我需要选择特定地区内的服务器，比如上tiktok。


## 依赖
1，有可用的第三方shadowsocks服务，这里是我目前用的：https://portal.shadowsocks.nz/clientarea.php

2，本机安装有Python3

## 原理
gui-config.json --> cbs.py --> best server in current network --> start trojan cmd with the best server config --> repeat previous processes every 5 mins

## 基本使用
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
