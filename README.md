# Graphite-Grafana-Intro
by [Oriana Balizan](https://github.com/oribaldi)

An introduction to monitoring with Graphite and Grafana. Here I explain how to collect, store and visualize application metrics with them and Statsd. These metrics allow us to understand what is going on, and help us make supported decisions to improve our applications. For instance, metrics can show us how a system behaves before and after the deployment of new features. Moreover, they provide an additional source of information that might be missing in the logs.

# Overview

## Graphite
[Graphite](http://graphiteapp.org/) is a tool used to visualize representations of data over time. Graphite does 2 things:

1. Store numeric time-series data.
2. Render graphs of this data on demand.

Graphite is divided in 3 components:

1. **Carbon**: metric processing daemons that handle the storage backend.
2. **Whisper**: time-series database library.
3. **Graphite-Web**: web application you use to design and plot your data.

## Grafana
[Grafana](http://grafana.org/) is an open source suite used for visualizing time-series data for infrastructure and app analytics, from numerous sources. Grafana has a Graphite query editor that allows to navigate the metric space, add functions, create dashboards, and much more. A particularly useful feature is the possibility to synchronize timescales of different graphs. This helps spotting correlations among different events.

# How to deliver metrics to Graphite?
Given that Graphite does not collect data, we need to use other tools to gather them for it. But first, let's have a look at the formats that Graphite expects. Then, we can check some collecting tools and how we can connect them with Graphite.

## Protocols
Graphite expects you to deliver data by using one of the following protocols:

### Plain Text
Messages include the metric name, the value, and a timestamp. Example:
```
$ PORT=2003
$ SERVER=graphite.your.org
echo "foo.bar 1 `date +%s`" | nc -c ${SERVER} ${PORT}
```

Port `2003` is the default for this type of format.

### Pickle
Pickled data forms a list of multi-level tuples. This allows to buffer and send multiple values in a single transaction. Example:
```python
[(path, (timestamp, value)), ...]
```

Then, this list is put into a packet with a simple header:
```python
payload = pickle.dumps(listOfMetricTuples, protocol=2)
header  = struct.pack("!L", len(payload))
message = header + payload
```

The "message" object is then sent through a socket to Carbon's pickle receiver. The default port is `2004`.

### AMQP messages
They allow to handle large loads of data more gracefully. Can handle interruptions in network connections between remote hosts without losing data.

## Collectors
Instead of doing this manually, we can use collecting tools that can gather, aggregate and send metrics.

### Collectd
[Collectd](https://collectd.org/) is a system statistics daemon that can collect near-realtime information about a running service. For instance, statistics about memory usage, CPU load and network traffic, among other services.

It is quite useful if you want to track the behavior of your infrastructure or services you rely on (Apache, PostgreSQL, etc). You just need to install it on the machine your app is running, and connect it with Graphite. Follow the instructions of this [Tutorial](https://www.digitalocean.com/community/tutorials/how-to-configure-collectd-to-gather-system-metrics-for-graphite-on-ubuntu-14-04).

Check the [documentation](https://collectd.org/documentation.shtml) for more details.

### Statsd
[Statsd](https://github.com/etsy/statsd) is a statistics aggregator that can be used to collect and organize data. It can aggregate the values it receives and pass them to Graphite as summarized data points, in the time frame it expects.

Statsd must be installed on the machine running the application. You have to configure it so that it is connected with Graphite. Follow the instructions of this [Tutorial](https://www.digitalocean.com/community/tutorials/how-to-configure-statsd-to-collect-arbitrary-stats-for-graphite-on-ubuntu-14-04) or the official [documnetation](https://github.com/etsy/statsd/blob/master/docs/graphite.md).

** Pros and Cons **

You may ask.. why use Statsd when I can simply send my app's metrics directly to Carbon? Here are some reasons to consider:

Pros

1. Lets applications work around the effective rate-limit (10s) for sending Graphite stats; given that Statsd aggregates all data between flush intervals.
2. Available as a library for many programming languages, which facilitates the stats gathering of applications.
3. Provides several data types for metrics collections.
4. Operates over UDP, which reduces the overhead Carbon can suffer with TCP.
5. Lets the application be decoupled from the monitoring. If Carbon is down your application would not be affected. It will continue sending UDP messages, which will get lost.. but at least your app would not stop working ;)
6. Introduces sampling, which avoids overwhelming Statsd when tracking very frequent events.

Cons 

1. Operated over UDP, which does not guarantee a reliable transfer of information. However, recent versions can be configured to use TCP. Just think which gives you less headaches.


# Start Monitoring
Let's start monitoring our apps! Assuming you already installed and configured Graphite, Grafana and a collector (I will use Statsd).

## Use Statsd in your code
My app is in Python, so I install it like:
```
sudo apt-get install python-pip
sudo pip install statsd
```

Then, I import it in my code and start gathering some metrics. Example:
``` python
import statsd

...

"""
 - hostname and port must match: /etc/statsd/localConfig.js
 - "testapp" is the prefix for your app: 
"""
statsd_client = statsd.StatsClient('localhost', 8125, 'testapp')

...

# Check how long this function takes to execute
# Stored as stats/timers/testapp/login/time in Graphite-Web
@statsd_client.timer('login.time')
def login(username, password):

    ...

    # Check how frequently the function is being accessed
    # Stored as stats/counters/testapp/login/invocations in Graphite-Web
    statsd_client.incr('login.invocations')

    ...

...
```

## Verify your data is in Graphite-Web
You should have something similar to
![Graphite-Web](/images/graphite_start.png?raw=true)


## Connect Graphite with Grafana
Let's create elegant dashboards, notifications and alerts for our app with Grafana.

### Add Graphite as a DataSource
Grafana supports different data sources for your time series data. The following steps show how to add a new Graphite data source to Grafana:

1. Go to the side menu and click on the link named **Data Sources**.
![Graphite-Web](/images/grafana_data_sources.png?raw=true)
2. Click the **Add new** link (in the top header).
3. Enter the http information of your graphite service.

This automatically creates a dashboard for Graphite Carbon metrics. You can create additional dashboards for the same data source, which display different metrics. See the next point. 


### Create a Dashboard
Dashboards are a collection of organized Panels. A Panel is simply a visualization building block, which can be a: graph, singlestat, dashlist, table, or text. 

The following steps show how to build a new dashboard:

1. Go to the side menu, hover the link named **Dashboards**. This will show you a list of options. Select the **+ New** link.
![New dashboard](/images/grafana_create_dashboard.png?raw=true)
2. Select the type of panel you want to add. For instance, a Graph.
![Select a panel](/images/grafana_graph_panel.png?raw=true)
3. Configure your "New Dashboard" by clicking on **Manage dashboard**.
![Dashboard configuration](/images/grafana_new_dashboard.png?raw=true)
4. Edit the graph panel by clicking on the **Panel Title**, and selecting **Edit**.
    1. Select the data source you want to use.
    2. Edit the query to visualize specific metrics. For example, lets query the CPU usage of Carbon from the data source GraphiteTest:
    3. You can add new queries, new panels, etc.
    4. Remember to save your work!.
![Dashboard example](/images/grafana_carbon_cpu_graph.png?raw=true)

### Create Alerts and Notifications
Currently only the Graph panel supports alert rules. You can attach different rules to your dashboard panels, and they are evaluated by the Grafana backend.

 In the alert tab of the graph panel you can configure how often the alert rule should be evaluated and the conditions that need to be met for the alert to change state and trigger its notifications.

The following steps show how to configure alerts in Grafana:

1. Add a new alert:
    1. Click to **edit** your panel.
    2. Go to the **Alert** tab.
    3. Click on **Create Alert**.
2. Configure the alert:
    1. Specify the name of the alert.
    2. Specify how often it should be evaluated.
    3. Edit the condition that must be satisfied for the alert to change the state and trigger a notification.
    ![Alerting overview](http://docs.grafana.org/img/docs/v4/drag_handles_gif.gif)
3. Create a notification for the alert:
    1. Go to the side menu and hover **Alerting**. This will show you two options. Select **Notifications**
    ![New notification](/images/grafana_create_notification.png?raw=true)
    2. Click on **New Notification** on the top header.
    3. Configure and setup a new notification:
        * Specify the name
        * Specify the type. For example, e-mail.
        * Specify the e-mail addresses that will receive a notification message when an alert is triggered.
    4. Go back to the **Alert** tab in your dashboard.
    5. Attach the notification, created on the previous step, with the panel:
        1. Specify the notification to attach.
        2. Specify the notification message that would be send.
        ![Alert notification](/images/grafana_alert_notification.png?raw=true)
4. Check that the SMTP settings are properly setup in the Grafana config file ("/etc/grafana/grafana.ini"), in order to enable e-mail notifications. Other notification types need other setups.
