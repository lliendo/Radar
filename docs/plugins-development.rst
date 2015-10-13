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
When all plugins finish processing a certain reply, full control is regained
by Radar. This process repeats indefinitely until of course you shut down Radar.

We've just described how Radar processes plugins. We're now going to take
a look at how a minimal plugin is written and what considerations should be
taken at development time.

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
  This is a string value.

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

If you want to verify this small plugin, then :

1. Create a directory called dummy-plugin (or name it as you want).
2. Create an __init__.py file inside this directory and copy the above code to it.
3. Move the directory you created in step one to your Radar server's plugins directory.
4. If Radar is already running then you'll need to restart it.
5. Make sure you get a new entry in the log every time a check reply arrives.

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
Suppose you want to proxy every reply to another service using a UDP socket.

Given this YAML file (called udp-proxy.yml) :

.. code-block:: yaml

    forward:
        to: localhost
        port: 2000


Let's adjust our initial example :

.. code-block:: python

    from socket import socket, AF_INET, SOCK_DGRAM
    from json import dumps
    from radar.plugin import ServerPlugin


    class UDPProxyPlugin(ServerPlugin):

        PLUGIN_NAME = 'UDP-Proxy'
        PLUGIN_CONFIG_FILE = ServerPlugin.get_path(__file__, 'udp-proxy.yml')
        DEFAULT_CONFIG = {
            'forward': {
                'to': '127.0.0.1',
                'port': 2000,
            }
        }

        def _create_socket(self):
            fd = None

            try:
                fd = socket(AF_INET, SOCK_DGRAM)
            except Exception, e:
                self.log('Error - Couldn\'t create UDP socket. Details : {:}.'.format(e))

            return fd

        def _disconnect(self):
            self._fd.close()

        def on_start(self):
            self._fd = self._create_socket()

        def _forward(self, address, checks, contacts):
            serialized = {
                'address': address,
                'checks': [c.to_dict() for c in checks],
                'contacts': [c.to_dict() for c in contacts],
            }

            payload = dumps(serialized) + '\n'
            self._fd.sendto(payload, (self.config['forward']['to'], self.config['forward']['port']))

            return payload

        def on_check_reply(self, address, port, checks, contacts):
            try:
                self._forward(address, checks, contacts)
            except Exception, e:
                self.log('Error - Couldn\'t forward data. Details : {:}.'.format(e))

        def on_shutdown(self):
            self._disconnect()


Ok, now we have a useful plugin. Every time we receive a reply we simply forward
it using a UDP socket. Note in this example that I've set the PLUGIN_CONFIG_FILE
to hold the filename of the YAML (udp-proxy.yml in this case) and that I use the
values that were read from that file in the _forward() method. Also note the
use of the get_path() static method to properly reference the YAML file and that
I convert every check and contact to a dictionary before serializing and sending
the data. The to_dict() method dumps every relevant attribute of each object to
a Python dictionary.

Now take a look at the DEFAULT_CONFIG class attribute. This class attribute allows
you to set default values for your plugin configuration provided that a user does
not set a certain parameter. Radar (internally) will merge the values read from
the file and those found in the DEFAULT_CONFIG class attribute. Setting this
dictionary is completly optional. This can be very useful for example if a user
forgets to create a configuration file for your plugin, by using a default config
you make sure that at least your plugin won't fail due to a missing configuration.

To get this example running follow the same steps we described for the DummyPlugin
and also create a file named udp-proxy.yml that contains the YAML commented above.
Don't forget to put this file inside the same directory where __init__.py is.

If you want to see these replies you'll probably need a tool like `Netcat <http://nc110.sourceforge.net/>`_.
If you indeed have Netcat installed on your system then open up a console and run :

.. code-block:: bash

    nc -ul 127.0.0.1 2000


The above command will capture and display UDP datagrams destined for localhost port 2000.

Before we end up this section you may be wondering : How should I use the
checks and contacts lists in the on_check_reply() method ?

Radar has (internally) among many abstractions two that you will use directly
in any plugin : Contact and Check. Whenever you get a reply you get a list
that contains contact objects and another list that contains check objects.

Contact and Check objects have some attributes that you can read to
perform some work. For example : every contact object contains a name,
an email and optionally a phone number. The following piece of code
shows how to read any useful value (both from a contact and a check) :

.. code-block:: python

    from radar.plugin import ServerPlugin


    class TestPlugin(ServerPlugin):

        PLUGIN_NAME = 'Test plugin'

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


Note that in the above example we're only inspecting the first contact and check.
Remember that you always receive two lists, so you may need to iterate them in
order to achieve your plugin's task.

One last thing. If you inspect the current_status and the previous_status attributes 
of a check you'll notice that both of them are integers. If you need to convert those
values to their respective names, here's how to do that :

.. code-block:: python

    from radar.plugin import ServerPlugin
    from radar.check import Check


    class TestPlugin(ServerPlugin):

        PLUGIN_NAME = 'Test plugin'

        def on_check_reply(self, address, port, checks, contacts):
            """ Converting check reply status values to string codes. """

            current_status = Check.get_status(check[0].current_status)
            previous_status = Check.get_status(check[0].previous_status)


The conversion is done using the static Check.get_status() method. Note that
I've also imported the Check class in the second line of the example. Now
current_status and previous_status hold any of the valid string codes that a
check can return (OK, WARINING, SEVERE or ERROR).


Guidelines
----------

All of the considerations taken to develop checks also apply to plugins.
So if in doubt review those guidelines in the checks development section.

Also note that Radar expects to find a unique plugin class per plugin directory.
It is a requirement that this class to be present only in the __init__.py file in
that directory. Despite this minor limitation you're allowed to code in as many
different directory/files inside the plugin directory as you want.

For example, assuming that you wrote the ProxyPlugin described above then, you
could have the following file hierarchy :

.. code-block:: bash

    /ProxyPlugin
        /__init__.py
        /proxy.yml


If your ProxyPlugin also depended on more modules then you could had :

.. code-block:: bash

    /ProxyPlugin
        /__init__.py
        /proxy.yml
            /another_module
                /__init__.py
                /another_file.py


Example
-------

If you still want to see a more elaborate example (actually something useful, right ?)
then you can take a look to an email notifier plugin `here <https://github.com/lliendo/Radar-Plugins>`_.
This plugin will notify its contacts when a check has any of its status
(current or previous) distinct from OK.
