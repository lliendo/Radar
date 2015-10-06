Server configuration
====================

Radar is simple and flexible in the way it defines different kind of components
(checks, contacts and monitors). It uses `YAML <https://en.wikipedia.org/wiki/YAML>`_ for all of its configuration.

When Radar starts it expects a main configuration file (this applies
to both client and server) as input. From that configuration file, further
locations are read to find checks, contacts, monitors definitions and plugins.

You're going to read a long document where the most important concepts
of Radar are described. Take a cup of your favourite beverage and read it
carefully. Once you read it you will find that configuring Radar is easy.
Try not to skip any sections because every part of it has something to say.
By the end of this document you'll have solid knowledge on how to configure
Radar and not going into trouble on the way.


Main configuration
------------------

The main configuration governs general aspects of the Radar server.
We'll take a look at a full configuration file and describe every available
option :

.. code-block:: yaml

    listen:
        address: 192.168.0.100
        port: 3333

    run as:
        user: radar
        group: radar

    log:
        to: /tmp/radar/logs/radar-server.log
        size: 10
        rotations: 3

    polling time: 300
    pidfile: /tmp/radar-server.pid
    checks: /tmp/radar/server/checks
    contacts: /tmp/radar/server/contacts
    monitors: /tmp/radar/server/monitors
    plugins: /tmp/radar/server/plugins


* listen : The listen options specifies the address and port number where
  Radar server is going to listen for new clients. At the moment only IPv4
  addresses are supported. The default values are to listen on localhost
  and port 3333.

* run as : On UNIX platforms this option tells Radar the effective user
  and group that the process should run as. This is a basic security
  consideration to allow Radar to run with an unprivileged user. The
  specified user should not be a able to login to the system.
  The default user and group is radar. This option does not apply to
  Windows platforms.

* polling time : This tells Radar the frequency of the execution of checks.
  It is expressed in seconds. By default Radar will poll all its clients
  every 300 seconds (that is five minutes). You're not allowed to specify
  values under one second. Fractions of a second are allowed so you can
  poll your clients let's say every 10.5 seconds.

* log : Radar will log all of its activity in this file. So if you
  feel that something is not working properly this is the place to look
  for any errors. Note that in the example there are two additional options :
  size and rotations. They indicate the maximum size (in MiB) that a log
  should grow, when its size goes beyond that amount then is rotated (backed
  up) and new logs are written to a new file. By default Radar sets a maximum 
  of 100 MiB for the log file and rotates it at most 5 times.

* pid file : On UNIX platforms this file holds the PID of the Radar
  process. When Radar starts it will record its pidfile here and when
  it shuts down this file is deleted. Pid files are not recorded on Windows
  platforms.

* checks, contacts, monitors, plugins : All these set of options tell
  Radar where to look for checks, contacts, monitors and plugins.
  They're just directory names. Radar does not impose on you any layout on these
  directories. This means that you are free to put configurations on any
  file on any directory below the ones you defined.
  The only requirement is that you are not allowed to mix for example
  contacts or contact groups with other components such as checks or check
  groups. Every directory is designed to contain specific elements.
  These set of directories are platform dependant. 
  
Let's now take a look at a minimum configuration. Every platform has a
default configuration and the options that are different from one another
are the ones that are platform dependant.

.. code-block:: yaml

    listen:
        address: 192.168.0.100

    polling time: 60

As you can see from the example most of the options are not defined. They
are not really missing, if you don't specify an option it will take its
default value. This means that you only need to worry about the options
you want to modify. The above example will poll clients every minute and
listen on 192.168.0.100:3333.


Checks configuration
--------------------

As commented above all checks and check groups definitions are expected to be
found in the checks defined directory.

How checks are defined ? Each check is defined as follows :

.. code-block:: yaml

    - check:
        name: CHECK NAME
        path: PATH TO CHECK
        args: CHECK ARGUMENTS

Let's review each parameter of a check definition :

* name : Each check must be uniquely identified. This is the purpose of the
  name parameter, it acts as a unique identifier. You can use whatever name
  you like. This parameter is mandatory.

* path : The full filesystem path to the check. If this path is not absolute
  then the check is looked up in the client's defined check directory.
  This parameter is mandatory.

