#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#
# Authors: limanman
# 51CTOBG: http://xmdevops.blog.51cto.com/
# Purpose:
#
"""
# 说明: 兼容绝对导入
from __future__ import absolute_import
# 说明: 导入公共模块
import os
import socket
import gevent
# 说明: 导入其他模块
from .. import plugins

from gevent import monkey
monkey.patch_all()


# 说明: 客户端监控类
class MonitorClient(object):
    def __init__(self, agent, info, error):
        self.info = info
        self.error = error
        # 重连AlertServer最大次数
        self.total_count = 7
        self.pluginlist = []
        self.agent_host = agent.get('host', '')
        self.bug_report = agent.get('bugreport', 0)
        self.alert_port = int(agent.get('alertport', '1314'))
        self.alert_host = agent.get('alerthost', '127.0.0.1')

        # 尝试创建连接
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, e:
            self.error.error('create socket with error {0}'.format(e))
            exit()
        retry_count = self._retry_reconnects()
        if retry_count > self.total_count:
            exit()

    def start(self):
        self._start_callplugin()

    def _retry_reconnects(self):
        retry_count = 0
        while True:
            retry_count += 1

            if retry_count > self.total_count:
                self.error.error('reconnect {0} times with errors'.format(self.total_count))
                break
            try:
                self.socket.connect((self.alert_host, self.alert_port))
            except socket.error, e:
                self.error.error('reconnect to AlertServer [{0}/{1}]'.format(retry_count, self.total_count))
                gevent.sleep(2)
                continue
            else:
                break
        return retry_count

    def _exception_senter(self, plugin_name, res, message):
        try:
            self.socket.sendall('{0} {1} {2}'.format(plugin_name, res, message))
        except socket.error, e:
            self.error.error('socket send data with error {0}'.format(e))
            # 尝试重建SOCKET重新连接
            self.socket.close()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            retry_count = self._retry_reconnects()
            if retry_count > self.total_count:
                self.error.error('reconnect {0} times with all errors'.format(self.total_count))
                return
            # 重新获取连接时重发数据
            else:
                self._exception_senter(plugin_name, res, message)
        else:
            if res:
                self.error.error('calls key#%s val#%s failure' % (plugin_name, message))
            else:
                self.info.info('calls key#%s val#%s success' % (plugin_name, message))



    def _start_collection(self):
        plugin_path = os.path.abspath(os.path.dirname(plugins.__file__))
        for py in os.listdir(plugin_path):
            if py != '__init__.py':
                if py.endswith('.py'):
                    plugin = py.rstrip('.py')
                    self.pluginlist.append(plugin)

    def _start_callplugin(self):
        while True:
            if not self.pluginlist:
                self._start_collection()
                gevent.sleep(1)
            eventlets = []
            for plugin in self.pluginlist:
                eventlets.append(gevent.spawn(self._start_plugincall, plugin, plugin))
            gevent.joinall(eventlets)

    def _start_plugincall(self, plugin_name, func_name):
        plugin_path = 'app.%s.%s' % ('plugins', plugin_name)
        try:
            plugin_mods = __import__(plugin_path, fromlist=[func_name])
        except ValueError, e:
            message = 'import key#%s val#%s with error %s' % (plugin_path, e)
            self._exception_senter(plugin_name, 1, message)
            return
        try:
            plugin_func = getattr(plugin_mods, plugin_name)
        except AttributeError, e:
            message = 'plugin key#%s val#%s not exists' % (plugin_mods, plugin_name)
            self._exception_senter(plugin_name, 1,  message)
            return
        try:
            plugin_data = plugin_func()
        except BaseException, e:
            message = 'pgcall key#%s val#%s with error %s' % (plugin_name, 'faild', e)
            self._exception_senter(plugin_name, 1, message)
            return
        # 除调用异常外,程序检测异常
        target = plugin_data['target']
        errors = plugin_data['errors']
        if target:
            self._exception_senter(plugin_name, 1, errors)
        else:
            self._exception_senter(plugin_name, 0, '')
