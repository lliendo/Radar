Client configuration
====================

If you understood how a Radar server is configured then configuring a Radar
client is even easier (mainly because you don't define elements such as
contacts, checks, monitors and plugins).


Main configuration
------------------

The main configuration governs general aspects of the Radar client.
We'll take a look at a full configuration file and describe every available
option (this time we will setup a Windows Radar client) :

.. code-block:: yaml

    connect:
        to: 192.168.0.100
        port: 3333

    log:
        to: C:\Radar\Client\radar-client.log
        size: 10
        rotations: 3

    checks: C:\Radar\Client\checks
    enforce ownership: False
    reconnect: False

* connect : This option tells Radar client where to connect to.
  At the moment only IPv4 addresses are supported. By default it tries to connect
  to localhost port 3333.

* run as : On Unix platforms this option tells Radar the effective user
  and group that the process should run as. This is a basic security
  consideration to allow Radar to run with an unprivileged user. The
  specified user should not be a able to login to the system.
  The default user and group is radar. This option does not apply to Windows
  platforms.

* log : Radar will log all of its activity in this file. So if you
  feel that something is not working properly this is the place to look
  for any errors. Note that in the example there are two additional options :
  size and rotations. They indicate the maximum size (in MiB) that a log
  should grow, when its size goes beyond that amount then is rotated (backed
  up) and new logs are written to a new file. By default Radar sets a maximum 
  of 100 MiB for the log file and rotates it at most 5 times.

* pid file : On Unix platforms this file holds the PID of the Radar
  process. When Radar starts it will record its pidfile here and when
  it shuts down this file is deleted. Pid files are not recorded on Windows
  platforms.

* checks : This is the location where all your checks are stored. Every time
  a Radar client receives a CHECK message from the server all checks are
  first looked up here if a relative path was given, otherwise it will be
  looked up by its absolute path. You can lay out this directory as you wish.

* enforce ownership : On Unix platforms if this option is True then every
  time the Radar client has to execute a check it will first verify that
  the user and group of any check matches the one defined in the run as
  option. If the user and group does not match and error is generated and
  the check won't run. On Windows platforms it will only check for the user.
  By default this option is set to True.

* reconnect : This option specifies the behaviour of the client when a Radar
  server goes down. If set to True and if the Radar server stops working
  the client will keep retrying to connect to the server. By default this
  option is set to True.

As usual you can leave out almost every option to its default value. A minimum
Radar client configuration file might look like this :

.. code-block:: yaml

    connect:
        to: 192.168.0.100

All remaining options take default values. Check these defaults on the
platform defaults section.
