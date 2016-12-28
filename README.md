# graphite-intro
An introduction to monitoring with Graphite and Grafana. This project explains how to collect, store and visualize application metrics. These metrics allow us to understand what is going on, and help us make supported decisions to improve our applications. For isntance, metrics can show us how a system behaves before and after the deployment of new features. Moreover, they provide an additional source of information that might be missing in the logs.

## Requirements
- Install Graphite

## Graphite
[Graphite](http://graphiteapp.org/) is a tool used to visualize representations of data over time. Graphite does 2 things:
1. Store numeric time-series data.
2. Render graphs of this data on demand.

### How is it composed?

Graphite is divided in 3 components:

1. Carbon: the metric processing daemons that handle the storage backend. There are different types of daemons:
	1.1 carbon-cache.py (basic one): listens for data on a port and writes to disk as it arrives.
	1.2 carbon-relay.py: shards data across different (carbon-cache) instances.
	1.3 carbon-aggregator.py: buffers data and dumps it into carbin-cache.py, after some ti,e.
2. Whisper: the time-series database library.
3. Graphite-Web: the web application to design graphs and plot your data.


### How to install it?

### How to configure it?

**Note:** that Graphite uses a dot-delimited namespace structure for metrics, graphs, and even dashboards.

### How can I deliver my metrics?

Given that Graphite does not collect data, it needs us or other tools to gather them for it. First, let's have a look at the formats that Graphite expects. Then, we can learn about some collecting tools.

#### Protocols
We can send data directly to Graphite by using one of the following protocols:

1. Plain Text: messages include the metric name, the value, and a timestamp. Example:
```
$ PORT=2003
$ SERVER=graphite.your.org
echo "foo.bar 1 `date +%s`" | nc -c ${SERVER} ${PORT}
```

Port `2003` is the default for this type of format.

2. Pickle: pickled data forms a list of multi-level tuples. This allows to buffer and send multiple values in a signle transaction. Example:
```
[(path, (timestamp, value)), ...]
```

Then, this list is put into a packet with a simple header:
```
payload = pickle.dumps(listOfMetricTuples, protocol=2)
header  = struct.pack("!L", len(payload))
message = header + payload
```

The "message" object is then sent through a socket to Carbon's pickle receiver. The default port is `2004`. Check this very simple example in TODO.

3. AMQP messages: they allow to handle large loads of data more gracefully. Can handle interruptions in network connections between remote hosts without losing data.


#### Collectd
[Collectd](https://collectd.org/) is a system statistics daemon that can collect near-realtime information about a running service. 

- Gather statistics about services like: memory usage, CPU load and network traffic.
- Used to track infrastructure's behavior.
- Can be used to track services like Apache, PostgreSQL, among others.

##### How to install it?
Install it on the machine running your application with:
```
sudo apt-get update
sudo apt-get install -y collectd collectd-utils
```
##### How to configure it?
The configuration is done in `/etc/collectd/collectd.conf`. Among the things you need to specify are:
- The hostname of your machine.
- The services you want to gather information from (apache, cpu, df, etc). Some services require additional configuration to enable the statistics collection.

Check the [documentation](https://collectd.org/documentation.shtml) for more details.

##### How to connect it  with Graphite?
- Add the hostname and the port of the machine running Graphite to `/etc/collectd/collectd.conf`.
- Set a storage-schema for Collectd in Carbon in `/etc/carbon/storage-schemas.conf`.
- Reload the services and verify that you have a section for Collectd in Graphite-Web.

#### Statsd

##### How to install it?

##### How to connect it  with Graphite?

##### How to send data to Statsd?

##### How to use it in my code?

##### What are the Pros and Cons?


## Grafana

### How to connect it with Graphite?

### How to build Dashboards?

### How to create alerts and notifications?


## References