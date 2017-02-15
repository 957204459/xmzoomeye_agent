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
import logging.config
# 说明: 导入其它模块
from .core.main import MonitorClient
from .libs.daemonize import write_pid
from .libs.runutils import parameters_test, configuration_test


def create_app():
    opts = parameters_test()
    conf = configuration_test(opts)

    logging_file = opts['-l']
    running_pids = conf['agent'].get('pidfile')
    logging.config.fileConfig(logging_file)
    info, error = logging.getLogger('info'), logging.getLogger('error')

    write_pid(os.getpid(), running_pids)
    app = MonitorClient(agent=conf['agent'], info=info, error=error)

    return app
