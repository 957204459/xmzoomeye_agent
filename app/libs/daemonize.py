#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#
# Authors: limanman
# 51CTOBG: http://xmdevops.blog.51cto.com/
# Purpose:
#
"""
# 说明: 导入公共模块
import os
import sys
# 说明: 导入其它模块


# 说明: 生成守护进程
def daemonize(stdin=os.devnull, stdout=os.devnull, stderr=os.devnull):
    try:
        cur_pid = os.fork()
        if cur_pid > 0:
            sys.exit(0)
    except OSError, e:
        pass

    os.chdir('/')
    os.umask(0)
    os.setsid()

    try:
        nxt_pid = os.fork()
        if nxt_pid > 0:
            sys.exit(0)
    except OSError, e:
        pass

    for f in (sys.stdin, sys.stdout, sys.stderr):
        f.flush()

    f_stdin = open(stdin, 'r')
    f_stderr = open(stderr, 'a+', 0)
    os.dup2(f_stdin.fileno(), sys.stdin.fileno())
    os.dup2(f_stderr.fileno(), sys.stderr.fileno())


# 说明: 写入PID 文件
def write_pid(pid, pid_file):
    with open(pid_file, 'w') as f:
        f.write(str(pid))