* args : This parameter is used to specify any additional arguments that
  you need to pass to the check. This parameter is optional.

Let's now move on defining check groups. Check groups can be defined in two
different ways, let's see the first one :

.. code-block:: yaml

    - check group:
        name: CHECK GROUP NAME
        checks:
            - check:
                name: CHECK NAME
                path: PATH TO CHECK
                args: CHECK ARGUMENTS

You define a check group by giving that group a name and a set of checks
that make up that group. This allows you to reference a check group later on
when you define monitors. Check groups are useful because you define only
once a group and then use it in any number of monitors.

Let's now take a look at a second way of defining a check group :

.. code-block:: yaml

    - check:
        name: CHECK NAME
        path: PATH TO CHECK
        args: CHECK ARGUMENTS

    - check group:
        name: CHECK GROUP NAME
        checks:
            - check:
                name: CHECK NAME

In this example we've defined a check first and referenced it later from a
check group. This is perfectly valid and is actually a very convenient way to
define check groups. Why ? Let's suppose that you have two or more check
groups that are very similar but some of them perform additionally other
checks, then by defining checks individually and referencing them allows
you to define checks once and use them in as many groups as you want making
the overall configuration shorter and easier to understand.
Note that the check definition could also had been defined after the check
group because Radar does not care about definition order. Being that said
the above configuration is equal to :

.. code-block:: yaml

    - check group:
        name: CHECK GROUP NAME
        checks:
            - check:
                name: CHECK NAME

    - check:
        name: CHECK NAME
        path: PATH TO CHECK
        args: CHECK ARGUMENTS

Here's a fragment of how a real configuration might look like :

.. code-block:: yaml

    - check group:
        name: Basic health
        checks:
            - check:
                name: Uptime
                path: uptime.py
                args: -S 300 

            - check:
                name: Ram usage
                path: ram-usage.py
                args: -O 0,1000 -W 1000,1900


    - check group:
        name: Disk usage
        checks:
            - check:
                name: Disk usage (/)
                path: disk-usage.py
                args: -p / -O 0,8 -W 8,10 -u gib

            - check:
                name: Disk usage (/home)
                path: disk-usage.py
                args: -p /home -O 0,100 -W 100,150 -u gib

Some final notes on defining checks (this actually applies to the overall
configuration) :

* Radar expects at least one check or check group to exist in the overall
  configuration. Otherwise, why use Radar if you don't want to check at
  least one resource ?

* Checks and check groups are allowed to be repeated and Radar won't complain
  at all. However there are no guarantees at all which of the repeated
  check or check groups Radar will keep. The rule is that you must not duplicate
  check or check groups names.

* As stated before the order of definition does not matter because Radar will
  first build all of its checks and then proceed to build all the check groups.
  The same applies for contacts and contact groups.

* If you have a relatively big configuration then it might be useful to split
  it among different files and in some cases among directories. Remember
  that Radar does not impose you any restrictions on this.


Contacts configuration
----------------------

If you understood how checks and checks groups are defined then defining
contacts and contact groups is exactly the same !

Here's an example of a contact definition :

.. code-block:: yaml

    - contact:
        name: CONTACT NAME
        email: CONTACT EMAIL
        phone: CONTACT PHONE NUMBER

* name : Each contact must be uniquely identified. This is the purpose of the
  name parameter, it acts as a unique identifier. You can use whatever name
  you like. This parameter is mandatory.

* email : The email of the contact you're defining. Radar won't check at
  all if the defined email address is valid, so be careful !
  This parameter is mandatory.

* phone : This is the phone number of the contact. Radar won't check
  if this is a valid phone number. This parameter is optional.

Let's see a contact group definition :

.. code-block:: yaml

    - contact group:
        name: CONTACT GROUP NAME
        contacts:
            - contact:
                name: CONTACT NAME
                email: CONTACT EMAIL
                phone: CONTACT PHONE NUMBER

Compare the above definitions (against checks and check groups). You'll realize
that they are almost identical, of course the identifiers for each component are
different but the same idea remains : you can compose contact groups as
you like and reference contacts from any contact group.

Here's a fragment of how a real configuration might look like :

