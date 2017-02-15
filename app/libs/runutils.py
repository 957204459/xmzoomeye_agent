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
import getopt
import ConfigParser
# 说明: 导入其它模块

program = __file__
version = '1.0.0.1'


# 说明: 显示使用说明
def show_usage_info():
    message = '''%s version: %s/%s
Usage: xmzoomeye-agent [-hv] [-c filename] [-l filename]

Options:
    -h      : this help
    -v      : show version and exit
    -c      : set running configuration file (default: docs/default.ini)
    -l      : set logging configuration file (default: docs/logging.ini)
''' % (program, program, version)
    print message


# 说明: 检测参数指定
def parameters_test():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hvc:l:', [])
    except getopt.GetoptError, e:
        print '%s: %s' % (program, e)
        sys.exit()

    exit_flag = [0, 0, 0]
    for key, val in opts:
        if '-v' == key:
            print 'version: %s/%s' % (program, version)
            exit_flag[0] = 1
        if '-h' == key:
            show_usage_info()
            exit_flag[0] = 1
        if '-c' == key:
            exit_flag[1] = 1
        if '-l' == key:
            exit_flag[2] = 1
    if exit_flag[0]:
        sys.exit()
    if not all(exit_flag[1:]):
        print '%s: option -c/-l requires arguments' % (program,)
        sys.exit()
    return dict(opts)


# 说明: 检测配置文件
def configuration_test(opts):
    cf = {}
    cp = ConfigParser.ConfigParser()

    for opt, arg in opts.iteritems():
        if not os.path.exists(arg):
            print '%s: no such config file %s' % (program, arg)
            sys.exit()

    runconfig = os.path.abspath(opts['-c'])
    with open(runconfig, 'r+b') as handler:
        cp.readfp(handler, runconfig)
    sections = cp.sections()
    if 'agent' not in sections:
        print '%s: no agent section' % (program,)
        sys.exit()
    for section in sections:
        if section not in cf:
            cf.setdefault(section, {})
            cf[section].update(cp.items(section))
    return cf

if __name__ == '__main__':
    pass

