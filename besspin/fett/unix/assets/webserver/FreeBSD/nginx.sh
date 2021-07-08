#!/bin/sh

# PROVIDE: nginx
# REQUIRE: DAEMON
# KEYWORD: shutdown

. /etc/rc.subr

name=fett_nginx
rcvar=fett_nginx_enable
command=/fett/nginx/sbin/nginx

load_rc_config $name
: ${nginx_enable:=no}
: ${nginx_prefix=/fett/nginx}

command_args="-p ${nginx_prefix}"
pidfile=${nginx_prefix}/logs/nginx.pid

run_rc_command "$1"
