Installation
============

    At the moment Radar is only available from its source code from Github.
    As the project evolves it will be eventually added to `pip <https://pip.pypa.io/en/stable/>`_.

    Pip packages will be delivered when the project is assured to be stable.
    Current Radar's status is ALPHA.

    To install Radar from Github from Github (you will need `GIT <https://git-scm.com/>`_ installed on your system)
    then open a terminal and run :

        .. code-block:: bash

            git clone https://github.com/lliendo/Radar.git
            cd Radar
            python setup.py install


Checking the installation
-------------------------

    You can check that Radar was successfully installed by running from the
    command line :

        .. code-block:: bash

            radar-client -v
            radar-server -v

    This will display the current version of Radar (client and server)
    installed on your system. If you see these versions then you got both
    client and server successfully installed, otherwise something went wrong.

    By default Radar expects to find configuration files in well-defined places.
    These directories are platform dependant (you can check these defaults from
    the platform defaults section of this document).

    It is a good practice to use these default directories. Of course if don't
    want to use those locations you can change them from the main configuration
    file.

    Radar only takes its main configuration file to be able to run. 
    If you want to override the default main configuration file path you can
    invoke Radar this way :

        .. code-block:: bash

            radar-client -c PATH_TO_MAIN_CONFIGURATION_FILE
            radar-server -c PATH_TO_MAIN_CONFIGURATION_FILE

    The -c option specifies an alternate main configuration file.
