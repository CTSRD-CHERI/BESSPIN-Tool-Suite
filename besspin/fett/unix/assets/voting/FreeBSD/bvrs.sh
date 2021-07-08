#!/bin/sh

# PROVIDE: fett_bvrs
# REQUIRE: fett_nginx
# KEYWORD: shutdown

. /etc/rc.subr

name="fett_bvrs"
desc="Voter registration system for FETT"
rcvar="fett_bvrs_enable"
start_precmd="bvrs_precmd"

procname="/fett/sbin/kfcgi"
command="/usr/sbin/daemon"
bvrs_prog="/fett/var/www/cgi-bin/bvrs"
pidfile="/var/run/bvrs.pid"

sqlite3="/fett/bin/sqlite3"
dbfile="/fett/var/www/data/bvrs.db"
sqlfile="/fett/share/bvrs.sql"
off_name="official"
off_password_file="/root/bvrs-official-password"

: ${fett_bvrs_enable:="no"}
: ${fett_bvrs_flags:="-s /fett/var/www/run/httpd.sock -U www -u www -p /"}

bvrs_precmd()
{
	if [ ! -f "${dbfile}" ]; then
		echo "Initializing database: ${dbfile}"
		${sqlite3} "${dbfile}" < "${sqlfile}"
		chown www:www "${dbfile}"

		echo "Adding a new election official (password in ${off_password_file})"
		openssl rand -base64 12 > "${off_password_file}"
		off_hash=`openssl passwd -in "${off_password_file}" -6`
		${sqlite3} "${dbfile}" "INSERT INTO electionofficial (id, username, hash) VALUES (0, '${off_name}', '${off_hash}');"
	fi
}

# run_rc_command would send ${name}_flags as parameters to $command (daemon).
# This ensures they are actually passed to kfcgi instead.
actual_fett_bvrs_flags="${fett_bvrs_flags}"
fett_bvrs_flags=""
command_args="-f -p ${pidfile} -- ${procname} -d ${actual_fett_bvrs_flags} -- ${bvrs_prog} ${dbfile}"

run_rc_command "$1"
