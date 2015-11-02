Installation
============

At the moment Radar is only available from its source code from `Github <https://github.com/lliendo/Radar>`_.
As the project evolves it will be eventually added to `PyPI <https://pypi.python.org/pypi>`_.

PyPI packages will be delivered when the project is assured to be stable.
Current Radar's status is ALPHA.

To install Radar from Github (you will need `GIT <https://git-scm.com/>`_ installed on your system)
open a terminal or command prompt and run :

.. code-block:: bash

    git clone https://github.com/lliendo/Radar.git
    cd Radar
    python setup.py install

Alternatively you can download Radar as a `.zip <https://github.com/lliendo/Radar/archive/master.zip>`_ file, extract it and then run :

.. code-block:: bash

    python setup.py install

from the project's root directory.


Checking the installation
-------------------------

You can check that Radar was successfully installed by running from the
command line :

.. code-block:: bash

    radar-client.py -v
    radar-server.py -v

This will display the current version of Radar (client and server)
installed on your system. If you see these versions then you got both
client and server successfully installed, otherwise something went wrong.

By default Radar expects to find configuration files in well-defined places.
These directories are platform dependent (you can check these defaults from
the platform defaults section of this document).

It is a good practice to use these default directories. Of course if you don't
want to use those locations you can change them from the main configuration
file.

Radar only takes its main configuration file to be able to run. 
If you want to override the default main configuration file path you can
invoke Radar this way :

.. code-block:: bash

    radar-client.py -c PATH_TO_MAIN_CONFIGURATION_FILE
    radar-server.py -c PATH_TO_MAIN_CONFIGURATION_FILE

The -c option specifies an alternate main configuration file.


Adding restricted account
-------------------------

As a basic security measure it is recommended to create a restricted account to
be used by Radar. By default Radar assumes that the name of this account is
'radar' (but you can use whatever account you want).


Unix OS
~~~~~~~

For any of the following systems :

1. Open a new console.
2. Switch to the root user using the `su <https://en.wikipedia.org/wiki/Su_%28Unix%29>`_ command.

* GNU/Linux systems typically have the 'useradd' commands to create a new user :

.. code-block:: bash

    useradd radar -r -s /usr/sbin/nologin -c "Radar user"


* On FreeBSD systems, run :

.. code-block:: bash

    pw groupadd radar
    pw adduser radar -g radar -d /nonexistent -s /usr/sbin/nologin -c "Radar user"


* On OpenBSD systems, run :

.. code-block:: bash

    groupadd radar
    useradd -g radar -s /sbin/nologin -c "Radar user" radar


3. As a last step, verify that you are not allowed to login with the 'radar' user.


Windows platforms
~~~~~~~~~~~~~~~~~

On Windows platforms little more work is needed. The following steps apply for
Windows 7 Professional or better :

1. Add a new user named 'radar' from Control Panel -> User Accounts.
2. Open GPEDIT.MSC (a.k.a. Local Group Policy Editor).
3. From the left side pane navigate through :

.. code-block:: bash

    Local Computer Policy 
     └─ Computer Configuration
         └─ Windows Settings 
             └─ Security Settings 
                 └─ Local Policies 
                     └─ User Right Assignment

4. On the right side pane locate the 'Deny log on locally' policy.
5. Right clic on 'Deny log on locally' and clic on Properties.
6. Clic the 'Add User or Group' button to add the radar user account.
7. On the text box type in : radar. Now clic the 'Check Names' button and then clic on 'OK'.
8. Repeat steps 5 and 6 but for the 'Deny log on through Remote Desktop Services' policy.
9. Log out and verify that you are not allowed to login with the 'radar' user (locally and remotely).


Setting up Radar
----------------

Before you start configuring Radar I recommend you to read the documentation
as some options may not make full sense. If you've already read the docs
then go ahead and start configuring Radar.

Radar comes with two useful scripts to help you configure it the first time.

To configure the server just run :

.. code-block:: bash

    radar-server-config.py

This script will ask you for some initial values. For every option you can
leave its default (these values are shown in squared brackets) value by pressing
Enter.

To configure the client run :

.. code-block:: bash

    radar-client-config.py

After you run those scripts the main configuration file gets generated in the
path that you chose. Note that the resulting YAML file may not look as tidy
as the ones presented in the rest of documentation. This is because the PyYAML
library does not care about new lines and does not handle element ordering.
Something similar happens on the order in which the options are scanned from
the console.
You can run these scripts as many times as you want but be aware that if you
point to the same output files they'll be completely overwritten.


Configuring startup scripts
---------------------------

Depending on which OS you're using here are instructions to make Radar (server or
client) automatically start at system boot.

Unix OS
~~~~~~~

For any of the following systems :

1. Open a new console.
2. Switch to the root user using the `su <https://en.wikipedia.org/wiki/Su_%28Unix%29>`_ command.

* For GNU/Linux (SysV) :

Copy the radar-server init script :

.. code-block:: bash

    cd Radar/init_scripts/linux/sysv
    cp radar-server /etc/init.d

Make sure that the owner/group of the file is root :

.. code-block:: bash

    chown root.root /etc/init.d/radar-server

Make sure the file permissions are :

.. code-block:: bash

    chmod u=rwx,go=rx /etc/init.d/radar-server

Make symlinks :

.. code-block:: bash

    cd /etc/rc2.d/
    ln -s ../init.d/radar-server S99radar-server

The above command adds automatic startup for runlevel 2 (repeat the last step
for different runlevels as you need).

Before starting the service :

1. Open the /etc/init.d/radar-server file.
2. Verify that the DAEMON_ARGS variable points to the same main configuration file
   that you setup with the radar-server-config.py configuration script or change
   that path as you need.

Start the service :

.. code-block:: bash

    /etc/init.d/radar-server start

To add the Radar client on system startup follow the same steps but replace 'radar-server'
by 'radar-client'.


* For GNU/Linux (Systemd) :

Copy the radar-server.service and radar-server files :

.. code-block:: bash

    cd Radar/init_scripts/linux/systemd
    cp radar-server.service /lib/systemd/system
    cp radar-server /etc/default

Make sure that the owner/group of the file is root :

.. code-block:: bash

    chown root.root /lib/systemd/system/radar-server.service /etc/default/radar-server

Make sure the file permissions are :

.. code-block:: bash

    chmod u=rw,go=r /lib/systemd/system/radar-server.service /etc/default/radar-server

Enable the unit :

.. code-block:: bash

    systemctl enable radar-server.service

Before starting the service :

1. Open the /etc/default/radar-server file.
2. Verify that the RADAR_SERVER_OPTS variable points to the same main configuration file
   that you setup with the radar-server-config.py configuration script or change
   that path as you need.

Start the service :

.. code-block:: bash

    systemctl start radar-server.service

To add the Radar client on system startup follow the same steps but replace 'radar-server'
by 'radar-client'.
