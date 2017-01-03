#!/usr/bin/python

"""
An application example that sends app metrics
to Graphite through Statsd.

Author: Oriana Baldizan
Date: 21.12.16

"""

import re
import sys
import time
import socket
import struct
import statsd


"""
 - hostname and port must match: /etc/statsd/localConfig.js
 - "testapp" is the prefix for your app: 
"""
statsd_client = statsd.StatsClient('localhost', 8125, 'testapp')

# Check how long it takes to execute this function
@statsd_client.timer('login.execTime')
def login_mock(userid, password):
	""" Login mock function """

	# Count how many times the function is being accessed
	# Stored as stats/counters/testapp/login/invocations
	statsd_client.incr('login.invocations')
	print "%s has logged in" % userid

	# Count the number of unique users in the same sample period
	# stats/sets/testapp/login/users
	statsd_client.set('login.users', userid)

	"""
	if valid_password(userid, password):
		render_welcome_page()
	else:
		render_error(403)
	"""

def run_app():
	""" Starts the app and metrics collection """

	# Time this block
	# stats/timers/testapp/login/timeBlock
	with statsd_client.timer('login.timeBlock'):
		for u in xrange(0,60):
			login_mock(u, 2*u)


def main():
	""" Starts the app and the Stats client """

	try:
		run_app()
	except KeyboardInterrupt:
		sys.stderr.write("\nExiting on CTRL-c\n")
		sys.exit(0)

if __name__ == "__main__":
	main()
