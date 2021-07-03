#!/usr/bin/python
#coding: utf-8
# -------------------------------------------------------------------
# 宝塔Linux面板
# -------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# -------------------------------------------------------------------
# Author: hwliang <hwl@bt.cn>
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# MySQL端口安全检测
# -------------------------------------------------------------------

import os,sys,re,public,json

_title = 'MySQL security'
_version = 1.0                              # 版本
_ps = "Checks whether the current server's MySQL port is secure"      # 描述
_level = 2                                  # 风险级别： 1.提示(低)  2.警告(中)  3.危险(高)
_date = '2020-08-03'                        # 最后更新时间
_ignore = os.path.exists("data/warning/ignore/sw_mysql_port.pl")
_tips = [
    "If not necessary, remove the MySQL port release from the [Security] page",
    "Restrict IP access to MySQL port through the [System firewall] plug-in to enhance security",
    "Use [ Fail2ban ] plug-in to protect MySQL service"
    ]
_help = ''

def check_run():
    '''
        @name 开始检测
        @author hwliang<2020-08-03>
        @return tuple (status<bool>,msg<string>)

        @example   
            status, msg = check_run()
            if status:
                print('OK')
            else:
                print('Warning: {}'.format(msg))
        
    '''
    mycnf_file = '/etc/my.cnf'
    if not os.path.exists(mycnf_file):
        return True,'MySQL is not installed'
    mycnf = public.readFile(mycnf_file)
    port_tmp = re.findall(r"port\s*=\s*(\d+)",mycnf)
    if not port_tmp:
        return True,'MySQL is not installed'
    if not public.ExecShell("lsof -i :{}".format(port_tmp[0]))[0]:
        return True,'MySQL is not installed'
    result = public.check_port_stat(int(port_tmp[0]),public.GetLocalIp())
    if result == 0:
        return True,'Risk-free'

    fail2ban_file = '/www/server/panel/plugin/fail2ban/config.json'
    if os.path.exists(fail2ban_file):
        try:
            fail2ban_config = json.loads(public.readFile(fail2ban_file))
            if 'mysql' in fail2ban_config.keys():
                if fail2ban_config['mysql']['act'] == 'true':
                    return True,'Fail2ban is enabled'
        except: pass

    return False,'当前MySQL端口: {}，可被任意服务器访问，这可能导致MySQL被暴力破解，存在安全隐患'.format(port_tmp[0])
