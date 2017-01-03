#!/usr/bin/python

"""
An application example that sends app metrics
to Graphite through the Pickle protocol.

Based on the example: 
https://github.com/graphite-project/carbon/blob/master/examples/example-pickle-client.py

Author: Oriana Baldizan
Date: 21.12.16

"""

import re
import sys
import time
import socket
import pickle
import struct
import random

DELAY              =  30
CARBON_SERVER      = '127.0.0.1'
CARBON_PICKLE_PORT = 2004

def get_random_load():
    """ Generates random load value """

    return random.sample(xrange(10,300), 3)

def get_memcache(gsock):
    """ """

    data      = []
    lines     = []
    timestamp = int(time.time())

    for line in open('/proc/meminfo').readlines():

        bits = line.split()

        # We dont care about the pages.
        if len(bits) == 2:
            continue

        # remove the : from the metric name
        metric = bits[0]
        metric = metric.replace(':', '')

        # Covert the default kb into mb
        value = int(bits[1])
        value = value / 1024

        data.append(("testapp." + metric, (timestamp, value)))
        lines.append("testapp.%s %d %d" % (metric, value, timestamp))

        message = '\n'.join(lines) + '\n'
        print "Sending metrics to Graphite ..."
        print message

        # Send metrics
        package = pickle.dumps(data, 2)
        header  = struct.pack('!L', len(package))
        gsock.sendall(header + package)


def run_app(gsock):
    """ Starts the app and metrics collection """

    message = ""

    while True:

        now    = int(time.time())
        tuples = []
        lines  = []

        # Gather metrics
        load = get_random_load()
        for u in xrange(1, 5):
            # Format: (metric_name, (timestamp, value))
            tuples.append( ('testapp.count', (now, u)) )
            lines.append("testapp.count %d %d" % (u, now))
            
        message = '\n'.join(lines) + '\n'
        print "Sending metrics to Graphite ..."
        print message

        # Send metrics
        package = pickle.dumps(tuples)
        header  = struct.pack('!L', len(package))
        gsock.sendall(header + package)
        time.sleep(DELAY)


def main():
    """ Starts the app and its connection with Graphite """
    
    # Open Graphite connection
    gsock = socket.socket()
    try:
        gsock.connect( (CARBON_SERVER, CARBON_PICKLE_PORT) )
    except socket.error:
        # Check if carbon-cache.py is running
        raise SystemExit("Couldn't connect to %(server)s on port %(port)s" % {'server': CARBON_SERVER, 'port': CARBON_PICKLE_PORT})

    try:
        run_app(gsock)
        #get_memcache(gsock)
    except KeyboardInterrupt:
        gsock.close()
        sys.stderr.write("\nExiting on CTRL-c\n")
        sys.exit(0)

if __name__ == "__main__":
    main()