.. code-block:: yaml

    - contact group:
        name: Sysadmins
        contacts:
            - contact:
                name: Hernan Liendo
                email: hernan@invader
            - contact:
                name: Javier Liendo
                email: javier@invader
            - contact:
                name: Lucas Liendo
                email: lucas@invader

There is one little difference between checks and contacts definitions. In
some scenarios it might not be needed to notify any contact at all, so Radar
allows you to leave contacts empty, in other words defining contacts and
contact groups is completely optional.


Monitors configuration
----------------------

Once you have defined all your contacts and checks the last step is to
define monitors. Monitors are the way to tell Radar which hosts to watch,
what to check and who notify.

Let's walk through a real example :

.. code-block:: yaml

    - monitor:
        hosts: [localhost, 192.168.0.101 - 192.168.0.200]
        watch: [Basic health, Disk usage]
        notify: [Sysadmins]

The above example is telling Radar to monitor localhost and all hosts that
are in the 192.168.0.101 - 192.168.0.200 range and to check for Basic health,
Disk usage and to notify Sysadmins. So to define monitors you basically have :

.. code-block:: yaml

    - monitor:
        hosts: [HOSTNAME | IP | IP RANGE, ...]
        watch: [CHECK | CHECK GROUP, ...]
        notify: [CONTACT | CONTACT GROUP, ...]

* hosts : There are three different way to specify hosts. You can specify
  a single host by its IPv4 (this if the preferred way) or by its
  hostname. The last way to define hosts is using an IPv4 range. This is
  useful for example if you want to run the same checks on a set of hosts.
  Ranges are specified by its start, a hyphen and its end ip. The initial
  and ending hosts are included in the range.

* watch : This is a list of checks or check groups to be run on the monitored
  hosts. You only need to reference previously defined checks or check
  group names.

* notify : Same as above but for contacts. You need to reference a list of
  previously defined contacts or contact groups.

Note that the hosts, watch and notify parameters are defined within squared
brackets. Don't forget this when defining monitors ! This is the only place
where we use a list (more precisely a YAML list) of elements.

You can include as many monitors as you want on each file. There are no
restrictions. You need to be careful when you reference checks and
contacts in the monitors definition because Radar will not validate
the referenced checks and contacts. This means that if you reference
a contact, contact group, check or check group that does not exist Radar
won't complain. All references in monitors are case sensitive so you
also need to be aware about this, the best practice to avoid this kind of
issue is to stick to a rule (e.g. always lower case references, camel case,
etc).

You may be wondering under which conditions Radar knows if it should notify
its contacts. The Radar core does not handle (and does not care) this, but
plugins might do. Every time a Radar client replies the server this information
is passed to all defined server plugins.
If you have a notification plugin installed (e.g. an email notification plugin)
it will probably inspect the current and previous status of a check to decide
if it should notify the affected contacts.

Don't worry if you don't want to write a Radar plugin (you don't have to,
although you're encouraged to at least understand how a plugin works and how
it should be designed).


Plugins configuration
---------------------

Radar server relies on plugins to perform certain actions. For example
assume that you want to notify your contacts by SMS and you also want
to be able to store all your checks data to a relational databse.
So it might be perfectly reasonable to ask yourself how to do that with Radar.

Radar does not provide any built-in mechanisms to do these kind of things 
because that responsability is left to plugins. For the moment we're not
going to describe how to write a plugin but how to install them.

As described previously there is one plugin directory defined in the main
configuration file. This directory holds all the plugins managed by Radar.
How is the layout of this directory ? If you've read previous sections
you noticed that you have full freedom to layout monitors, checks and contacts
directories. This is not the case for the plugins directory.

Let's assume that your plugins directory is : /tmp/Radar/server/plugins.
Then you have a bunch of plugins you want install. Simply copy all of them
to that directory.

The layout of the plugins directory might look something like this :

.. code-block:: bash

    /tmp/Radar/server/plugins
        /some-plugin
            /__init__.py
        /another-plugin
            /__init__.py
            /another-plugin.yml
        ...

Every plugin must be contained within one directory below the defined
plugins directory. Some plugins might contain configurations as well (from
the above example 'another-plugin' seems to have its own YAML configuration file).
Check each plugin's documentation to figure out the scope of a plugin and
how can you adjust it to fit your needs.
