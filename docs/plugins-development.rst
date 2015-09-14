Plugins development
===================

We're now going to describe plugin development. Although you may think
that this might be a complex task, a lot of effort has been put in the
design of this part of Radar so you can easily write a plugin.
You will need to at least understand a little of Python and object oriented
programming.

Even if you're not proficient with Python or object oriented programming
keep reading and decide by yourself if writing a Radar plugin is a
difficult task.


Introduction
------------

When you first launch Radar all plugins are instantiated, that is for every
plugin that Radar finds in its plugins directory it tries to create an
object. This isn't just any object, it has to comply somehow with what
Radar expects to be a valid plugin. If Radar instantiates a certain plugin
without problems then it proceeds to configure it. After it has been
configured it is appended to a set of plugins.

When the server receives a check reply every plugin is sequentially invoked
passing it some information. That's all Radar does, from that point (when
your plugin receives a check reply) you have partial control on what is done.
When all plugins finish processing a certain reply full control is regained
by Radar. This process repeats indefinitely until of course you shut down Radar.

We've just described how Radar processes plugins. We're now going to take
a look at how a very minimal plugin is written and what considerations
should be taken at development time.

Let's take a look at a minimal plugin and describe the key points.

Take a look a this piece of Python code :

.. code-block:: python

    from radar.plugin import ServerPlugin

    class DummyPlugin(ServerPlugin):

        PLUGIN_NAME = 'Dummy plugin'

        def on_start(self):
            self.log('Starting up.')

        def on_check_reply(self, address, port, checks, contacts):
            self.log('Received check reply from {:}:{:}.'.format(address, port))

        def on_shutdown(self):
            self.log('Shutting down.')


As explained before, a Radar plugin needs to comply with certain requirements.
In first place every plugin must inherit from the ServerPlugin class.
You achieve that by importing the ServerPlugin class and creating a new
class and inheriting from ServerPlugin. This is achieved in the first two
lines of the above example.

Every plugin must have a name. We define this in the PLUGIN_NAME class attribute.
Every plugin is uniquely identified by its name and a version. If you don't
specify a version then it defaults to 0.0.1. To define a version you only
need to overwrite the PLUGIN_VERSION class attribute with the desired value.
In this exaple we only defined the plugin name.

The example shows three methods. The on_start() method is invoked by Radar when
the plugin is initialized, so if you want to define any instance attributes
or acquire resources, this is one place to do that.

In a similar way the on_shutdown() method is called when Radar is shutdown,
this method's purpose is to gracefully release any resources that you might
have acquired during the life of the plugin.

We have only one remaining method: on_check_reply(). This is where the
action takes place and is your entry point to perform any useful work.
For every reply that the Radar server receives you'll get :

* address : The IP address of the Radar client that sent the check reply.
  This is a string value

* port : The TCP port of the Radar client that sent the check reply.
  This is an integer value.

* checks : A Python list containing Check objects that were updated by
  the server. This list will always respond to a given monitor, that means
  that the list of checks you got belongs to one and only one monitor.

* contacts : A Python list containing Contact objects that were related
  due to the replied checks. This list will always respond to a given
  monitor, that means that the list of contacts you got belongs to one
  and only one monitor.

In this minimal example we're basically doing nothing, just recording a few
things to the Radar log file using the log() method. A Radar plugin is just
a Python class where you can code anything you want.

Is that all you need to know to develop a plugin ? Basically yes, but there
is one more feature that can be extremely useful in some cases.
Let's say you want to allow your users configure your plugin, that is let
your users modify certain parameters of your plugin. If you've just wrote
a plugin that connects to a database to insert data then it is not a good
practice to modify the database parameters directly from the plugin code.
Radar plugins come with a YAML mapper for free.

What does it do ? Very simple : given a YAML filename it will map it to
a Python dictionary. This way you only specify the filename of your
configuration file, set the values that you need in that file and then
retrieve them from a dictionary. The only requirement is that this file
must be in your plugin directory !

To use it simply set the PLUGIN_CONFIG_FILE class attribute with the
configuration filename and that's it. How do you read those values ?
Easy again, just access the config dictionary. Let's see an example.

Given this YAML file (called dummy.yml) :

.. code-block:: yaml

    connect:
        to: localhost
        port: 2000


Now we have an different version of the dummy plugin :

.. code-block:: python

    from socket import create_connection
    from radar.plugin import ServerPlugin

    class DummyPlugin(ServerPlugin):

        PLUGIN_NAME = 'Dummy plugin'
        PLUGIN_CONFIG_FILE = ServerPlugin.get_path(__file__, 'dummy.yml')

        def _connect(self):
            address = self.config['connect']['to']
            port = self.config['connect']['port']
            self._fd = create_connection((address, port))

        def _disconnect(self):
            self._fd.close()

        def on_start(self):
            self._connect()

        def on_check_reply(self, address, port, checks, contacts):
            """ Perform some useful work here """

        def on_shutdown(self):
            self._disconnect()


This is still a very useless example ! However note, that I've set the
PLUGIN_CONFIG_FILE to hold the filename of the YAML (dummy.yml in this case)
and that I use the values that were read from that file in the _connect()
method. Note the use of the get_path() static method to properly reference
the YAML file.

Before we end up this section you may be wondering : How should I use the
checks and contacts lists in the on_check_reply() method ?

Radar has (internally) among many abstractions have two that you will use directly
in any plugin : Contact and Check. Whenever you get a reply you get a list
that contains contact objects and another list that contains check objects.

Contact and check objects have some attributes that you can read to
perform some work. For example : every contact object contains a name,
an email an optionally a phone number. The following piece of code
shows how to read any useful value (both from a contact and a check) :

.. code-block:: python

    def on_check_reply(self, address, port, checks, contacts):
        """ Accesing properties of a check and contact object """

        """ Contact properties. """
        contact_name = contacts[0].name
        email = contacts[0].email
        phone = contacts[0].phone

        """ Check properties. """
        check_name = check[0].name
        path = check[0].path
        args = check[0].args
        details = check[0].details
        data = check[0].data
        current_status = check[0].current_status
        previous_status = check[0].previous_status


Guidelines
----------

All of the considerations taken to develop checks also apply to plugins.
So if in doubt review those guidelines in the checks development section.

Also note that Radar expects to find a unique plugin class per plugin
directory. It is a requirement that this class to be present only in the
__init__.py file in that directory. Despite this minor limitation you're
allowed to code in as many different directory/files inside the plugin
directory as you want.

For example assuming that you wrote a plugin called A-Plugin then, you
could have the following file hierarchy :

.. code-block:: bash

    /A-Plugin
        /__init__.py
        /a-plugin.yml
        /local_module_a
            /__init__.py
            /some_file_module_a.py
        /local_module_b
            /__init__.py
            /some_file_module_b.py

Then .../A-Plugin/__init__.py file must contain exactly one class that inherits
from the ServerPlugin class.
        

Example
-------

If you still want to see a more elaborated example (actually something
useful, right ?) then you can take a look to an email notifier plugin here.
This plugin will notify its contacts when a check has any of its status
(current or previous) distinct from OK.
