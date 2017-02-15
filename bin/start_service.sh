#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Authors: limanman
# 51CTOBG: http://xmdevops.blog.51cto.com/
# Purpose:
#

prog_name='xmzoomeye-agent'
prog_path="`pwd`/${prog_name}"
prog_conf="`pwd`/app/conf/default.ini"
prog_logs="`pwd`/app/conf/logging.ini"
prog_pids="`pwd`/logs/${prog_name}.pid"
prog_ppid=`(cat ${prog_pids}|grep -o "[^ ]\+\( \+[^ ]\+\)*") 2>/dev/null`

if [[ "X${prog_ppid}" != "X" ]];then
    echo -e "Host: $(hostname) Pid: ${prog_ppid:-"None"} Prog: ${prog_path} Status: start"
else
    (python ${prog_path} -c ${prog_conf} -l ${prog_logs} &>/dev/null)&
    sleep 5
    prog_ppid=`(cat ${prog_pids}|grep -o "[^ ]\+\( \+[^ ]\+\)*") 2>/dev/null`
    echo -e "Host: $(hostname) Pid: ${prog_ppid:-"None"} Prog: ${prog_path} Status: start"
fi
